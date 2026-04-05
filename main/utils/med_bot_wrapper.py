# main/med_bot_wrapper.py
"""
Wrapper for med_bot RAG engine with graceful fallback
Handles missing FAISS index and other import errors
"""

import sys
import os
import logging

logger = logging.getLogger('med_bot_wrapper')

# Add med_bot to path
med_bot_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'med_bot', 'src')
sys.path.insert(0, med_bot_path)

RAG_AVAILABLE = False
IMPORT_ERROR = None

def _safe_import_rag():
    """Safely import RAG engine with graceful fallback"""
    global RAG_AVAILABLE, IMPORT_ERROR
    
    try:
        # Try to import the answer_question function
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

def answer_question(question: str) -> str:
    """
    Answer medical questions using RAG engine with graceful fallback
    Returns helpful message if RAG is not available
    """
    if not _answer_question_orig:
        # Provide fallback response
        return (
            "⚠️ База протоколов временно недоступна.\n\n"
            "В случае неотложной ситуации (боль в груди, сильная одышка, обморок) "
            "немедленно вызовите скорую помощь: *103*.\n\n"
            "Пожалуйста, обратитесь к врачу для профессиональной консультации.\n\n"
            f"Техническая информация: {IMPORT_ERROR}"
        )
    
    try:
        return _answer_question_orig(question)
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {e}")
        return (
            "Извините, произошла ошибка при обработке вашего вопроса.\n\n"
            "В случае неотложной ситуации обратитесь к врачу."
        )

def is_rag_available() -> bool:
    """Check if RAG engine is available"""
    return RAG_AVAILABLE and _answer_question_orig is not None
