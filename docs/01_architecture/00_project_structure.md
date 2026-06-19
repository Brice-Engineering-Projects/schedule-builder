# Schedule Builder - Project Structure

```text
schedule-builder/
│
├── README.md
├── LICENSE
├── pyproject.toml
├── .gitignore
│
├── docs/
│   │
│   ├── 00_overview.md
│   │
│   ├── 01_architecture/
│   │   ├── 00_project_structure.md
│   │   ├── 01_system_architecture.md
│   │   ├── 02_data_models.md
│   │   ├── 03_data_flow.md
│   │   └── 04_llm_workflow.md
│   │
│   ├── 02_requirements/
│   │   ├── 00_functional_requirements.md
│   │   ├── 01_non_functional_requirements.md
│   │   └── 02_user_stories.md
│   │
│   ├── 03_design/
│   │   ├── 00_mvp_design.md
│   │   ├── 01_document_processing.md
│   │   ├── 02_scope_analysis.md
│   │   ├── 03_wbs_generation.md
│   │   └── 04_exports.md
│   │
│   └── 04_development/
│       ├── 00_build_checklist.md
│       ├── 01_backlog.md
│       └── 02_release_notes.md
│
├── data/
│   │
│   ├── prompts/
│   │   ├── scope_analysis.md
│   │   ├── discipline_extraction.md
│   │   ├── deliverable_extraction.md
│   │   └── wbs_generation.md
│   │
│   ├── examples/
│   │   ├── sample_rfp.pdf
│   │   ├── sample_scope.docx
│   │   └── sample_output.json
│   │
│   └── outputs/
│
├── src/
│   │
│   └── schedule_builder/
│       │
│       ├── api/
│       │
│       ├── config/
│       │
│       ├── core/
│       │
│       ├── models/
│       │   ├── project_scope.py
│       │   ├── deliverable.py
│       │   ├── discipline.py
│       │   ├── permit.py
│       │   └── wbs.py
│       │
│       ├── schemas/
│       │
│       ├── services/
│       │   ├── document_service.py
│       │   ├── extraction_service.py
│       │   ├── scope_analysis_service.py
│       │   ├── wbs_generation_service.py
│       │   └── validation_service.py
│       │
│       ├── integrations/
│       │   ├── claude_client.py
│       │   ├── openai_client.py
│       │   ├── pdf_processor.py
│       │   └── docx_processor.py
│       │
│       ├── exports/
│       │   ├── markdown_exporter.py
│       │   ├── csv_exporter.py
│       │   └── json_exporter.py
│       │
│       ├── utils/
│       │
│       ├── __init__.py
│       └── main.py
│
├── tests/
│   │
│   ├── services/
│   ├── integrations/
│   ├── exports/
│   └── fixtures/
│
├── notebooks/
│   │
│   ├── prompt_testing.ipynb
│   ├── scope_extraction_testing.ipynb
│   └── wbs_generation_testing.ipynb
│
└── examples/
    │
    ├── example_rfp.pdf
    ├── example_scope.docx
    └── example_wbs.md
```

## Architectural Overview

The Schedule Builder MVP is organized around a single objective:

> Transform unstructured engineering project requirements into a structured Work Breakdown Structure (WBS).

The architecture is intentionally focused on document processing, scope understanding, and WBS generation. Features such as schedule generation, staffing estimation, risk assessment, and resource planning are considered future enhancements and are intentionally excluded from the MVP.

---

## Core Workflow

The system follows a straightforward workflow:

```text
Project Document
        ↓
Document Extraction
        ↓
Scope Analysis
        ↓
ProjectScope
        ↓
WBS Generation
        ↓
Export
```

The primary responsibility of the platform is to convert project requirements into structured planning information suitable for engineering project planning.

---

## ProjectScope-Centric Design

The central object within the application is the `ProjectScope`.

The ProjectScope represents the structured understanding of a project extracted from an uploaded document.

Examples of information contained within a ProjectScope include:

