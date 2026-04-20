# OTP Email Verification - Quick Start Guide

## 🎯 What Was Built

A complete two-step email verification system for user registration:
1. User signs up with email/password ↓
2. Receives 6-digit OTP code via email ↓
3. Enters OTP to verify email ↓
4. Account created, ready to login

---

## ✅ Verification Steps

### Step 1: Verify Environment Variables
```powershell
# Check if environments are set correctly
echo $Env:MAIL_USERNAME
echo $Env:MAIL_PASSWORD
echo $Env:MAIL_SERVER
```

**Expected Output:**
```
ssshipaiii@gmail.com
retkqmngionadbhg
smtp.gmail.com
```

### Step 2: Run System Tests
```bash
cd c:\Users\yernu\Project
.\.venv\Scripts\activate
python test_otp_system.py
```

**Expected Output:** ✓ ALL TESTS COMPLETED!

### Step 3: Test Live Signup Flow (Optional)
```bash
# Start the Flask app
python run.py
# Visit http://localhost:5000/signup
# Fill form and check your email for OTP
```

---

## 📁 Files Created/Modified

### New Files:
- ✅ `main/email_otp.py` - OTP generation and email sending
- ✅ `main/templates/verify_otp.html` - OTP verification UI
- ✅ `test_otp_system.py` - Test suite
- ✅ `OTP_VERIFICATION_GUIDE.md` - Detailed documentation

### Modified Files:
- ✅ `main/forms.py` - Added VerifyOTPForm
- ✅ `main/app.py` - Updated signup routes with OTP flow
- ✅ `main/templates/signup.html` - Added verification notice

---

## 🔄 The Signup Flow

```
[Signup Form] → Fill credentials
                ↓
            [Generate OTP] → Send email
                ↓
          [Verify OTP Page] → Enter code
                ↓
           [Verify Code] → Match check
                ↓
        [Create Account] → Email verified
                ↓
          [Redirect Login] → Ready to login
```

---

## 🚀 How to Use

### From User Perspective:
1. Click "Sign Up"
2. Enter username, email, password
3. Click "Continue to Verification"
4. Check email for code (arrives in seconds)
5. Enter 6-digit code
6. Click "Verify Email"
7. Account created! Go to login page
8. Login with your credentials

### From Developer Perspective:

**Send OTP Test:**
```python
from main.app import create_app
from main.email_otp import generate_otp, send_otp_email

app = create_app()
with app.app_context():
    otp = generate_otp()  # e.g., "123456"
    result = send_otp_email('test@example.com', otp)
    print(f"Sent: {result}")
```

**Check Routes:**
```python
from main.app import create_app

app = create_app()
routes = [rule.rule for rule in app.url_map.iter_rules()]
print([r for r in routes if 'signup' in r or 'verify' in r or 'otp' in r])
```

**Result:**
```
['/signup', '/verify-otp', ...]
```

---

## ⚙️ Email Configuration

### Current Setup:
- **SMTP Server:** smtp.gmail.com
- **SMTP Port:** 587
- **TLS Encryption:** Enabled
- **From Email:** ssshipaiii@gmail.com
- **Credentials:** Stored in Windows environment variables

### To Use Different Email:
1. Update environment variables:
   ```powershell
   setx MAIL_USERNAME "your-email@gmail.com"
   setx MAIL_PASSWORD "your-app-password"
   ```
2. Generate Gmail App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy generated password
   - Use as MAIL_PASSWORD

---

## 🛡️ Security Features

✅ **Implemented:**
- OTP not stored in code (generated fresh each time)
- Server-side session storage for OTP
- TLS encryption for SMTP
- Password hashing (bcrypt)
- Email verification required
- Environment variable protection
- Comprehensive error handling
- Input validation on client & server

✅ **Ready to Add:**
- OTP expiration timer (10 min)
- Rate limiting (prevent brute force)
- Resend OTP functionality
- SMS fallback option
- Two-factor authentication

---

## 📋 Troubleshooting

### Email Not Received?
- [ ] Check spam/junk folder
- [ ] Verify MAIL_USERNAME is correct
- [ ] Check error logs in Flask output
- [ ] Ensure MAIL_PASSWORD is a Gmail App Password, not your account password

### OTP Code Doesn't Work?
- [ ] Make sure all 6 digits entered
- [ ] Code is case-sensitive (numbers only)
- [ ] Check against email exactly
- [ ] Session may have expired (start over)

### Wrong Credentials Error?
- [ ] Check environment variables: `echo $Env:MAIL_PASSWORD`
- [ ] In Windows Settings → Environment Variables
- [ ] Reduplicate exact values
- [ ] Restart terminal/IDE after changes

---

## 📊 Test Results

```
✓ OTP Generation: PASS
✓ Mail Configuration: PASS  
✓ OTP Email Send: PASS
✓ Forms Import: PASS
✓ Routes Check: PASS
✓ ALL TESTS COMPLETED!
```

---

## 🔗 Related Files

- **Email Module:** `main/email_otp.py`
- **Flask Routes:** `main/app.py` (lines ~151-210)
- **OTP Form:** `main/forms.py` (VerifyOTPForm class)
- **Signup Template:** `main/templates/signup.html`
- **Verify Template:** `main/templates/verify_otp.html`
- **Config:** `main/config.py` (MAIL_* settings)
- **Models:** `main/models.py` (User.email_verified field)

---

## 📞 Support

**Issue:** Email sending fails
**Solution:** Run `python verify_mail_config.py` to debug

**Issue:** OTP verification page blank
**Solution:** Check browser console for errors, reload cache

**Issue:** Can't log in after signup
**Solution:** Email must be verified first. Check for OTP in email.

---

## ✨ Next Enhancements

Future features you can add:
1. OTP expiration (currently no limit)
2. Resend OTP button (throttled)
3. SMS alternative verification
4. Remember device option
5. Backup codes for 2FA
6. OTP attempt limiting (3 tries)

---

**Status:** ✅ **READY TO USE**

The OTP verification system is fully functional and tested. Users can now:
- Register with email verification
- Receive OTP codes via email
- Verify email before account creation
- Login with verified accounts

