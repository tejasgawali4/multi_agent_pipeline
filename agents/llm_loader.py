"""
LLM loader — wraps HuggingFace Inference API via LangChain.
All agents import get_llm() from here so the model is configured in one place.
"""

import os
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from dotenv import load_dotenv

load_dotenv()

# Recommended free-tier HuggingFace Inference API models:
#   - mistralai/Mistral-7B-Instruct-v0.3      (fast, reliable)
#   - mistralai/Mixtral-8x7B-Instruct-v0.1    (higher quality, slower)
#   - HuggingFaceH4/zephyr-7b-beta             (good structured output)

DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"


def get_llm(repo_id: str = DEFAULT_MODEL, max_new_tokens: int = 2048):
    """
    Returns a ChatHuggingFace LLM instance backed by the HF Inference API.

    Args:
        repo_id: HuggingFace model repo ID (must be an instruct/chat model).
        max_new_tokens: Maximum tokens the model will generate per call.

    Returns:
        ChatHuggingFace instance ready for .invoke() calls.

    Requires:
        HF_TOKEN environment variable set in .env
    """
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise EnvironmentError(
            "HF_TOKEN not found. Please set it in your .env file."
        )

    endpoint = HuggingFaceEndpoint(
        repo_id=repo_id,
        huggingfacehub_api_token=hf_token,
        task="text-generation",
        max_new_tokens=max_new_tokens,
        temperature=0.2,       # Low temp for deterministic code generation
        do_sample=True,
        repetition_penalty=1.1,
    )

    return ChatHuggingFace(llm=endpoint, verbose=False)
