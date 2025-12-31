from pydantic import BaseModel
from .schemas import AgentState
from utils.llm_service import LLMService
from utils.logger import get_logger

logger = get_logger("QualityCheckerAgent")

class QualityCheckResult(BaseModel):
    is_valid: bool
    feedback: str

class QualityCheckerAgent:
    def __init__(self):
        self.llm = LLMService()

    def audit_node(self, state: AgentState) -> dict:
        logger.info("--- AUDITING CONTENT QUALITY ---")
        
        if not state.faqs or len(state.faqs) != 15:
            logger.warning("Deterministic Check Failed: Incorrect FAQ count.")
            return {
                "quality_feedback": "FAILED: FAQ list must contain exactly 15 items.",
                "iteration_count": state.iteration_count + 1
            }

        prompt = f"""
        Audit the following generated content for professionalism, accuracy, and formatting.
        
        FAQs: {state.faqs}
        Logic Blocks: {state.logic_blocks}
        Comparison: {state.comparison_data}
        
        If there are formatting errors (like triple newlines or broken strings), mark as is_valid=false.
        Otherwise, if everything looks professional, mark is_valid=true.
        """
        
        try:
            res = self.llm.generate_structured_output(prompt, QualityCheckResult)
            if not res:
                logger.error("Auditor failed to generate structured output.")
                return {
                    "quality_feedback": "LLM_AUDIT_FAILED: Content could not be validated by AI auditor.",
                    "errors": state.errors + ["Quality checker LLM failed to generate structured output."],
                    "iteration_count": state.iteration_count + 1
                }
                
            return {
                "quality_feedback": "PASSED" if res.is_valid or state.iteration_count >= 2 else res.feedback,
                "iteration_count": state.iteration_count + 1
            }
        except Exception as e:
            logger.error(f"Auditor Node Failure: {e}")
            return {
                "quality_feedback": f"AUDIT_ERROR: {e}",
                "iteration_count": state.iteration_count + 1
            }
