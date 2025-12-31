from typing import Any
from .schemas import AgentState, FAQItem
from .template_manager import TemplateManager
from utils.logger import get_logger

logger = get_logger("PageAssemblerAgent")

class PageAssemblerAgent:
    def __init__(self):
        self.template_agent = TemplateManager()

    def assemble_node(self, state: AgentState) -> dict:
        logger.info("--- ASSEMBLING OUTPUT PAGES ---")
        product_data = state.product_data
        faqs = state.faqs
        logic_blocks = state.logic_blocks
        comparison_data = state.comparison_data
        
        if not product_data:
            logger.error("No product data available for assembly.")
            return {"errors": ["No product data available for assembly"]}

        faq_template = self.template_agent.get_template("faq_page", product_data)
        faq_page = self._fill_faq(faq_template, product_data, faqs)
        
        product_template = self.template_agent.get_template("product_page", product_data)
        product_page = self._fill_product(product_template, product_data, logic_blocks)
        
        comp_template = self.template_agent.get_template("comparison_page", product_data)
        comparison_page = self._fill_comparison(comp_template, product_data, comparison_data, logic_blocks)
        
        if comparison_page is None:
            logger.error("Comparison data missing during assembly.")
            return {
                "errors": ["Comparison data missing during page assembly"],
                "iteration_count": state.iteration_count + 1
            }
            
        return {
            "output_files": {
                "faq.json": faq_page,
                "product_page.json": product_page,
                "comparison_page.json": comparison_page
            }
        }

    def _fill_faq(self, template: dict, product: Any, faqs: list[FAQItem]) -> dict:
        assembled = template.copy()
        if not assembled.get("title"):
             assembled["title"] = f"{product.name} - FAQ"
        for section in assembled.get("sections", []):
            if section.get("type") == "faq_list":
                section["content"] = [item.model_dump() for item in faqs]
        return assembled

    def _fill_product(self, template: dict, product: Any, blocks: dict) -> dict:
        assembled = template.copy()
        if not assembled.get("title"):
            assembled["title"] = f"{product.name} - Product Details"
        assembled["description"] = product.description
        if "blocks" in assembled:
            assembled["blocks"] = [
                {"title": "Benefits", "content": blocks.get("benefits", "")},
                {"title": "Usage Instructions", "content": blocks.get("usage_instructions", "")},
                {"title": "Safety Summary", "content": blocks.get("safety_summary", "")}
            ]
        return assembled

    def _fill_comparison(self, template: dict, product: Any, comparison_data: Any, blocks: dict) -> dict:
        assembled = template.copy()
        if not assembled.get("title"):
             assembled["title"] = f"{product.name} - Comparison Guide"
        
        if comparison_data:
            assembled["comparison_table"] = {
                "attributes": comparison_data.attributes,
                "products": comparison_data.products
            }
            assembled["comparison_summary"] = comparison_data.comparison_summary
        else:
            return None
            
        return assembled
