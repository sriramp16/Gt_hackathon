import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import logging
from pathlib import Path
from modules.utils import DataValidator, DataCleaner, StatisticalAnalyzer, DataFrameHelper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngester:
    
    @staticmethod
    def ingest_csv(file_path: str, **kwargs) -> pd.DataFrame:
        logger.info(f"Ingesting CSV: {file_path}")
        return pd.read_csv(file_path, **kwargs)
    
    @staticmethod
    def ingest_excel(file_path: str, sheet_name: int = 0, **kwargs) -> pd.DataFrame:
        logger.info(f"Ingesting Excel: {file_path}")
        return pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
    
    @staticmethod
    def ingest_json(file_path: str, **kwargs) -> pd.DataFrame:
        logger.info(f"Ingesting JSON: {file_path}")
        return pd.read_json(file_path, **kwargs)
    
    @staticmethod
    def ingest_parquet(file_path: str, **kwargs) -> pd.DataFrame:
        logger.info(f"Ingesting Parquet: {file_path}")
        return pd.read_parquet(file_path, **kwargs)
    
    @staticmethod
    def ingest_auto(file_path: str, **kwargs) -> pd.DataFrame:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == ".csv":
            return DataIngester.ingest_csv(file_path, **kwargs)
        elif file_ext in [".xlsx", ".xls"]:
            return DataIngester.ingest_excel(file_path, **kwargs)
        elif file_ext == ".json":
            return DataIngester.ingest_json(file_path, **kwargs)
        elif file_ext == ".parquet":
            return DataIngester.ingest_parquet(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

class DataProcessor:
    
    def __init__(self):
        self.data: Dict[str, pd.DataFrame] = {}
        self.analysis_results: Dict[str, Any] = {}
        self.quality_report: Dict[str, Any] = {}
    
    def load_data(self, file_path: str, name: str = "main") -> None:
        self.data[name] = DataIngester.ingest_auto(file_path)
        logger.info(f"Loaded data '{name}': {self.data[name].shape}")
    
    def merge_data(self, left_key: str, right_key: str, on: str, how: str = "inner") -> None:
        if left_key not in self.data or right_key not in self.data:
            raise ValueError(f"Data '{left_key}' or '{right_key}' not loaded")
        
        self.data["merged"] = self.data[left_key].merge(
            self.data[right_key], on=on, how=how
        )
        logger.info(f"Merged data: {self.data['merged'].shape}")
    
    def clean_data(self, data_key: str = "main", remove_dups: bool = True,
                   handle_missing: str = "drop", normalize_cols: bool = True) -> None:
        if data_key not in self.data:
            raise ValueError(f"Data '{data_key}' not loaded")
        
        df = self.data[data_key]
        
        # Quality check before
        quality_before = DataValidator.check_data_quality(df)
        
        # Remove duplicates
        if remove_dups:
            df = DataCleaner.remove_duplicates(df)
        
        # Handle missing values
        df = DataCleaner.handle_missing_values(df, strategy=handle_missing)
        
        # Normalize column names
        if normalize_cols:
            df = DataCleaner.normalize_columns(df)
        
        self.data[data_key] = df
        
        # Quality check after
        quality_after = DataValidator.check_data_quality(df)
        
        self.quality_report[data_key] = {
            "before": quality_before,
            "after": quality_after,
            "missing_patterns": DataValidator.detect_missing_patterns(df)
        }
        
        logger.info(f"Data cleaned: {data_key}")
    
    def calculate_kpis(self, data_key: str = "main", metric_configs: List[Dict] = None) -> Dict:
        if data_key not in self.data:
            raise ValueError(f"Data '{data_key}' not loaded")
        
        df = self.data[data_key]
        kpis = {}
        
        # Default metric configurations for CTR-like data
        if metric_configs is None:
            metric_configs = self._get_default_metrics()
        
        for config in metric_configs:
            metric_name = config.get("name")
            metric_type = config.get("type")
            params = config.get("params", {})
            
            if metric_type == "ctr":
                kpis[metric_name] = self._calculate_ctr(df, **params)
            elif metric_type == "aggregation":
                kpis[metric_name] = self._calculate_aggregation(df, **params)
            elif metric_type == "ratio":
                kpis[metric_name] = self._calculate_ratio(df, **params)
        
        self.analysis_results["kpis"] = kpis
        logger.info(f"Calculated {len(kpis)} KPIs")
        
        return kpis
    
    def analyze_data(self, data_key: str = "main", group_by: str = None,
                     enable_outliers: bool = True) -> Dict:
        """Comprehensive data analysis"""
        if data_key not in self.data:
            raise ValueError(f"Data '{data_key}' not loaded")
        
        df = self.data[data_key]
        analysis = {}
        
        # Summary statistics
        analysis["summary_stats"] = StatisticalAnalyzer.calculate_summary_stats(df)
        
        # Outlier detection (exclude binary/ID-like columns)
        if enable_outliers:
            analysis["outliers"] = {}
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            # Filter out columns that are likely IDs or binary flags
            filtered_numeric_cols = [
                c for c in numeric_cols
                if (df[c].nunique() > 2) and ('id' not in c.lower())
            ]
            for col in filtered_numeric_cols:
                outlier_indices, outlier_stats = StatisticalAnalyzer.detect_outliers_iqr(df[col])
                analysis["outliers"][col] = {
                    "indices": outlier_indices,
                    "stats": outlier_stats
                }
        
        # Correlation analysis
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            analysis["correlations"] = StatisticalAnalyzer.calculate_correlations(df).to_dict()
        
        # Grouped analysis
        if group_by and group_by in df.columns:
            analysis["grouped"] = self._analyze_groups(df, group_by)
        
        self.analysis_results["analysis"] = analysis
        logger.info("Data analysis complete")
        
        return analysis
    
    def get_top_performers(self, data_key: str = "main", metric: str = None,
                           n: int = 10) -> pd.DataFrame:
        if data_key not in self.data or metric is None:
            raise ValueError("Invalid data_key or metric")
        
        df = self.data[data_key]
        return DataFrameHelper.top_performers(df, metric, n)
    
    def get_bottom_performers(self, data_key: str = "main", metric: str = None,
                              n: int = 10) -> pd.DataFrame:
        if data_key not in self.data or metric is None:
            raise ValueError("Invalid data_key or metric")
        
        df = self.data[data_key]
        return DataFrameHelper.bottom_performers(df, metric, n)
    
    # Private helper methods
    
    def _get_default_metrics(self) -> List[Dict]:
        return [
            {
                "name": "total_volume",
                "type": "aggregation",
                "params": {"operation": "count"}
            },
            {
                "name": "total_value",
                "type": "aggregation",
                "params": {"operation": "sum"}
            }
        ]
    
    def _calculate_ctr(self, df: pd.DataFrame, click_col: str, impression_col: str) -> Dict:
        grouped = df.groupby(df.columns[0] if len(df.columns) > 0 else df.index).agg({
            click_col: 'sum',
            impression_col: 'count'
        }).reset_index()
        
        grouped['ctr'] = (grouped[click_col] / grouped[impression_col] * 100).round(2)
        
        return {
            "overall_ctr": (df[click_col].sum() / len(df) * 100),
            "data": grouped.to_dict('records')
        }
    
    def _calculate_aggregation(self, df: pd.DataFrame, operation: str = "sum") -> Dict:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if operation == "sum":
            return df[numeric_cols].sum().to_dict()
        elif operation == "count":
            return len(df)
        elif operation == "mean":
            return df[numeric_cols].mean().to_dict()
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _calculate_ratio(self, df: pd.DataFrame, numerator: str,
                        denominator: str) -> float:
        if numerator not in df.columns or denominator not in df.columns:
            raise ValueError("Columns not found")
        
        return (df[numerator].sum() / df[denominator].sum())
    
    def _analyze_groups(self, df: pd.DataFrame, group_by: str) -> Dict:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        grouped_analysis = {}
        for col in numeric_cols:
            grouped_analysis[col] = df.groupby(group_by)[col].agg(['sum', 'mean', 'count']).to_dict()
        
        return grouped_analysis
    
    def get_data(self, data_key: str = "main") -> pd.DataFrame:
        return self.data.get(data_key, None)
    
    def get_analysis(self) -> Dict[str, Any]:
        return self.analysis_results
    
    def get_quality_report(self) -> Dict[str, Any]:
        return self.quality_report
