# Schedule Builder — Application Instructions

## Overview

Schedule Builder is a FastAPI-based platform for analyzing engineering project scopes and generating Work Breakdown Structures (WBS). This guide covers local development setup, running the application, and testing.

---

## Prerequisites

- **Python 3.12+** (specified in `.python-version`)
- **PostgreSQL 13+** (for database)
- **uv** (Python package manager — install from https://astral.sh/uv)
- **Git**

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd schedule_builder
```

### 2. Set Up Python Environment

The project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and update with your local settings:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
# Environment
ENVIRONMENT=development
DEBUG=true

# Database (create these databases first)
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/schedule_builder_db
DEV_DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/dev_schedule_builder_db
TEST_DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/test_schedule_builder_db

# Security (change in production)
SECRET_KEY=your-secret-key-here
ADMIN_API_TOKEN=your-admin-token-here

# AI Provider (Claude recommended for MVP)
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-...  # Get from https://console.anthropic.com
OPENAI_API_KEY=           # Optional: OpenAI fallback

# File Storage
UPLOAD_DIRECTORY=uploads
```

### 4. Set Up PostgreSQL Database

Create the required databases:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create databases
CREATE DATABASE schedule_builder_db;
CREATE DATABASE dev_schedule_builder_db;
CREATE DATABASE test_schedule_builder_db;

# Exit
\q
```

### 5. Run Database Migrations

```bash
uv run alembic upgrade head
```

This creates all tables defined in `src/schedule_builder/models/`.

---

## Running the Application

### Development Server

```bash
# Activate environment
source .venv/bin/activate

# Run the app with auto-reload
uv run uvicorn src/schedule_builder/main:app --reload --host 0.0.0.0 --port 8000
```

The application will start at **http://localhost:8000**

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Production Server

```bash
# Run without auto-reload
uv run uvicorn src/schedule_builder/main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Testing

### Run All Tests

```bash
# Run tests with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=src/schedule_builder tests/
```

### Run Specific Test Suites

```bash
# Unit tests
uv run pytest tests/unit/ -v

# Integration tests
uv run pytest tests/integration/ -v

# API/Route tests
uv run pytest tests/api/ -v
```

### Run Single Test

```bash
uv run pytest tests/unit/test_wbs_service.py::test_wbs_service_generates_from_scope -v
```

### Pre-Commit Hooks

The project uses `pre-commit` hooks for code quality:

```bash
# Install hooks (one-time)
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Check specific tools
uv run mypy src/schedule_builder/
uv run ruff check src/ tests/
uv run black --check src/ tests/
```

---

## Typical Workflow

### 1. Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "S3curePassw0rd!",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "id": "uuid...",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "S3curePassw0rd!"
  }'
```

**Response:**
```json
{
  "user": { "id": "...", "email": "..." },
  "tokens": {
    "access_token": "eyJ0eXAi...",
    "refresh_token": "...",
    "token_type": "bearer"
  }
}
```

Save the `access_token` for subsequent requests.

### 3. Create a Project

```bash
curl -X POST http://localhost:8000/v1/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "name": "Water Main Replacement",
    "description": "Design and permitting for main replacement project"
  }'
```

### 4. Upload a Document

```bash
curl -X POST http://localhost:8000/v1/documents/upload \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@scope_document.pdf" \
  -F "project_id=<project-id>"
```

### 5. Generate WBS

```bash
curl -X POST http://localhost:8000/v1/wbs/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"document_id": "<document-id>"}'
```

**Response includes:** `wbs_run_id`, generated items count, and WBS structure.

### 6. Export WBS

**As JSON:**
```bash
curl -X GET "http://localhost:8000/v1/wbs/runs/<wbs_run_id>/export?format=json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -o wbs_export.json
```

**As Markdown:**
```bash
curl -X GET "http://localhost:8000/v1/wbs/runs/<wbs_run_id>/export?format=markdown" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -o wbs_export.md
```

**As CSV:**
```bash
curl -X GET "http://localhost:8000/v1/wbs/runs/<wbs_run_id>/export?format=csv" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -o wbs_export.csv
```

### 7. Retrieve Project-Level Data

```bash
# Get project details
curl -X GET http://localhost:8000/v1/projects/<project-id> \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get most recent WBS
curl -X GET http://localhost:8000/v1/projects/<project-id>/wbs \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get scope analysis
curl -X GET http://localhost:8000/v1/projects/<project-id>/scope \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get extracted disciplines
curl -X GET http://localhost:8000/v1/projects/<project-id>/disciplines \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get extracted deliverables
curl -X GET http://localhost:8000/v1/projects/<project-id>/deliverables \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Docker Setup (Optional)

