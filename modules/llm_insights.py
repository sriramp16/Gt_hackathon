import json
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import requests
    HAS_GROK = True
except ImportError:
    HAS_GROK = False


class LLMProvider(ABC):
    @abstractmethod
    def generate_insights(self, data_context: Dict[str, Any], depth: str = "executive") -> str:
        pass


class GPT4oProvider(LLMProvider):
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        if not HAS_OPENAI:
            raise ImportError("openai package not installed")
        
        openai.api_key = api_key
        self.model = model
        self.client = openai
    
    def generate_insights(self, data_context: Dict[str, Any], depth: str = "executive") -> str:
        
        # Build prompt based on data context
        prompt = self._build_prompt(data_context, depth)
        
        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert data analyst and business consultant. "
                                   "Generate insightful, actionable analysis from data contexts."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"GPT-4o error: {str(e)}")
            return self._fallback_insights(data_context, depth)
    
    def _build_prompt(self, data_context: Dict[str, Any], depth: str) -> str:
        context_json = json.dumps(data_context, indent=2)
        
        if depth == "executive":
            return f"""Analyze the following data and provide a concise executive summary with key insights and recommendations.
Keep it to 3-5 bullet points.

Data Context:
{context_json}

Please provide:
1. Key findings (most important insights)
2. Performance trends
3. Critical issues or anomalies
4. Top 3 recommendations"""
        
        elif depth == "detailed":
            return f"""Provide a detailed analysis of the following data with comprehensive insights.

Data Context:
{context_json}

Please provide:
1. Summary statistics interpretation
2. Outlier analysis
3. Correlation insights
4. Segment performance
5. Root cause analysis
6. Specific recommendations with impact estimates"""
        
        else:  # summary
            return f"""Summarize the key findings from this data in 1-2 sentences.

Data Context:
{context_json}"""


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        if not HAS_GEMINI:
            raise ImportError("google-generativeai package not installed")
        
        genai.configure(api_key=api_key)
        self.model = model
        self.client = genai
    
    def generate_insights(self, data_context: Dict[str, Any], depth: str = "executive") -> str:
        prompt = self._build_prompt(data_context, depth)
        
        try:
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            return self._fallback_insights(data_context, depth)
    
    def _build_prompt(self, data_context: Dict[str, Any], depth: str) -> str:
        context_json = json.dumps(data_context, indent=2)
        
        if depth == "executive":
            return f"""Analyze the following data and provide a concise executive summary with key insights and recommendations.
Keep it to 3-5 bullet points.

Data Context:
{context_json}

Please provide:
1. Key findings (most important insights)
2. Performance trends
3. Critical issues or anomalies
4. Top 3 recommendations"""
        
        elif depth == "detailed":
            return f"""Provide a detailed analysis of the following data with comprehensive insights.

Data Context:
{context_json}

Please provide:
1. Summary statistics interpretation
2. Outlier analysis
3. Correlation insights
4. Segment performance
5. Root cause analysis
6. Specific recommendations with impact estimates"""
        
        else:  # summary
            return f"""Summarize the key findings from this data in 1-2 sentences.

Data Context:
{context_json}"""


class GrokProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "grok-2"):
        if not HAS_GROK:
            raise ImportError("requests package not installed")
        
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.x.ai/v1"
        self.client = None
    
    def generate_insights(self, data_context: Dict[str, Any], depth: str = "executive") -> str:
        prompt = self._build_prompt(data_context, depth)
        
        try:
            # Test the API key first
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert data analyst and business consultant. "
                                     "Generate insightful, actionable analysis from data contexts. "
                                     "Be concise and actionable."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Unexpected Grok response format: {result}")
                    return self._fallback_insights(data_context, depth)
            else:
                logger.error(f"Grok API error: {response.status_code} - {response.text}")
                return self._fallback_insights(data_context, depth)
        
        except Exception as e:
            logger.error(f"Grok error: {str(e)}")
            return self._fallback_insights(data_context, depth)
    
    def _build_prompt(self, data_context: Dict[str, Any], depth: str) -> str:
        # Convert numpy types to native Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy types like int64, float64
                return obj.item()
            else:
                return obj
        
        converted_context = convert_types(data_context)
        context_json = json.dumps(converted_context, indent=2, default=str)
        
        if depth == "executive":
            return f"""Analyze the following data and provide a concise executive summary with key insights and recommendations.
Keep it to 3-5 bullet points.

Data Context:
{context_json}

Please provide:
1. Key findings (most important insights)
2. Performance trends
3. Critical issues or anomalies
4. Top 3 recommendations"""
        
        elif depth == "detailed":
            return f"""Provide a detailed analysis of the following data with comprehensive insights.

Data Context:
{context_json}

Please provide:
1. Summary statistics interpretation
2. Outlier analysis
3. Correlation insights
4. Segment performance
5. Root cause analysis
6. Specific recommendations with impact estimates"""
        
        else:  # summary
            return f"""Summarize the key findings from this data in 1-2 sentences.

Data Context:
{context_json}"""
    
    def _fallback_insights(self, data_context: Dict[str, Any], depth: str) -> str:
        """Fallback when API is unavailable"""
        return "Analysis unavailable - Please check Grok API connection and credentials."


