import json
import os
import re
from utils.logger import get_logger

logger = get_logger("TemplateManager")

class TemplateManager:
    def __init__(self, template_path: str = "templates/page_templates.json"):
        self.template_path = template_path
        self.templates = self._load_templates()

    def _load_templates(self):
        try:
            with open(self.template_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load templates from {self.template_path}: {e}")
            return {}

    def get_template(self, template_name: str, product_data: any = None) -> dict:
        template = self.templates.get(template_name, {})
        if not template:
            logger.warning(f"Template '{template_name}' not found.")
            return {}
            
        if product_data:
            template_str = json.dumps(template)
            vars_found = re.findall(r'\{\{(.*?)\}\}', template_str)
            for var in vars_found:
                val = getattr(product_data, var, None)
                if val:
                    template_str = template_str.replace(f"{{{{{var}}}}}", str(val))
            try:
                template = json.loads(template_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse template after injection: {e}")
                
        return template
