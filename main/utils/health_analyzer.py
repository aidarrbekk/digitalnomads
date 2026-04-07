"""
Health analysis engine based on established medical guidelines.
All recommendations reference WHO, AHA/ACC, and other trusted sources.
No AI or external API calls — pure rule-based evaluation.
"""


def analyze_health(metrics):
    """Analyze a user's MedicalMetrics and return guideline-based recommendations."""
    results = []

    bmi = _analyze_bmi(metrics.height_cm, metrics.weight_kg)
    if bmi:
        results.append(bmi)

    bp = _analyze_blood_pressure(
        metrics.blood_pressure_systolic, metrics.blood_pressure_diastolic
    )
    if bp:
        results.append(bp)

    hr = _analyze_heart_rate(metrics.heart_rate)
    if hr:
        results.append(hr)

    temp = _analyze_temperature(metrics.temperature_c)
    if temp:
        results.append(temp)

    spo2 = _analyze_oxygen_saturation(metrics.oxygen_saturation)
    if spo2:
        results.append(spo2)

    if not results:
        return {"has_data": False}

    risk_factors, risk_factors_ru = _identify_risk_factors(metrics, results)
    score, label, label_ru, color = _compute_health_score(results, len(risk_factors))

    warnings_count = sum(1 for r in results if r["status"] != "normal")

    return {
        "has_data": True,
        "health_score": score,
        "health_score_label": label,
        "health_score_label_ru": label_ru,
        "health_score_color": color,
        "metrics": results,
        "risk_factors": risk_factors,
        "risk_factors_ru": risk_factors_ru,
        "recommendations_count": warnings_count,
        "risk_factors_count": len(risk_factors),
        "last_updated": (
            metrics.last_updated.strftime("%Y-%m-%d %H:%M")
            if metrics.last_updated
            else None
        ),
    }


# ---------------------------------------------------------------------------
# BMI — WHO Global Database on Body Mass Index, 2000
# ---------------------------------------------------------------------------

def _analyze_bmi(height_cm, weight_kg):
    if not height_cm or not weight_kg or height_cm <= 0:
        return None

    bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)

    if bmi < 18.5:
        cat, status = "Underweight", "warning"
        rec = (
            "Your BMI is below the healthy range. Consider consulting a nutritionist "
            "to develop a balanced meal plan that supports healthy weight gain. "
            "Ensure adequate caloric intake with nutrient-dense foods."
        )
        rec_ru = (
            "Ваш ИМТ ниже нормы. Рекомендуется обратиться к диетологу для составления "
            "сбалансированного плана питания. Обеспечьте достаточное потребление калорий."
        )
    elif bmi < 25:
        cat, status = "Normal", "normal"
        rec = (
            "Your BMI is within the healthy range. Maintain your current lifestyle "
            "with regular physical activity and balanced nutrition."
        )
        rec_ru = (
            "Ваш ИМТ в пределах нормы. Поддерживайте текущий образ жизни "
            "с регулярной физической активностью и сбалансированным питанием."
        )
    elif bmi < 30:
        cat, status = "Overweight", "warning"
        rec = (
            "Your BMI indicates overweight. The WHO recommends at least 150 minutes "
            "of moderate-intensity physical activity per week and a diet rich in "
            "fruits, vegetables, and whole grains."
        )
        rec_ru = (
            "Ваш ИМТ указывает на избыточный вес. ВОЗ рекомендует не менее 150 минут "
            "умеренной физической активности в неделю и диету, богатую фруктами, "
            "овощами и цельнозерновыми продуктами."
        )
    elif bmi < 35:
        cat, status = "Obese (Class I)", "danger"
        rec = (
            "Your BMI indicates Class I obesity. This is associated with increased "
            "risk for heart disease, diabetes, and other conditions. Consult a "
            "healthcare provider for a personalized weight management plan."
        )
        rec_ru = (
            "Ваш ИМТ указывает на ожирение I степени. Это связано с повышенным риском "
            "сердечных заболеваний, диабета и других заболеваний. Обратитесь к врачу."
        )
    elif bmi < 40:
        cat, status = "Obese (Class II)", "danger"
        rec = (
            "Your BMI indicates Class II obesity, which significantly increases "
            "health risks. Please seek medical guidance for a comprehensive "
            "weight management and health improvement plan."
        )
        rec_ru = (
            "Ваш ИМТ указывает на ожирение II степени, что значительно увеличивает "
            "риски для здоровья. Обратитесь к врачу для комплексного плана лечения."
        )
    else:
        cat, status = "Obese (Class III)", "danger"
        rec = (
            "Your BMI indicates Class III (severe) obesity. This carries serious "
            "health risks. Immediate consultation with a healthcare provider is "
            "strongly recommended."
        )
        rec_ru = (
            "Ваш ИМТ указывает на ожирение III степени. Это несёт серьёзные риски "
            "для здоровья. Настоятельно рекомендуется немедленно обратиться к врачу."
        )

    return {
        "metric": "BMI",
        "metric_ru": "ИМТ",
        "value": bmi,
        "display_value": f"{bmi} kg/m\u00b2",
        "normal_range": "18.5 \u2013 24.9 kg/m\u00b2",
        "status": status,
        "category": cat,
        "category_ru": {
            "Underweight": "Недостаточный вес",
            "Normal": "Норма",
            "Overweight": "Избыточный вес",
            "Obese (Class I)": "Ожирение I ст.",
            "Obese (Class II)": "Ожирение II ст.",
            "Obese (Class III)": "Ожирение III ст.",
        }.get(cat, cat),
        "recommendation": rec,
        "recommendation_ru": rec_ru,
        "source": "WHO Global Database on Body Mass Index, 2000",
    }


