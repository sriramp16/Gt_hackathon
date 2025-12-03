# 🚀 Automated Insight Engine

> **Tagline:** An automated ETL pipeline that transforms raw CSV data into executive-ready PDF and PowerPoint reports with AI-generated narratives in under 30 seconds.

---

## 1. The Problem (Real World Scenario)

**Context:** Marketing and Analytics teams waste 3-5 hours every week manually downloading CSVs, cleaning data, calculating metrics, and writing reports for stakeholders.

**The Pain Point:** This manual process is slow, repetitive, and error-prone. Critical insights about campaign performance get buried in spreadsheets. By the time an analyst finishes the report, the data is stale and actionable decisions are delayed.

> **My Solution:** I built the **Automated Insight Engine**, an intelligent ETL system. You simply upload a raw CSV file, and 30 seconds later, you receive a professionally formatted PDF report and PowerPoint deck containing:
> - Cleaned, validated data with calculated KPIs
> - Automated anomaly detection and trend analysis
> - AI-generated executive insights explaining the "why" behind the numbers
> - Ready-to-share visualizations and narratives

---

## 2. Expected End Result

**For the User:**

- **Input:** Upload a raw CSV file via API or web interface
- **Action:** Wait ~30 seconds for processing
- **Output:** Receive professionally formatted reports containing:
  - Key performance indicators (CTR, Impressions, Conversions, etc.)
  - Week-over-Week and Month-over-Month trend analysis
  - Detected anomalies and performance bottlenecks (e.g., "CTR dropped 23% in Region X")
  - AI-written executive summary explaining the metrics and actionable recommendations
  - Executive-ready PDF and PowerPoint presentation

---

## 3. Technical Approach

**Production-Ready ETL Pipeline** focusing on scalability, reliability, and automation.

**System Architecture:**

1. **Data Ingestion (Multi-Format):** Accepts CSV, JSON, and API sources with schema validation
2. **Data Processing Pipeline:**
   - **Cleaning:** Handles missing values, duplicates, type coercion using Pandas
   - **Validation:** Enforces data quality constraints using custom DataValidator
   - **KPI Calculation:** Computes CTR, aggregations, time-series analysis
3. **Intelligent Analysis:**
   - Statistical analysis (mean, median, std deviation)
   - Trend detection and correlation analysis
   - Top performer identification
4. **AI-Powered Insights (The Analyst):**
   - Pass processed data to **OpenAI GPT-4o**, **Google Gemini**, or **xAI Grok**
   - Use **Few-Shot Prompting** to generate analyst-grade narratives
   - Fallback to template-based insights if APIs unavailable
   - Guardrail: Validate AI responses match actual metrics
5. **Report Generation:**
   - **PDF Reports:** ReportLab renders clean, professional layouts with charts
   - **PowerPoint Decks:** python-pptx creates presentation-ready slides
   - Consistent branding and formatting across all outputs

---

## 4. Tech Stack

- **Language:** Python 3.8+
- **Data Processing:** Pandas, NumPy, SciPy
- **AI Models:** OpenAI GPT-4o, Google Gemini, xAI Grok (with fallbacks)
- **Report Generation:** ReportLab (PDF), python-pptx (PowerPoint)
- **Web Framework:** FastAPI (for API endpoints)
- **Configuration:** python-dotenv (environment management)

---

## 5. Challenges & Learnings

**Challenge 1: AI Hallucinations in Insights**
- **Issue:** Initially, the AI would invent reasons for metric changes without data to support them
- **Solution:** Implemented strict Few-Shot prompting with context windows, enforcing data-driven analysis

**Challenge 2: Multi-Source Data Standardization**
- **Issue:** Different data sources had different schemas, column names, and date formats
- **Solution:** Built a flexible DataProcessor with configurable mappings and DataValidator

**Challenge 3: Report Generation Performance**
- **Issue:** Generating complex PDF reports with charts was slow (~10-15 seconds)
- **Solution:** Optimized by caching calculations and using efficient ReportLab rendering

