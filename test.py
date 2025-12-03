"""
Test script for Automated Insight Engine with CTR dataset
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import AutomatedInsightEngine
import config

def test_pipeline():
    """Test the complete pipeline with CTR data"""
    
    print("="*70)
    print("AUTOMATED INSIGHT ENGINE - CTR DATASET TEST")
    print("="*70)
    
    # Initialize engine (without LLM for faster testing)
    print("\n[1] Initializing Automated Insight Engine...")
    engine = AutomatedInsightEngine(use_llm=False)
    print("✓ Engine initialized (LLM disabled for testing)")
    
    # Check if data files exist
    train_path = "../train_adc/train.csv"
    item_path = "../train_adc/item_data.csv"
    
    if not os.path.exists(train_path):
        print(f"✗ Training data not found: {train_path}")
        return False
    
    print(f"✓ Data files found")
    
    try:
        # Run pipeline
        print("\n[2] Running pipeline...")
        results = engine.process_ctr_data(
            train_file=train_path,
            item_file=item_path if os.path.exists(item_path) else None
        )
        
        print("✓ Pipeline completed successfully!")
        
        # Display results
        print("\n[3] RESULTS SUMMARY")
        print("-" * 70)
        
        if "reports" in results:
            print("\nGenerated Reports:")
            for report_type, path in results["reports"].items():
                if path:
                    print(f"  ✓ {report_type.upper()}: {path}")
        
        print("\n[4] INSIGHTS GENERATED")
        print("-" * 70)
        if "insights" in results:
            for insight_type, content in results["insights"].items():
                print(f"\n{insight_type.replace('_', ' ').title()}:")
                print(content[:200] + "..." if len(content) > 200 else content)
        
        print("\n" + "="*70)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        return True
    
    except Exception as e:
        print(f"\n✗ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