# ---------------------------------------------------------------------------
# Blood Pressure — AHA/ACC Hypertension Guidelines, 2017
# ---------------------------------------------------------------------------

def _analyze_blood_pressure(systolic, diastolic):
    if not systolic or not diastolic:
        return None

    if systolic > 180 or diastolic > 120:
        cat, status = "Hypertensive Crisis", "danger"
        rec = (
            "Your blood pressure is dangerously high (hypertensive crisis). "
            "Seek emergency medical attention immediately."
        )
        rec_ru = (
            "Ваше артериальное давление опасно высокое (гипертонический криз). "
            "Немедленно обратитесь за экстренной медицинской помощью."
        )
    elif systolic >= 140 or diastolic >= 90:
        cat, status = "Hypertension Stage 2", "danger"
        rec = (
            "Your blood pressure is in the Stage 2 hypertension range. The AHA "
            "recommends a combination of lifestyle changes and medication. "
            "Consult your doctor promptly."
        )
        rec_ru = (
            "Ваше давление соответствует гипертонии 2 стадии. АКК рекомендует "
            "сочетание изменения образа жизни и медикаментов. Обратитесь к врачу."
        )
    elif systolic >= 130 or diastolic >= 80:
        cat, status = "Hypertension Stage 1", "warning"
        rec = (
            "Your blood pressure is in the Stage 1 hypertension range. The AHA "
            "recommends lifestyle changes: reduce sodium intake, exercise regularly, "
            "limit alcohol, and manage stress."
        )
        rec_ru = (
            "Ваше давление соответствует гипертонии 1 стадии. Рекомендуется: "
            "снижение потребления соли, регулярные упражнения, ограничение алкоголя."
        )
    elif systolic >= 120:
        cat, status = "Elevated", "warning"
        rec = (
            "Your blood pressure is elevated. Without lifestyle changes, you may "
            "develop high blood pressure. Maintain a healthy weight, exercise, "
            "and reduce sodium."
        )
        rec_ru = (
            "Ваше давление повышено. Без изменений образа жизни может развиться "
            "гипертония. Поддерживайте здоровый вес и занимайтесь спортом."
        )
    else:
        cat, status = "Normal", "normal"
        rec = (
            "Your blood pressure is within the normal range. Continue maintaining "
            "a healthy lifestyle with regular exercise and balanced diet."
        )
        rec_ru = (
            "Ваше артериальное давление в пределах нормы. Продолжайте вести "
            "здоровый образ жизни."
        )

    return {
        "metric": "Blood Pressure",
        "metric_ru": "Артериальное давление",
        "value": f"{systolic}/{diastolic}",
        "display_value": f"{systolic}/{diastolic} mmHg",
        "normal_range": "< 120/80 mmHg",
        "status": status,
        "category": cat,
        "category_ru": {
            "Normal": "Норма",
            "Elevated": "Повышенное",
            "Hypertension Stage 1": "Гипертония 1 ст.",
            "Hypertension Stage 2": "Гипертония 2 ст.",
            "Hypertensive Crisis": "Гипертонический криз",
        }.get(cat, cat),
        "recommendation": rec,
        "recommendation_ru": rec_ru,
        "source": "AHA/ACC Hypertension Guidelines, 2017",
    }


# ---------------------------------------------------------------------------
# Heart Rate — American Heart Association
# ---------------------------------------------------------------------------

