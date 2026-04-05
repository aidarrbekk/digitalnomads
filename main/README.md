# Main Application Package

Core Flask application for Digital Nomads.

## Structure

```
main/
├── app.py              # Flask app factory & route handlers
├── models.py           # SQLAlchemy database models
├── config.py           # Configuration classes
├── forms.py            # WTForms validation classes
├── static/             # Static assets (CSS, images, 3D models)
├── templates/          # Jinja2 HTML templates
├── utils/              # Shared utility modules
└── routes/             # Blueprint routes
```

## Core Files

### app.py
- `create_app()`: Application factory function
- Route handlers for all pages:
  - Authentication (signup, login, email verification)
  - User dashboard and profile
  - Medical records
  - Anatomy module
  - AI assistant

### models.py
Database models:
- **User**: User accounts and profiles
- **Doctor**: Medical professionals
- **Hospital**: Healthcare facilities
- **Visit**: Appointments and visits
- **MedicalRecord**: Patient medical history
- **Organ**: Anatomy information
- **Disease**: Medical conditions

### config.py
Configuration classes:
- **Config**: Base configuration
- **DevelopmentConfig**: Debug enabled
- **ProductionConfig**: Production optimizations
- **TestingConfig**: Test database in memory

### forms.py
WTForms for validation:
- SignUpForm
- LoginForm
- VerifyOTPForm
- UpdateProfileForm
- ResetPasswordForm

## Static Files

### CSS
- `static/css/main.css`: Main stylesheet

### Images
- `static/images/logo.PNG`: Application logo
- `static/images/full_logo.png`: Full logo variant

### 3D Models
GLTF models for anatomy viewer:
- Female body muscular system
- Female skeleton
- Male body muscular system
- Male skeleton

## Templates

### Authentication
- `base.html`: Base template with navigation
- `login.html`: Login form
- `signup.html`: Registration form
- `verify_otp.html`: OTP verification
- `forgot_password.html`: Password reset request
- `reset_password.html`: Password reset form
- `resend_confirmation.html`: Email re-verification

### User Pages
- `profile.html`: User profile view
- `edit_profile.html`: Profile editing
- `dashboard.html`: User dashboard
- `settings.html`: Account settings

### Features
- `medical_card.html`: Medical records
- `human_anatomy.html`: 3D anatomy viewer
- `human_anatomy_react.html`: React-based anatomy (alternative)
- `assistant_page.html`: AI assistant chat
- `pharmacy.html`: Pharmacy information
- `common_illnesses.html`: Health information

### Other
- `about.html`: About page
- `home.html`: Home/landing page

## Utilities

### utils/email_otp.py
Email and OTP functionality:
- `generate_otp()`: Create 6-digit OTP
- `send_otp_email()`: Send OTP via email
- Background email sending with threading

### utils/med_bot_wrapper.py
Medical AI chatbot:
- Wrapper for medical knowledge base
- Sentence transformers for NLP
- FAISS for vector search

## Routes

### routes/assistant_route.py
Separate blueprint for AI assistant:
- `GET /assistant/`: Assistant page
- `POST /assistant/ask`: Question answering

## Environment Variables

Configure in `.env`:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/digitalnomads.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=ShipAI <noreply@shipai.com>
```

## Running

```bash
# Development
python run.py

# With specific config
FLASK_ENV=production python run.py
```

## Testing

```bash
# Run application tests
python -m pytest tests/

# Test specific route
python -m pytest tests/test_flask_email.py -v
```

## Notes

- Uses SQLAlchemy ORM for database operations
- Flask-Login for session management
- Jinja2 for template rendering
- Static files auto-discovered by Flask
- 3D models loaded client-side with Three.js
