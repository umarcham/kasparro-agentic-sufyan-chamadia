import os
import json
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .schemas import AgentState, RawProductInput
from .product_parser import ProductParserAgent
from .question_generator import QuestionGenerationAgent
from .content_logic import ContentLogicAgent
from .comparison_agent import ComparisonAgent
from .quality_checker import QualityCheckerAgent
from .page_assembler import PageAssemblerAgent
from utils.logger import get_logger

logger = get_logger("Orchestrator")

class Orchestrator:
    def __init__(self):
        self.parser = ProductParserAgent()
        self.question_gen = QuestionGenerationAgent()
        self.content_logic = ContentLogicAgent()
        self.comparison_agent = ComparisonAgent()
        self.quality_checker = QualityCheckerAgent()
        self.assembler = PageAssemblerAgent()
        self.memory = MemorySaver()
        self.builder = self._create_graph()

    def validate_input_node(self, state: AgentState) -> dict:
        """New node to strictly validate raw input before parsing."""
        logger.info("--- VALIDATING RAW INPUT ---")
        try:
            RawProductInput(**state.raw_input)
            return {"errors": []}
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return {"errors": [f"Invalid input data: {e}"]}

    def _create_graph(self):
        workflow = StateGraph(AgentState)

        # Add Nodes
        workflow.add_node("validate_input", self.validate_input_node)
        workflow.add_node("parse_product", self.parser.parse_node)
        workflow.add_node("generate_faq", self.question_gen.generate_node)
        workflow.add_node("extract_logic", self.content_logic.extract_node)
        workflow.add_node("generate_comparison", self.comparison_agent.compare_node)
        workflow.add_node("audit_quality", self.quality_checker.audit_node)
        workflow.add_node("assemble_pages", self.assembler.assemble_node)

        # Build Edges
        workflow.set_entry_point("validate_input")
        
        # Decision after validation
        workflow.add_conditional_edges(
            "validate_input",
            lambda x: "failed" if x.errors else "passed",
            {
                "passed": "parse_product",
                "failed": END
            }
        )

        workflow.add_edge("parse_product", "generate_faq")
        workflow.add_edge("generate_faq", "extract_logic")
        workflow.add_edge("extract_logic", "generate_comparison")
        workflow.add_edge("generate_comparison", "audit_quality")

        workflow.add_conditional_edges(
            "audit_quality",
            self.quality_gate_logic,
            {
                "retry": "generate_faq",
                "halt": END,
                "passed": "assemble_pages"
            }
        )

        workflow.add_edge("assemble_pages", END)

        return workflow.compile(checkpointer=self.memory)

    def quality_gate_logic(self, state: AgentState) -> str:
        # Loop safety guard
        if state.iteration_count >= 3:
            logger.error("Max iterations reached. Halting pipeline.")
            return "halt"
            
        if state.quality_feedback == "PASSED":
            logger.info("Quality gate PASSED.")
            return "passed"
        else:
            logger.info(f"Quality gate FAILED. Retry count: {state.iteration_count}")
            return "retry"

    def run_pipeline(self, input_data: dict, thread_id: str = "default_thread"):
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = AgentState(raw_input=input_data)
        
        logger.info(f"Starting pipeline for thread: {thread_id}")
        final_state = self.builder.invoke(initial_state, config)
        
        # Cleanup output files for terminal reporting
        if final_state.get("output_files"):
            for filename, content in final_state["output_files"].items():
                out_path = os.path.join("output", filename)
                os.makedirs("output", exist_ok=True)
                with open(out_path, "w") as f:
                    json.dump(content, f, indent=2)
                logger.info(f"Saved: {out_path}")
                
        return final_state

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="output/")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    orch = Orchestrator()
    results = orch.run_pipeline(data)
    
    if results.get("errors"):
        logger.error(f"Pipeline finished with errors: {results['errors']}")
        exit(1)
    else:
        logger.info("Pipeline completed successfully.")
