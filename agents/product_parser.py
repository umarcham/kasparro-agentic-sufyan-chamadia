import json
from .schemas import AgentState, ProductData
from utils.logger import get_logger
from utils.llm_service import LLMService

# Import the tool
try:
    from utils.tools import spec_validator
except ImportError:
    spec_validator = None

logger = get_logger("ProductParserAgent")

class ProductParserAgent:
    def __init__(self):
        self.llm = LLMService()

    def parse_node(self, state: AgentState) -> dict:
        logger.info("--- PARSING PRODUCT DATA ---")
        prompt = f"""
        Parse the following raw product information into a structured JSON format.
        
        Raw Input: {state.raw_input}
        
        Requirements:
        1. Extract product name, description, specs (price, target, primary_spec).
        2. Identify key highlights and benefits.
        3. Extract usage instructions and safety information.
        """
        
        try:
            product_data = self.llm.generate_structured_output(prompt, ProductData)
        except Exception as e:
            logger.error(f"LLM Parsing failed: {e}")
            return {"errors": [f"Parsing failed: {e}"]}

        # Tool usage for reasoning/processing with robust error handling
        validation_result = "Tool unavailable"
        if spec_validator:
            try:
                if product_data.specs:
                    validation_result = spec_validator.invoke({"specs": product_data.specs.model_dump()})
                logger.info(f"Spec Tool Validation result: {validation_result}")
            except Exception as tool_err:
                logger.warning(f"Tool execution failed: {tool_err}")
                validation_result = f"Tool Error: {tool_err}"
        else:
            logger.warning("spec_validator tool is missing/not imported.")

        return {
            "product_data": product_data,
            "metadata": {**state.metadata, "spec_validation": validation_result}
        }
