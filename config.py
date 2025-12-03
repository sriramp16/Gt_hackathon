import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "grok-2")  # Options: "gpt-4o", "gemini-1.5-pro", "grok-2"

# Data Configuration
MAX_FILE_SIZE_MB = 500
SUPPORTED_FORMATS = ["csv", "xlsx", "json", "parquet", "sql"]
CHUNK_SIZE = 10000  # For processing large files

# Report Configuration
REPORT_FORMAT = ["pdf", "pptx"]
REPORT_TITLE = "Executive Insight Report"
REPORT_THEME = "professional"

# Output paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Analysis Configuration
ANALYSIS_CONFIG = {
    "enable_kpi_calculation": True,
    "enable_outlier_detection": True,
    "enable_correlation_analysis": True,
    "enable_forecasting": False,
    "min_volume_threshold": 10,  # Minimum samples for reliable metrics
    "outlier_method": "iqr",  # Options: "iqr", "zscore", "isolation_forest"
}

# LLM Prompt Configuration
INSIGHT_DEPTH = "executive"  # Options: "summary", "executive", "detailed"
TONE = "professional"  # Options: "professional", "casual", "technical"
