# Refactored Codebase Guide

After the recent refactoring, the application is now cleaner and more maintainable. Here's what changed and how to work with it.

## Quick Overview

### What Was Refactored
- **app.py**: Reduced from 660 to 83 lines (now just app factory)
- **Routes**: Split into focused blueprint modules
- **Email code**: Deduplicated into `utils/email_templates.py`
- **Security**: Removed hardcoded credentials and debug prints
- **Code**: Removed ~100 lines of debug/dead code

### What Stayed the Same
- All features work exactly as before
- Database models unchanged
- Forms and validation unchanged
- Email functionality unchanged
- Authentication flow unchanged

---

## New Project Structure

```
main/
├── app.py                    # App factory only (83 lines)
│
├── models.py                 # Database models
├── config.py                 # Configuration
├── forms.py                  # Form validation
│
├── static/                   # CSS, images, 3D models
├── templates/                # HTML templates
│
├── utils/                    # Shared utilities
│   ├── email_otp.py         # OTP generation & sending
│   ├── email_templates.py   # Email templates (NEW)
│   └── med_bot_wrapper.py   # AI bot wrapper
│
└── routes/                   # Blueprints (route modules)
    ├── auth.py              # Auth routes (signup, login, etc.)
    ├── user.py              # User profile & medical
    ├── medical.py           # Anatomy API & pharmacy
    └── assistant_route.py   # AI assistant
```

---

## Working with Each Module

### 1. Adding Auth Routes
**File**: `main/routes/auth.py`

```python
from flask import Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/new-route', methods=['GET'])
def my_new_route():
    return "Hello"
```

### 2. Adding User Routes
**File**: `main/routes/user.py`

```python
from flask import Blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route('/new-page')
@login_required
def my_page():
    return render_template('my_page.html')
```

### 3. Adding Medical/API Routes
**File**: `main/routes/medical.py`

```python
@medical_bp.route('/api/new-endpoint')
def api_endpoint():
    return {"data": "value"}
```

### 4. Email Functions
**File**: `main/utils/email_templates.py`

```python
from main.utils.email_templates import (
    create_email_message,
    send_email,
    get_confirmation_email_template
)

# Create and send email
html, plain = get_confirmation_email_template(link)
msg = create_email_message("Subject", email, html, plain)
send_email(msg)
```

---

## Common Tasks

### Add a New Feature Routes
1. Create `main/routes/feature_name.py`
2. Define blueprint and routes
3. Register in `main/app.py`:
   ```python
   from main.routes.feature_name import feature_bp
   app.register_blueprint(feature_bp)
   ```

### Modify Authentication
- Auth logic is now in `main/routes/auth.py` (not scattered in app.py)
- Email templates in `main/utils/email_templates.py`
- Forms in `main/forms.py` (unchanged)

### Send Emails
- Use `email_otp.py` for OTP emails (async)
- Use `email_templates.py` for other emails
- Never use raw SMTP directly

### Access Current User
```python
from flask_login import current_user

if current_user.is_authenticated:
    return f"Hello {current_user.username}"
```

---

## Security Best Practices

✅ **Do**:
- Use environment variables for secrets
- Keep credentials out of code
- Use Flask's security features (CSRF, password hashing)
- Validate all user input

❌ **Don't**:
- Hardcode passwords or API keys
- Print sensitive info (even in debug code)
- Use raw SQL queries
- Skip email verification

---

## Testing the Refactored App

```bash
# Run the application
python run.py

# Check application loads
python -c "from main.app import app; print('OK')"

# Check blueprints are registered
python -c "from main.app import app; print(app.blueprints.keys())"

# Expected output: dict_keys(['auth', 'user', 'medical', 'assistant'])
```

---

## File Structure Philosophy

Each route module is responsible for ONE domain:
- **auth.py** → Authentication (signup, login, password reset)
- **user.py** → User accounts (profile, settings, medical card)
- **medical.py** → Medical data (organs, diseases, pharmacy)
- **assistant_route.py** → AI assistant chat

This makes it:
- ✅ Easy to find code
- ✅ Easy to add features
- ✅ Easy to test
- ✅ Easy to maintain

---

## Migration from Old Code

If you have old code that imports from `app.py` directly:

```python
# OLD WAY (don't use)
from main.app import send_confirmation_email

# NEW WAY
from main.utils.email_templates import (
    get_confirmation_email_template,
    create_email_message,
    send_email
)
```

## Key Differences

| Old | New | Why |
|-----|-----|-----|
| `import app` | `from main.routes.auth import auth_bp` | Modular |
| Hardcoded email in app | `utils/email_templates.py` | Reusable |
| 660 lines in app.py | 83 lines in app.py | Maintainable |
| Debug prints | None | Secure |

---

## Next Steps

1. Review the new structure
2. Get familiar with the blueprint pattern
3. When adding features, use the blueprint pattern
4. Keep related routes together in one file
5. Keep app.py as just the factory

For questions, refer to the REFACTORING_SUMMARY.md for details.
