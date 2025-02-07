from langchain_openai import ChatOpenAI

import os

# Initialize the LLM
llm = ChatOpenAI(
    model_name="gpt-4o",
    openai_api_key=" "
)

def llm_call(prompt: str) -> str:
    response = llm.invoke(prompt)
    return response.content

def extract_xml(text: str, tag: str) -> str:
    # Simple XML extraction
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    start = text.find(start_tag) + len(start_tag)
    end = text.find(end_tag)
    return text[start:end].strip() 
