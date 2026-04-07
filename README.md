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

We use `black` for code formatting and `ruff` for fast linting. These tools are included in `requirements-dev.txt`. We enforce code quality at three different stages of the development lifecycle:

#### 1. `.pre-commit` Hooks (The Gatekeeper)
Automated checks that run locally every time you type `git commit`. They prevent badly formatted or lint-failing code from entering your git history by automatically fixing staged files and aborting the commit if issues were found.

To install the git hook scripts:
```bash
pre-commit install
```

#### 2. Local Fixer Script (`scripts/format.sh`)
An eager, on-demand script used during development. It runs `black` and `ruff --fix` across your entire `app/` and `tests/` directories to instantly auto-format and clean up the whole project.

```bash
# Auto-format code and fix linting errors
bash scripts/format.sh
```

#### 3. CI/CD Enforcer Script (`scripts/lint.sh`)
A strict pass/fail script used in your automated CI/CD pipelines. It runs `black --check` and `ruff check` in a read-only mode. If any files are unformatted or contain lint violations, the script exits with an error, failing the CI/CD pipeline build.

```bash
# Verify formatting and linting without modifying files (fails if issues are found)
bash scripts/lint.sh
```