def _analyze_heart_rate(heart_rate):
    if not heart_rate:
        return None

    if heart_rate < 60:
        cat, status = "Bradycardia", "warning"
        rec = (
            "Your resting heart rate is below 60 bpm (bradycardia). While this "
            "can be normal for athletes, if you experience dizziness, fatigue, or "
            "fainting, consult a doctor."
        )
        rec_ru = (
            "Ваш пульс в покое ниже 60 уд/мин (брадикардия). Это нормально для "
            "спортсменов, но если вы ощущаете головокружение или усталость — "
            "обратитесь к врачу."
        )
    elif heart_rate <= 100:
        cat, status = "Normal", "normal"
        rec = (
            "Your resting heart rate is within the normal range. Continue regular "
            "cardiovascular exercise to maintain heart health."
        )
        rec_ru = (
            "Ваш пульс в покое в пределах нормы. Продолжайте регулярные "
            "кардиотренировки для поддержания здоровья сердца."
        )
    else:
        cat, status = "Tachycardia", "danger"
        rec = (
            "Your resting heart rate exceeds 100 bpm (tachycardia). This may "
            "indicate stress, dehydration, or a medical condition. Reduce caffeine "
            "intake and consult a healthcare provider if persistent."
        )
        rec_ru = (
            "Ваш пульс в покое превышает 100 уд/мин (тахикардия). Это может "
            "указывать на стресс, обезвоживание или заболевание. Снизьте потребление "
            "кофеина и обратитесь к врачу при сохранении симптомов."
        )

    return {
        "metric": "Heart Rate",
        "metric_ru": "Пульс",
        "value": heart_rate,
        "display_value": f"{heart_rate} bpm",
        "normal_range": "60 \u2013 100 bpm",
        "status": status,
        "category": cat,
        "category_ru": {
            "Bradycardia": "Брадикардия",
            "Normal": "Норма",
            "Tachycardia": "Тахикардия",
        }.get(cat, cat),
        "recommendation": rec,
        "recommendation_ru": rec_ru,
        "source": "American Heart Association, Resting Heart Rate",
    }


# ---------------------------------------------------------------------------
# Body Temperature — WHO / Clinical Thermometry Guidelines
# ---------------------------------------------------------------------------

def _analyze_temperature(temp_c):
    if not temp_c:
        return None

    if temp_c < 35.0:
        cat, status = "Hypothermia", "danger"
        rec = (
            "Your body temperature indicates hypothermia. Warm up gradually and "
            "seek medical attention if symptoms persist."
        )
        rec_ru = (
            "Температура тела указывает на гипотермию. Постепенно согрейтесь и "
            "обратитесь за медицинской помощью."
        )
    elif temp_c <= 36.0:
        cat, status = "Below Normal", "warning"
        rec = (
            "Your body temperature is slightly below normal. Ensure you are warm "
            "enough and monitor for any symptoms."
        )
        rec_ru = (
            "Температура тела немного ниже нормы. Убедитесь, что вам тепло, "
            "и следите за симптомами."
        )
    elif temp_c <= 37.2:
        cat, status = "Normal", "normal"
        rec = "Your body temperature is within the normal range."
        rec_ru = "Температура тела в пределах нормы."
    elif temp_c <= 38.0:
        cat, status = "Low-Grade Fever", "warning"
        rec = (
            "You have a low-grade fever. Rest, stay hydrated, and monitor your "
            "temperature. Consult a doctor if it persists more than 3 days."
        )
        rec_ru = (
            "У вас субфебрильная температура. Отдыхайте, пейте больше жидкости. "
            "Обратитесь к врачу, если температура держится более 3 дней."
        )
    elif temp_c <= 39.0:
        cat, status = "Fever", "danger"
        rec = (
            "You have a fever. Stay hydrated, rest, and consider an antipyretic. "
            "Seek medical attention if accompanied by severe symptoms."
        )
        rec_ru = (
            "У вас повышенная температура. Пейте больше жидкости, отдыхайте. "
            "Обратитесь к врачу при тяжёлых симптомах."
        )
    else:
        cat, status = "High Fever", "danger"
        rec = (
            "You have a high fever (above 39\u00b0C). Seek medical attention promptly. "
            "Use antipyretics and stay hydrated."
        )
        rec_ru = (
            "У вас высокая температура (выше 39\u00b0C). Срочно обратитесь к врачу. "
            "Примите жаропонижающее и пейте больше жидкости."
        )

    return {
        "metric": "Temperature",
        "metric_ru": "Температура",
        "value": temp_c,
        "display_value": f"{temp_c} \u00b0C",
        "normal_range": "36.1 \u2013 37.2 \u00b0C",
        "status": status,
        "category": cat,
        "category_ru": {
            "Hypothermia": "Гипотермия",
            "Below Normal": "Ниже нормы",
            "Normal": "Норма",
            "Low-Grade Fever": "Субфебрильная",
            "Fever": "Лихорадка",
            "High Fever": "Высокая температура",
        }.get(cat, cat),
        "recommendation": rec,
        "recommendation_ru": rec_ru,
        "source": "WHO Guidelines on Body Temperature",
    }


