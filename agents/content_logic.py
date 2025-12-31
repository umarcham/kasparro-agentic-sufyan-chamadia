from pydantic import BaseModel
from typing import Dict
from .schemas import AgentState
from utils.llm_service import LLMService
from utils.logger import get_logger

logger = get_logger("ContentLogicAgent")

class LogicResponse(BaseModel):
    blocks: Dict[str, str]

class ContentLogicAgent:
    def __init__(self):
        self.llm = LLMService()

    def extract_node(self, state: AgentState) -> dict:
        logger.info("--- EXTRACTING LOGIC BLOCKS ---")
        prompt = f"""
        Extract the following logic blocks for the product: {state.product_data.name}.
        
        Available Data: {state.product_data.model_dump()}
        
        Required Blocks:
        - benefits: Key advantages and USP.
        - usage_instructions: Step-by-step apply guide.
        - safety_summary: Quick safety reference.
        
        Format as a JSON dictionary.
        """
        
        try:
            res = self.llm.generate_structured_output(prompt, LogicResponse)
            return {"logic_blocks": res.blocks}
        except Exception as e:
            logger.error(f"Logic extraction failed: {e}")
            return {"errors": [f"Logic extraction failed: {e}"]}
