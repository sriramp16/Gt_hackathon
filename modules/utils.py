import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidator:
    
    @staticmethod
    def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
        return {
            "shape": df.shape,
            "missing_values": df.isnull().sum().sum(),
            "duplicates": df.duplicated().sum(),
            "dtypes": df.dtypes.to_dict(),
            "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
        }
    
    @staticmethod
    def detect_missing_patterns(df: pd.DataFrame) -> Dict[str, List]:
        missing = {}
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 0:
                missing[col] = {
                    "count": df[col].isnull().sum(),
                    "percentage": missing_pct
                }
        return missing

class DataCleaner:
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        initial_rows = len(df)
        df = df.drop_duplicates(subset=subset)
        logger.info(f"Removed {initial_rows - len(df)} duplicate rows")
        return df
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: str = "drop") -> pd.DataFrame:
        if strategy == "drop":
            df = df.dropna()
        elif strategy == "forward_fill":
            df = df.fillna(method='ffill')
        elif strategy == "mean":
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        
        return df
    
    @staticmethod
    def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        return df

class StatisticalAnalyzer:
    
    @staticmethod
    def detect_outliers_iqr(series: pd.Series, multiplier: float = 1.5) -> Tuple[List, Dict]:
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)].index.tolist()
        
        return outliers, {
            "Q1": Q1,
            "Q3": Q3,
            "IQR": IQR,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "outlier_count": len(outliers)
        }
    
    @staticmethod
    def calculate_summary_stats(df: pd.DataFrame) -> Dict[str, Dict]:
        """Calculate summary statistics for numeric columns"""
        numeric_df = df.select_dtypes(include=[np.number])
        stats = {}
        
        for col in numeric_df.columns:
            stats[col] = {
                "mean": numeric_df[col].mean(),
                "median": numeric_df[col].median(),
                "std": numeric_df[col].std(),
                "min": numeric_df[col].min(),
                "max": numeric_df[col].max(),
                "25_percentile": numeric_df[col].quantile(0.25),
                "75_percentile": numeric_df[col].quantile(0.75),
            }
        
        return stats
    
    @staticmethod
    def calculate_correlations(df: pd.DataFrame) -> pd.DataFrame:
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr()

class TextFormatter:
    
    @staticmethod
    def format_number(num: float, decimals: int = 2) -> str:
        return f"{num:,.{decimals}f}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_currency(amount: float, currency: str = "$") -> str:
        return f"{currency}{amount:,.2f}"
    
    @staticmethod
    def timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class DataFrameHelper:
    @staticmethod
    def top_performers(df: pd.DataFrame, metric_col: str, n: int = 10) -> pd.DataFrame:
        return df.nlargest(n, metric_col)
    
    @staticmethod
    def bottom_performers(df: pd.DataFrame, metric_col: str, n: int = 10) -> pd.DataFrame:
        """Get bottom n performers by metric"""
        return df.nsmallest(n, metric_col)
    
    @staticmethod
    def segment_by_percentile(df: pd.DataFrame, value_col: str, segments: int = 4) -> Dict:
        """Segment data into percentile buckets"""
        return pd.qcut(df[value_col], q=segments, labels=False).to_dict()
