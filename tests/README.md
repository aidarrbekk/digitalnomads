# Testing Suite

Test files for the Digital Nomads application.

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_otp_system.py

# Run with verbose output
python -m pytest tests/ -v
```

## Test Files

- **test_otp_system.py** - OTP generation and verification
- **test_async_signup.py** - Asynchronous user signup flow
- **test_email_timing.py** - Email sending performance
- **test_flask_email.py** - Flask email integration
- **test_complete_flow.py** - End-to-end user flow
- **test_credentials.py** - Authentication testing
- **test_real_email.py** - Real email sending tests
- Other utility tests for specific features

## Notes

- Tests use in-memory SQLite by default (see config)
- CSRF protection disabled in testing mode
- Mock email configurations available
