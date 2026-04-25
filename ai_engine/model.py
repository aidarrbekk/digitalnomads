# ai_engine/model.py
"""
Groq LLM client for RAG pipeline.
Exposes generate_answer(prompt) and set_model(name).
"""

import os
import logging
import yaml
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI


# -- Config --------------------------------------------------------------------

def load_config() -> dict:
    src  = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(src)
    with open(os.path.join(root, "config.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)

def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


ROOT = project_root()
load_dotenv(os.path.join(ROOT, ".env"))

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("model")

cfg = load_config()

MAX_TOKENS  = cfg["model"]["max_tokens"]
TEMPERATURE = cfg["model"]["temperature"]

DEFAULT_MODEL = "llama-3.3-70b-versatile"
ALLOWED_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

CURRENT_MODEL: str = DEFAULT_MODEL

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Initialize OpenAI client for Google Gemini fallback
gemini_fallback_client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY", "paste_your_gemini_api_key_here")
)


# -- Public API ----------------------------------------------------------------

def set_model(name: str) -> None:
    """Switch the active model. Raises ValueError for unknown names."""
    global CURRENT_MODEL
    if name not in ALLOWED_MODELS:
        raise ValueError(f"Unknown model '{name}'. Allowed: {ALLOWED_MODELS}")
    CURRENT_MODEL = name
    logger.info(f"Model switched to: {CURRENT_MODEL}")


def generate_answer(prompt: str) -> str:
    """Send prompt to Groq API and return the response. Fallbacks to OpenRouter if Groq fails or times out."""
    try:
        response = client.chat.completions.create(
            model=CURRENT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            timeout=1.0,
        )
        answer = response.choices[0].message.content
        return answer.strip() if answer else ""
    except Exception as e:
        logger.warning(f"Groq request failed or timed out ({e}). Switching to Gemini fallback.")
        try:
            fallback_response = gemini_fallback_client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
            )
            answer = fallback_response.choices[0].message.content
            return answer.strip() if answer else ""
        except Exception as fallback_e:
            logger.error(f"Gemini fallback also failed: {fallback_e}")
            raise
