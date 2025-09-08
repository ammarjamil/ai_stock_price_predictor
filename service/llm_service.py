


from langchain.prompts import PromptTemplate
from template.prompt_template_new import prompt
from langchain_groq import ChatGroq
import os


class LLMService:
    """Service for LLM-powered analysis"""

    def __init__(self, model: str = "openai/gpt-oss-20b"):
        """Initialize the system with Groq LLM"""
        try:
            self.model = model
            self.llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name=model, temperature=0.3)
            print(f"Initialized with model: {model}")
        except Exception as e:
            raise Exception(f"Failed to initialize Groq model '{model}': {e}")
        
        # Create a more focused prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["coin_data"],
            template=prompt
        )

    def analyze_coin(self, coin_data: str) -> dict:
        """Analyze news using Groq LLM"""
        try:
            # prompt = self.create_analysis_prompt(headline, content, symbol)
            formatted_prompt = self.prompt_template.format(coin_data=coin_data)

            if(os.getenv("DEBUG").lower() == "true"):
                with open("prompt.txt", "w", encoding="utf-8") as f:
                    f.write(formatted_prompt)
            response = self.llm.invoke(formatted_prompt)

            print(f"Received response, length: {len(response.content)} characters")
            if(os.getenv("DEBUG").lower() == "true"):
                with open("response.txt", "w", encoding="utf-8") as ff:
                    ff.write(response.content)
                
            # # Parse JSON response
            # response_text = json.loads(json_str)
            return True
        
                
        except Exception as e:
            print(f"LLM analysis error: {e}")
            return False