**Challenge 4: JSON Serialization with NumPy Types**
- **Issue:** NumPy int64/float64 types couldn't be serialized to JSON for LLM APIs
- **Solution:** Added type conversion utility to automatically convert numpy types to native Python types

---

## 6. How to Run

```bash
# 1. Setup
cd automated_insight_engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys (optional - system works without them)
export OPENAI_API_KEY="your_key_here"
export GEMINI_API_KEY="your_key_here"
export GROK_API_KEY="your_key_here"

# 4. Set LLM model (default: grok-2)
export LLM_MODEL="grok-2"  # Options: "gpt-4o", "gemini-1.5-pro", "grok-2"

# 5. Process your data
python main.py

# 6. Or use the web API
uvicorn api:app --reload
```

---

## 7. Usage Examples

**Example 1: CLI Processing with Grok**
```python
from main import AutomatedInsightEngine

engine = AutomatedInsightEngine(use_llm=True, llm_model="grok-2")
reports = engine.process_ctr_data("data/campaign_metrics.csv")
```

**Example 2: Using GPT-4o**
```python
engine = AutomatedInsightEngine(use_llm=True, llm_model="gpt-4o")
results = engine.process_ctr_data("data/metrics.csv")
```

**Example 3: API Upload**
```bash
curl -X POST -F "file=@data/metrics.csv" http://localhost:8000/api/upload
```

**Example 4: Custom Analysis**
```python
from modules.data_processor import DataProcessor
from modules.llm_insights import GrokProvider

processor = DataProcessor()
data = processor.load_data("metrics.csv")
clean_data = processor.clean_data(data)
kpis = processor.calculate_kpis(clean_data)

grok = GrokProvider(api_key="your_key")
insights = grok.generate_insights({"kpis": kpis})
```

---

## Testing & Validation

```bash
python test.py                  # Full pipeline test
python test_pipeline_grok.py    # Test with Grok
python test_api_key.py          # Validate API connectivity
```

- ✅ Data ingestion (237K+ rows)
- ✅ Cleaning and KPI calculation
- ✅ PDF/PowerPoint generation
- ✅ AI insight generation (Grok/GPT-4o/Gemini or fallback)
- ✅ Complete execution in ~1.4 seconds

---

## Project Structure

```
├── main.py                 # Pipeline orchestrator
├── config.py              # Configuration management
├── api.py                 # FastAPI web interface
├── test.py                # Validation suite
├── test_grok.py           # Grok integration test
├── test_api_key.py        # API key validation
├── examples.py            # Usage examples
├── modules/
│   ├── data_processor.py   # ETL & KPI calculation
│   ├── llm_insights.py     # AI insight generation (GPT-4o, Gemini, Grok)
│   ├── report_generator.py # PDF & PPTX creation
│   └── utils.py            # Helper utilities
└── requirements.txt       # Dependencies
```

---

## Key Features

✅ **3 LLM Providers Supported**
- OpenAI GPT-4o (advanced reasoning)
- Google Gemini 1.5 Pro (fast & cost-effective)
- **xAI Grok-2** (real-time analysis) 🆕

✅ **Production-ready** ETL pipeline (not a prototype)
✅ **End-to-end automation** from raw CSV to executive reports
✅ **Dual report formats** (PDF + PowerPoint)
✅ **AI-powered analysis** with fallback mechanisms
✅ **Sub-30-second processing** on large datasets
✅ **RESTful API** for easy integration
✅ **Graceful degradation** - works even without API keys

---

## Supported LLM Models

| Provider | Model | Features | Status |
|----------|-------|----------|--------|
| OpenAI | gpt-4o | Advanced reasoning | ✅ Active |
| Google | gemini-1.5-pro | Fast, cost-effective | ✅ Active |
| xAI | grok-2 | Real-time data analysis | ✅ NEW |

