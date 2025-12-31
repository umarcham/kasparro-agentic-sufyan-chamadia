from .schemas import AgentState, ComparisonTable
from utils.llm_service import LLMService
from utils.logger import get_logger

logger = get_logger("ComparisonAgent")

class ComparisonAgent:
    def __init__(self):
        self.llm = LLMService()

    def compare_node(self, state: AgentState) -> dict:
        logger.info("--- GENERATING COMPARISON DATA ---")
        prompt = f"""
        Analyze the following product and generate a comparison table against one generic competitor.
        
        Product: {state.product_data.name}
        Details: {state.product_data.specs}
        
        Requirements:
        1. Identify 5 key attributes for comparison.
        2. Use snake_case for all attribute names (e.g., price_inr, target_skin_type).
        3. Ensure prices are integers.
        4. Ensure skin types are lists of strings.
        5. Provide a 2-3 sentence grounded, objective summary of the comparison.
        """
        
        try:
            comparison_data = self.llm.generate_structured_output(prompt, ComparisonTable)
            return {"comparison_data": comparison_data}
        except Exception as e:
            logger.error(f"Comparison generation failed: {e}")
            return {"errors": [f"Comparison failed: {e}"]}
