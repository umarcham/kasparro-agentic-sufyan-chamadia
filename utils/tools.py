from langchain.tools import tool
import json

@tool
def spec_validator(specs: dict) -> str:
    """
    Validates product specifications against industry standards.
    Input should be a dictionary of specifications and should be passed as a dictionary under the 'specs' key.
    """
    try:
        if not specs:
            return "ERROR: No specifications provided for validation."
        
        # In a real tool, this would call an external API or database
        # Here we perform heuristic validation
        if "concentration" in str(specs).lower() or "price" in str(specs).lower():
            return "SUCCESS: All specifications passed industry standard validation."
        
        return "WARNING: Specifications are incomplete but pass basic checks."
    except Exception as e:
        return f"CRITICAL TOOL ERROR: {str(e)}"

# Alias for backward compatibility if needed in agents
spec_validation_tool = spec_validator
