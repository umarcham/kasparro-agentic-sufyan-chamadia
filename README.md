# Kasparro Agentic System: High-Hygiene Enterprise Pipeline

An advanced, production-grade agentic pipeline built with **LangGraph** and **Pydantic V2**. This system transforms raw product data into high-quality, validated FAQs and Product Pages.

## 🛡️ Applied Hardening (Redemption Overhaul)
- **Zero-Fallback deterministic execution**.
- **Exponential Backoff Retries** (3 attempts).
- **Centralized Logging** (`logs/execution.log`).
- **Strict Input Validation Node**.
- **Loop Safety Guards** (`max_iterations=3`).

## 🛠️ Execution
1. Install dependencies: `pip install -r requirements.txt`
2. Set key: `export GOOGLE_API_KEY=your_key`
3. Run: `python3 -m agents.orchestrator --input data/product_input.json --output output/`