* Project type
* Deliverables
* Disciplines
* Permits
* Meetings
* Services
* Scope requirements
* Assumptions

The ProjectScope serves as the foundation for all downstream processing.

Rather than generating a WBS directly from an uploaded document, the system first creates a structured ProjectScope and then generates the WBS from that structured representation.

This approach provides a reusable foundation for future capabilities such as:

* Staffing recommendations
* Risk identification
* Proposal support
* Schedule support
* Historical analytics
* Organizational knowledge bases

---

## Models

Models represent the primary business entities within the system.

Examples include:

### ProjectScope

Represents the structured understanding of an uploaded project document.

### Deliverable

Represents a required project deliverable identified during scope analysis.

Examples:

* Survey
* Report
* Permit Application
* Construction Plans

### Discipline

Represents a professional discipline required to execute the project.

Examples:

* Civil Engineering
* Survey
* Environmental
* Geotechnical

### Permit

Represents a permit or regulatory approval requirement.

Examples:

* ERP
* USACE
* Right-of-Way

### WBS

Represents the generated Work Breakdown Structure.

---

## Services

Services coordinate business workflows throughout the application.

Services are responsible for transforming information between processing stages.

Examples include:

### Document Service

Coordinates document processing workflows.

### Extraction Service

Extracts text from uploaded project documents.

### Scope Analysis Service

Uses AI and business logic to analyze extracted project requirements.

### WBS Generation Service

Generates structured WBS outputs from ProjectScope objects.

### Validation Service

Validates AI responses and generated project data.

---

## Integrations

Integrations provide communication with external systems and third-party tools.

Examples include:

### Claude API

Provides scope analysis and WBS generation capabilities.

### OpenAI API

Alternative AI provider used for testing, benchmarking, or future flexibility.

### PDF Processing

Responsible for PDF text extraction.

### DOCX Processing

Responsible for Word document processing.

The integration layer isolates third-party dependencies from core business logic and allows providers to be replaced without impacting application architecture.

---

## Exports

Exports are responsible for delivering generated outputs to users.

The MVP supports:

### Markdown

Human-readable WBS output.

### CSV

Spreadsheet-compatible export format.

### JSON

Structured output format suitable for future integrations.

Future releases may support:

* Microsoft Project XML
* Excel
* PDF

---

## Data

The data directory stores reusable project assets used throughout the application.

Examples include:

### Prompts

Prompt templates used by the AI analysis workflow.

Examples:

* Scope analysis
* Discipline extraction
* Deliverable extraction
* WBS generation

### Examples

Sample project documents and expected outputs used for testing and development.

### Outputs

Generated project artifacts used during development and validation.

---

## Testing Strategy

Testing is organized around system workflows rather than individual utility functions.

Key testing areas include:

### Services

Validation of business logic and workflow coordination.

### Integrations

Validation of AI providers and document processors.

### Exports

Validation of generated output formats.

### Fixtures

Reusable project documents and expected outputs used throughout the test suite.

---

## Design Principles

### Engineer-in-the-Loop

The platform assists engineers but does not replace engineering judgment.

The engineer remains responsible for:

* Schedule development
* Durations
* Staffing decisions
* Resource planning
* Project delivery strategy

---

### AI-Assisted, Not AI-Controlled

AI is used to accelerate scope review and planning activities.

The platform generates recommendations and draft WBS structures while preserving human review and decision-making.

---

### Structured Outputs

The system converts unstructured project documents into structured project data.

This structured approach enables future expansion without requiring major architectural changes.

---

### Separation of Concerns

Document processing, AI analysis, WBS generation, and export functionality are separated into dedicated components.

This improves maintainability and supports future enhancements.

---

### Future Scalability

The architecture is designed to support future capabilities including:

* Staffing recommendations
* Risk identification
* Proposal support
* Schedule support
* Microsoft Project integration
* Historical project analytics
* Organizational knowledge bases

without requiring significant restructuring of the codebase.
