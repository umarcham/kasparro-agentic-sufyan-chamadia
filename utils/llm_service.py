import os
import time
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from .logger import get_logger

load_dotenv()

logger = get_logger("LLMService")
T = TypeVar("T", bound=BaseModel)

class LLMService:
    def __init__(self, model_name: str = "gemini-flash-latest", max_retries: int = 3):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found in environment.")
            raise RuntimeError(
                "GOOGLE_API_KEY not found in environment. "
                "LLM execution is required and cannot proceed without it."
            )
            
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0,
        )
        self.max_retries = max_retries

    def generate_content(self, prompt: str) -> str:
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Generating content (Attempt {attempt + 1})")
                response = self.llm.invoke([HumanMessage(content=prompt)])
                if not response.content:
                    raise RuntimeError("LLM returned empty content.")
                return response.content
            except Exception as e:
                last_error = e
                logger.warning(f"LLM attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt) # Exponential backoff
        
        logger.error(f"LLM exhausted all {self.max_retries} attempts. Final error: {last_error}")
        raise RuntimeError(f"LLM Failure after {self.max_retries} retries: {last_error}")

    def generate_structured_output(self, prompt: str, schema: Type[T]) -> T:
        structured_llm = self.llm.with_structured_output(schema)
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Generating structured output for {schema.__name__} (Attempt {attempt + 1})")
                result = structured_llm.invoke([HumanMessage(content=prompt)])
                if not result:
                    raise RuntimeError(f"LLM failed to return structured output for schema {schema.__name__}")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"Structured LLM attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt)
        
        logger.error(f"Structured LLM exhausted all {self.max_retries} attempts for {schema.__name__}. Final error: {last_error}")
        raise RuntimeError(f"Structured LLM Failure after {self.max_retries} retries for {schema.__name__}: {last_error}")
