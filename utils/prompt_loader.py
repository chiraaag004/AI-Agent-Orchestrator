# d:\Work\ai_hackathon\utils\prompt_loader.py
from langchain.prompts import PromptTemplate

def load_prompt_from_file(file_path: str) -> PromptTemplate:
    """Helper to load a prompt template from a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return PromptTemplate.from_template(f.read())