# ---------------------------------------------------------------------------
# Oxygen Saturation — WHO Pulse Oximetry Training Manual, 2011
# ---------------------------------------------------------------------------

def _analyze_oxygen_saturation(spo2):
    if not spo2:
        return None

    if spo2 < 90:
        cat, status = "Critical Hypoxemia", "danger"
        rec = (
            "Your oxygen saturation is critically low. This requires immediate "
            "medical attention. Seek emergency care."
        )
        rec_ru = (
            "Уровень насыщения кислородом критически низкий. Требуется немедленная "
            "медицинская помощь."
        )
    elif spo2 < 95:
        cat, status = "Concerning", "warning"
        rec = (
            "Your oxygen saturation is below the normal range. Monitor your "
            "breathing and consult a healthcare provider, especially if you have "
            "respiratory conditions."
        )
        rec_ru = (
            "Уровень насыщения кислородом ниже нормы. Следите за дыханием и "
            "обратитесь к врачу, особенно при наличии респираторных заболеваний."
        )
    else:
        cat, status = "Normal", "normal"
        rec = "Your oxygen saturation is within the normal range."
        rec_ru = "Уровень насыщения кислородом в пределах нормы."

    return {
        "metric": "Oxygen Saturation",
        "metric_ru": "Сатурация кислорода",
        "value": spo2,
        "display_value": f"{spo2}%",
        "normal_range": "95 \u2013 100%",
        "status": status,
        "category": cat,
        "category_ru": {
            "Normal": "Норма",
            "Concerning": "Требует внимания",
            "Critical Hypoxemia": "Критическая гипоксемия",
        }.get(cat, cat),
        "recommendation": rec,
        "recommendation_ru": rec_ru,
        "source": "WHO Pulse Oximetry Training Manual, 2011",
    }


# ---------------------------------------------------------------------------
# Risk factor identification
# ---------------------------------------------------------------------------

def _identify_risk_factors(metrics, metric_results):
    factors_en = []
    factors_ru = []

    # Build a lookup for quick status checks
    status_map = {r["metric"]: r for r in metric_results}

    bmi_result = status_map.get("BMI")
    bp_result = status_map.get("Blood Pressure")
    hr_result = status_map.get("Heart Rate")
    spo2_result = status_map.get("Oxygen Saturation")

    chronic = (metrics.chronic_conditions or "").lower()
    allergies = (metrics.allergies or "").strip()
    medications_text = (metrics.medications or "").strip()

    # Obesity + high BP
    if (
        bmi_result
        and bmi_result["status"] == "danger"
        and bp_result
        and bp_result["status"] != "normal"
    ):
        factors_en.append(
            "Obesity combined with elevated blood pressure increases cardiovascular risk."
        )
        factors_ru.append(
            "Ожирение в сочетании с повышенным давлением увеличивает сердечно-сосудистый риск."
        )

    # Diabetes + elevated BMI
    if "диабет" in chronic or "diabetes" in chronic:
        if bmi_result and bmi_result["status"] != "normal":
            factors_en.append(
                "Diabetes with elevated BMI increases risk of metabolic complications."
            )
            factors_ru.append(
                "Диабет с повышенным ИМТ увеличивает риск метаболических осложнений."
            )

    # Tachycardia + hypertension
    if (
        hr_result
        and hr_result["status"] == "danger"
        and bp_result
        and bp_result["status"] != "normal"
    ):
        factors_en.append(
            "Elevated heart rate with high blood pressure may indicate cardiac stress."
        )
        factors_ru.append(
            "Учащённый пульс с повышенным давлением может указывать на нагрузку на сердце."
        )

    # Low O2 + respiratory conditions
    if spo2_result and spo2_result["status"] != "normal":
        respiratory_terms = ["asthma", "астма", "copd", "хобл", "bronchitis", "бронхит"]
        if any(term in chronic for term in respiratory_terms):
            factors_en.append(
                "Low oxygen saturation with a respiratory condition requires close monitoring."
            )
            factors_ru.append(
                "Низкая сатурация при респираторном заболевании требует наблюдения."
            )

    # Active chronic conditions
    if chronic:
        factors_en.append(
            "Active chronic conditions require ongoing medical monitoring."
        )
        factors_ru.append(
            "Хронические заболевания требуют постоянного медицинского наблюдения."
        )

    # Medications + allergies
    if allergies and medications_text:
        factors_en.append(
            "Patients on medications with known allergies should verify drug compatibility."
        )
        factors_ru.append(
            "Пациентам с аллергиями, принимающим лекарства, следует проверять совместимость."
        )

    return factors_en, factors_ru


# ---------------------------------------------------------------------------
# Health score computation
# ---------------------------------------------------------------------------

