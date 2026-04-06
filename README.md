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
