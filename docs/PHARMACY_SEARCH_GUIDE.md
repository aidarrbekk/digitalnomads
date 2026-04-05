# Medication Search & Browse Feature Guide

## Overview
The pharmacy section now has a complete medication search, browse, and discovery system similar to i-teka.kz, allowing users to search medications by name or browse alphabetically.

## Features Added

### 1. API Endpoints

All endpoints return JSON responses and are located at `/api/medications/*`

#### Get Medications by Letter
```
GET /api/medications/alphabet?letter=A
```
**Response:**
```json
{
  "letter": "A",
  "count": 3,
  "medications": [
    {
      "id": 1,
      "name": "Amoxicillin",
      "generic_name": "Amoxicillin",
      "description": "...",
      "dosage_forms": "Capsule, Tablet",
      "is_otc": false,
      "requires_prescription": true
    }
  ]
}
```

**Without letter parameter** - returns count of available letters:
```json
{
  "letters": {
    "A": 2,
    "I": 1,
    "M": 2,
    "O": 1,
    "P": 1
  }
}
```

#### Search Medications
```
GET /api/medications/search?q=ibu&page=1
```
**Response:**
```json
{
  "query": "ibu",
  "page": 1,
  "total": 15,
  "pages": 1,
  "medications": [...]
}
```

#### Get Medication Details
```
GET /api/medications/123
```
**Response:**
```json
{
  "id": 123,
  "name": "Ibuprofen",
  "generic_name": "Ibuprofen",
  "description": "...",
  "active_ingredient": "Ibuprofen 200mg",
  "dosage_forms": "Tablet",
  "available_strengths": "200mg, 400mg",
  "manufacturer": "Various",
  "side_effects": "Stomach upset, heartburn",
  "contraindications": "...",
  "storage_instructions": "Store at room temperature",
  "is_otc": true,
  "requires_prescription": false,
  "pharmacies": [
    {
      "pharmacy_id": 1,
      "pharmacy_name": "HealthPlus Pharmacy",
      "location": "Downtown Medical Center",
      "quantity": 50,
      "price": 5.99,
      "currency": "USD"
    }
  ]
}
```

#### Get All Medications (Paginated)
```
GET /api/medications?page=1
```

### 2. Frontend Interface (Pharmacy Page)

#### Search Bar
- Minimum 2 characters required
- Real-time API search
- Enter key support

#### Alphabet Navigation
- A-Z buttons
- Shows count of available medications for each letter
- Disabled state for letters with no medications
- Click to browse medications starting with that letter

#### Medication Cards
Each medication displays:
- Medication name
- Generic name (if available)
- Description
- Dosage forms
- OTC/Rx badges
- "View Details" button (opens modal)

#### Detail Modal
Shows complete medication information:
- Description
- Active ingredient
- Dosage forms and strengths
- Manufacturer
- Side effects
- Contraindications
- Storage instructions
- Available pharmacies with prices and quantities

#### Pagination
- Automatic for search results
- Previous/Next navigation
- Current page indicator

### 3. Database Models

#### Medication Model
Fields populated:
- `name` - Medication name
- `generic_name` - Generic equivalent
- `description` - Full description
- `active_ingredient` - Active component
- `dosage_forms` - Forms available (Tablet, Capsule, etc.)
- `available_strengths` - Available doses
- `manufacturer` - Manufacturer name
- `side_effects` - Common side effects
- `contraindications` - Use contraindications
- `storage_instructions` - Storage info
- `is_otc` - Over-the-counter flag
- `requires_prescription` - Prescription required flag

#### Pharmacy Model
Fields:
- `name` - Pharmacy name
- `address` - Physical address
- `phone` - Contact number
- `city` - City location
- `country` - Country location
- `operates_24_7` - 24/7 operation flag

#### PharmacyStock Model
Links medications to pharmacies:
- `pharmacy_id` - Which pharmacy
- `medication_id` - Which medication
- `quantity` - Available quantity
- `price` - Price per unit
- `currency` - Currency code

### 4. Sample Data

The system comes pre-populated with:
- **8 Medications**: Ibuprofen, Amoxicillin, Aspirin, Metformin, Lisinopril, Omeprazole, Atorvastatin, Paracetamol
- **3 Pharmacies**: HealthPlus, Care Pharmacy, MediCare Plus
- **Pharmacy Stocks**: Medications linked to pharmacies with prices and quantities

## Usage

### For Users

1. **Search by Name**
   - Type medication name (min 2 characters)
   - Click Search or press Enter
   - Review results
   - Click "View Details" to see full information and pharmacy availability

2. **Browse by Letter**
   - Click any A-Z letter button
   - View all medications starting with that letter
   - Click medication to view details

3. **View Medication Details**
   - See full description, ingredients, side effects
   - View which pharmacies stock the medication
   - Check prices and quantities

### For Developers

#### Add New Medication
```python
from main.models import db, Medication

new_med = Medication(
    name='Drug Name',
    generic_name='Generic Name',
    description='Description',
    active_ingredient='Active ingredient',
    dosage_forms='Tablet, Capsule',
    available_strengths='500mg, 1000mg',
    manufacturer='Manufacturer',
    side_effects='Side effects',
    is_otc=True,
    requires_prescription=False
)
db.session.add(new_med)
db.session.commit()
```

#### Add Pharmacy Stock
```python
from main.models import db, PharmacyStock

stock = PharmacyStock(
    pharmacy_id=1,
    medication_id=5,
    quantity=25,
    price=9.99,
    currency='USD'
)
db.session.add(stock)
db.session.commit()
```

#### Query Medications
```python
from main.models import Medication

# Get all medications starting with 'A'
meds = Medication.query.filter(
    Medication.name.ilike('A%')
).all()

# Search by name
meds = Medication.query.filter(
    Medication.name.ilike('%ibu%')
).all()

# Get OTC medications only
otc_meds = Medication.query.filter_by(is_otc=True).all()
```

## File Changes

### New/Modified Files
- `main/routes/medical.py` - Added 5 new API endpoints
- `main/templates/pharmacy.html` - Complete redesign with search UI and JavaScript
- `main/app.py` - Added medication/pharmacy/stock seeding

### API Endpoints Reference
```
GET  /api/medications                  - Get all medications (paginated)
GET  /api/medications/alphabet         - Browse by letter or get letter counts
GET  /api/medications/search?q=term    - Search medications
GET  /api/medications/<id>             - Get medication details with pharmacy info
POST /human-anatomy                    - Anatomy viewer (unchanged)
GET  /pharmacy                         - Pharmacy page (updated)
```

## Performance Notes

- Search requires minimum 2 characters to prevent broad queries
- Alphabet browsing is optimized with letter counts
- Pagination defaults to 20 items per page
- Database indexes on `name` and `generic_name` for fast searching
- All results are ordered alphabetically for consistency

## Future Enhancements

Potential improvements:
- Drug interaction checker (multiple drug search)
- Rating/review system
- User save/bookmark medications
- Price comparison across pharmacies
- Real-time pharmacy inventory sync
- Medication reminder system
- Filters: OTC vs Rx, Price range, Manufacturer
- Advanced search with filters
- Mobile-optimized view
- Export medication list