def _compute_health_score(metric_results, risk_factor_count):
    score = 100

    for r in metric_results:
        if r["status"] == "warning":
            score -= 10
        elif r["status"] == "danger":
            score -= 20

    score -= risk_factor_count * 5
    score = max(0, score)

    if score >= 90:
        return score, "Excellent", "Отлично", "success"
    elif score >= 75:
        return score, "Good", "Хорошо", "success"
    elif score >= 60:
        return score, "Fair", "Удовлетворительно", "warning"
    elif score >= 40:
        return score, "Poor", "Плохо", "danger"
    else:
        return score, "Critical", "Критическое", "danger"


# ===========================================================================
# Lab Result Analysis — rule-based assessment of extracted lab values
# ===========================================================================

# Reference ranges and recommendations for common lab tests
_LAB_REFERENCES = {
    "glucose": {
        "name": "Glucose (Fasting)", "name_ru": "Глюкоза (натощак)",
        "low": 3.9, "high": 6.1, "unit": "mmol/L",
        "source": "American Diabetes Association, Standards of Care 2024",
        "ranges": [
            (0, 3.9, "low", "Low Blood Sugar", "Низкий сахар",
             "Your fasting glucose is below normal. Eat regular meals and carry a fast-acting sugar source. Consult a doctor if this persists.",
             "Уровень глюкозы натощак ниже нормы. Питайтесь регулярно. Обратитесь к врачу, если это сохраняется.",
             [("Eat regular, balanced meals every 3-4 hours", "Питайтесь регулярно, каждые 3-4 часа"),
              ("Include complex carbohydrates: whole grains, oats", "Включите сложные углеводы: цельнозерновые, овсянку")]),
            (3.9, 6.1, "normal", "Normal", "Норма",
             "Your fasting glucose is within the normal range.", "Уровень глюкозы натощак в пределах нормы.", []),
            (6.1, 7.0, "high", "Pre-diabetic", "Преддиабет",
             "Your glucose is elevated (pre-diabetic range). Reduce refined carbohydrates and increase physical activity.",
             "Уровень глюкозы повышен (преддиабет). Снизьте потребление рафинированных углеводов и увеличьте физическую активность.",
             [("Reduce sugar and refined carbohydrates", "Снизьте потребление сахара и рафинированных углеводов"),
              ("Increase fiber: vegetables, legumes, whole grains", "Увеличьте клетчатку: овощи, бобовые, цельнозерновые"),
              ("Exercise at least 150 min/week", "Занимайтесь спортом не менее 150 мин/неделю")]),
            (7.0, 999, "critical", "Diabetic Range", "Диабетический уровень",
             "Your fasting glucose is in the diabetic range. Consult a healthcare provider promptly for management.",
             "Уровень глюкозы в диабетическом диапазоне. Срочно обратитесь к врачу.",
             [("Strictly limit sugar and refined carbs", "Строго ограничьте сахар и рафинированные углеводы"),
              ("Focus on low-glycemic foods: legumes, non-starchy vegetables", "Сосредоточьтесь на продуктах с низким ГИ")])
        ],
    },
    "cholesterol": {
        "name": "Total Cholesterol", "name_ru": "Общий холестерин",
        "low": 3.6, "high": 5.2, "unit": "mmol/L",
        "source": "AHA/ACC Cholesterol Guidelines, 2018",
        "ranges": [
            (0, 3.6, "low", "Low", "Пониженный",
             "Your cholesterol is below typical range. While low cholesterol is generally not harmful, discuss with your doctor.",
             "Ваш холестерин ниже нормы. Обсудите это с врачом.", []),
            (3.6, 5.2, "normal", "Desirable", "Норма",
             "Your total cholesterol is within the desirable range.", "Общий холестерин в пределах нормы.", []),
            (5.2, 6.2, "high", "Borderline High", "Пограничный",
             "Your cholesterol is borderline high. Reduce saturated fats and increase fiber.",
             "Холестерин на верхней границе нормы. Снизьте насыщенные жиры и увеличьте клетчатку.",
             [("Reduce saturated fats: fried food, fatty meat, butter", "Снизьте насыщенные жиры: жареное, жирное мясо, масло"),
              ("Eat more omega-3: fish, walnuts, flaxseed", "Ешьте больше омега-3: рыба, грецкие орехи, льняное семя"),
              ("Increase soluble fiber: oats, beans, apples", "Увеличьте растворимую клетчатку: овёс, бобы, яблоки")]),
            (6.2, 999, "critical", "High", "Высокий",
             "Your cholesterol is high, increasing cardiovascular risk. Consult a doctor about lifestyle and possible medication.",
             "Холестерин повышен, что увеличивает сердечно-сосудистый риск. Обратитесь к врачу.",
             [("Avoid trans fats and limit saturated fats", "Избегайте трансжиров и ограничьте насыщенные жиры"),
              ("Eat Mediterranean-style: olive oil, fish, vegetables", "Средиземноморская диета: оливковое масло, рыба, овощи")])
        ],
    },
    "hemoglobin": {
        "name": "Hemoglobin", "name_ru": "Гемоглобин",
        "low": 120, "high": 160, "unit": "g/L",
        "source": "WHO Haemoglobin Thresholds, 2011",
        "ranges": [
            (0, 70, "critical", "Severe Anemia", "Тяжёлая анемия",
             "Your hemoglobin indicates severe anemia. Seek medical attention immediately.",
             "Гемоглобин указывает на тяжёлую анемию. Немедленно обратитесь к врачу.",
             [("Iron-rich foods: red meat, liver, spinach, lentils", "Продукты с железом: красное мясо, печень, шпинат, чечевица"),
              ("Take vitamin C with meals to aid iron absorption", "Принимайте витамин C с едой для усвоения железа")]),
            (70, 120, "low", "Anemia", "Анемия",
             "Your hemoglobin is below normal, indicating anemia. Increase iron-rich foods and consult a doctor.",
             "Гемоглобин ниже нормы (анемия). Увеличьте потребление железа и обратитесь к врачу.",
             [("Eat iron-rich foods: red meat, beans, dark leafy greens", "Ешьте продукты с железом: мясо, бобы, тёмную зелень"),
              ("Pair iron foods with vitamin C (citrus, bell peppers)", "Сочетайте с витамином C (цитрусовые, перец)")]),
            (120, 160, "normal", "Normal", "Норма",
             "Your hemoglobin is within the normal range.", "Гемоглобин в пределах нормы.", []),
            (160, 999, "high", "Elevated", "Повышенный",
             "Your hemoglobin is elevated. Stay well-hydrated and consult a doctor if persistent.",
             "Гемоглобин повышен. Пейте достаточно воды и обратитесь к врачу.",
             [("Stay well-hydrated: 8+ glasses of water daily", "Пейте достаточно воды: 8+ стаканов в день")])
        ],
    },
    "alt": {
        "name": "ALT (Liver)", "name_ru": "АЛТ (печень)",
        "low": 7, "high": 56, "unit": "U/L",
        "source": "American College of Gastroenterology, 2017",
        "ranges": [
            (0, 7, "low", "Low", "Пониженный",
             "Your ALT is below typical range.", "АЛТ ниже нормы.", []),
            (7, 56, "normal", "Normal", "Норма",
             "Your ALT levels are normal, indicating healthy liver function.", "АЛТ в норме, печень функционирует нормально.", []),
            (56, 200, "high", "Elevated", "Повышенный",
             "Your ALT is elevated, which may indicate liver stress. Limit alcohol and consult a doctor.",
             "АЛТ повышен, что может указывать на нагрузку на печень. Ограничьте алкоголь и обратитесь к врачу.",
             [("Limit or avoid alcohol", "Ограничьте или исключите алкоголь"),
              ("Reduce fatty and processed foods", "Снизьте потребление жирной и переработанной пищи"),
              ("Eat liver-friendly foods: garlic, green tea, leafy greens", "Ешьте полезные для печени продукты: чеснок, зелёный чай")]),
            (200, 99999, "critical", "Very High", "Значительно повышен",
             "Your ALT is significantly elevated. Seek medical evaluation promptly.",
             "АЛТ значительно повышен. Срочно обратитесь к врачу.",
             [("Avoid alcohol completely", "Полностью исключите алкоголь")])
        ],
    },
    "creatinine": {
        "name": "Creatinine", "name_ru": "Креатинин",
        "low": 62, "high": 106, "unit": "umol/L",
        "source": "KDIGO Clinical Practice Guidelines, 2012",
        "ranges": [
            (0, 62, "low", "Low", "Пониженный",
             "Your creatinine is below normal. This is usually not concerning but mention it to your doctor.",
             "Креатинин ниже нормы. Обычно это не опасно, но упомяните врачу.", []),
            (62, 106, "normal", "Normal", "Норма",
             "Your creatinine is normal, indicating healthy kidney function.", "Креатинин в норме, почки функционируют нормально.", []),
            (106, 200, "high", "Elevated", "Повышенный",
             "Your creatinine is elevated, which may indicate reduced kidney function. Stay hydrated and consult a doctor.",
             "Креатинин повышен, что может указывать на снижение функции почек. Пейте воду и обратитесь к врачу.",
             [("Stay well-hydrated throughout the day", "Пейте достаточно воды в течение дня"),
              ("Reduce excessive protein intake", "Снизьте избыточное потребление белка"),
              ("Limit sodium: avoid processed and salty foods", "Ограничьте натрий: избегайте солёного")]),
            (200, 99999, "critical", "High", "Высокий",
             "Your creatinine is significantly elevated. Consult a nephrologist promptly.",
             "Креатинин значительно повышен. Срочно обратитесь к нефрологу.",
             [("Reduce protein and sodium intake", "Снизьте потребление белка и натрия")])
        ],
    },
    "tsh": {
        "name": "TSH", "name_ru": "ТТГ",
        "low": 0.4, "high": 4.0, "unit": "mIU/L",
        "source": "American Thyroid Association Guidelines, 2014",
        "ranges": [
            (0, 0.4, "low", "Low (Hyperthyroid)", "Пониженный (гипертиреоз)",
             "Your TSH is low, suggesting overactive thyroid. Consult an endocrinologist.",
             "ТТГ понижен, что может указывать на гиперфункцию щитовидной железы. Обратитесь к эндокринологу.",
             [("Limit iodine-rich foods: seaweed, iodized salt", "Ограничьте продукты с йодом: водоросли, йодированную соль"),
              ("Reduce caffeine intake", "Снизьте потребление кофеина")]),
            (0.4, 4.0, "normal", "Normal", "Норма",
             "Your TSH is normal, indicating healthy thyroid function.", "ТТГ в норме, щитовидная железа функционирует нормально.", []),
            (4.0, 10.0, "high", "Elevated (Hypothyroid)", "Повышенный (гипотиреоз)",
             "Your TSH is elevated, suggesting underactive thyroid. Consult an endocrinologist.",
             "ТТГ повышен, что может указывать на гипофункцию щитовидной железы. Обратитесь к эндокринологу.",
             [("Include selenium: Brazil nuts, fish, eggs", "Включите селен: бразильские орехи, рыба, яйца"),
              ("Ensure adequate iodine intake", "Обеспечьте достаточное потребление йода")]),
            (10.0, 999, "critical", "Very High", "Значительно повышен",
             "Your TSH is significantly elevated. Seek endocrinology consultation promptly.",
             "ТТГ значительно повышен. Срочно обратитесь к эндокринологу.", [])
        ],
    },
    "iron": {
        "name": "Iron", "name_ru": "Железо",
        "low": 9, "high": 30, "unit": "umol/L",
        "source": "WHO Iron Deficiency Guidelines",
        "ranges": [
            (0, 9, "low", "Low", "Пониженный",
             "Your iron is low. Increase iron-rich foods and consider supplementation after consulting a doctor.",
             "Железо понижено. Увеличьте потребление продуктов с железом.",
             [("Red meat, liver, oysters are excellent iron sources", "Красное мясо, печень — отличные источники железа"),
              ("Dark leafy greens: spinach, kale", "Тёмная зелень: шпинат, капуста кале"),
              ("Pair with vitamin C for better absorption", "Сочетайте с витамином C для лучшего усвоения")]),
            (9, 30, "normal", "Normal", "Норма",
             "Your iron levels are within the normal range.", "Уровень железа в пределах нормы.", []),
            (30, 999, "high", "Elevated", "Повышенный",
             "Your iron is elevated. Avoid iron supplements and limit red meat. Consult a doctor.",
             "Железо повышено. Избегайте добавок с железом и ограничьте красное мясо.",
             [("Avoid iron supplements unless prescribed", "Не принимайте добавки с железом без назначения"),
              ("Limit red meat intake", "Ограничьте потребление красного мяса")])
        ],
    },
    "vitamin_d": {
        "name": "Vitamin D", "name_ru": "Витамин D",
        "low": 30, "high": 100, "unit": "ng/mL",
        "source": "Endocrine Society Clinical Practice Guidelines, 2011",
        "ranges": [
            (0, 20, "low", "Deficient", "Дефицит",
             "You have vitamin D deficiency. Consider supplementation and increase sun exposure.",
             "У вас дефицит витамина D. Рассмотрите приём добавок и увеличьте пребывание на солнце.",
             [("Get 15-20 min of sun exposure daily", "Проводите 15-20 мин на солнце ежедневно"),
              ("Eat fatty fish: salmon, mackerel, sardines", "Ешьте жирную рыбу: лосось, скумбрию, сардины"),
              ("Consider vitamin D3 supplement (1000-2000 IU/day)", "Рассмотрите приём витамина D3 (1000-2000 МЕ/день)")]),
            (20, 30, "low", "Insufficient", "Недостаточность",
             "Your vitamin D is insufficient. Increase sun exposure and dietary sources.",
             "Витамин D недостаточен. Увеличьте пребывание на солнце и потребление продуктов с витамином D.",
             [("More sun exposure and fatty fish", "Больше солнца и жирной рыбы"),
              ("Egg yolks, fortified dairy products", "Яичные желтки, обогащённые молочные продукты")]),
            (30, 100, "normal", "Normal", "Норма",
             "Your vitamin D is within the optimal range.", "Витамин D в пределах нормы.", []),
            (100, 999, "high", "Excess", "Избыток",
             "Your vitamin D is elevated. Stop supplementation and consult a doctor.",
             "Витамин D повышен. Прекратите приём добавок и обратитесь к врачу.", [])
        ],
    },
}

