# Digital Nomads - Project Architecture

Clean, organized Flask web application for medical records and anatomy education.

## 📁 Project Structure

```
digitalnomads-main/
├── main/                      # Flask application package
│   ├── app.py                # Flask app factory and routes
│   ├── models.py             # SQLAlchemy database models
│   ├── config.py             # Configuration management
│   ├── forms.py              # WTForms definitions
│   ├── static/               # CSS, images, 3D models
│   │   ├── css/
│   │   ├── images/
│   │   └── models/          # 3D GLTF models for anatomy
│   ├── templates/            # HTML templates (Jinja2)
│   ├── utils/                # Utility modules
│   │   ├── email_otp.py     # Email and OTP verification
│   │   └── med_bot_wrapper.py # Medical AI bot integration
│   └── routes/               # Blueprint routes
│       └── assistant_route.py # AI assistant blueprint
│
├── instance/                 # Instance-specific files (not in git)
│   └── digitalnomads.db     # SQLite database
│
├── tests/                    # Test suite
│   ├── test_async_signup.py
│   ├── test_otp_system.py
│   └── ... (other test files)
│
├── docs/                     # Documentation
│   ├── README.md            # Main documentation
│   ├── OTP_QUICK_START.md
│   └── ... (guides, solutions)
│
├── scripts/                  # Utility scripts
│   ├── diagnose_gmail.py    # Email diagnostics
│   └── verify_mail_config.py # Mail configuration
│
├── .github/                 # GitHub-specific files
│   └── copilot-instructions.md
│
├── .venv/                   # Python virtual environment
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── README.md              # This file
```

## 🚀 Quick Start

### Setup
```bash
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run Application
```bash
python run.py
```
The app will be available at `http://localhost:5000`

## 📋 Directory Guide

### `main/` - Core Application
- **app.py**: Flask app factory, route handlers
- **models.py**: Database models (User, Doctor, Hospital, etc.)
- **config.py**: Environment-based configuration
- **forms.py**: Web form validation
- **static/**: CSS, images, 3D models (served by Flask)
- **templates/**: HTML templates rendered with Jinja2

### `main/utils/` - Shared Utilities
- **email_otp.py**: Email sending and OTP verification
- **med_bot_wrapper.py**: Medical AI chatbot integration

### `main/routes/` - Blueprints
- **assistant_route.py**: AI assistant page blueprint

### `instance/` - Instance Files
SQLite database and local configuration (excluded from git).

### `tests/` - Testing
Test files for:
- Async signup flow
- OTP system
- Email timing
- Flask integration

### `docs/` - Documentation
Guides and troubleshooting:
- Email verification setup
- OTP quick start
- Gmail error solutions

### `scripts/` - Utility Scripts
- Email diagnostics
- Configuration validation

## 🔧 Key Features

- **User Authentication**: Sign up, login, email verification
- **Email OTP**: Multi-factor verification via OTP
- **Medical Records**: Patient history and medical data
- **Anatomy Module**: 3D interactive anatomy viewer (React/Three.js)
- **AI Assistant**: Medical information chatbot
- **Admin Dashboard**: User and data management

## 📚 Database Models

- **User**: Account and profile management
- **Hospital**: Healthcare facility info
- **Doctor**: Medical professional data
- **Visit**: Appointment/visit records
- **MedicalRecord**: Patient medical history
- **Organ**: Anatomy information
- **Disease**: Medical condition data

## ⚙️ Configuration

Email configuration in `main/config.py`:
- SMTP server settings
- Authentication credentials
- Default sender address

Database URI: `sqlite:///instance/digitalnomads.db` (default)

## 🔐 Security Notes

- Passwords hashed with Werkzeug
- Email verification required
- Session cookies HTTP-only and SameSite Lax
- CSRF protection via Flask-WTF

## 📦 Dependencies

Key packages:
- Flask: Web framework
- Flask-SQLAlchemy: ORM
- Flask-Login: Authentication
- Flask-WTF: Form handling
- python-dotenv: Environment variables
- sentence-transformers: NLP/RAG
- faiss-cpu: Vector search

See `requirements.txt` for full list.

## 🤝 Contributing

1. Keep code organized in appropriate modules
2. Add tests for new features
3. Update docs for significant changes
4. Follow existing import patterns

## 📝 Notes

- Database file is stored in `instance/` (excluded from git)
- Use `.venv` for virtual environment
- Email credentials should be in environment variables
- 3D models are static assets loaded client-side
