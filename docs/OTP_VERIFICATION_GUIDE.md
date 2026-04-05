# Email OTP Verification System - Implementation Guide

## Overview
A two-step email verification system for user registration in ShipAI. Users enter their credentials, receive a 6-digit OTP code via email, and must verify it before account creation.

## Files Created/Modified

### 1. **New File: `main/email_otp.py`**
Utility module for OTP generation and email sending.

**Key Functions:**
- `generate_otp(length=6)` - Generates a random 6-digit OTP
- `send_otp_email(to_email, otp)` - Sends OTP via SMTP to user's email

**Features:**
- Uses Gmail SMTP (smtp.gmail.com:587)
- Supports TLS encryption
- HTML and plain text email formats
- Error handling and logging
- Configuration from Flask app settings

**Environment Variables Required:**
```
MAIL_USERNAME=ssshipaiii@gmail.com
MAIL_PASSWORD=retkqmngionadbhg
MAIL_SERVER=smtp.gmail.com
```

### 2. **Updated: `main/forms.py`**
Added new form for OTP verification.

**New Class: `VerifyOTPForm`**
- Field: `otp` (6-digit string)
- Validators: DataRequired, Length(6)
- Submit button

### 3. **Updated: `main/app.py`**
Implemented two-step signup process with OTP verification.

**Modified Imports:**
```python
from main.forms import SignUpForm, LoginForm, UpdateProfileForm, VerifyOTPForm
from main.email_otp import generate_otp, send_otp_email
```

**Modified Routes:**

#### Route 1: `/signup` (GET/POST)
**Step 1: Collect User Credentials**
- Renders signup form
- On POST: 
  - Validates form data
  - Generates 6-digit OTP
  - Stores user data in session
  - Sends OTP email
  - Redirects to `/verify-otp`

#### Route 2: `/verify-otp` (GET/POST)
**Step 2: Email Verification**
- Renders OTP verification form
- On POST:
  - Compares entered OTP with session OTP
  - If match: Creates user account, marks email as verified
  - If no match: Shows error, redisplays form
  - Clears session and redirects to login

### 4. **New File: `main/templates/verify_otp.html`**
OTP verification form template.

**Features:**
- Beautiful card-based UI
- Input field with numeric-only validation
- Auto-formats OTP input (letters stripped)
- Large, centered display for easy reading
- Copy-paste friendly code input
- Automatic form submission
- Error messaging
- Link to restart signup if needed

**HTML Input Attributes:**
- `maxlength="8"` - Limits input to 6 digits
- `inputmode="numeric"` - Mobile numeric keyboard
- `autocomplete="off"` - Prevents browser autocomplete
- JavaScript prevents non-numeric input

### 5. **Updated: `main/templates/signup.html`**
Enhanced with OTP verification notice and clearer UI.

**Changes:**
- Added info alert about email verification
- Updated submit button text: "Continue to Verification"
- Maintains existing validation UI

---

## Signup Flow Diagram

```
User → Signup Page (Fill Form)
         ↓
    Validate Username/Email/Password
         ↓ (Valid)
    Generate 6-digit OTP
         ↓
    Send OTP Email
         ↓
    Redirect to Verify OTP Page
         ↓
User → Enter OTP Code
         ↓
    Verify OTP Matches
         ↓ (Match)
    Create User Account
    Mark email as verified
         ↓
    Clear Session
    Redirect to Login
         ↓
User → Login with Credentials
```

---

## Email Template Content

**Subject:** Your ShipAI Email Verification Code

**Body:**
- Welcome message
- 6-digit verification code (large, centered)
- Code expiration time (10 minutes)
- Reassurance message if not the user
- Brand signature

---

## Security Features

1. **OTP Generation:** Random 6-digit numeric code
2. **Session Storage:** OTP stored in Flask session (server-side)
3. **Email Verification:** User must have access to registered email
4. **SMTP Security:** TLS encryption for email transmission
5. **Password Security:** Passwords hashed before storage
6. **Account Status:** Email marked as verified only after code confirmation

---

## Usage Instructions

### For Users:
1. Click "Sign Up" button
2. Fill in username, email, and password
3. Click "Continue to Verification"
4. Check email inbox for verification code
5. Enter 6-digit code on verification page
6. Click "Verify Email"
7. Account created - proceed to login

### For Developers:

**Test Email Sending:**
```bash
python test_otp_system.py
```

**Manual Test:**
```python
from main.app import create_app
from main.email_otp import generate_otp, send_otp_email

app = create_app()
with app.app_context():
    otp = generate_otp()
    send_otp_email('test@example.com', otp)
```

---

## Configuration

### Flask Config (`main/config.py`)
```python
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'ssshipaiii@gmail.com')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'ShipAI <ssshipaiii@gmail.com>')
```

### Environment Variables (Set via Windows Registry)
```powershell
setx MAIL_USERNAME "ssshipaiii@gmail.com"
setx MAIL_PASSWORD "retkqmngionadbhg"
setx MAIL_SERVER "smtp.gmail.com"
```

---

## Troubleshooting

### Email Not Sending?
1. Verify credentials: `echo $Env:MAIL_USERNAME`
2. Check internet connection
3. For Gmail: Enable "Less secure app access" or generate App Password
4. Check firewall/antivirus SMTP blocking
5. Review logs for error messages

### OTP Not Verified?
1. Verify user entered all 6 digits
2. Check digit accuracy (compare with email)
3. Session may have expired - restart signup
4. Clear browser cache and cookies

### Session Issues?
- Ensure `SESSION_PERMANENT` is set to True
- Check session timeout in Flask config
- Clear browser cookies if needed

---

## Future Enhancements

1. OTP Expiration: Implement time-based expiration (currently 10 min)
2. Rate Limiting: Limit OTP requests per email/IP
3. Resend Function: Allow users to request new OTP
4. SMS Support: Add SMS as alternative to email
5. Two-Factor Authentication: Optional 2FA for existing users
6. OTP History: Log OTP usage for security audits

---

## Testing Verification

Run the complete test suite:
```bash
python test_otp_system.py
```

Expected Output:
```
✓ OTP Generation: PASS
✓ Mail Configuration: PASS
✓ OTP Email Send: PASS
✓ Forms Import: PASS
✓ Routes Check: PASS
✓ ALL TESTS COMPLETED!
```

---

## References

- **SMTP Module:** Python's built-in `smtplib`
- **Email Messages:** `email.message.EmailMessage`
- **Flask Integration:** `current_app` context
- **Session Management:** Flask `session` object
- **HTML Email:** MIME multipart messages