# Map common test names to our reference keys
_NAME_MAP = {
    "glucose": "glucose", "глюкоза": "glucose", "fasting glucose": "glucose",
    "blood sugar": "glucose", "сахар крови": "glucose",
    "cholesterol": "cholesterol", "total cholesterol": "cholesterol",
    "общий холестерин": "cholesterol", "холестерин": "cholesterol",
    "hemoglobin": "hemoglobin", "hgb": "hemoglobin", "hb": "hemoglobin",
    "гемоглобин": "hemoglobin",
    "alt": "alt", "алт": "alt", "alanine aminotransferase": "alt",
    "аланинаминотрансфераза": "alt",
    "creatinine": "creatinine", "креатинин": "creatinine",
    "tsh": "tsh", "ттг": "tsh", "thyroid stimulating hormone": "tsh",
    "тиреотропный гормон": "tsh",
    "iron": "iron", "железо": "iron", "serum iron": "iron",
    "сывороточное железо": "iron",
    "vitamin d": "vitamin_d", "витамин d": "vitamin_d", "25-oh vitamin d": "vitamin_d",
    "витамин д": "vitamin_d",
}


def analyze_lab_results(lab_results):
    """Analyze a list of LabResult objects using guideline-based reference ranges.

    Returns dict with 'has_data', 'lab_metrics' list, 'abnormal_count', 'total_count'.
    """
    if not lab_results:
        return {"has_data": False}

    results = []
    for lab in lab_results:
        analysis = _analyze_single_lab(lab)
        if analysis:
            results.append(analysis)

    if not results:
        return {"has_data": False}

    abnormal_count = sum(1 for r in results if r["status"] != "normal")
    return {
        "has_data": True,
        "lab_metrics": results,
        "abnormal_count": abnormal_count,
        "total_count": len(results),
    }


