# AI Coding Agent Instructions

## Project Overview
A Python project with a minimal structure. Expand this document as the codebase evolves.

**Repository Structure:**
- `main/` - Primary application code
- `.github/` - GitHub workflows and configuration

## Development Environment

### Setup
- Python environment: `venv/` (virtual environment)
- Entry point: `main/app.py`

### Common Commands
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Run the application
python main/app.py
```

## Code Conventions

### Python Standards
- **Style**: Follow PEP 8 (use tools like `black`, `pylint` for consistency)
- **Type Hints**: Add type annotations for function parameters and return values
- **Documentation**: Include docstrings for modules, classes, and functions

### Module Organization
- Keep `main/app.py` focused on application entry point and initialization
- Extract reusable logic into separate modules as the codebase grows
- Use clear module names that reflect their responsibility

## Testing & Validation

- Add unit tests in a `tests/` directory as features develop
- Use `pytest` as the testing framework (recommended)
- Run tests before committing changes

## Dependencies

Currently no external dependencies configured. As new packages are added:
- Document in `requirements.txt`
- Update this guide with installation instructions

## Key Patterns to Follow

- **Single Responsibility**: Each module should have one clear purpose
- **Error Handling**: Implement proper exception handling and logging
- **Configuration**: Use environment variables or config files for settings (not hardcoded)

---

*Last updated: February 10, 2026*  
*Update this file as project structure and conventions become established.*
