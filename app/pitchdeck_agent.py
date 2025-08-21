import openai
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PitchDeckAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.analysis_prompt = """You are a Venture Capital analyst.
Your task is to analyze the provided pitch deck and produce a structured Executive Summary that is concise, investment-oriented, and ready to be displayed on a front end.

INSTRUCTIONS

Read Carefully

Review the pitch deck text and extract the most relevant insights.

If information is missing, mark as Not specified. Never invent numbers.

Be VC-Oriented

Use precise VC/tech jargon (e.g., “B2B SaaS”, “Consumer HealthTech”, “Enterprise AI”).

Focus on clarity, conciseness, and what investors need to know at a glance.

Formatting & Style

Output must always be in Markdown.

Use short bullet points (max 1 sentence each).

Keep a professional, executive-level tone.

Sections to Output
Always follow this structure exactly:

[Insert Company Name]  
Sector: [Sector]

Quick Facts
[Insert Stage]
[HQ - City, Country (country emoji)]
[Insert Founded year]

Company Overview  
🔹 [What the company does / core mission]  
🔹 [Problem being solved / why it matters]  
🔹 [Unique value proposition / key differentiation]  

Product  
🔹 [Main product(s) or service(s)]  
🔹 [Technical Strucuture]  
🔹 [Technical or functional highlights]  

Business Model  
🔹 [How the company makes money]  
🔹 [Target customers or segments]  
🔹 [Scalability or revenue potential]  

Market Opportunity  
🔹 [Urgency and importance of problem in the market]  
🔹 [Adoption drivers or trends supporting growth]  

Traction & Metrics  
🔹 [Any KPIs that demonstrates progress or history]  
🔹 [Partnerships, funding rounds, or milestones]  

Team  
🔹 [Founders and key roles]  
🔹 [Relevant experience / strengths / complementarity]  
🔹 [Are they are suited to win in this space?]  

RULES

If some section has no info, still output the header but write: Not specified.

Never exceed 3 bullet points per section.

Keep everything objective, concise, and scannable.

Do not add commentary, conclusions, or recommendations.
"""

    async def analyze_pitchdeck(self, extracted_text: str) -> str:
        try:
            logger.info("🔍 Starting pitch deck analysis...")
            logger.info(f"📄 Text length: {len(extracted_text)} characters")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": self.analysis_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Analise o seguinte pitch deck:\n\n{extracted_text}"
                    }
                ],
                temperature=0.1
            )
            
            analysis = response.choices[0].message.content
            
            logger.info(f"✅ Analysis completed. Response length: {len(analysis)} characters")
            logger.info(f"📄 Analysis preview: {analysis[:200]}...")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Pitch deck analysis error: {str(e)}")
            raise Exception(f"Failed to analyze pitch deck: {str(e)}")