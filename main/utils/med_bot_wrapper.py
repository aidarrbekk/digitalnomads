# main/med_bot_wrapper.py
"""
Wrapper for med_bot RAG engine with graceful fallback
Handles missing FAISS index and other import errors
"""

import sys
import os
import logging

logger = logging.getLogger('med_bot_wrapper')

# Add ai_engine to path
med_bot_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ai_engine')
sys.path.insert(0, med_bot_path)

RAG_AVAILABLE = False
IMPORT_ERROR = None

def _safe_import_rag():
    """Safely import RAG engine with graceful fallback"""
    global RAG_AVAILABLE, IMPORT_ERROR
    
    try:
        from rag_engine import answer_question as _answer_question
        RAG_AVAILABLE = True
        return _answer_question
    except FileNotFoundError as e:
        IMPORT_ERROR = f"FAISS index not found: {e}"
        logger.warning(IMPORT_ERROR)
        return None
    except ImportError as e:
        IMPORT_ERROR = f"Import error: {e}"
        logger.warning(IMPORT_ERROR)
        return None
    except Exception as e:
        IMPORT_ERROR = f"Unexpected error loading RAG: {e}"
        logger.warning(IMPORT_ERROR)
        return None

# Try to load RAG engine
_answer_question_orig = _safe_import_rag()

def answer_question(question: str, medical_context: str = "") -> str:
    """
    Answer medical questions using RAG engine with graceful fallback.
    medical_context: optional string with user's medical card info.
    """
    if not _answer_question_orig:
        return (
            "Warning: Protocol database is temporarily unavailable.\n\n"
            "In case of emergency (chest pain, severe shortness of breath, fainting) "
            "call an ambulance immediately: *103*.\n\n"
            "Please consult a doctor for professional advice.\n\n"
            f"Technical info: {IMPORT_ERROR}"
        )
    
    try:
        return _answer_question_orig(question, medical_context=medical_context)
    except TypeError:
        # Fallback if rag_engine doesn't accept medical_context yet
        return _answer_question_orig(question)
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {e}")
        return (
            "Sorry, an error occurred while processing your question.\n\n"
            "In case of emergency, please consult a doctor."
        )

def is_rag_available() -> bool:
    """Check if RAG engine is available"""
    return RAG_AVAILABLE and _answer_question_orig is not None
