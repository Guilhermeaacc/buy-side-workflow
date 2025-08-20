import openai
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketSizeAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def format_analysis(self, raw_analysis: str) -> str:
        """
        Format the raw market analysis into a beautiful, professional presentation.
        """
        try:
            logger.info("🎨 Starting analysis formatting...")
            logger.info(f"📄 Raw analysis length: {len(raw_analysis)} characters")
            
            formatting_prompt = f"""You are a professional text writer and business analyst. Your task is to take raw market research data and transform it into a beautifully formatted, professional text showing all the data in a clear and easy to understand way.

RAW MARKET ANALYSIS:
{raw_analysis}

INSTRUCTIONS:
Transform this raw analysis into a polished, professional format optimized for executive presentation and frontend display.

FORMATTING REQUIREMENTS:

1. **Visual Hierarchy**: Use clear markdown headers (##, ###) for perfect section organization
2. **Data Emphasis**: Bold important numbers, percentages, and market sizes
3. **Professional Structure**: Logical flow that tells a complete story

FORMATTING STYLE:
- Use bullet points for lists and key features
- Add relevant emojis to section headers for visual appeal
- Ensure proper spacing and readability
- Make numbers and data pop visually
- Keep paragraphs concise and impactful

YOU MUST FOLLOW THE OUTPUT FORMAT BELOW.

OUTPUT FORMAT:

# 📊 Market Size Analysis

### 🌍 TAM (Total Addressable Market)
**Market Size:** [Bold the $ amount and year]
[Clean explanation - 3 bullet points]

[Sources with links]

### 🎯 SAM (Serviceable Available Market)
**Market Size:** [Bold the $ amount and year]
[Clean explanation - 3 bullet points]

[Sources with links]

### 🔥 SOM (Serviceable Obtainable Market)
**Market Size:** [Bold the $ amount and year]
[Clean explanation - 3 bullet points]
**Market Share Assumptions:** [Bold the percentage]

[Sources with links]

## 💡 Key Insights
[Professional insights formatted as short paragraphs]"""

            # Format the analysis using GPT-5
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert presentation formatter. Transform raw business analysis into beautiful, professional presentations."
                    },
                    {
                        "role": "user",
                        "content": formatting_prompt
                    }
                ]
            )
            
            formatted_analysis = response.choices[0].message.content
            
            logger.info(f"✅ Analysis formatting completed")
            logger.info(f"📊 Formatted length: {len(formatted_analysis)} characters")
            logger.info(f"📄 Preview: {formatted_analysis[:200]}...")
            
            return formatted_analysis
            
        except Exception as e:
            logger.error(f"❌ Formatting error: {str(e)}")
            # Return raw analysis if formatting fails
            return f"# Market Size Analysis\n\n{raw_analysis}"

    async def analyze_market_size(self, extracted_text: str) -> dict:
        """
        Analyze market size using web search to get real-time market data.
        Returns comprehensive TAM/SAM/SOM analysis with current market information.
        """
        try:
            logger.info("🚀 Starting market size analysis with web search...")
            logger.info(f"📄 Analyzing text length: {len(extracted_text)} characters")
            
            # Comprehensive prompt that combines extraction and analysis
            prompt = f"""You are a senior market research analyst with access to real-time web search. 

TASK: Analyze the following pitch deck content and provide a comprehensive market sizing analysis.

PITCH DECK CONTENT:
{extracted_text}

INSTRUCTIONS:
1. First, extract key product and company information from the pitch deck
2. Then search the web for current market data, industry reports, and competitor information
3. Provide a detailed TAM/SAM/SOM analysis with real-time market data
3. Use web search to help you with this taks, epecially to get data

OUTPUT FORMAT:
Provide a comprehensive analysis with these sections:

## PRODUCT & COMPANY SUMMARY
[Brief summary of the product and company from the pitch deck. (1 paragaph)]

## MARKET SIZE ANALYSIS

### TAM (Total Addressable Market)
- Market Size: [$ amount with source and year]
- Explanation

### SAM (Serviceable Available Market) 
- Market Size: [$ amount with source and year]
- Explanation

### SOM (Serviceable Obtainable Market)
- Market Size: [$ amount with source and year]
- Explanation
- Market Share Assumptions: [% of SAM achievable]

## INSIGHTS
- Write your own insights about the analysis. (1 paragaph)

## DATA SOURCES
[List web sources used with titles and URLs]

IMPORTANT: Use web search to find the most current market data available"""

            # Make web search API call
            response = self.client.responses.create(
                model="gpt-5",
                tools=[{"type": "web_search_preview"}],
                input=prompt
            )
            
            # Get the raw analysis result
            raw_analysis = response.output_text
            
            logger.info(f"✅ Raw market analysis completed")
            logger.info(f"📊 Raw analysis length: {len(raw_analysis)} characters")
            logger.info(f"📄 Raw preview: {raw_analysis[:200]}...")
            
            # Step 2: Format the analysis for beautiful presentation
            logger.info("🎨 Starting formatting pipeline...")
            formatted_analysis = await self.format_analysis(raw_analysis)
            
            logger.info(f"✅ Complete market analysis pipeline finished")
            logger.info(f"📊 Final formatted analysis length: {len(formatted_analysis)} characters")
            logger.info(f"📄 Formatted preview: {formatted_analysis[:200]}...")
            
            return {
                "success": True,
                "market_analysis": formatted_analysis,
                "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
            }
            
        except Exception as e:
            error_msg = f"Market size analysis failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            # Return clear error without fallback
            return {
                "success": False,
                "error": error_msg,
                "message": "Web search market analysis is currently unavailable. Please try again later."
            }

    async def full_market_analysis(self, extracted_text: str) -> dict:
        """
        Main entry point for market analysis - calls the web search analysis method.
        """
        return await self.analyze_market_size(extracted_text)