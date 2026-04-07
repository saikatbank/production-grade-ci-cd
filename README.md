# FastAPI Production Starter

A production-grade, highly modular FastAPI application structured for scalability and simplicity. This repository includes an integrated PostgreSQL database (orchestrated via Docker Compose) and a clean, dynamic Vanilla JS dashboard that serves directly from the backend.

## Features
- **FastAPI Backend**: Organized routing, dependencies, and DB sessions.
- **SQLAlchemy ORM**: Defined declarative models connected to PostgreSQL.
- **Modern Dashboard**: A single-page application (UI) built with raw HTML, CSS, and JS served natively.
- **Docker Ready**: Completely containerized for instant local deployments without installing system dependencies.
- **Test-Driven Design**: Integrated Pytest suite that swaps Postgres for an in-memory SQLite database, guaranteeing frictionless CI/CD execution.

## Getting Started

### 1. Boot up dependencies

To fire up both the PostgreSQL container and the FastAPI Web server locally, ensure you have Docker installed and run:

```bash
docker-compose up -d --build
```
*Note: The web service relies on the native `pg_isready` healthcheck to prevent boot failures before Postgres fully initializes.*

### 2. View the application

Navigate your browser to:
- **Dashboard**: `http://localhost:8000/`
- **Interactive Documentation**: `http://localhost:8000/docs`

## Running Tests

Because tests operate against a transient in-memory SQLite database, they run without needing Docker containers active!

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Execute Pytest:
   ```bash
   pytest tests/ -v
   ```

### 4. Code Quality (Linting & Formatting)

We use `black` for code formatting and `ruff` for fast linting. These tools are included in `requirements-dev.txt` and are designed to fail if the code does not meet quality standards, making them easy to integrate into any CI/CD pipeline (Jenkins, GitHub Actions, GitLab CI).

To run formatting and linting checks interactively during development:
```bash
# Auto-format code and fix linting errors
bash scripts/format.sh
```

To run formatting and linting purely as CI tests (this will fail the build if issues are found):
```bash
# Verify formatting and linting without modifying files
bash scripts/lint.sh
```
