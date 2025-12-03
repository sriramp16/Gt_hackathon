"""
Test script - Full pipeline with Grok fallback
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import AutomatedInsightEngine
import config

def test_full_pipeline():
    """Test full pipeline with Grok (or fallback)"""
    
    print("="*70)
    print("AUTOMATED INSIGHT ENGINE - FULL PIPELINE TEST")
    print("="*70)
    
    print(f"\nConfiguration:")
    print(f"  - LLM Model: {config.LLM_MODEL}")
    print(f"  - Grok API Key: {'Configured' if config.GROK_API_KEY else 'Not configured'}")
    
    try:
        # Initialize with Grok (will fallback if key invalid)
        print("\n[1] Initializing engine with Grok provider...")
        engine = AutomatedInsightEngine(use_llm=True, llm_model="grok-2")
        print("✓ Engine initialized")
        
        # Check data
        train_path = "../train_adc/train.csv"
        item_path = "../train_adc/item_data.csv"
        
        if not os.path.exists(train_path):
            print(f"✗ Training data not found: {train_path}")
            return False
        
        print("✓ Data files found")
        
        # Run pipeline
        print("\n[2] Running complete pipeline...")
        results = engine.process_ctr_data(
            train_file=train_path,
            item_file=item_path if os.path.exists(item_path) else None
        )
        
        print("✓ Pipeline completed!")
        
        # Display results
        if "reports" in results:
            print("\n[3] Generated Reports:")
            for report_type, path in results["reports"].items():
                if path and os.path.exists(path):
                    size_kb = os.path.getsize(path) / 1024
                    print(f"  ✓ {report_type.upper()}: {size_kb:.1f} KB - {os.path.basename(path)}")
        
        if "insights" in results:
            print("\n[4] Generated Insights:")
            for insight_type, content in results["insights"].items():
                lines = content.split('\n')
                first_line = lines[0] if lines else "N/A"
                print(f"  - {insight_type.replace('_', ' ').title()}:")
                print(f"    {first_line[:70]}")
        
        print("\n[5] Analysis Summary:")
        if "analysis" in results:
            analysis = results["analysis"]
            if "quality_report" in analysis:
                print(f"  - Total records processed: {analysis.get('quality_report', {}).get('total_records', 'N/A')}")
            if "kpis" in analysis:
                print(f"  - KPIs calculated: {len(analysis.get('kpis', {}))}")
        
        print("\n" + "="*70)
        print("✓ TEST COMPLETED SUCCESSFULLY!")
        print("="*70)
        return True
    
    except Exception as e:
        print(f"\n✗ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_pipeline()
    sys.exit(0 if success else 1)
