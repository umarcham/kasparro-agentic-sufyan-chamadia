from .schemas import AgentState, FAQList
from utils.llm_service import LLMService
from utils.logger import get_logger

logger = get_logger("QuestionGenerationAgent")

class QuestionGenerationAgent:
    def __init__(self):
        self.llm = LLMService()

    def generate_node(self, state: AgentState) -> dict:
        logger.info("--- GENERATING FAQS ---")
        prompt = f"""
        Generate exactly 15 frequently asked questions and answers for the following product:
        
        Product: {state.product_data.name}
        Description: {state.product_data.description}
        Details: {state.product_data.specs}
        
        Requirements:
        1. Produce exactly 15 items.
        2. Categorize into: informational, usage, safety, pricing, comparison.
        3. Ensure answers are grounded in the provided product data.
        """
        
        try:
            faq_list = self.llm.generate_structured_output(prompt, FAQList)
            
            if not faq_list or len(faq_list.items) != 15:
                logger.warning(f"Contract Violation: Expected 15 FAQs, got {len(faq_list.items) if faq_list else 0}")
                return {
                    "errors": [f"FAQ generation failed: expected 15 items, got {len(faq_list.items) if faq_list else 0}"],
                    "iteration_count": state.iteration_count + 1
                }
                
            return {"faqs": faq_list.items}
        except Exception as e:
            logger.error(f"FAQ Generation failed: {e}")
            return {
                "errors": [f"FAQ Generation failed: {e}"],
                "iteration_count": state.iteration_count + 1
            }