class InsightGenerator:
    """Manages LLM-based insight generation"""
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider
    
    def set_provider(self, provider: LLMProvider) -> None:
        self.llm_provider = provider
    
    def generate_executive_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        insights = {}
        
        # KPI Insights
        if "kpis" in analysis_results:
            insights["kpi_summary"] = self._generate_kpi_insights(analysis_results["kpis"])
        
        # Performance Analysis
        if "analysis" in analysis_results:
            insights["performance_analysis"] = self._generate_performance_insights(
                analysis_results["analysis"]
            )
        
        # Recommendations
        insights["recommendations"] = self._generate_recommendations(analysis_results)
        
        return insights
    
    def _generate_kpi_insights(self, kpis: Dict) -> str:
        if not self.llm_provider:
            return self._fallback_kpi_insights(kpis)
        
        context = {
            "type": "KPI Analysis",
            "data": kpis,
            "focus": "key performance indicators"
        }
        
        return self.llm_provider.generate_insights(context, depth="executive")
    
    def _generate_performance_insights(self, analysis: Dict) -> str:
        """Generate performance analysis insights"""
        
        if not self.llm_provider:
            return self._fallback_performance_insights(analysis)
        
        context = {
            "type": "Performance Analysis",
            "summary_stats": analysis.get("summary_stats", {}),
            "outliers": analysis.get("outliers", {}),
            "focus": "overall performance trends"
        }
        
        return self.llm_provider.generate_insights(context, depth="executive")
    
    def _generate_recommendations(self, results: Dict) -> str:
        """Generate actionable recommendations"""
        
        if not self.llm_provider:
            return self._fallback_recommendations(results)
        
        context = {
            "type": "Recommendations",
            "data": results,
            "focus": "top 5-7 actionable recommendations"
        }
        
        return self.llm_provider.generate_insights(context, depth="executive")
    
    # Fallback methods (template-based)
    
    def _fallback_kpi_insights(self, kpis: Dict) -> str:
        """Fallback KPI insights without LLM"""
        
        insights = "## KPI Summary\n\n"
        
        if isinstance(kpis, dict):
            for key, value in kpis.items():
                if isinstance(value, dict):
                    insights += f"- **{key}**: {value}\n"
                else:
                    insights += f"- **{key}**: {value}\n"
        
        return insights
    
    def _fallback_performance_insights(self, analysis: Dict) -> str:
        """Fallback performance insights without LLM"""
        
        insights = "## Performance Analysis\n\n"
        
        if "summary_stats" in analysis:
            insights += "### Summary Statistics:\n"
            for col, stats in analysis["summary_stats"].items():
                insights += f"- **{col}**: Mean={stats.get('mean', 'N/A')}, "
                insights += f"Median={stats.get('median', 'N/A')}, "
                insights += f"Std={stats.get('std', 'N/A')}\n"
        
        if "outliers" in analysis:
            insights += "\n### Outliers Detected:\n"
            for col, outlier_info in analysis["outliers"].items():
                count = outlier_info["stats"].get("outlier_count", 0)
                insights += f"- **{col}**: {count} outliers detected\n"
        
        return insights
    
    def _fallback_recommendations(self, results: Dict) -> str:
        """Fallback recommendations without LLM"""
        
        return """## Recommendations

1. **Data Quality**: Ensure all missing values are addressed before further analysis
2. **Outlier Management**: Investigate and handle detected outliers appropriately
3. **Performance Optimization**: Focus on top-performing segments
4. **Monitoring**: Implement continuous monitoring of key metrics
5. **Documentation**: Maintain detailed records of all changes and decisions
"""
