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
        self.analysis_prompt = """# TAREFA

Você é um analista de negócios especializado em extrair e organizar as informações mais importantes de pitch decks de startups. Analise o texto fornecido e responda de forma objetiva às seguintes perguntas.

# INSTRUÇÕES

* Responda cada pergunta de forma direta e concisa.
* Utilize a formatação especificada.
* Se a informação para uma pergunta específica não estiver claramente no texto, responda com `[Informação não encontrada no material]`.

# FORMATO DE SAÍDA

**O que a Companhia faz?**
[Responda em um parágrafo único, explicando o core business da empresa, o problema que ela resolve e seu público-alvo.]

**Produto e Como ganha dinheiro**
[Em um parágrafo, descreva o que é o produto ou serviço oferecido. Em um segundo parágrafo, explique claramente o modelo de negócio e como a empresa gera receita (ex: assinatura, taxa por transação, etc.).]

**Highlights?**
[Liste exatamente 5 bullet points com as conquistas e métricas mais impactantes mencionadas no texto. Priorize dados quantitativos como receita, número de clientes, crescimento percentual, prêmios ou parcerias estratégicas.]

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