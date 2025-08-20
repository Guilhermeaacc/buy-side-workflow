import openai
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGeneratorAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        self.report_generation_prompt = """# COMPREHENSIVE BUSINESS REPORT GENERATOR

## ROLE
You are an executive-level business analyst responsible for creating comprehensive, professional reports that synthesize multiple analyses into a cohesive, executive-ready document.

## TASK
Generate a beautifully formatted, comprehensive business report that merges all provided analyses into a single, professional document suitable for investment decisions and executive review.

## OUTPUT FORMAT REQUIREMENTS

Use this EXACT structure with markdown formatting:

# 📊 Comprehensive Business Analysis Report

## 🎯 Executive Summary
[Write a concise 2-3 paragraph executive summary that synthesizes the key findings from all analyses. Focus on investment potential, key metrics, and strategic insights.]

---

## 🎪 Pitch Deck Analysis
[Insert the complete pitch deck analysis here, maintaining its original formatting]

---

## 🚀 Product Overview
[Insert the complete product analysis here, maintaining its original formatting]

---

## 🌐 Market Research & Intelligence
[Insert the complete web research analysis here, maintaining its original formatting]

---

## 📈 Market Size & Opportunity
[Insert the complete market size analysis here, maintaining its original formatting]

---

## 💡 Strategic Insights & Recommendations

### Key Strengths
- [Synthesize 3-4 key strengths from all analyses]

### Market Opportunities
- [Synthesize 3-4 key market opportunities]

### Investment Considerations
- [Synthesize 3-4 key investment considerations]

### Risk Factors
- [Identify 2-3 potential risk factors based on the analyses]

---

## 📋 Report Summary

**Company:** [Extract company name]
**Industry:** [Identify industry/sector]
**Analysis Date:** [Current date]
**Report Sections:** 4 comprehensive analyses + strategic synthesis

---

*This report was generated using AI-powered analysis of pitch deck materials and real-time market research.*

## FORMATTING INSTRUCTIONS
- Use clean markdown formatting with proper headers
- Maintain professional tone throughout
- Preserve original formatting of individual analyses
- Add visual separators (---) between sections
- Use emojis in headers for visual appeal
- Ensure consistent spacing and readability
- Bold important numbers and key points
- Keep the executive summary concise but comprehensive"""

    async def generate_complete_report(self, pitchdeck_analysis: str, product_analysis: str, 
                                     web_research: str, market_analysis: str, company_name: str = None) -> str:
        """
        Generate a comprehensive business report by merging all agent analyses.
        
        Args:
            pitchdeck_analysis: Output from PitchDeckAgent
            product_analysis: Output from ProductAgent  
            web_research: Output from WebResearchAgent
            market_analysis: Output from MarketSizeAgent
            company_name: Optional company name from web research
        
        Returns:
            Formatted comprehensive business report
        """
        try:
            logger.info("🎯 Starting comprehensive report generation...")
            logger.info(f"📄 Input lengths - Pitch: {len(pitchdeck_analysis)}, Product: {len(product_analysis)}")
            logger.info(f"📄 Input lengths - Research: {len(web_research)}, Market: {len(market_analysis)}")
            
            # Prepare the complete input for the LLM
            complete_input = f"""Please generate a comprehensive business report using the following analyses:

COMPANY NAME: {company_name if company_name else "Not specified"}

PITCH DECK ANALYSIS:
{pitchdeck_analysis}

PRODUCT ANALYSIS:
{product_analysis}

WEB RESEARCH ANALYSIS:
{web_research}

MARKET SIZE ANALYSIS:
{market_analysis}

Please follow the exact format specified in your system prompt to create a professional, executive-ready report."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": self.report_generation_prompt
                    },
                    {
                        "role": "user",
                        "content": complete_input
                    }
                ],
                temperature=0.1,
                max_tokens=4000  # Ensure we have enough tokens for a comprehensive report
            )
            
            comprehensive_report = response.choices[0].message.content
            
            logger.info(f"✅ Comprehensive report generated successfully")
            logger.info(f"📊 Report length: {len(comprehensive_report)} characters")
            logger.info(f"📄 Report preview: {comprehensive_report[:300]}...")
            
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"❌ Report generation error: {str(e)}")
            raise Exception(f"Failed to generate comprehensive report: {str(e)}")