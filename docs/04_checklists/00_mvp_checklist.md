# MVP Checklist — Schedule Builder v0.1

## Purpose

This checklist tracks development progress for the Schedule Builder MVP.

The MVP delivers a single end-to-end workflow:

> Upload an engineering scope document → Extract text → Analyze scope with AI → Generate a structured WBS → Export results.

Use this checklist to track what has been completed, what is in progress, and what remains before the MVP is considered functional.

---

## Legend

- `[ ]` Not started
- `[x]` Complete
- `[-]` In progress
- `[~]` Deferred (post-MVP)

---

## 1. Project Infrastructure

### 1.1 Repository and Configuration

- [x] Repository initialized with version control
- [x] Python version pinned (`.python-version`)
- [x] `pyproject.toml` configured with dependencies
- [x] `.env.example` created with required environment variables
- [x] `.gitignore` configured
- [x] `.dockerignore` configured
- [x] Pre-commit hooks configured (`.pre-commit-config.yaml`)
- [x] All required MVP dependencies added to `pyproject.toml`
  - [x] `pymupdf` (PDF processing)
  - [x] `pdfplumber` (PDF processing fallback)
  - [x] `python-docx` (DOCX processing)
  - [x] `anthropic` (Claude API)
  - [x] `openai` (OpenAI API, optional secondary)
  - [x] `pydantic` (data validation)
  - [x] `fastapi` (web framework)
  - [x] `sqlalchemy` (ORM)
  - [x] `alembic` (database migrations)

### 1.2 Application Entrypoint

- [x] `main.py` entrypoint exists at project root
- [x] FastAPI application instance created (`src/schedule_builder/main.py`)
- [x] API router registered (`src/schedule_builder/api/router.py`)
- [x] Application settings configured (`src/schedule_builder/config/settings.py`)
- [x] Logging configured (`src/schedule_builder/core/logging.py`)
- [x] Core middleware registered (`src/schedule_builder/core/middleware.py`)
- [x] Core exceptions defined (`src/schedule_builder/core/exceptions.py`)

### 1.3 Database

- [x] Database session management implemented (`src/schedule_builder/db/session.py`)
- [x] SQLAlchemy declarative base configured (`src/schedule_builder/db/base.py`)
- [x] Base model with common fields defined (`src/schedule_builder/models/base.py`)
- [x] Alembic migration environment initialized
- [x] Initial database migration created and applied
- [x] Project record model created (`src/schedule_builder/models/project.py`)
- [x] Document record model created (`src/schedule_builder/models/document.py`)
- [x] WBS record model created (`src/schedule_builder/models/wbs.py`)

### 1.4 Authentication

- [x] Authentication service implemented (`src/schedule_builder/auth/service.py`)
- [x] JWT token utilities implemented (`src/schedule_builder/auth/tokens.py`)
- [x] Auth route handlers implemented (`src/schedule_builder/auth/routes.py`)
- [x] Auth schemas defined (`src/schedule_builder/auth/schemas.py`)
- [x] Auth dependencies implemented (`src/schedule_builder/auth/dependencies.py`)
- [x] Password hashing utilities implemented (`src/schedule_builder/utils/hashing.py`)
- [x] Security utilities implemented (`src/schedule_builder/core/security.py`)

### 1.5 User Management

- [x] User model defined (`src/schedule_builder/models/user.py`)
- [x] User repository implemented (`src/schedule_builder/repositories/user_repository.py`)
- [x] User service implemented (`src/schedule_builder/services/user_service.py`)
- [x] User schemas defined (`src/schedule_builder/schemas/user.py`)
- [x] User routes implemented (`src/schedule_builder/api/v1/routes_users.py`)
- [x] Admin routes implemented (`src/schedule_builder/api/v1/routes_admin.py`)
- [x] Health check route implemented (`src/schedule_builder/api/v1/routes_health.py`)

---

## 2. Document Processing

### 2.1 Document Ingestion Service

