import os
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import tempfile
import logging

from main import AutomatedInsightEngine
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Automated Insight Engine", version="1.0.0")

# Global engine instance
engine = None


@app.on_event("startup")
async def startup():
    global engine
    engine = AutomatedInsightEngine(use_llm=True, llm_model="gpt-4o")
    logger.info("FastAPI server started with Automated Insight Engine")


@app.get("/")
async def root():
    return {
        "name": "Automated Insight Engine",
        "version": "1.0.0",
        "description": "Automated data analysis and report generation",
        "endpoints": {
            "upload": "/api/upload",
            "status": "/api/status",
            "reports": "/api/reports"
        }
    }


@app.get("/api/status")
async def get_status():
    return {
        "status": "active",
        "llm_enabled": engine.use_llm,
        "llm_model": engine.llm_model,
        "data_loaded": len(engine.processor.data) > 0
    }


@app.post("/api/upload")
async def upload_files(
    main_file: UploadFile = File(...),
    secondary_file: Optional[UploadFile] = None,
    analysis_type: str = "general"
):
    try:
        # Save uploaded files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as main_tmp:
            content = await main_file.read()
            main_tmp.write(content)
            main_path = main_tmp.name
        
        secondary_path = None
        if secondary_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as secondary_tmp:
                content = await secondary_file.read()
                secondary_tmp.write(content)
                secondary_path = secondary_tmp.name
        
        # Process data
        data_files = {"main": main_path}
        if secondary_path:
            data_files["secondary"] = secondary_path
        
        results = engine.process(data_files)
        
        # Cleanup temp files
        os.unlink(main_path)
        if secondary_path:
            os.unlink(secondary_path)
        
        return {
            "status": "success",
            "message": "Analysis complete",
            "insights": results.get("insights"),
            "reports": results.get("reports")
        }
    
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/{report_file}")
async def download_report(report_file: str):
    """Download generated report"""
    
    report_path = os.path.join(config.REPORTS_DIR, report_file)
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        report_path,
        media_type="application/octet-stream",
        filename=report_file
    )


@app.get("/api/reports")
async def list_reports():
    """List all generated reports"""
    
    reports = []
    if os.path.exists(config.REPORTS_DIR):
        for file in os.listdir(config.REPORTS_DIR):
            file_path = os.path.join(config.REPORTS_DIR, file)
            reports.append({
                "name": file,
                "size": os.path.getsize(file_path),
                "created": os.path.getctime(file_path)
            })
    
    return {"reports": reports}


@app.post("/api/analyze")
async def analyze_data(
    analysis_config: Dict[str, Any]
):
    """
    Analyze previously loaded data with custom config
    
    Args:
        analysis_config: Configuration for analysis
    
    Returns:
        Analysis results
    """
    
    try:
        if len(engine.processor.data) == 0:
            raise HTTPException(status_code=400, detail="No data loaded")
        
        # Run custom analysis
        analysis = engine.processor.analyze_data("main", enable_outliers=True)
        
        return {
            "status": "success",
            "analysis": analysis
        }
    
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": str(datetime.now())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
