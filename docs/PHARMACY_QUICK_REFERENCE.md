# Quick Reference - Medication Search Feature

## Getting Started

### Start the Application
```bash
python run.py
```

### Access the Pharmacy
Navigate to: `http://localhost:5000/pharmacy`

---

## User Guide

### Search for a Medication
1. Type medication name (minimum 2 characters)
2. Click "Search" or press Enter
3. View results in grid layout
4. Click "View Details" to see full information

**Example searches:**
- "Ibu" → Ibuprofen
- "Amoxi" → Amoxicillin
- "Metformin" → Full name search

### Browse by Letter
1. Click any letter button (A-Z)
2. View medications starting with that letter
3. Click medication for details
4. Navigate with Previous/Next if paginated

**Letter buttons show:**
- ✓ Enabled with count (has medications)
- ✗ Disabled (no medications)

### View Medication Details
Modal shows:
- ✓ Full description
- ✓ Active ingredient
- ✓ Dosage information
- ✓ Manufacturer
- ✓ Side effects & contraindications
- ✓ Available pharmacies with prices
- ✓ Stock quantities
- ✓ OTC/Rx status

---

## API Reference

### Get All Medications (Paginated)
```
GET /api/medications?page=1
```

### Browse by Letter
```
GET /api/medications/alphabet                 (get letter counts)
GET /api/medications/alphabet?letter=A        (get medications for letter)
```

### Search Medications
```
GET /api/medications/search?q=ibu&page=1
```

### Get Medication Details
```
GET /api/medications/123
```

---

## Sample Data

### Pre-loaded Medications
- Ibuprofen (OTC)
- Amoxicillin (Rx)
- Aspirin (OTC)
- Metformin (Rx)
- Lisinopril (Rx)
- Omeprazole (OTC)
- Atorvastatin (Rx)
- Paracetamol (OTC)

### Pre-loaded Pharmacies
- HealthPlus Pharmacy
- Care Pharmacy
- MediCare Plus

---

## Developer Guide

### Add a New Medication

```python
from main.models import db, Medication

new_med = Medication(
    name='Ciprofloxacin',
    generic_name='Ciprofloxacin',
    description='Fluoroquinolone antibiotic',
    active_ingredient='Ciprofloxacin 500mg',
    dosage_forms='Tablet, Solution',
    available_strengths='250mg, 500mg, 750mg',
    manufacturer='Various',
    side_effects='Nausea, diarrhea, rash',
    is_otc=False,
    requires_prescription=True
)
db.session.add(new_med)
db.session.commit()
```

### Add Pharmacy Stock

```python
from main.models import db, PharmacyStock

stock = PharmacyStock(
    pharmacy_id=1,              # HealthPlus Pharmacy
    medication_id=9,            # New medication
    quantity=30,
    price=14.99,
    currency='USD'
)
db.session.add(stock)
db.session.commit()
```

### Query Medications

```python
from main.models import Medication

# All OTC medications
otc = Medication.query.filter_by(is_otc=True).all()

# All Rx medications
rx = Medication.query.filter_by(requires_prescription=True).all()

# Search by name
results = Medication.query.filter(
    Medication.name.ilike('%ibu%')
).all()

# By first letter
by_letter = Medication.query.filter(
    Medication.name.ilike('A%')
).order_by(Medication.name).all()
```

### Get Pharmacy Info for a Medication

```python
from main.models import Medication, PharmacyStock

med = Medication.query.get(1)

# Get all stocks for this medication
stocks = PharmacyStock.query.filter_by(
    medication_id=med.id
).all()

for stock in stocks:
    print(f"Pharmacy: {stock.pharmacy.name}")
    print(f"Price: {stock.currency} {stock.price}")
    print(f"Quantity: {stock.quantity}")
```

---

## File Locations

### Backend
- **Routes**: `main/routes/medical.py`
- **Models**: `main/models.py`
- **Database Seeding**: `main/app.py`

### Frontend
- **Template**: `main/templates/pharmacy.html`
- **Styles**: CSS in HTML template
- **Scripts**: JavaScript in HTML template (vanilla JS, no framework)

### Documentation
- **PHARMACY_SEARCH_GUIDE.md**: Complete feature guide
- **API_REFERENCE**: Inline comments in medical.py

---

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/medications` | All medications (paginated) |
| GET | `/api/medications/alphabet` | Letter counts or medications by letter |
| GET | `/api/medications/search?q=term` | Search by name |
| GET | `/api/medications/<id>` | Get full medication details |
| GET | `/pharmacy` | Pharmacy page (HTML) |

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (e.g., search < 2 chars) |
| 404 | Medication not found |
| 500 | Server error |

---

## Performance Tips

- **Search**: Minimum 2 characters to prevent broad queries
- **Pagination**: 20 items per page by default
- **Database**: Indexed on `name` and `generic_name` for fast search
- **Frontend**: Uses vanilla JavaScript (no jQuery dependency)

---

## Future Enhancements

Add to pharmacy.html script:
```javascript
// Drug interaction checker
// User favorites/bookmarks
// Price alerts
// Availability notifications
// Review/rating system
// Mobile app integration
```

Add to backend:
```python
# Advanced filtering (price range, class, etc.)
# Drug interaction database
# User reviews and ratings
# Real-time inventory sync
# Manufacturer information
# Clinical studies/research links
```

---

## Troubleshooting

### No medications showing
- Check database seeding (see app.py)
- Verify Medication model has data
- Check browser console for JavaScript errors

### Search not working
- Minimum 2 characters required
- Check API calls in browser Network tab
- Verify /api/medications/search endpoint responds

### Pharmacy info not showing
- Ensure PharmacyStock records exist
- Check that pharmacy_id and medication_id are valid
- Verify pharmacy relationship is loaded

---

## Contact & Support

For issues:
1. Check `PHARMACY_SEARCH_GUIDE.md` for detailed docs
2. Review browser console for errors
3. Check Flask logs for backend errors
4. Verify database connectivity