- [ ] Document upload endpoint created (`POST /api/v1/documents/upload`)
- [ ] Accepted file types validated (PDF, DOCX, TXT)
- [ ] File size limits enforced
- [ ] Uploaded file stored (local filesystem or object storage)
- [ ] Document record saved to database
- [ ] Document upload schema defined (`src/schedule_builder/schemas/document.py`)

### 2.2 PDF Processing

- [ ] PDF text extraction service created (`src/schedule_builder/services/document_service.py`)
- [ ] PyMuPDF integration implemented for PDF text extraction
- [ ] Page-level text extraction working
- [ ] Multi-page document handling verified
- [ ] Extracted text cleaned (whitespace normalization, encoding issues resolved)
- [ ] Extraction metadata captured (page count, file size, extraction timestamp)

### 2.3 DOCX Processing

- [ ] python-docx integration implemented
- [ ] Paragraph-level text extraction working
- [ ] Table extraction working (scope-of-services tables common in RFPs)
- [ ] Heading structure preserved where possible

### 2.4 TXT Processing

- [ ] Plain text ingestion implemented
- [ ] Encoding detection and normalization implemented (UTF-8, Latin-1)

### 2.5 Document Validation

- [ ] Extracted text minimum length validated (reject empty or near-empty extractions)
- [ ] Pydantic schema defined for validated document text output
- [ ] Extraction failure handled with clear error response

---

## 3. AI Scope Analysis

### 3.1 AI Client Setup

- [ ] Claude API client configured (`src/schedule_builder/integrations/claude_client.py`)
- [ ] API key loaded from environment settings
- [ ] OpenAI API client configured as secondary option (`src/schedule_builder/integrations/openai_client.py`)
- [ ] AI provider selection configurable via environment variable
- [ ] Client connection validated on application startup

### 3.2 Prompt Engineering

- [ ] System prompt designed for engineering scope analysis
- [ ] Prompt instructs extraction of:
  - [ ] Project type
  - [ ] Project deliverables
  - [ ] Required disciplines
  - [ ] Meetings and coordination requirements
  - [ ] Permitting requirements
  - [ ] Scope summary
- [ ] Prompt instructs structured JSON output
- [ ] Prompt tested against representative engineering RFP documents
- [ ] Prompt refined to minimize hallucination on standard engineering project types

### 3.3 Scope Extraction Service

- [ ] Scope analysis service created (`src/schedule_builder/services/scope_service.py`)
- [ ] Document text chunked appropriately for LLM context window
- [ ] Structured JSON response parsed and validated with Pydantic
- [ ] Pydantic model defined for AI scope response (`src/schedule_builder/schemas/scope.py`)
  - [ ] `project_type` field
  - [ ] `scope_summary` field
  - [ ] `deliverables` list
  - [ ] `disciplines` list
  - [ ] `meetings` list
  - [ ] `permits` list
  - [ ] `services` list
- [ ] Malformed AI responses handled gracefully (retry logic or fallback)
- [ ] AI response stored to database or output file

### 3.4 AI Response Validation

- [ ] Required fields validated (project_type, deliverables minimum one item)
- [ ] Unexpected or empty AI responses caught and logged
- [ ] Validation failures surfaced to user with actionable error message

---

## 4. WBS Generation

### 4.1 WBS Builder Service

- [ ] WBS generation service created (`src/schedule_builder/services/wbs_service.py`)
- [ ] WBS built from validated scope analysis output
- [ ] WBS follows standard hierarchical numbering (1.0, 1.1, 1.2, 2.0, etc.)
- [ ] Standard project phases included by default:
  - [ ] Project Management
  - [ ] Data Collection
  - [ ] Geotechnical Services (when applicable)
  - [ ] Environmental Services (when applicable)
  - [ ] Design (with sub-phases)
  - [ ] Procurement Support (when applicable)
- [ ] Phases included/excluded based on extracted scope elements
- [ ] WBS items mapped from extracted deliverables and services

### 4.2 WBS Validation