def _analyze_single_lab(lab):
    """Analyze a single LabResult against known reference ranges."""
    if lab.value is None:
        return None

    # Try to match test name to our reference data
    key = _NAME_MAP.get(lab.test_name.lower().strip())
    if not key:
        # Try partial matching
        name_lower = lab.test_name.lower().strip()
        for pattern, ref_key in _NAME_MAP.items():
            if pattern in name_lower or name_lower in pattern:
                key = ref_key
                break

    ref = _LAB_REFERENCES.get(key) if key else None

    if not ref:
        # No reference data — return basic info without recommendation
        status = lab.status or "normal"
        return {
            "metric": lab.test_name,
            "metric_ru": lab.test_name_ru or lab.test_name,
            "value": lab.value,
            "display_value": f"{lab.value} {lab.unit or ''}".strip(),
            "normal_range": lab.reference_range_text or "—",
            "status": status,
            "category": lab.category or "other",
            "category_label": (lab.test_name_ru or lab.test_name) if status == "normal" else lab.test_name,
            "category_label_ru": lab.test_name_ru or lab.test_name,
            "recommendation": "",
            "recommendation_ru": "",
            "nutrition_tips": [],
            "source": "",
        }

    # Find matching range
    for low_bound, high_bound, status, cat, cat_ru, rec, rec_ru, tips in ref["ranges"]:
        if low_bound <= lab.value < high_bound:
            return {
                "metric": ref["name"],
                "metric_ru": ref["name_ru"],
                "value": lab.value,
                "display_value": f"{lab.value} {ref['unit']}",
                "normal_range": f"{ref['low']} – {ref['high']} {ref['unit']}",
                "status": status,
                "category": cat,
                "category_ru": cat_ru,
                "recommendation": rec,
                "recommendation_ru": rec_ru,
                "nutrition_tips": [{"en": t[0], "ru": t[1]} for t in tips],
                "source": ref["source"],
            }

    # Fallback if value is outside all defined ranges
    return {
        "metric": ref["name"],
        "metric_ru": ref["name_ru"],
        "value": lab.value,
        "display_value": f"{lab.value} {ref['unit']}",
        "normal_range": f"{ref['low']} – {ref['high']} {ref['unit']}",
        "status": "high" if lab.value >= ref["high"] else "low",
        "category": lab.test_name,
        "category_ru": lab.test_name_ru or lab.test_name,
        "recommendation": "Value is outside expected range. Consult a healthcare provider.",
        "recommendation_ru": "Значение за пределами нормы. Обратитесь к врачу.",
        "nutrition_tips": [],
        "source": ref["source"],
    }
