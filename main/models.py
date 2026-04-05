from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User profile information
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    bio = db.Column(db.Text)
    country = db.Column(db.String(120))
    
    # Email verification
    email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password: str) -> None:
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def verify_email(self) -> None:
        """Mark email as verified"""
        self.email_verified = True
        self.email_verified_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'

class Hospital(db.Model):
    """Hospital model"""
    __tablename__ = 'hospitals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    
    doctors = db.relationship('Doctor', backref='hospital', lazy=True)
    
    def __repr__(self) -> str:
        return f'<Hospital {self.name}>'


class Doctor(db.Model):
    """Doctor model"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)
    
    visits = db.relationship('Visit', backref='doctor', lazy=True)
    
    def __repr__(self) -> str:
        return f'<Doctor {self.first_name} {self.last_name}>'


class Visit(db.Model):
    """Visit/Appointment model"""
    __tablename__ = 'visits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    
    user = db.relationship('User', backref='visits', lazy=True)
    diagnoses = db.relationship('Diagnosis', backref='visit', lazy=True, cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', backref='visit', lazy=True, cascade='all, delete-orphan')
    lab_tests = db.relationship('LabTest', backref='visit', lazy=True, cascade='all, delete-orphan')
    imaging_records = db.relationship('ImagingRecord', backref='visit', lazy=True, cascade='all, delete-orphan')
    ai_analyses = db.relationship('AIAnalysis', backref='visit', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'<Visit {self.id} - User {self.user_id}>'


class Diagnosis(db.Model):
    """Diagnosis model"""
    __tablename__ = 'diagnoses'
    
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    disease_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(50))  # mild, moderate, severe
    
    def __repr__(self) -> str:
        return f'<Diagnosis {self.disease_name}>'


class Prescription(db.Model):
    """Prescription model"""
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    medication_name = db.Column(db.String(255), nullable=False)
    dosage = db.Column(db.String(100))
    frequency = db.Column(db.String(100))  # e.g., "twice daily"
    duration = db.Column(db.String(100))  # e.g., "7 days"
    instructions = db.Column(db.Text)
    
    def __repr__(self) -> str:
        return f'<Prescription {self.medication_name}>'


class LabTestType(db.Model):
    """Lab test type model"""
    __tablename__ = 'lab_test_types'
    
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    lab_tests = db.relationship('LabTest', backref='test_type', lazy=True)
    
    def __repr__(self) -> str:
        return f'<LabTestType {self.test_name}>'


class LabTest(db.Model):
    """Lab test results model"""
    __tablename__ = 'lab_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    test_type_id = db.Column(db.Integer, db.ForeignKey('lab_test_types.id'), nullable=False)
    result_value = db.Column(db.String(255))
    reference_range = db.Column(db.String(255))
    unit = db.Column(db.String(50))
    status = db.Column(db.String(50))  # normal, low, high
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<LabTest {self.test_type.test_name}>'


class ImagingRecord(db.Model):
    """Imaging records model"""
    __tablename__ = 'imaging_records'
    
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    imaging_type = db.Column(db.String(100))  # X-ray, CT, MRI, etc.
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    findings = db.Column(db.Text)
    scan_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<ImagingRecord {self.imaging_type}>'


class AIAnalysis(db.Model):
    """AI analysis model"""
    __tablename__ = 'ai_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    risk_score = db.Column(db.Float)  # 0-100
    analysis_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    recommendations = db.relationship('AIRecommendation', backref='analysis', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'<AIAnalysis {self.id}>'


class AIRecommendation(db.Model):
    """AI recommendations model"""
    __tablename__ = 'ai_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('ai_analyses.id'), nullable=False)
    recommendation_text = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(50))  # low, medium, high
    category = db.Column(db.String(100))  # prevention, treatment, lifestyle, etc.
    
    def __repr__(self) -> str:
        return f'<AIRecommendation {self.id}>'



class Organ(db.Model):
    """Anatomical organ model for human anatomy module"""
    __tablename__ = 'organs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    system = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)

    diseases = db.relationship('Disease', backref='organ', lazy=True, cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<Organ {self.name}>'


class MedicalMetrics(db.Model):
    """Personal medical metrics model"""
    __tablename__ = 'medical_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Body measurements
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    blood_type = db.Column(db.String(10))
    
    # Vital signs
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    temperature_c = db.Column(db.Float)
    oxygen_saturation = db.Column(db.Float)
    
    # Medical history
    allergies = db.Column(db.Text)
    chronic_conditions = db.Column(db.Text)
    medications = db.Column(db.Text)
    surgeries = db.Column(db.Text)
    
    # Emergency contact
    emergency_contact_name = db.Column(db.String(255))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relation = db.Column(db.String(100))
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='medical_metrics', uselist=False)
    
    def __repr__(self) -> str:
        return f'<MedicalMetrics User {self.user_id}>'


class Disease(db.Model):
    """Disease/Illness database model"""
    __tablename__ = 'diseases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    medical_name = db.Column(db.String(255))  # Medical/Latin name
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # infectious, chronic, genetic, etc.
    symptoms = db.Column(db.Text)  # Comma-separated or JSON
    causes = db.Column(db.Text)
    prevention = db.Column(db.Text)
    treatment_overview = db.Column(db.Text)
    severity_level = db.Column(db.String(50))  # mild, moderate, severe
    is_contagious = db.Column(db.Boolean, default=False)
    icd_code = db.Column(db.String(20))  # ICD-10 code
    organ_id = db.Column(db.Integer, db.ForeignKey('organs.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_health_conditions = db.relationship('UserHealthCondition', backref='disease', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'<Disease {self.name}>'


class UserHealthCondition(db.Model):
    """User's health conditions/illnesses"""
    __tablename__ = 'user_health_conditions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    disease_id = db.Column(db.Integer, db.ForeignKey('diseases.id'), nullable=False)
    diagnosis_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')  # active, cured, managed, inactive
    is_chronic = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref='health_conditions', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<UserHealthCondition User {self.user_id} - {self.disease.name}>'


