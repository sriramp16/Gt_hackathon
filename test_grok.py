"""
Test script for Grok API integration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.llm_insights import GrokProvider, InsightGenerator
import config

def test_grok_api():
    """Test Grok API integration"""
    
    print("="*70)
    print("GROK API INTEGRATION TEST")
    print("="*70)
    
    # Check if API key is set
    if not config.GROK_API_KEY:
        print("\n✗ GROK_API_KEY not found in environment")
        return False
    
    print(f"\n✓ Grok API Key found (length: {len(config.GROK_API_KEY)} chars)")
    
    try:
        # Initialize Grok provider
        print("\n[1] Initializing Grok Provider...")
        provider = GrokProvider(config.GROK_API_KEY, model="grok-2")
        print(f"✓ Grok Provider initialized")
        print(f"  - Model: {provider.model}")
        print(f"  - Base URL: {provider.base_url}")
        
        # Test with sample data
        print("\n[2] Testing Grok API with sample data...")
        sample_context = {
            "type": "KPI Analysis",
            "data": {
                "total_volume": 237609,
                "ctr": 4.57,
                "impressions": 237609,
                "clicks": 10862,
                "top_app": "App_001"
            },
            "focus": "key performance indicators"
        }
        
        print("\nSample Context:")
        print(f"  - Total Volume: {sample_context['data']['total_volume']}")
        print(f"  - CTR: {sample_context['data']['ctr']}%")
        print(f"  - Clicks: {sample_context['data']['clicks']}")
        
        # Generate insights
        print("\n[3] Generating insights via Grok...")
        insights = provider.generate_insights(sample_context, depth="executive")
        
        print("\n✓ Grok API Response:")
        print("-" * 70)
        print(insights)
        print("-" * 70)
        
        # Verify response is not empty and not a fallback message
        if "unavailable" in insights.lower():
            print("\n✗ API returned fallback message - check API key and rate limits")
            return False
        
        if len(insights) < 50:
            print("\n✗ Response too short - may indicate API issue")
            return False
        
        print("\n✓ Grok API test PASSED!")
        return True
    
    except Exception as e:
        print(f"\n✗ Grok API test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline_with_grok():
    """Test full pipeline with Grok"""
    
    print("\n\n" + "="*70)
    print("FULL PIPELINE TEST WITH GROK API")
    print("="*70)
    
    from main import AutomatedInsightEngine
    
    try:
        # Initialize with Grok
        print("\n[1] Initializing engine with Grok...")
        engine = AutomatedInsightEngine(use_llm=True, llm_model="grok-2")
        print("✓ Engine initialized with Grok")
        
        # Check data
        train_path = "../train_adc/train.csv"
        item_path = "../train_adc/item_data.csv"
        
        if not os.path.exists(train_path):
            print(f"✗ Training data not found: {train_path}")
            return False
        
        # Run pipeline
        print("\n[2] Running pipeline with Grok insights...")
        results = engine.process_ctr_data(
            train_file=train_path,
            item_file=item_path if os.path.exists(item_path) else None
        )
        
        print("✓ Pipeline completed with Grok insights!")
        
        # Display results
        if "reports" in results:
            print("\nGenerated Reports:")
            for report_type, path in results["reports"].items():
                if path and os.path.exists(path):
                    size_kb = os.path.getsize(path) / 1024
                    print(f"  ✓ {report_type.upper()}: {size_kb:.1f} KB")
        
        if "insights" in results:
            print("\nGrok-Generated Insights:")
            for insight_type, content in results["insights"].items():
                preview = content[:150] if content else "N/A"
                print(f"  - {insight_type.replace('_', ' ').title()}: {preview}...")
        
        print("\n✓ Full pipeline with Grok PASSED!")
        return True
    
    except Exception as e:
        print(f"\n✗ Full pipeline test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test Grok API
    grok_test = test_grok_api()
    
    # Test full pipeline if Grok test passed
    if grok_test:
        pipeline_test = test_full_pipeline_with_grok()
    else:
        pipeline_test = False
    
    print("\n\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Grok API Test: {'✓ PASSED' if grok_test else '✗ FAILED'}")
    print(f"Full Pipeline Test: {'✓ PASSED' if pipeline_test else '✗ FAILED'}")
    print("="*70)
    
    sys.exit(0 if (grok_test and pipeline_test) else 1)
