# Scripts Directory

Utility scripts for development and maintenance.

## Available Scripts

### diagnose_gmail.py
Diagnostic tool for Gmail SMTP configuration and email sending issues.

```bash
python scripts/diagnose_gmail.py
```

### verify_mail_config.py
Verifies email configuration settings and connectivity.

```bash
python scripts/verify_mail_config.py
```

## Usage

Run scripts from project root:
```bash
cd /path/to/digitalnomads-main
python scripts/diagnose_gmail.py
```

## Notes

- Scripts use environment variables for sensitive credentials
- Set `MAIL_USERNAME`, `MAIL_PASSWORD`, etc. in `.env` or environment
- Ensure `.venv` is activated before running