- [ ] Pydantic model defined for WBS structure (`src/schedule_builder/schemas/wbs.py`)
  - [ ] `wbs_number` field
  - [ ] `title` field
  - [ ] `level` field (1 = phase, 2 = task)
  - [ ] `parent_wbs_number` field (nullable for top-level items)
- [ ] WBS numbering validated (sequential, no gaps, no duplicates)
- [ ] Minimum required sections validated (Project Management required)
- [ ] Maximum WBS depth enforced (MVP: 2 levels)

### 4.3 WBS Storage

- [ ] Generated WBS saved to database
- [ ] WBS linked to originating document and project record
- [ ] WBS retrievable by project ID

---

## 5. Output Generation

### 5.1 Scope Summary Output

- [ ] Scope summary text generated from AI analysis
- [ ] Summary length appropriate for proposal use (2–5 sentences)
- [ ] Summary included in all export formats

### 5.2 Discipline List Output

- [ ] Discipline list generated from AI analysis
- [ ] Disciplines formatted as clean text list
- [ ] Disciplines sorted alphabetically

### 5.3 Deliverable List Output

- [ ] Deliverable list generated from AI analysis
- [ ] Deliverables formatted as clean text list
- [ ] Deliverables sorted by project phase where possible

### 5.4 WBS Output — Markdown

- [ ] WBS exported as formatted Markdown
- [ ] Hierarchical numbering preserved
- [ ] Phase and task indentation applied
- [ ] Markdown output readable in standard editors and renderers

### 5.5 WBS Output — CSV

- [ ] WBS exported as CSV
- [ ] Columns: `wbs_number`, `title`, `level`, `parent_wbs_number`
- [ ] CSV compatible with standard spreadsheet applications
- [ ] UTF-8 encoding applied

### 5.6 WBS Output — JSON

- [ ] WBS exported as structured JSON
- [ ] JSON schema consistent with internal Pydantic models
- [ ] JSON suitable for future API integrations

### 5.7 Output Service

- [ ] Output generation service created (`src/schedule_builder/services/output_service.py`)
- [ ] All output formats generated from a single service call
- [ ] Output files saved to project output directory or returned as API response

---

## 6. API Endpoints

### 6.1 Document Endpoints

- [ ] `POST /api/v1/documents/upload` — Upload document and trigger processing
- [ ] `GET /api/v1/documents/{document_id}` — Retrieve document record and status
- [ ] `GET /api/v1/documents/{document_id}/text` — Retrieve extracted text

### 6.2 Project Endpoints

- [ ] `POST /api/v1/projects` — Create a new project
- [ ] `GET /api/v1/projects/{project_id}` — Retrieve project details
- [ ] `GET /api/v1/projects` — List projects for authenticated user

### 6.3 WBS Endpoints

- [ ] `GET /api/v1/projects/{project_id}/wbs` — Retrieve generated WBS
- [ ] `GET /api/v1/projects/{project_id}/wbs/export?format=markdown` — Export WBS as Markdown
- [ ] `GET /api/v1/projects/{project_id}/wbs/export?format=csv` — Export WBS as CSV
- [ ] `GET /api/v1/projects/{project_id}/wbs/export?format=json` — Export WBS as JSON

### 6.4 Analysis Endpoints

- [ ] `GET /api/v1/projects/{project_id}/scope` — Retrieve scope analysis results
- [ ] `GET /api/v1/projects/{project_id}/disciplines` — Retrieve identified disciplines
- [ ] `GET /api/v1/projects/{project_id}/deliverables` — Retrieve identified deliverables

### 6.5 Existing Infrastructure Endpoints

- [ ] `GET /health` — Health check
- [ ] `POST /auth/login` — User login
- [ ] `POST /auth/register` — User registration
- [ ] `GET /api/v1/users/me` — Current user profile

---

## 7. Testing

### 7.1 Unit Tests

- [ ] Document processing service unit tests (`tests/unit/test_document_service.py`)
  - [ ] PDF extraction test with sample RFP
  - [ ] DOCX extraction test with sample scope document
  - [ ] TXT extraction test
  - [ ] Empty file rejection test
  - [ ] Unsupported file type rejection test
