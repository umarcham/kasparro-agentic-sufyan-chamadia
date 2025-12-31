from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any

class FAQItem(BaseModel):
    category: str = Field(description="Category of the question (informational, usage, safety, pricing, comparison)")
    question: str = Field(description="The frequently asked question")
    answer: str = Field(description="The accurate answer based on product data")

class FAQList(BaseModel):
    items: List[FAQItem] = Field(description="List of exactly 15 FAQ items")

class LogicBlock(BaseModel):
    title: str
    content: str

class ComparisonTable(BaseModel):
    attributes: List[str] = Field(description="List of snake_case attributes to compare (e.g., price_inr, target_skin_type)")
    products: List[Dict[str, Any]] = Field(description="List of product comparison data. Keys MUST be snake_case. 'price_inr' MUST be integer. 'target_skin_type' MUST be a list of strings.")
    comparison_summary: str = Field(description="A concise, 2-3 sentence grounded summary of the comparison data, avoiding marketing fluff.")

    @validator("products")
    def products_not_empty(cls, v):
        if len(v) < 2:
            raise ValueError("Comparison requires at least two products")
        return v

    @validator("products")
    def validate_product_fields(cls, products):
        for product in products:
            if "price_inr" in product and not isinstance(product["price_inr"], int):
                try:
                    product["price_inr"] = int(product["price_inr"])
                except (ValueError, TypeError):
                    raise ValueError(f"price_inr must be an integer, got {type(product['price_inr']).__name__}")
            
            if "target_skin_type" in product and not isinstance(product["target_skin_type"], list):
                if isinstance(product["target_skin_type"], str):
                    product["target_skin_type"] = [s.strip() for s in product["target_skin_type"].split(",")]
                else:
                    raise ValueError(f"target_skin_type must be a list, got {type(product['target_skin_type']).__name__}")
        return products

class ProductSpecs(BaseModel):
    primary_spec: str
    secondary_spec: Optional[str] = ""
    target: Any
    price: str

class SafetyInfo(BaseModel):
    details: str
    warnings: List[str]

class ProductData(BaseModel):
    name: str
    description: str
    specs: ProductSpecs
    highlights: List[str]
    benefits: List[str]
    usage: str
    safety: SafetyInfo

class RawProductInput(BaseModel):
    """Schema for the initial raw input validation."""
    title: str = Field(description="Name of the product")
    description: str = Field(description="Brief product summary")
    price: Any = Field(description="Retail price")
    ingredients: List[str] = Field(default_factory=list)
    usage: Optional[str] = ""
    safety: Optional[str] = ""
    target_skin_type: List[str] = Field(default_factory=list)

class AgentState(BaseModel):
    raw_input: Dict[str, Any] = Field(default_factory=dict)
    product_data: Optional[ProductData] = None
    faqs: List[FAQItem] = Field(default_factory=list)
    logic_blocks: Dict[str, str] = Field(default_factory=dict)
    comparison_data: Optional[ComparisonTable] = None
    output_files: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    quality_feedback: str = ""
    iteration_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
