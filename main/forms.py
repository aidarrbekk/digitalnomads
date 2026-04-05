from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from main.models import User
import re

def fast_email_validator(form, field):
    """
    Fast email validator without DNS/SMTP checks
    Uses simple regex pattern matching instead of expensive deliverability checks
    """
    # Simple email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, field.data):
        raise ValidationError('Invalid email address')


class SignUpForm(FlaskForm):
    """Sign up form"""
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters')
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            fast_email_validator  # Use fast validation without DNS checks
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message='Password must be at least 8 characters long')
        ]
    )
    password_confirm = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username) -> None:
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email) -> None:
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one or log in.')

class VerifyOTPForm(FlaskForm):
    """OTP verification form"""
    otp = StringField(
        'Verification Code',
        validators=[
            DataRequired(message='Please enter the verification code'),
            Length(min=6, max=6, message='Verification code must be 6 digits')
        ]
    )
    submit = SubmitField('Verify Email')


class LoginForm(FlaskForm):
    """Login form - accept username or email"""
    identifier = StringField(
        'Username or Email',
        validators=[
            DataRequired(message='Please enter your username or email')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class UpdateProfileForm(FlaskForm):
    """Update user profile form"""
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=3, max=80)
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            fast_email_validator  # Use fast validation without DNS checks
        ]
    )
    first_name = StringField('First Name', validators=[Length(max=120)])
    last_name = StringField('Last Name', validators=[Length(max=120)])
    bio = StringField('Bio', validators=[Length(max=500)])
    country = StringField('Country', validators=[Length(max=120)])
    submit = SubmitField('Update Profile')
    
    def validate_username(self, username) -> None:
        """Check if username is available (excluding current user)"""
        if username.data is not None:
            user = User.query.filter_by(username=username.data).first()
            if user and user.id != self.user_id:
                raise ValidationError('Username already taken.')
    
    def validate_email(self, email) -> None:
        """Check if email is available (excluding current user)"""
        if email.data is not None:
            user = User.query.filter_by(email=email.data).first()
            if user and user.id != self.user_id:
                raise ValidationError('Email already registered.')
    
    def set_user_id(self, user_id: int) -> None:
        """Set current user ID for validation"""
        self.user_id = user_id

class ForgotPasswordForm(FlaskForm):
    """Forgot password form"""
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(),
            fast_email_validator
        ]
    )
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    """Reset password form"""
    password = PasswordField(
        'New Password',
        validators=[
            DataRequired(),
            Length(min=8, message='Password must be at least 8 characters long')
        ]
    )
    password_confirm = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Reset Password')

class MedicalMetricsForm(FlaskForm):
    """Medical metrics form for storing personal health information"""
    # Body measurements
    height_cm = FloatField('Height (cm)', validators=[Optional()])
    weight_kg = FloatField('Weight (kg)', validators=[Optional()])
    blood_type = SelectField(
        'Blood Type',
        choices=[
            ('', 'Select Blood Type'),
            ('O-', 'O-'),
            ('O+', 'O+'),
            ('A-', 'A-'),
            ('A+', 'A+'),
            ('B-', 'B-'),
            ('B+', 'B+'),
            ('AB-', 'AB-'),
            ('AB+', 'AB+')
        ],
        validators=[Optional()]
    )
    
    # Vital signs
    blood_pressure_systolic = IntegerField('Blood Pressure (Systolic - mmHg)', validators=[Optional()])
    blood_pressure_diastolic = IntegerField('Blood Pressure (Diastolic - mmHg)', validators=[Optional()])
    heart_rate = IntegerField('Heart Rate (bpm)', validators=[Optional()])
    temperature_c = FloatField('Temperature (°C)', validators=[Optional()])
    oxygen_saturation = FloatField('Oxygen Saturation (%)', validators=[Optional()])
    
    # Medical history
    allergies = TextAreaField('Allergies', validators=[Optional(), Length(max=1000)])
    chronic_conditions = TextAreaField('Chronic Conditions', validators=[Optional(), Length(max=1000)])
    medications = TextAreaField('Current Medications', validators=[Optional(), Length(max=1000)])
    surgeries = TextAreaField('Previous Surgeries', validators=[Optional(), Length(max=1000)])
    
    # Emergency contact
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional(), Length(max=255)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[Optional(), Length(max=20)])
    emergency_contact_relation = StringField('Relationship', validators=[Optional(), Length(max=100)])
    
    submit = SubmitField('Save Medical Information')