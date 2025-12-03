from main import AutomatedInsightEngine
import os

# ============================================================================
# EXAMPLE 1: Analyze CTR Data (Recommended for Hackathon)
# ============================================================================

def example_ctr_analysis():
    """Example: Analyze CTR/AdTech data"""
    
    print("\n" + "="*70)
    print("EXAMPLE 1: CTR/AdTech Data Analysis")
    print("="*70)
    
    # Initialize engine
    engine = AutomatedInsightEngine(use_llm=False)  # Disable LLM for quick test
    
    # Process CTR data
    results = engine.process_ctr_data(
        train_file="train_adc/train.csv",
        item_file="train_adc/item_data.csv"
    )
    
    print(f"\n✓ Analysis complete!")
    print(f"  - PDF Report: {results['reports']['pdf']}")
    print(f"  - PPTX Report: {results['reports']['pptx']}")
    
    return results


# ============================================================================
# EXAMPLE 2: General Data Analysis (Any CSV)
# ============================================================================

def example_general_analysis(csv_file):
    """Example: Analyze any CSV file"""
    
    print("\n" + "="*70)
    print(f"EXAMPLE 2: General Data Analysis - {csv_file}")
    print("="*70)
    
    engine = AutomatedInsightEngine(use_llm=False)
    
    results = engine.process(
        data_files={"main": csv_file}
    )
    
    print(f"\n✓ Analysis complete!")
    return results


# ============================================================================
# EXAMPLE 3: Multi-File Analysis with Merging
# ============================================================================

def example_merge_analysis():
    """Example: Merge and analyze multiple files"""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Multi-File Analysis with Merging")
    print("="*70)
    
    engine = AutomatedInsightEngine(use_llm=False)
    
    results = engine.process(
        data_files={
            "main": "train_adc/train.csv",
            "items": "train_adc/item_data.csv"
        },
        merge_config={
            "left_key": "main",
            "right_key": "items",
            "on": "item_id",  # Adjust based on your schema
            "how": "left"
        }
    )
    
    print(f"\n✓ Merge analysis complete!")
    return results


# ============================================================================
# EXAMPLE 4: Access Detailed Analysis Results
# ============================================================================

def example_detailed_access():
    """Example: Access and inspect detailed analysis results"""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Accessing Detailed Analysis Results")
    print("="*70)
    
    engine = AutomatedInsightEngine(use_llm=False)
    
    # Load and process data
    engine.process_ctr_data(
        train_file="train_adc/train.csv"
    )
    
    # Get processor
    processor = engine.get_processor()
    
    # Access main data
    df = processor.get_data("main")
    print(f"\nData shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Get analysis results
    analysis = processor.get_analysis()
    print(f"\nAnalysis keys: {list(analysis.keys())}")
    
    # Get quality report
    quality = processor.get_quality_report()
    print(f"Quality report keys: {list(quality.keys())}")
    
    # Get top performers
    top_10 = processor.get_top_performers("main", metric="is_click", n=10)
    print(f"\nTop 10 by clicks:\n{top_10}")
    
    return processor, analysis, quality


# ============================================================================
# EXAMPLE 5: Using with LLM (Requires API Keys)
# ============================================================================

def example_with_llm():
    """Example: Use engine with AI-powered insights (requires API key)"""
    
    print("\n" + "="*70)
    print("EXAMPLE 5: AI-Powered Analysis with GPT-4o")
    print("="*70)
    
    # Initialize with LLM enabled
    # Make sure OPENAI_API_KEY is set in .env
    engine = AutomatedInsightEngine(use_llm=True, llm_model="gpt-4o")
    
    results = engine.process_ctr_data(
        train_file="train_adc/train.csv"
    )
    
    print(f"\n✓ AI analysis complete!")
    print(f"Insights generated:")
    
    for insight_type, content in results['insights'].items():
        print(f"\n  {insight_type.replace('_', ' ').title()}:")
        print(f"  {content[:150]}...")
    
    return results


# ============================================================================
# EXAMPLE 6: Custom Metric Calculation
# ============================================================================

def example_custom_metrics():
    """Example: Define and calculate custom metrics"""
    
    print("\n" + "="*70)
    print("EXAMPLE 6: Custom Metrics Calculation")
    print("="*70)
    
    engine = AutomatedInsightEngine(use_llm=False)
    processor = engine.processor
    
    # Load data
    processor.load_data("train_adc/train.csv", "main")
    processor.clean_data("main")
    
    # Define custom metrics
    custom_metrics = [
        {
            "name": "ctr",
            "type": "ctr",
            "params": {
                "click_col": "is_click",
                "impression_col": "impression_id"
            }
        },
        {
            "name": "engagement_rate",
            "type": "ratio",
            "params": {
                "numerator": "is_click",
                "denominator": "impression_id"
            }
        }
    ]
    
    # Calculate KPIs
    kpis = processor.calculate_kpis("main", metric_configs=custom_metrics)
    
    print(f"\nCustom KPIs calculated:")
    for metric_name, metric_value in kpis.items():
        print(f"  {metric_name}: {metric_value}")
    
    return processor, kpis


# ============================================================================
# MAIN - Run Examples
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("AUTOMATED INSIGHT ENGINE - EXAMPLES")
    print("="*70)
    
    # Run examples
    choice = input("\nSelect example to run (1-6): ")
    
    if choice == "1":
        example_ctr_analysis()
    
    elif choice == "2":
        csv_file = input("Enter CSV file path: ")
        if os.path.exists(csv_file):
            example_general_analysis(csv_file)
        else:
            print(f"File not found: {csv_file}")
    
    elif choice == "3":
        example_merge_analysis()
    
    elif choice == "4":
        example_detailed_access()
    
    elif choice == "5":
        example_with_llm()
    
    elif choice == "6":
        example_custom_metrics()
    
    else:
        print("Running all examples...")
        example_ctr_analysis()
        example_detailed_access()
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)
