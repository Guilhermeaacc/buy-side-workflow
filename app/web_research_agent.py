import openai
import httpx
import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebResearchAgent:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        
        self.company_extraction_prompt = """You are a company name extractor. Your only task is to identify and return the company name from the provided text.

INSTRUCTIONS:
- Extract only the company name from the text
- Return ONLY the company name, nothing else
- No explanations, no additional text, no formatting
- If multiple companies are mentioned, return the main company being discussed
- If no clear company name is found, return "COMPANY NOT FOUND"

Example outputs:
- "Apple"
- "Microsoft Corporation" 
- "Tesla"
- "COMPANY NOT FOUND"

Your response must be only the company name."""

    async def extract_company_name(self, extracted_text: str) -> str:
        try:
            logger.info("🔍 Starting company name extraction...")
            logger.info(f"📄 Text length: {len(extracted_text)} characters")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": self.company_extraction_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Extract the company name from this text:\n\n{extracted_text}"
                    }
                ],
                temperature=0.1
            )
            
            company_name = response.choices[0].message.content.strip()
            
            logger.info(f"✅ Company name extracted: {company_name}")
            
            return company_name
            
        except Exception as e:
            logger.error(f"❌ Company name extraction error: {str(e)}")
            raise Exception(f"Failed to extract company name: {str(e)}")

    async def research_company(self, company_name: str) -> str:
        try:
            logger.info(f"🔍 Starting research for company: {company_name}")
            
            if not self.perplexity_api_key:
                raise Exception("PERPLEXITY_API_KEY not found in environment variables")
            
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Identify news or other relevant content about this company: {company_name}. 
                        
                        The output format must be **exactly** like this (keep emojis and spacing):  
                        
                        
                        ### 📌 [Title]  

                        **Resumo**  
                        - 🔹 [Relevant point 1]  
                        - 🔹 [Relevant point 2]

                        - Date: [input the date here]
                        - [Source Name]: [input the link here]
                        """
                    }
                ]
            }
            
            response = requests.post(self.perplexity_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
            
            response_data = response.json()
            research_content = response_data["choices"][0]["message"]["content"]
            
            logger.info(f"✅ Research completed. Response length: {len(research_content)} characters")
            logger.info(f"📄 Research preview: {research_content[:200]}...")
            
            return research_content
            
        except Exception as e:
            logger.error(f"❌ Company research error: {str(e)}")
            raise Exception(f"Failed to research company: {str(e)}")

    async def full_research(self, extracted_text: str) -> dict:
        try:
            # Step 1: Extract company name
            company_name = await self.extract_company_name(extracted_text)
            
            if company_name == "COMPANY NOT FOUND":
                return {
                    "company_name": company_name,
                    "research_content": "No company name could be extracted from the provided text."
                }
            
            # Step 2: Research the company
            research_content = await self.research_company(company_name)
            
            return {
                "company_name": company_name,
                "research_content": research_content
            }
            
        except Exception as e:
            logger.error(f"❌ Full research error: {str(e)}")
            raise Exception(f"Failed to complete research: {str(e)}")