class MedicationCategory(db.Model):
    """Medication category for browsing"""
    __tablename__ = 'medication_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    name_ru = db.Column(db.String(100))
    icon = db.Column(db.String(50))

    medications = db.relationship('Medication', backref='category', lazy=True)

    def __repr__(self):
        return f'<MedicationCategory {self.name}>'


class Medication(db.Model):
    """Medication/Drug database model"""
    __tablename__ = 'medications'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    generic_name = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('medication_categories.id'), nullable=True)
    description = db.Column(db.Text)
    active_ingredient = db.Column(db.String(255))
    dosage_forms = db.Column(db.String(255))  # tablet, injection, cream, etc.
    available_strengths = db.Column(db.String(255))  # e.g., "500mg, 1000mg"
    manufacturer = db.Column(db.String(255))
    side_effects = db.Column(db.Text)
    contraindications = db.Column(db.Text)
    storage_instructions = db.Column(db.Text)
    is_otc = db.Column(db.Boolean, default=False)  # Over-the-counter
    requires_prescription = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pharmacy_stocks = db.relationship('PharmacyStock', backref='medication', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'<Medication {self.name}>'


class Pharmacy(db.Model):
    """Pharmacy model"""
    __tablename__ = 'pharmacies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    
    # Location info
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    city = db.Column(db.String(120))
    country = db.Column(db.String(120))
    
    # Operating hours
    opening_time = db.Column(db.String(10))  # HH:MM format
    closing_time = db.Column(db.String(10))
    operates_24_7 = db.Column(db.Boolean, default=False)
    
    # Services
    accepts_prescription = db.Column(db.Boolean, default=True)
    delivery_available = db.Column(db.Boolean, default=False)
    home_service = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stocks = db.relationship('PharmacyStock', backref='pharmacy', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'<Pharmacy {self.name}>'


class PharmacyStock(db.Model):
    """Medication stock in pharmacies"""
    __tablename__ = 'pharmacy_stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float)  # Price per unit
    currency = db.Column(db.String(10), default='KZT')
    expiry_date = db.Column(db.DateTime)
    batch_number = db.Column(db.String(100))
    last_restocked = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<PharmacyStock {self.pharmacy.name} - {self.medication.name}>'


class UserPrescriptionOrder(db.Model):
    """User prescription orders from pharmacies"""
    __tablename__ = 'user_prescription_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=True)  # From doctor's prescription
    
    # Order details
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, delivered, cancelled
    total_price = db.Column(db.Float)
    delivery_address = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref='pharmacy_orders', lazy=True)
    pharmacy = db.relationship('Pharmacy', backref='orders', lazy=True)
    prescription = db.relationship('Prescription', backref='pharmacy_orders', lazy=True)
    order_items = db.relationship('PrescriptionOrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<UserPrescriptionOrder {self.id}>'


class PrescriptionOrderItem(db.Model):
    """Individual items in a prescription order"""
    __tablename__ = 'prescription_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('user_prescription_orders.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float)
    subtotal = db.Column(db.Float)
    
    medication = db.relationship('Medication', backref='order_items', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<PrescriptionOrderItem Order {self.order_id}>'


# Enhanced Hospital model with additional fields
class HospitalDepartment(db.Model):
    """Hospital departments"""
    __tablename__ = 'hospital_departments'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    head_doctor = db.Column(db.String(255))
    phone_extension = db.Column(db.String(20))
    description = db.Column(db.Text)
    
    hospital = db.relationship('Hospital', backref='departments', lazy=True)
    
    def __repr__(self) -> str:
        return f'<HospitalDepartment {self.name}>'


# Enhanced Doctor model with additional fields
class DoctorSpecialization(db.Model):
    """Doctor specializations"""
    __tablename__ = 'doctor_specializations'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    specialization = db.Column(db.String(255), nullable=False)
    years_of_experience = db.Column(db.Integer)
    license_number = db.Column(db.String(100))
    
    doctor = db.relationship('Doctor', backref='specializations', lazy=True)
    
    def __repr__(self) -> str:
        return f'<DoctorSpecialization {self.specialization}>'