### Build and Run with Docker Compose

```bash
# Build images
docker-compose build

# Start services (app + database)
docker-compose up

# Run migrations
docker-compose exec app alembic upgrade head

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

The application will be available at **http://localhost:8000** inside the Docker network.

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `development` | Runtime environment: `development`, `testing`, `staging`, `production` |
| `DEBUG` | `true` | Enable FastAPI debug mode |
| `DATABASE_URL` | — | PostgreSQL connection string for prod/staging |
| `DEV_DATABASE_URL` | — | PostgreSQL connection string for development |
| `TEST_DATABASE_URL` | — | SQLite path or PostgreSQL for tests |
| `SECRET_KEY` | — | Secret key for JWT signing |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token lifetime |
| `ADMIN_API_TOKEN` | — | Token for admin endpoints |
| `AI_PROVIDER` | `claude` | AI provider: `claude` or `openai` |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `OPENAI_API_KEY` | — | OpenAI API key (optional) |
| `UPLOAD_DIRECTORY` | `uploads` | Directory for file uploads |

---

## Troubleshooting

### Database Connection Error

**Problem:** `psycopg2.OperationalError: could not connect to server`

**Solution:**
1. Verify PostgreSQL is running: `psql -U postgres`
2. Check `DATABASE_URL` in `.env`
3. Ensure databases exist: `psql -U postgres -l | grep schedule_builder`
4. Create missing databases (see setup section above)

### AI API Key Error

**Problem:** `AuthenticationError` or 401 from Anthropic/OpenAI

**Solution:**
1. Verify API key in `.env`: `echo $ANTHROPIC_API_KEY`
2. Check key is valid at https://console.anthropic.com or https://platform.openai.com
3. Ensure no extra whitespace in `.env`

### Upload Directory Permission Error

**Problem:** `PermissionError: [Errno 13] Permission denied: 'uploads'`

**Solution:**
```bash
# Create and set permissions
mkdir -p uploads
chmod 755 uploads
```

### Tests Failing with Settings Validation

**Problem:** `pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings`

**Solution:**
1. Check `.env` for invalid values (e.g., `AI_PROVIDER=...` instead of `claude`)
2. Ensure all required variables are set
3. Run tests with debug: `uv run pytest -vv --tb=short`

---

## Project Structure

```
schedule_builder/
├── src/schedule_builder/       # Main application code
│   ├── api/                    # FastAPI routes
│   ├── auth/                   # Authentication & JWT
│   ├── config/                 # Settings management
│   ├── core/                   # Exceptions, logging, middleware
│   ├── db/                     # Database session, migrations
│   ├── models/                 # SQLAlchemy ORM models
│   ├── repositories/           # Data access layer
│   ├── schemas/                # Pydantic request/response models
│   ├── services/               # Business logic
│   ├── integrations/           # External API clients (Claude, OpenAI)
│   └── main.py                 # FastAPI app entrypoint
├── tests/                      # Test suites
│   ├── unit/                   # Service/logic tests
│   ├── api/                    # Route/endpoint tests
│   └── integration/            # End-to-end tests
├── docs/                       # Documentation
├── alembic/                    # Database migrations
├── .env.example                # Environment template
├── pyproject.toml              # Dependencies & tool config
└── README.md                   # Project overview
```

---

## Additional Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/
- **Alembic (Migrations):** https://alembic.sqlalchemy.org/
- **Anthropic API:** https://docs.anthropic.com/
- **OpenAI API:** https://platform.openai.com/docs/

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test files for usage examples
3. Check FastAPI auto-generated docs at `/docs`
4. Review error messages carefully — they often indicate the root cause
