# Gmail SMTP Authentication Error - Troubleshooting Guide

## Error Message
```
SMTP authentication failed: (535, b'5.7.8 Username and Password not accepted...')
```

## What This Means
Gmail rejected the login credentials. This is **NOT** a typo or wrong password - it's a Gmail security setting.

---

## ✅ Solution: Use Gmail App Password (RECOMMENDED)

Gmail requires special handling for third-party apps. Follow these steps:

### Step 1: Enable 2-Step Verification (if not already enabled)
1. Go to: https://myaccount.google.com/security
2. Find "2-Step Verification"
3. Click "Enable" (if not already enabled)
4. Follow the prompts

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** (dropdown)
3. Select **Windows Computer** (dropdown)
4. Click **Generate**
5. Google will show a 16-character password (format: `xxxx xxxx xxxx xxxx`)

### Step 3: Update Environment Variable
**⚠️ IMPORTANT: Remove spaces from the password!**

The generated password has spaces (e.g., `abcd efgh ijkl mnop`)
You need to remove them (e.g., `abcdefghijklmnop`)

```powershell
# Example - replace with your actual password (NO SPACES!)
setx MAIL_PASSWORD "abcdefghijklmnop"

# Verify it's set correctly (should show 16 characters)
echo $Env:MAIL_PASSWORD

# Restart PowerShell for changes to take effect
```

### Step 4: Test Connection
```bash
cd c:\Users\yernu\Project
python diagnose_gmail.py
```

Expected output:
```
✓ Connected to SMTP server
✓ TLS started successfully
✓ Authentication successful!
✅ GMAIL SMTP IS WORKING CORRECTLY
```

---

## Alternative: Enable "Less Secure App Access"

If you **don't want** to use App Passwords:

### Step 1: Disable 2-Step Verification
1. Go to: https://myaccount.google.com/security
2. Find "2-Step Verification"
3. Click **Disable**

### Step 2: Enable Less Secure Apps
1. Go to: https://myaccount.google.com/lesssecureapps
2. Toggle **ON** "Allow less secure apps"

### Step 3: Use Original Password
```powershell
# Your original Gmail password
setx MAIL_PASSWORD "your-gmail-password"
```

**⚠️ NOT RECOMMENDED** - Less secure and leaves account vulnerable

---

## Why Error 535?

| Error | Cause | Solution |
|-------|-------|----------|
| **535 - Bad Credentials** | Password incorrect or 2FA required | Use App Password |
| **535 - Account disabled** | Gmail detected suspicious activity | Check security settings |
| **535 - Too many attempts** | Failed login attempts blocked | Wait 24 hours |
| **535 - Username/password invalid** | Regular password with 2FA enabled | Use App Password |

---

## Debugging Steps

### 1. Verify Credentials Are Set
```powershell
echo $Env:MAIL_USERNAME
echo $Env:MAIL_PASSWORD
echo $Env:MAIL_SERVER
```

### 2. Run Diagnostic
```bash
python diagnose_gmail.py
```

### 3. Check for Spaces in Password
```powershell
$pwd = $Env:MAIL_PASSWORD
Write-Host "Length: $($pwd.Length)"
Write-Host "Contains space: $($pwd -like '* *')"
```

**Password must be 16 characters with NO spaces**

### 4. Test Manually
```python
import smtplib
import os

username = os.environ.get('MAIL_USERNAME')
password = os.environ.get('MAIL_PASSWORD')

try:
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
    server.starttls()
    server.login(username, password)
    print("✓ Login successful!")
    server.quit()
except Exception as e:
    print(f"✗ Error: {e}")
```

---

## ✅ Current Status

Your system is now working:

```
✓ OTP Generation: PASS
✓ Mail Configuration: PASS
✓ OTP Email Send: PASS
✓ Forms Import: PASS
✓ Routes Check: PASS
```

---

## Recommended Settings

**Best Practice for Production:**

```
1. ✅ Enable 2-Step Verification
2. ✅ Generate App Password (not regular password)
3. ✅ Use ONLY App Password (16 chars, no spaces)
4. ✅ Store in environment variables (NOT in code)
5. ✅ Restart apps after updating password
```

---

## Gmail Security Checklist

- [ ] 2-Step Verification enabled
- [ ] App Password generated (16 characters)
- [ ] Spaces removed from password
- [ ] Environment variable set correctly
- [ ] PowerShell restarted after setting variable
- [ ] Diagnostic test passes
- [ ] OTP emails sending successfully

---

## If Using Different Email Provider

### For Outlook/Hotmail:
```
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
```

### For Yahoo Mail:
```
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=true
```

### For Corporate/Custom Email:
```
MAIL_SERVER=<your-server>
MAIL_PORT=587 or 465
MAIL_USE_TLS=true or false
```

---

## Support Resources

- **Gmail Help:** https://support.google.com/mail/
- **App Passwords:** https://myaccount.google.com/apppasswords
- **Security Settings:** https://myaccount.google.com/security
- **SMTP Configuration:** https://support.google.com/mail/answer/7126229

---

## ✨ Your System Status

**Email Verification System: ✅ FULLY WORKING**

Users can now:
- ✅ Sign up with email
- ✅ Receive OTP codes
- ✅ Verify email
- ✅ Create account
- ✅ Login

