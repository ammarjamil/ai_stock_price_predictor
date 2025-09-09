from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from data.coingecko_scraper import CoinGeckoAPIScraper
from service.llm_service import LLMService
from utils.output_formatter import print_formatted_output
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize services
scraper = CoinGeckoAPIScraper()
llm_service = LLMService(model="openai/gpt-oss-20b")

@app.route('/')
def serve_index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze_coin():
    """Analyze cryptocurrency data"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        coin = data.get('coin', '').strip()
        timeframe = data.get('timeframe', 'weekly')
        
        if not coin:
            return jsonify({'error': 'Coin name is required'}), 400
        
        print(f"🚀 Analyzing {coin} with {timeframe} timeframe")
        
        # Scrape coin data
        coin_data = scraper.scrape_coin_data(coin, timeframe)
        
        if not coin_data:
            return jsonify({'error': f'Could not find data for coin: {coin}'}), 404
        
        # Format data for console output (to get formatted string for LLM)
        formatted_data = print_formatted_output(coin_data)
        
        # Get LLM analysis
        llm_analysis = None
        parsed_analysis = None
        try:
            # Capture the LLM analysis result
            if llm_service.analyze_coin(formatted_data):
                # If DEBUG is enabled, read the response from response.txt
                if os.getenv("DEBUG", "").lower() == "true":
                    try:
                        with open("response.txt", "r", encoding="utf-8") as f:
                            llm_analysis = f.read()
                            
                        # Try to parse JSON from LLM response
                        try:
                            import json
                            parsed_analysis = json.loads(llm_analysis)
                            print("✅ Successfully parsed LLM JSON response")
                        except json.JSONDecodeError as je:
                            print(f"⚠️ Could not parse LLM response as JSON: {je}")
                            # Try to extract JSON from response if it contains other text
                            import re
                            json_match = re.search(r'\{.*\}', llm_analysis, re.DOTALL)
                            if json_match:
                                try:
                                    parsed_analysis = json.loads(json_match.group(0))
                                    print("✅ Successfully extracted and parsed JSON from LLM response")
                                except json.JSONDecodeError:
                                    print("⚠️ Could not parse extracted JSON")
                                    
                    except FileNotFoundError:
                        llm_analysis = "LLM analysis completed but response file not found."
                else:
                    llm_analysis = "LLM analysis completed successfully."
            else:
                llm_analysis = "LLM analysis failed."
        except Exception as e:
            print(f"LLM analysis error: {e}")
            llm_analysis = f"LLM analysis error: {str(e)}"
        
        # Add LLM analysis to the response
        coin_data['llm_analysis'] = llm_analysis
        coin_data['parsed_analysis'] = parsed_analysis
        
        print("✅ Analysis completed successfully")
        return jsonify(coin_data)
        
    except Exception as e:
        print(f"❌ Error analyzing coin: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'coingecko_scraper': 'active',
            'llm_service': 'active'
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check required environment variables
    if not os.getenv('GROQ_API_KEY'):
        print("❌ Warning: GROQ_API_KEY not found in environment variables")
        print("💡 Make sure to set your GROQ_API_KEY in the .env file")
    
    print("🚀 Starting Cryptocurrency Analysis Web Server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔧 Press Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )