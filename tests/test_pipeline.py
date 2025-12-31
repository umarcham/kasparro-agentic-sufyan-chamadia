import pytest
import os
import json
from agents.orchestrator import Orchestrator

def test_full_pipeline_contract():
    """Tests that the pipeline respects the strict engineering contracts."""
    orch = Orchestrator()
    sample_input = {
        "title": "Test Serum",
        "description": "High hygiene test product",
        "price": 1000,
        "ingredients": ["Clean Code"],
        "target_skin_type": ["Developer", "Reviewer"]
    }
    
    results = orch.run_pipeline(sample_input, thread_id="test_run")
    
    # 1. Check for success
    assert not results.get("errors"), f"Pipeline failed with errors: {results.get('errors')}"
    
    # 2. Check FAQ Contract (Gap 15)
    assert len(results["faqs"]) == 15, f"FAQ count mismatch: {len(results['faqs'])}"
    
    # 3. Check for output files
    assert "faq.json" in results["output_files"]
    assert "product_page.json" in results["output_files"]
    assert "comparison_page.json" in results["output_files"]

def test_input_validation_failure():
    """Tests that the new validation node catches bad data early (Gap 12)."""
    orch = Orchestrator()
    bad_input = {"title": "Missing Fields"} # Lacks required fields
    
    results = orch.run_pipeline(bad_input, thread_id="fail_test")
    assert len(results["errors"]) > 0
    assert "Invalid input data" in results["errors"][0]
