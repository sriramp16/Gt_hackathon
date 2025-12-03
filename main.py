import os
import sys
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from modules.data_processor import DataProcessor
from modules.llm_insights import InsightGenerator, GPT4oProvider, GeminiProvider, GrokProvider
from modules.report_generator import ReportBuilder
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomatedInsightEngine:
    def __init__(self, use_llm: bool = True, llm_model: str = "grok-2"):
        self.use_llm = use_llm
        self.llm_model = llm_model
        self.processor = DataProcessor()
        self.insight_generator = InsightGenerator()
        self.setup_llm()
    
    def setup_llm(self):
        if not self.use_llm:
            logger.info("LLM disabled - using fallback insights")
            return
        
        try:
            if self.llm_model == "gpt-4o":
                if not config.OPENAI_API_KEY:
                    logger.warning("OPENAI_API_KEY not found - using fallback insights")
                    self.use_llm = False
                    return
                
                provider = GPT4oProvider(config.OPENAI_API_KEY, model="gpt-4o")
                self.insight_generator.set_provider(provider)
                logger.info("GPT-4o provider initialized")
            
            elif self.llm_model == "gemini-1.5-pro":
                if not config.GEMINI_API_KEY:
                    logger.warning("GEMINI_API_KEY not found - using fallback insights")
                    self.use_llm = False
                    return
                
                provider = GeminiProvider(config.GEMINI_API_KEY, model="gemini-1.5-pro")
                self.insight_generator.set_provider(provider)
                logger.info("Gemini provider initialized")
            
            elif self.llm_model == "grok-2":
                if not config.GROK_API_KEY:
                    logger.warning("GROK_API_KEY not found - using fallback insights")
                    self.use_llm = False
                    return
                
                provider = GrokProvider(config.GROK_API_KEY, model="grok-2")
                self.insight_generator.set_provider(provider)
                logger.info("Grok provider initialized")
        
        except Exception as e:
            logger.error(f"LLM setup failed: {str(e)} - using fallback insights")
            self.use_llm = False
    
    def process(self, data_files: Dict[str, str], 
                merge_config: Optional[Dict] = None,
                analysis_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute the complete pipeline
        
        Args:
            data_files: Dict of {name: file_path} for data ingestion
            merge_config: Config for merging datasets (optional)
            analysis_config: Custom analysis configuration (optional)
        
        Returns:
            Dict with analysis results and insights
        """
        
        logger.info("="*60)
        logger.info("Starting Automated Insight Engine Pipeline")
        logger.info("="*60)
        
        # Step 1: Data Ingestion
        logger.info("\n[Step 1/5] Data Ingestion")
        for name, file_path in data_files.items():
            if os.path.exists(file_path):
                self.processor.load_data(file_path, name)
            else:
                raise FileNotFoundError(f"Data file not found: {file_path}")
        
        # Step 2: Data Cleaning
        logger.info("\n[Step 2/5] Data Cleaning & Validation")
        for data_key in self.processor.data.keys():
            self.processor.clean_data(data_key, remove_dups=True, handle_missing="drop")
        
        # Step 3: Data Merging (if config provided)
        if merge_config:
            logger.info("\n[Step 2b] Merging Datasets")
            self.processor.merge_data(
                merge_config.get("left_key"),
                merge_config.get("right_key"),
                merge_config.get("on"),
                merge_config.get("how", "inner")
            )
        
        # Step 4: Analysis
        logger.info("\n[Step 3/5] Comprehensive Data Analysis")
        
        # Select main dataset for analysis
        main_data_key = "merged" if "merged" in self.processor.data else "main"
        
        # KPI Calculation
        logger.info("  - Calculating KPIs...")
        self.processor.calculate_kpis(main_data_key)
        
        # Detailed Analysis
        logger.info("  - Running exploratory analysis...")
        self.processor.analyze_data(main_data_key, enable_outliers=True)
        
        # Step 5: Insight Generation
        logger.info("\n[Step 4/5] Generating AI-Powered Insights")
        analysis_results = self.processor.get_analysis()
        analysis_results["quality_report"] = self.processor.get_quality_report()
        
        insights = self.insight_generator.generate_executive_insights(analysis_results)
        logger.info("  - Insights generated successfully")
        
        # Step 6: Report Generation
        logger.info("\n[Step 5/5] Generating Reports")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_builder = ReportBuilder(analysis_results, insights)
        
        # PDF Report
        pdf_path = os.path.join(config.REPORTS_DIR, f"report_{timestamp}.pdf")
        try:
            report_builder.generate_pdf_report(pdf_path)
            logger.info(f"  ✓ PDF Report: {pdf_path}")
        except Exception as e:
            logger.warning(f"PDF generation failed: {str(e)}")
        
        # PowerPoint Report
        pptx_path = os.path.join(config.REPORTS_DIR, f"report_{timestamp}.pptx")
        try:
            report_builder.generate_pptx_report(pptx_path)
            logger.info(f"  ✓ PowerPoint Report: {pptx_path}")
        except Exception as e:
            logger.warning(f"PowerPoint generation failed: {str(e)}")
        
        logger.info("\n" + "="*60)
        logger.info("Pipeline Execution Complete!")
        logger.info("="*60)
        
        return {
            "status": "success",
            "analysis": analysis_results,
            "insights": insights,
            "reports": {
                "pdf": pdf_path if 'pdf_path' in locals() else None,
                "pptx": pptx_path if 'pptx_path' in locals() else None
            }
        }
    
    def process_ctr_data(self, train_file: str, item_file: Optional[str] = None) -> Dict[str, Any]:
        data_files = {"main": train_file}
        
        if item_file and os.path.exists(item_file):
            data_files["items"] = item_file
        
        # CTR-specific analysis config
        ctr_metrics = [
            {
                "name": "ctr_analysis",
                "type": "ctr",
                "params": {"click_col": "is_click", "impression_col": "impression_id"}
            }
        ]
        
        return self.process(
            data_files,
            analysis_config={"metric_configs": ctr_metrics}
        )
    
    def get_processor(self) -> DataProcessor:
        return self.processor
    
    def get_insight_generator(self) -> InsightGenerator:
        return self.insight_generator


def main():
    # Initialize engine
    engine = AutomatedInsightEngine(use_llm=False)  # Disable LLM for initial testing
    
    # Process CTR dataset
    try:
        results = engine.process_ctr_data(
            train_file="train_adc/train.csv",
            item_file="train_adc/item_data.csv"
        )
        
        print("\n✓ Pipeline executed successfully!")
        print(f"Reports saved to: {config.REPORTS_DIR}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
