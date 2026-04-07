"""
Medical and Anatomy API routes blueprint
Handles: anatomy data API, pharmacy page, anatomy viewer, medication search
"""
from flask import Blueprint, render_template, request, jsonify

from main.models import db, Organ, Disease, Medication, Pharmacy, PharmacyStock, MedicationCategory

medical_bp = Blueprint('medical', __name__)


def _get_letter_counts():
    """Get count of medications for each letter A-Z."""
    letters = {}
    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        count = Medication.query.filter(Medication.name.ilike(f'{char}%')).count()
        if count > 0:
            letters[char] = count
    return letters


def _serialize_med(m):
    """Serialize a medication for list endpoints."""
    return {
        "id": m.id,
        "name": m.name,
        "generic_name": m.generic_name,
        "description": m.description,
        "dosage_forms": m.dosage_forms,
        "manufacturer": m.manufacturer,
        "is_otc": m.is_otc,
        "requires_prescription": m.requires_prescription,
        "category": m.category.name if m.category else None,
        "pharmacy_count": len(m.pharmacy_stocks),
        "min_price": min((s.price for s in m.pharmacy_stocks if s.price), default=None),
    }


# ============================================================================
# ANATOMY ENDPOINTS
# ============================================================================

@medical_bp.route('/api/organs', methods=['GET'])
def api_get_organs():
    organs = Organ.query.all()
    return {
        "organs": [
            {"id": o.id, "name": o.name, "system": o.system, "description": o.description}
            for o in organs
        ]
    }


@medical_bp.route('/api/organs/<int:organ_id>', methods=['GET'])
def api_get_organ(organ_id):
    o = Organ.query.get_or_404(organ_id)
    diseases = [{"id": d.id, "name": d.name, "symptoms": d.symptoms} for d in o.diseases]
    return {"id": o.id, "name": o.name, "system": o.system, "description": o.description, "diseases": diseases}


@medical_bp.route('/api/diseases', methods=['GET'])
def api_get_diseases():
    diseases = Disease.query.all()
    return {"diseases": [{"id": d.id, "name": d.name, "organ_id": d.organ_id} for d in diseases]}


@medical_bp.route('/api/diseases/<int:disease_id>', methods=['GET'])
def api_get_disease(disease_id):
    d = Disease.query.get_or_404(disease_id)
    return {"id": d.id, "name": d.name, "symptoms": d.symptoms, "organ_id": d.organ_id}


# ============================================================================
# MEDICATION SEARCH & BROWSE ENDPOINTS
# ============================================================================

@medical_bp.route('/api/medications/alphabet', methods=['GET'])
def api_medications_by_letter():
    """Get medications by first letter with pagination, or all letter counts."""
    letter = request.args.get('letter', '').upper()

    if not letter or len(letter) != 1 or not letter.isalpha():
        return jsonify({"letters": _get_letter_counts()})

    page = request.args.get('page', 1, type=int)
    per_page = 20

    paginated = Medication.query.filter(
        Medication.name.ilike(f'{letter}%')
    ).order_by(Medication.name).paginate(page=page, per_page=per_page)

    return jsonify({
        "letter": letter,
        "count": paginated.total,
        "page": page,
        "pages": paginated.pages,
        "medications": [_serialize_med(m) for m in paginated.items]
    })


@medical_bp.route('/api/medications/search', methods=['GET'])
def api_search_medications():
    """Search medications by name or generic name."""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    if not query or len(query) < 2:
        return jsonify({"error": "Search query too short", "medications": []}), 400

    medications = Medication.query.filter(
        (Medication.name.ilike(f'%{query}%')) |
        (Medication.generic_name.ilike(f'%{query}%'))
    ).order_by(Medication.name).paginate(page=page, per_page=per_page)

    return jsonify({
        "query": query,
        "page": page,
        "total": medications.total,
        "pages": medications.pages,
        "medications": [_serialize_med(m) for m in medications.items]
    })


@medical_bp.route('/api/medications/<int:med_id>', methods=['GET'])
def api_get_medication(med_id):
    """Get detailed medication information with pharmacy availability."""
    m = Medication.query.get_or_404(med_id)

    stocks = PharmacyStock.query.filter_by(medication_id=med_id).all()
    pharmacies = []
    for stock in stocks:
        pharmacies.append({
            "pharmacy_id": stock.pharmacy_id,
            "pharmacy_name": stock.pharmacy.name,
            "address": stock.pharmacy.address,
            "city": stock.pharmacy.city,
            "phone": stock.pharmacy.phone,
            "opening_time": stock.pharmacy.opening_time,
            "closing_time": stock.pharmacy.closing_time,
            "operates_24_7": stock.pharmacy.operates_24_7,
            "delivery_available": stock.pharmacy.delivery_available,
            "quantity": stock.quantity,
            "price": float(stock.price) if stock.price else None,
            "currency": stock.currency,
        })

    return jsonify({
        "id": m.id,
        "name": m.name,
        "generic_name": m.generic_name,
        "description": m.description,
        "active_ingredient": m.active_ingredient,
        "dosage_forms": m.dosage_forms,
        "available_strengths": m.available_strengths,
        "manufacturer": m.manufacturer,
        "side_effects": m.side_effects,
        "contraindications": m.contraindications,
        "storage_instructions": m.storage_instructions,
        "is_otc": m.is_otc,
        "requires_prescription": m.requires_prescription,
        "category": m.category.name if m.category else None,
        "pharmacies": pharmacies,
    })


@medical_bp.route('/api/medications', methods=['GET'])
def api_get_all_medications():
    """Get all medications with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    medications = Medication.query.order_by(Medication.name).paginate(page=page, per_page=per_page)

    return jsonify({
        "page": page,
        "total": medications.total,
        "pages": medications.pages,
        "medications": [_serialize_med(m) for m in medications.items]
    })


@medical_bp.route('/api/medications/categories', methods=['GET'])
def api_medication_categories():
    """Get all medication categories with counts."""
    categories = MedicationCategory.query.all()
    return jsonify({
        "categories": [
            {"id": c.id, "name": c.name, "name_ru": c.name_ru, "icon": c.icon, "count": len(c.medications)}
            for c in categories
        ]
    })


@medical_bp.route('/api/medications/category/<int:cat_id>', methods=['GET'])
def api_medications_by_category(cat_id):
    """Get medications in a category with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    paginated = Medication.query.filter_by(category_id=cat_id).order_by(
        Medication.name
    ).paginate(page=page, per_page=per_page)

    return jsonify({
        "page": page,
        "total": paginated.total,
        "pages": paginated.pages,
        "medications": [_serialize_med(m) for m in paginated.items]
    })


# ============================================================================
# PAGE ROUTES
# ============================================================================

@medical_bp.route('/human-anatomy')
def human_anatomy():
    return render_template('human_anatomy_react.html')


@medical_bp.route('/pharmacy')
def pharmacy():
    letters = _get_letter_counts()
    total_medications = Medication.query.count()
    categories = MedicationCategory.query.all()
    cities = [c[0] for c in db.session.query(Pharmacy.city).distinct().order_by(Pharmacy.city).all() if c[0]]
    return render_template(
        'pharmacy.html',
        available_letters=letters,
        total_medications=total_medications,
        categories=categories,
        cities=cities,
    )
