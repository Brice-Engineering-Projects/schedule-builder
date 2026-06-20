# Schedule Builder

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Status](https://img.shields.io/badge/status-concept%20development-orange)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-0.1.0-lightgrey)
![Domain](https://img.shields.io/badge/domain-project%20planning%20%26%20analytics-blue)

A project planning and proposal support platform for engineering consultants, utilities, and infrastructure organizations.

Schedule Builder assists project teams with developing schedules, staffing plans, resource allocations, schedule assumptions, risk registers, and proposal support documentation through a structured and repeatable workflow.

---

## Overview

Engineering schedules are frequently developed by modifying previous projects rather than leveraging a structured planning process. While experienced project managers possess valuable knowledge regarding project sequencing, staffing requirements, permitting durations, and schedule risks, that knowledge is often difficult to capture and reuse consistently.

Schedule Builder seeks to standardize project planning workflows while preserving engineering judgment.

The platform is initially focused on municipal infrastructure projects including:

* Water distribution systems
* Wastewater collection systems
* Lift stations
* Force mains
* Stormwater systems
* Water treatment facilities
* Wastewater treatment facilities
* Capital improvement programs

---

## Problem Statement

Project schedules are among the most important planning tools used by engineering organizations, yet schedule development often remains a manual process.

Common challenges include:

* Recreating similar schedules for every proposal
* Inconsistent planning assumptions
* Limited visibility into staffing requirements
* Resource conflicts across projects
* Lack of standardized schedule templates
* Poor documentation of schedule logic
* Limited ability to compare planned versus actual performance

Schedule Builder aims to improve consistency, efficiency, and transparency throughout the planning process.

---

## Key Features

### Schedule Template Library

>Generate schedules from predefined project templates.

### Task and Milestone Generation

>Create project-specific task lists and milestone schedules.

### Staffing Planning

>Develop staffing allocations by discipline and project phase.

### Resource Allocation

>Generate labor-hour summaries and resource loading tables.

### Schedule Assumptions

>Produce standardized planning assumptions suitable for proposal documents.

### Risk Registers

>Generate project-specific risks and mitigation measures.

### Proposal Narratives

>Generate schedule narratives for proposal submissions.

---

## MVP Scope (Version 0.1)

The initial release focuses on proposal support and project planning.

Included features:

* Project templates
* Task generation
* Milestone generation
* Staffing tables
* Schedule assumptions
* Risk registers
* Proposal narrative generation
* Excel exports

Excluded features:

* Microsoft Project integration
* Resource leveling
* Schedule optimization
* Historical analytics
* Monte Carlo simulation
* Multi-user collaboration

---

## Development Roadmap

### Version 0.1 - Proposal Support

* Project templates
* Task generation
* Staffing plans
* Proposal narratives
* Risk registers

### Version 0.2 - Resource Planning

* Multi-project staffing analysis
* Resource loading calculations
* Resource conflict identification
* Enhanced reporting

### Version 0.3 - Project Delivery Analytics

* Planned vs actual tracking
* Milestone performance analysis
* Schedule variance reporting
* Historical benchmarking

### Version 0.4 - Organizational Knowledge Base

* Historical project repository
* Lessons learned integration
* Schedule benchmarking
* Performance metrics

### Version 0.5 - Schedule Forecasting

* Schedule risk scoring
* Delay probability analysis
* Contingency recommendations
* Monte Carlo schedule simulation

---

## Technology Stack

Planned technologies include:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pandas
* OpenPyXL
* Plotly

Specific implementation details are documented within the project architecture documentation.

---

## Getting Started

### Prerequisites

* Python 3.12 or higher
* [`uv`](https://docs.astral.sh/uv/) – Fast Python package installer and resolver

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd schedule-builder
```

2. Install dependencies using `uv`:
```bash
uv sync
```

This command will:
- Create a virtual environment (`.venv`)
- Install all project dependencies
- Install development dependencies from the `dev` group

For detailed `uv` setup instructions, see the [uv documentation](https://docs.astral.sh/uv/getting-started/).

### Running the FastAPI Development Server

Start the development server with auto-reload enabled:

```bash
uv run uvicorn schedule_builder.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Accessing the API Documentation

Once the server is running:

* **Swagger UI (Interactive API docs):** http://localhost:8000/docs
* **ReDoc (Alternative API docs):** http://localhost:8000/redoc
* **OpenAPI Schema:** http://localhost:8000/openapi.json

### Health Check

Verify the server is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

### Running Tests

Run the test suite:

```bash
uv run pytest
```

Run tests with verbose output:

```bash
uv run pytest -v
```

Run a specific test file:

```bash
uv run pytest tests/api/test_health.py
```

---

## Documentation

### Project Documentation

| Document                                         | Description                                     |
| ------------------------------------------------ | ----------------------------------------------- |
| `docs/00_overview.md`                            | Project overview, vision, and roadmap           |
| `docs/01_architecture/00_project_structure.md`   | Repository organization and architecture        |
| `docs/01_architecture/01_system_architecture.md` | System architecture and component relationships |
| `docs/02_requirements/`                          | Functional and non-functional requirements      |
| `docs/03_design/`                                | Design decisions and implementation planning    |
| `docs/04_development/`                           | Development notes and implementation tracking   |

---

## Project Status

**Current Phase:** Concept Development

Current activities include:

* Requirements gathering
* Architecture planning
* Template design
* Staffing model development
* MVP definition

No production implementation has begun.

---

## Long-Term Vision

The long-term vision of Schedule Builder is to evolve into a project delivery analytics platform that supports schedule development, staffing optimization, resource planning, project performance tracking, and schedule forecasting.

By combining engineering knowledge, historical project data, and analytical tools, the platform aims to improve project planning and delivery outcomes across engineering organizations.

---

## License

This project is licensed under the MIT License.