- [ ] Scope analysis service unit tests (`tests/unit/test_scope_service.py`)
  - [ ] AI response parsing test (valid JSON)
  - [ ] Malformed AI response handling test
  - [ ] Missing required fields handling test
- [ ] WBS generation service unit tests (`tests/unit/test_wbs_service.py`)
  - [ ] WBS numbering validation test
  - [ ] Required sections inclusion test
  - [ ] Hierarchical structure test
- [ ] Output service unit tests (`tests/unit/test_output_service.py`)
  - [ ] Markdown export format test
  - [ ] CSV export format and encoding test
  - [ ] JSON export schema test

### 7.2 Integration Tests

- [ ] End-to-end document upload and WBS generation test (`tests/integration/test_wbs_workflow.py`)
- [ ] API endpoint response format tests
- [ ] Database persistence tests (document, WBS records saved and retrievable)

### 7.3 Sample Documents

- [ ] At minimum three sample engineering RFPs collected for testing
  - [ ] Water distribution project RFP
  - [ ] Wastewater collection project RFP
  - [ ] Force main project RFP
- [ ] Sample documents stored in `tests/fixtures/documents/`
- [ ] Expected WBS outputs documented for each sample document

### 7.4 Performance

- [ ] End-to-end processing time benchmarked against target (< 2 minutes per document)
- [ ] API response time acceptable for document upload endpoint

---

## 8. Configuration and Environment

- [ ] All AI API keys stored in environment variables (not hardcoded)
- [ ] `.env.example` updated with all MVP-required variables:
  - [ ] `ANTHROPIC_API_KEY`
  - [ ] `OPENAI_API_KEY` (optional)
  - [ ] `AI_PROVIDER` (claude or openai)
  - [ ] `DATABASE_URL`
  - [ ] `SECRET_KEY`
  - [ ] `UPLOAD_DIR`
  - [ ] `OUTPUT_DIR`
- [ ] Settings class updated to include all new configuration fields
- [ ] Application startup validates required environment variables

---

## 9. Docker and Deployment

- [ ] `docker/` configuration reviewed and updated for MVP services
- [ ] Docker Compose file includes required services (app, database)
- [ ] Application starts successfully in Docker environment
- [ ] Database migrations run automatically on container startup
- [ ] Upload and output directories mounted as volumes

---

## 10. Documentation

- [ ] API endpoint documentation (FastAPI auto-generated OpenAPI docs verified at `/docs`)
- [ ] README updated to reflect current MVP scope and workflow
- [ ] Setup instructions documented (local development, Docker)
- [ ] Sample workflow documented (upload → analyze → export)
- [ ] Known limitations documented

---

## MVP Acceptance Criteria

Before the MVP is considered complete, verify the following:

- [ ] A PDF engineering RFP can be uploaded via the API
- [ ] Text is successfully extracted from the uploaded document
- [ ] The AI correctly identifies the project type, deliverables, and disciplines
- [ ] A structured WBS is generated with correct hierarchical numbering
- [ ] The WBS is exported in Markdown, CSV, and JSON formats
- [ ] The generated WBS requires only minor editing for a typical municipal infrastructure RFP
- [ ] At least 80% of major project tasks are identified in the WBS
- [ ] End-to-end processing completes in under two minutes
- [ ] All MVP API endpoints return correct HTTP status codes and response formats
- [ ] Unit tests pass for document processing, scope analysis, and WBS generation
- [ ] The application runs without errors in the Docker environment

---

## Out of Scope — Not Tracked Here

The following features are intentionally excluded from the MVP and are not tracked in this checklist:

- Task duration generation
- Schedule logic (predecessors, successors, critical path)
- Staffing estimates and resource loading
- Cost or fee estimation
- Risk register generation
- Microsoft Project or Primavera export
- Gantt chart generation
- Multi-user collaboration
- Historical project analytics

These features are planned for future releases (v0.2 and beyond).
