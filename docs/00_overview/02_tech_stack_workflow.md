# Technology Stack and Workflow

## Technology Philosophy

The MVP is designed to solve a narrowly defined problem:

> Convert engineering scope documents into a structured Work Breakdown Structure (WBS).

The technology stack should prioritize simplicity, maintainability, rapid development, and reliable document processing.

The MVP is not intended to be a full scheduling platform, project management system, or project analytics platform. The initial implementation should focus on document ingestion, scope analysis, and WBS generation.

---

# Proposed Technology Stack

## Programming Language

### Python

Python is selected as the primary development language due to:

* Strong document processing ecosystem
* Excellent AI and LLM integration support
* Rapid development capabilities
* Extensive data processing libraries
* Future compatibility with analytics and machine learning workflows

---

## AI Layer

### Primary Option: Claude API

Potential uses:

* Scope analysis
* Requirement extraction
* Deliverable identification
* Discipline identification
* WBS generation

Advantages:

* Strong performance with long-form documents
* Structured output generation
* Effective hierarchical reasoning
* High-quality document summarization

---

### Secondary Option: OpenAI API

Potential uses:

* WBS generation
* Scope summarization
* Future planning features

Maintaining support for multiple providers may reduce vendor dependency and allow future benchmarking.

---

## Document Processing

### PyMuPDF

Primary PDF processing library.

Responsibilities:

* PDF text extraction
* Page-level processing
* Metadata extraction

Advantages:

* Fast performance
* Reliable text extraction
* Strong support for engineering documents

---

### python-docx

Used for processing Microsoft Word documents.

Responsibilities:

* Scope extraction
* Proposal document ingestion

---

### OCR Support (Future Enhancement)

Potential tools:

* Tesseract OCR
* Azure Document Intelligence
* Amazon Textract

These capabilities may support scanned documents and image-based RFPs in future releases.

---

## Data Validation

### Pydantic

Used to validate:

* Extracted scope information
* AI responses
* WBS structures
* Project metadata

Example:

```text
Uploaded Scope Document
        ↓
Extracted Tasks
        ↓
Pydantic Validation
        ↓
Structured WBS Object
```

This reduces the risk of malformed AI responses entering the workflow.

---

## Data Storage

### MVP Approach

No database required.

Project data may be stored as:

* JSON files
* Markdown files
* CSV exports

This simplifies development and deployment.

---

### Future Approach

Potential migration to:

* PostgreSQL
* SQLite (development)

once project history and analytics capabilities are introduced.

---

## Output Generation

### Markdown

Primary human-readable output format.

Advantages:

* Easy review
* Easy editing
* Git-friendly
* Lightweight

---

### CSV

Used for:

* Spreadsheet import
* Schedule preparation
* Data exchange

---

### JSON

Used for:

* Structured system outputs
* API responses
* Future integrations

---

# High-Level Workflow

## Step 1 - Upload Document

The user uploads:

* PDF
* DOCX
* TXT

Example:

```text
Force Main Design RFP.pdf
```

---

## Step 2 - Extract Text

Document processing services extract text from the uploaded file.

Example:

```text
Consultant shall provide:

• Survey
• Utility Coordination
• Geotechnical Investigation
• ERP Permitting
• Preliminary Design
• 60% Design
• 90% Design
• Final Design
```

---

## Step 3 - Scope Analysis

The extracted text is sent to the LLM.

The AI evaluates:

* Project type
* Scope elements
* Deliverables
* Required disciplines
* Meetings
* Permits
* Coordination requirements

Example output:

```json
{
  "project_type": "force_main",
  "deliverables": [
    "survey",
    "geotechnical_report",
    "design_plans"
  ],
  "disciplines": [
    "civil",
    "survey",
    "geotechnical"
  ]
}
```

---

## Step 4 - WBS Generation

The AI generates a structured WBS.

Example:

```text
1.0 Project Management

2.0 Data Collection

    2.1 Survey
    2.2 Utility Coordination

3.0 Geotechnical Services

4.0 Design

    4.1 Preliminary Design
    4.2 60% Design
    4.3 90% Design
    4.4 Final Design
```

---

## Step 5 - Validation

System validation verifies:

* Proper WBS numbering
* Hierarchical structure
* Required sections
* Consistent formatting

Potential future rules:

* Project Management section required
* Design section required
* Deliverables mapped correctly

---

## Step 6 - Output Generation

The final outputs are generated.

### Scope Summary

Project description.

### Discipline List

Required disciplines.

### Deliverable List

Required deliverables.

### WBS

Primary project output.

---

## Step 7 - Export

Outputs are exported as:

* Markdown
* CSV
* JSON

for use by engineers and project managers.

---

# Future Workflow Evolution

## Version 0.2

### Discipline Recommendations

```text
Scope
    ↓
WBS
    ↓
Recommended Disciplines
```

---

## Version 0.3

### Risk Identification

```text
Scope
    ↓
WBS
    ↓
Risk Identification
```

---

## Version 0.4

### Schedule Support

```text
Scope
    ↓
WBS
    ↓
Schedule Framework
```

---

## Version 0.5

### Microsoft Project Integration

```text
Scope
    ↓
WBS
    ↓
Project XML Export
```

---

# Architecture Principles

The MVP should follow several guiding principles:

## Engineer-in-the-Loop

The system assists engineers but does not replace engineering judgment.

Engineers remain responsible for:

* Schedule development
* Durations
* Staffing
* Resource planning
* Project strategy

---

## AI-Assisted, Not AI-Controlled

The AI generates recommendations and draft WBS structures.

Final decisions remain with the user.

---

## Deterministic Outputs

Where possible, outputs should be validated and structured to ensure repeatable and reliable results.

---

## Incremental Growth

The architecture should support future additions including:

* Staffing recommendations
* Risk identification
* Schedule support
* Analytics
* Historical project knowledge bases

without requiring significant restructuring of the codebase.
