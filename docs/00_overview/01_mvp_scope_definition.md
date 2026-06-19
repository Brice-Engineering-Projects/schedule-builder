# MVP Scope Definition

## Purpose

The Schedule Builder MVP is designed to assist engineering consultants, project managers, and proposal teams by converting project scope documents into a structured Work Breakdown Structure (WBS).

The system analyzes project requirements contained within RFPs, RFQs, scope documents, and similar project planning materials and generates a draft WBS suitable for schedule development.

The MVP is intended to accelerate the project planning process by reducing the manual effort required to review scope documents and organize project activities.

The generated WBS serves as a starting point for engineers and project managers who will ultimately develop the project schedule using their professional judgment.

---

# Problem Statement

Proposal teams frequently spend significant effort reviewing project documents and manually translating scope requirements into a project WBS.

This process often involves:

* Reviewing lengthy RFP documents
* Identifying project deliverables
* Identifying required disciplines
* Identifying permitting requirements
* Identifying meetings and coordination activities
* Organizing tasks into a logical WBS structure

The process is repetitive, time-consuming, and highly dependent on individual experience.

The MVP seeks to automate the initial scope analysis and WBS generation process while leaving schedule development decisions to the engineer.

---

# Primary Objective

Generate a structured WBS from project scope documents.

The generated WBS should provide a strong foundation for schedule development and proposal planning.

The objective is not to replace engineering judgment but to reduce the time required to organize project scope information into a usable project framework.

---

# User Workflow

## Step 1 – Upload Project Document

The user uploads a project document.

Supported formats:

* PDF
* DOCX
* TXT

Future versions may support:

* Images
* Scanned documents
* Multi-document project packages

---

## Step 2 – Scope Extraction

The system extracts project scope information from the uploaded document.

Examples include:

* Scope of services
* Deliverables
* Design milestones
* Meetings
* Coordination requirements
* Permitting requirements
* Agency requirements

---

## Step 3 – Scope Analysis

The AI engine analyzes the extracted project information and identifies:

### Deliverables

Examples:

* Survey
* Plans
* Specifications
* Reports

### Services

Examples:

* Survey
* SUE
* Geotechnical
* Environmental
* Engineering Design

### Meetings

Examples:

* Kickoff Meeting
* Progress Meetings
* Workshops
* Stakeholder Meetings

### Permits

Examples:

* ERP
* USACE
* Right-of-Way
* Utility Permits

### Disciplines

Examples:

* Project Management
* Civil Engineering
* Survey
* Environmental
* Geotechnical
* CAD

---

## Step 4 – WBS Generation

The system generates a hierarchical WBS.

Example:

```text
1.0 Project Management

    1.1 Kickoff Meeting
    1.2 Progress Meetings

2.0 Data Collection

    2.1 Survey
    2.2 Utility Coordination

3.0 Geotechnical Services

    3.1 Investigation
    3.2 Report

4.0 Environmental Services

    4.1 Permitting

5.0 Design

    5.1 Preliminary Design
    5.2 60% Design
    5.3 90% Design
    5.4 Final Design

6.0 Procurement Support

    6.1 Bid Phase Services
```

---

# MVP Outputs

For each uploaded document, the system generates:

## WBS

Primary deliverable.

A structured WBS suitable for project planning and schedule development.

---

## Scope Summary

A concise summary of the project scope.

Example:

```text
24-inch force main replacement project including
survey, geotechnical investigation, environmental
permitting, engineering design, and bid support.
```

---

## Discipline Identification

Example:

```text
Project Management
Civil Engineering
Survey
Environmental
Geotechnical
CAD
```

---

## Deliverable Identification

Example:

```text
Survey
Geotechnical Report
Permit Applications
Construction Plans
Specifications
Bid Documents
```

---

# Explicitly Out of Scope

The following features are intentionally excluded from the MVP.

## Duration Generation

The MVP will not generate task durations.

Duration determination requires project-specific engineering judgment and depends on:

* Project complexity
* Client requirements
* Regulatory agencies
* Staffing availability
* Delivery approach

Duration development remains the responsibility of the engineer or project manager.

---

## Schedule Logic

The MVP will not generate:

* Predecessors
* Successors
* Critical path logic
* Schedule sequencing

These decisions remain the responsibility of the project team.

---

## Schedule Creation

The MVP will not create:

* Microsoft Project schedules
* Primavera schedules
* Gantt charts

The generated WBS serves as the foundation for subsequent schedule development.

---

## Staffing Estimates

The MVP will not estimate:

* Labor hours
* Staffing levels
* Resource loading

---

## Cost Estimation

The MVP will not generate:

* Fee estimates
* Cost estimates
* Budget information

---

## Risk Analysis

The MVP will not generate:

* Risk registers
* Risk scoring
* Contingency recommendations

These features may be added in future releases.

---

# Success Criteria

The MVP will be considered successful if it can:

* Extract project scope information from engineering project documents.
* Generate a logical and structured WBS.
* Correctly identify major project phases.
* Correctly identify primary project deliverables.
* Correctly identify major disciplines.
* Reduce the time required to develop a project WBS.

Target performance:

* Identify at least 80% of major project tasks.
* Produce a WBS requiring only minor editing.
* Generate results in less than two minutes.

---

# Technical Scope

## Backend

* Python

## AI Layer

* Claude API and/or OpenAI API

## Document Processing

* PyMuPDF
* pdfplumber
* python-docx

## Output Formats

* Markdown
* TXT
* CSV
* JSON

---

# Future Enhancements

## Version 0.2

* Staffing recommendations
* Discipline mapping

## Version 0.3

* Risk register generation

## Version 0.4

* Schedule logic recommendations

## Version 0.5

* Microsoft Project XML export

## Version 0.6

* Proposal narrative generation

## Version 1.0

* Full project planning and schedule support platform
