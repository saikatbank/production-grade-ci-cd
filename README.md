# FastAPI Production Starter

A production-grade, highly modular FastAPI application structured for scalability and simplicity. This repository includes an integrated PostgreSQL database (orchestrated via Docker Compose), a clean dynamic Vanilla JS dashboard served directly from the backend, and a fully automated Jenkins CI/CD pipeline that handles linting, testing, versioning, Docker publishing, and EC2 deployment.

## Features
- **FastAPI Backend**: Organized routing, dependencies, and DB sessions.
- **SQLAlchemy ORM**: Defined declarative models connected to PostgreSQL.
- **Modern Dashboard**: A single-page application (UI) built with raw HTML, CSS, and JS served natively.
- **Docker Ready**: Completely containerized for instant local and production deployments.
- **Test-Driven Design**: Integrated Pytest suite that swaps Postgres for an in-memory SQLite database, guaranteeing frictionless CI/CD execution.
- **Automated CI/CD**: Full Jenkins pipeline with semantic versioning, Docker Hub publishing, and zero-downtime EC2 deployment with auto-rollback.

---

## Getting Started (Local Development)

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

---

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

---

## Code Quality (Linting & Formatting)

We use `black` for code formatting and `ruff` for fast linting. These tools are included in `requirements-dev.txt`. Code quality is enforced at three different stages:

#### 1. `.pre-commit` Hooks (The Gatekeeper)
Automated checks that run locally every time you type `git commit`. They prevent badly formatted or lint-failing code from entering your git history.

```bash
pre-commit install
```

#### 2. Local Fixer Script (`scripts/format.sh`)
An on-demand script for development. Runs `black` and `ruff --fix` across your entire project to auto-format and clean up.

```bash
bash scripts/format.sh
```

#### 3. CI/CD Enforcer Script (`scripts/lint.sh`)
A strict pass/fail script used in the Jenkins pipeline. Runs in read-only mode — if any files are unformatted or contain lint violations, the pipeline fails.

```bash
bash scripts/lint.sh
```

---

## CI/CD Pipeline (Jenkins)

The project uses a Jenkins pipeline (`Jenkinsfile`) for fully automated continuous integration and deployment.

### Running Jenkins

A dedicated `jenkins-docker-compose.yaml` is provided to spin up a Jenkins instance locally:

```bash
docker compose -f jenkins-docker-compose.yaml up -d
```

Jenkins will be available at `http://localhost:8080`.

> **Note:** The Jenkins container uses `Dockerfile.jenkins`, a custom image that bundles the Docker CLI alongside the standard Jenkins image so pipelines can build and push Docker images.

---

### Pipeline Stages

The pipeline follows a strict quality-gate order — code is only tagged and deployed if it passes all checks first:

```
Checkout → Lint & Format → Unit Tests → Version Bump → Docker Build → Docker Push → Deploy to EC2
```

| Stage | Description |
|---|---|
| **Checkout** | Clones the repository from GitHub |
| **Lint & Format** | Runs `black --check` and `ruff check` inside a `python:3.11-slim` container. Fails fast if code quality issues exist. |
| **Unit Tests** | Runs the full Pytest suite and publishes JUnit XML results to Jenkins. |
| **Version Bump** | Reads the latest Git tag and the last commit message to compute and push a new [Semantic Version](#semantic-versioning) tag to GitHub. Only runs after all quality gates pass. |
| **Docker Build** | Builds the application Docker image and tags it with both the new version and `latest`. |
| **Docker Push** | Authenticates with Docker Hub and pushes both image tags. |
| **Deploy to EC2** | SSHs into the EC2 instance, transfers `docker-compose.prod.yml`, pulls the new image, and starts it. Runs a health check with auto-rollback on failure. |

---

### Semantic Versioning

Versions are determined automatically from your commit messages using the [Conventional Commits](https://www.conventionalcommits.org/) specification. No manual version bumping needed.

| Commit Message Prefix | Version Bump | Example |
|---|---|---|
| `fix:` / `chore:` / `docs:` / `ci:` etc. | **Patch** | `1.0.0` → `1.0.1` |
| `feat:` or `feat(scope):` | **Minor** | `1.0.1` → `1.1.0` |
| `feat!:` or `BREAKING CHANGE` in body | **Major** | `1.1.0` → `2.0.0` |

Each successful build creates an annotated Git tag (e.g., `v1.2.3`) in this repository and a versioned Docker image on Docker Hub (e.g., `saikatbank/fastapi-app:1.2.3`).

---

### Rollback Strategy

The pipeline supports two levels of rollback:

#### 1. Automatic Rollback (Health Check Failure)
After every deployment, Jenkins polls the `/health/live` endpoint up to 6 times (10s apart). If the new deployment is unresponsive, it automatically redeploys the previous image and marks the build as **FAILED**.

#### 2. Manual Rollback (Parameterized Build)
To instantly rollback to any previous version without a full rebuild:

1. Go to your Jenkins Pipeline dashboard.
2. Click **"Build with Parameters"**.
3. Enter the target version in the `ROLLBACK_VERSION` field (e.g., `1.1.0`).
4. Click **Build**.

Jenkins will skip all build/test/push stages and SSH directly into EC2 to redeploy the specified version in ~30 seconds.

---

### Required Jenkins Credentials

Set these up under **Manage Jenkins → Credentials → (global)**:

| Credential ID | Type | Purpose |
|---|---|---|
| `docker-registry-creds` | Username with Password | Docker Hub login |
| `github-token` | Secret text | GitHub PAT for pushing version tags |
| `app-server-cred` | SSH Username with private key | SSH access to EC2 (PEM key, username: `ubuntu`) |

---

### Production Deployment

The production environment uses `docker-compose.prod.yml` which:
- Pulls the versioned image from Docker Hub instead of building locally.
- Exposes the app on **Port 80**.
- Runs with `restart: always` for automatic recovery on server reboot.
- Does **not** mount local source code (runs fully from the built image).

The app is accessible at `http://<EC2_PUBLIC_IP>/` after a successful deployment.
