"""
Groq LLM client for medical document analysis.
Extracts structured lab values from medical text and generates health tips.
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

# Load .env from the project root (not the cwd) so the key is always found
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env'))

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_AVAILABLE = bool(GROQ_API_KEY)

EXTRACTION_PROMPT = """You are a medical lab report parser. Extract lab test results from the following medical text.

Return ONLY a valid JSON object with this exact structure:
{
  "lab_results": [
    {
      "test_name": "Glucose",
      "test_name_ru": "Глюкоза",
      "value": 5.8,
      "unit": "mmol/L",
      "reference_range_low": 3.9,
      "reference_range_high": 6.1,
      "reference_range_text": "3.9-6.1 mmol/L",
      "status": "normal",
      "category": "blood_sugar"
    }
  ],
  "summary": "Brief 1-2 sentence summary of the overall lab report",
  "summary_ru": "Краткое описание результатов анализов на русском"
}

Rules:
1. Only extract values that are EXPLICITLY present in the text. Do NOT invent values.
2. Status must be one of: "normal", "low", "high", "critical"
3. If reference range is in the text, use it. Otherwise use standard medical ranges.
4. Category must be one of: blood_sugar, lipid, hematology, kidney, liver, thyroid, minerals, vitamins, urine, other
5. The text may be in English or Russian — handle both.
6. Return empty lab_results array if no lab values found.
7. Always provide both English test_name and Russian test_name_ru.

Medical text to parse:
---
{text}
---"""

HEALTH_TIPS_PROMPT = """You are a health advisor. Based on the following lab results and vital signs, provide personalized health and nutrition recommendations.

Lab Results:
{lab_json}

Vital Signs:
{vitals_json}

Return ONLY a valid JSON object:
{{
  "tips": [
    {{
      "category": "nutrition",
      "title": "Improve Iron Intake",
      "title_ru": "Повысьте потребление железа",
      "description": "Your ferritin is low. Include red meat, spinach, and legumes in your diet.",
      "description_ru": "Ваш ферритин понижен. Включите в рацион красное мясо, шпинат и бобовые.",
      "priority": "high",
      "related_test": "Ferritin"
    }}
  ]
}}

