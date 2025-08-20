from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
import uuid
from dotenv import load_dotenv
from direct_pdf_extractor import DirectPDFExtractor
from pitchdeck_agent import PitchDeckAgent
from product_agent import ProductAgent
from web_research_agent import WebResearchAgent
from market_size_agent import MarketSizeAgent
from report_generator_agent import ReportGeneratorAgent

load_dotenv()

app = FastAPI(title="PDF Text Extractor")

app.mount("/static", StaticFiles(directory="static"), name="static")

direct_pdf_extractor = DirectPDFExtractor()
pitchdeck_agent = PitchDeckAgent()
product_agent = ProductAgent()
web_research_agent = WebResearchAgent()
market_size_agent = MarketSizeAgent()
report_generator_agent = ReportGeneratorAgent()

class AnalyzeRequest(BaseModel):
    extracted_text: str

class ReportRequest(BaseModel):
    pitchdeck_analysis: str
    product_analysis: str
    web_research: str
    market_analysis: str
    company_name: str = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}.pdf"
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Direct PDF processing using OpenAI Responses API
        extracted_text = await direct_pdf_extractor.extract_text_from_pdf(file_path)
        
        os.remove(file_path)
        
        return JSONResponse(content={
            "success": True,
            "extracted_text": extracted_text
        })
    
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/analyze")
async def analyze_pitchdeck(request: AnalyzeRequest):
    try:
        analysis = await pitchdeck_agent.analyze_pitchdeck(request.extracted_text)
        
        return JSONResponse(content={
            "success": True,
            "analysis": analysis
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing pitch deck: {str(e)}")

@app.post("/analyze_product")
async def analyze_product(request: AnalyzeRequest):
    try:
        analysis = await product_agent.analyze_product(request.extracted_text)
        
        return JSONResponse(content={
            "success": True,
            "analysis": analysis
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing product: {str(e)}")

@app.post("/research_company")
async def research_company(request: AnalyzeRequest):
    try:
        research_result = await web_research_agent.full_research(request.extracted_text)
        
        return JSONResponse(content={
            "success": True,
            "company_name": research_result["company_name"],
            "research_content": research_result["research_content"]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error researching company: {str(e)}")

@app.post("/analyze_market_size")
async def analyze_market_size(request: AnalyzeRequest):
    try:
        market_result = await market_size_agent.full_market_analysis(request.extracted_text)
        
        if market_result["success"]:
            return JSONResponse(content={
                "success": True,
                "extracted_info": market_result.get("extracted_text", ""),
                "market_analysis": market_result["market_analysis"]
            })
        else:
            raise HTTPException(status_code=500, detail=market_result.get("message", "Market analysis failed"))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing market size: {str(e)}")

@app.post("/generate_report")
async def generate_report(request: ReportRequest):
    try:
        comprehensive_report = await report_generator_agent.generate_complete_report(
            pitchdeck_analysis=request.pitchdeck_analysis,
            product_analysis=request.product_analysis,
            web_research=request.web_research,
            market_analysis=request.market_analysis,
            company_name=request.company_name
        )
        
        return JSONResponse(content={
            "success": True,
            "comprehensive_report": comprehensive_report
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comprehensive report: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)