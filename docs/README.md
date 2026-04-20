# Documentation

Guides, tutorials, and solutions for the Digital Nomads project.

## Quick Start Guides

- **OTP_QUICK_START.md** - Quick start for OTP verification system
- **OTP_VERIFICATION_GUIDE.md** - Detailed OTP setup and troubleshooting

## Email Configuration

- **EMAIL_VERIFICATION_READY.md** - Email verification system documentation

## API Documentation

- **PHARMACY_SEARCH_GUIDE.md** - Medication search and pharmacy API
- **PHARMACY_QUICK_REFERENCE.md** - Quick reference for pharmacy endpoints

## API Endpoints

### Anatomy Module

* API endpoints:
  * `GET /api/organs` – list of organs
  * `GET /api/organs/<id>` – details for a single organ (includes associated diseases)
  * `GET /api/diseases` – list of diseases
  * `GET /api/diseases/<id>` – disease details

* Frontend: visit `/human-anatomy` after logging in to see the React/Three.js viewer. Click organs to fetch data from the API.

## Contributing

When adding new features or solving problems:

1. Document the approach and reasoning
2. Include code examples
3. Note any dependencies or requirements
4. Mark outdated information as such

## Project Status

All major systems documented and tested:
- ✅ Email verification
- ✅ OTP system
- ✅ Gmail integration
- ✅ Anatomy module with 3D models
- ✅ Database models
- ✅ AI assistant integration