Rules:
1. Categories: nutrition, exercise, lifestyle, supplement, medical_attention
2. Priority: low, medium, high
3. Provide 3-8 specific, actionable tips
4. Always include both English and Russian text
5. Base recommendations on actual abnormal values only
6. For nutrition tips, mention specific foods
7. If lab results are all normal, provide general wellness tips"""


def extract_lab_values(text):
    """Extract lab values from medical text using Groq LLM.

    Returns dict with 'lab_results' list and 'summary' string.
    Returns error dict if Groq is unavailable.
    """
    if not GROQ_AVAILABLE:
        return {
            "error": "Groq API key not configured. Please enter lab values manually.",
            "error_ru": "API-ключ Groq не настроен. Пожалуйста, введите значения вручную.",
            "lab_results": [],
            "summary": "",
            "summary_ru": "",
        }

    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        prompt = EXTRACTION_PROMPT.replace("{text}", text[:8000])

        response = client.chat.completions.create(
            model=os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4000,
            response_format={"type": "json_object"},
            timeout=1.0,
        )

        content = response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Groq extraction failed or timed out ({e}). Switching to OpenRouter fallback.")
        try:
            from openai import OpenAI
            openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ.get("OPENROUTER_API_KEY", "paste_your_api_key_here")
            )
            fallback_response = openrouter_client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct:free",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )
            content = fallback_response.choices[0].message.content
        except Exception as fallback_e:
            logger.error(f"OpenRouter extraction fallback failed: {fallback_e}")
            return {
                "error": f"Extraction failed: {str(fallback_e)}",
                "error_ru": f"Ошибка извлечения: {str(fallback_e)}",
                "lab_results": [],
                "summary": "",
                "summary_ru": "",
            }
    
    try:
        result = json.loads(content)

        if "lab_results" not in result:
            result["lab_results"] = []
        if "summary" not in result:
            result["summary"] = ""
        if "summary_ru" not in result:
            result["summary_ru"] = ""

        # Validate and clean each lab result
        cleaned = []
        for lr in result["lab_results"]:
            if not lr.get("test_name") or lr.get("value") is None:
                continue
            try:
                lr["value"] = float(lr["value"])
            except (ValueError, TypeError):
                continue
            for key in ("reference_range_low", "reference_range_high"):
                if lr.get(key) is not None:
                    try:
                        lr[key] = float(lr[key])
                    except (ValueError, TypeError):
                        lr[key] = None
            if lr.get("status") not in ("normal", "low", "high", "critical"):
                lr["status"] = _compute_status(
                    lr["value"], lr.get("reference_range_low"), lr.get("reference_range_high")
                )
            cleaned.append(lr)

        result["lab_results"] = cleaned
        return result

        result["lab_results"] = cleaned
        return result

    except Exception as e:
        logger.error(f"Failed to parse extraction result: {e}")
        return {
            "error": f"Extraction parsing failed: {str(e)}",
            "error_ru": f"Ошибка извлечения: {str(e)}",
            "lab_results": [],
            "summary": "",
            "summary_ru": "",
        }


def generate_health_tips(lab_results, metrics=None):
    """Generate personalized health tips based on lab results and vitals.

    Args:
        lab_results: list of LabResult model objects
        metrics: MedicalMetrics model object (optional)

    Returns dict with 'tips' list.
    """
    if not GROQ_AVAILABLE:
        return {"tips": [], "error": "Groq API not configured"}

    lab_json = json.dumps([
        {
            "test_name": lr.test_name,
            "value": lr.value,
            "unit": lr.unit,
            "status": lr.status,
            "reference_range": lr.reference_range_text,
        }
        for lr in lab_results
    ], indent=2)

    vitals_json = "{}"
    if metrics:
        vitals = {}
        if metrics.height_cm and metrics.weight_kg:
            vitals["BMI"] = round(metrics.weight_kg / ((metrics.height_cm / 100) ** 2), 1)
        if metrics.blood_pressure_systolic:
            vitals["Blood Pressure"] = f"{metrics.blood_pressure_systolic}/{metrics.blood_pressure_diastolic}"
        if metrics.heart_rate:
            vitals["Heart Rate"] = f"{metrics.heart_rate} bpm"
        if metrics.oxygen_saturation:
            vitals["SpO2"] = f"{metrics.oxygen_saturation}%"
        if metrics.chronic_conditions:
            vitals["Chronic Conditions"] = metrics.chronic_conditions
        vitals_json = json.dumps(vitals, indent=2)

    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        prompt = HEALTH_TIPS_PROMPT.replace("{lab_json}", lab_json).replace("{vitals_json}", vitals_json)

        response = client.chat.completions.create(
            model=os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3000,
            response_format={"type": "json_object"},
            timeout=1.0,
        )

        content = response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Groq health tips generation failed or timed out ({e}). Switching to OpenRouter fallback.")
        try:
            from openai import OpenAI
            openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ.get("OPENROUTER_API_KEY", "paste_your_api_key_here")
            )
            fallback_response = openrouter_client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct:free",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=3000,
                response_format={"type": "json_object"},
            )
            content = fallback_response.choices[0].message.content
        except Exception as fallback_e:
            logger.error(f"OpenRouter health tips fallback failed: {fallback_e}")
            return {"tips": [], "error": str(fallback_e)}
            
    try:
        result = json.loads(content)

        if "tips" not in result:
            result["tips"] = []
        return result

    except Exception as e:
        logger.error(f"Failed to parse health tips result: {e}")
        return {"tips": [], "error": str(e)}


def _compute_status(value, low, high):
    """Compute status from value and reference range."""
    if low is None or high is None:
        return "normal"
    if value < low * 0.7 or value > high * 1.5:
        return "critical"
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "normal"
