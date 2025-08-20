import openai
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.analysis_prompt = """# AGENTE ANALISADOR DE PRODUTO

## FUNÇÃO
Você é um especialista responsável por explicar detalhadamente o produto da startup: o que faz, como funciona e quais tecnologias utiliza.

## OBJETIVO
Criar uma explicação clara e completa do produto, suas funcionalidades e aspectos técnicos, trabalhando com as informações disponíveis.

## INSTRUÇÕES
- Use as informações do pitch deck sobre o produto
- Explique de forma que qualquer pessoa entenda o que o produto faz
- Faça inferências quando necessário baseado no tipo de solução
- Identifique o que torna o produto diferente
- Seja claro sobre o que não está explícito nas informações

## O QUE EXPLICAR

### O PRODUTO EM SI
- O que exatamente o produto faz
- Como o usuário interage com ele
- Principais funcionalidades
- Para quem é direcionado

### COMO FUNCIONA
- Fluxo básico de funcionamento
- Tecnologias que provavelmente usa
- Integrações necessárias
- Complexidade técnica aparente

### DIFERENCIAÇÃO
- O que torna único no mercado
- Vantagens técnicas ou funcionais
- Dificuldade de replicação

## ABORDAGEM
- Trabalhe com as informações que tem
- Faça inferências lógicas quando necessário
- Seja transparente sobre limitações de informação
- Mantenha clareza e objetividade

## RESULTADO ESPERADO
Uma explicação em no máximo 2 parágrafos respondendo a pergunta: qual o produto da companhia"""

    async def analyze_product(self, extracted_text: str) -> str:
        try:
            logger.info("🔍 Starting product analysis...")
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
                        "content": f"Analise o produto desta startup com base no pitch deck:\n\n{extracted_text}"
                    }
                ],
                temperature=0.1
            )
            
            analysis = response.choices[0].message.content
            
            logger.info(f"✅ Product analysis completed. Response length: {len(analysis)} characters")
            logger.info(f"📄 Analysis preview: {analysis[:200]}...")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Product analysis error: {str(e)}")
            raise Exception(f"Failed to analyze product: {str(e)}")