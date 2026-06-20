# Alembic Initial Migration Spec - MVP Schema

## Purpose

This document provides the concrete migration specification for the initial database setup described in [docs/05_database/00_schema.md](docs/05_database/00_schema.md).

It includes:
- Alembic bootstrap steps
- Required Alembic config wiring
- Initial revision structure
- Ordered DDL operations for upgrade and downgrade

---

## Target State

After applying this migration, the database should include:
- `users`
- `projects`
- `documents`
- `scope_analyses`
- `wbs_runs`
- `wbs_items`

With all primary keys, foreign keys, uniqueness, checks, and indexes from the MVP schema.

---

## Prerequisites

- SQLAlchemy and Alembic already present in dependencies
- Runtime settings include `database_url` in [src/schedule_builder/config/settings.py](src/schedule_builder/config/settings.py)
- Base metadata will be defined in:
  - [src/schedule_builder/db/base.py](src/schedule_builder/db/base.py)
  - [src/schedule_builder/models/base.py](src/schedule_builder/models/base.py)

---

## Bootstrap Commands

Run from repository root:

```bash
uv run alembic init src/schedule_builder/db/migrations
```

Expected generated files:
- `alembic.ini`
- `src/schedule_builder/db/migrations/env.py`
- `src/schedule_builder/db/migrations/script.py.mako`
- `src/schedule_builder/db/migrations/versions/`

---

## Alembic Config Wiring

## 1) alembic.ini

Set script location to project path:

- `script_location = src/schedule_builder/db/migrations`

Leave `sqlalchemy.url` empty or placeholder if `env.py` injects URL from app settings.

## 2) env.py

In `src/schedule_builder/db/migrations/env.py`, wire:

- `from schedule_builder.config.settings import settings`
- `from schedule_builder.db.base import Base`
- `target_metadata = Base.metadata`
- In online mode, use `settings.database_url`

Goal: one source of truth for DB URL from app config.

---

## Initial Revision Metadata

Create revision after models are defined:

```bash
uv run alembic revision -m "create initial mvp schema"
```

Revision header template:

```python
"""create initial mvp schema

Revision ID: 0001_initial_mvp_schema
Revises:
Create Date: YYYY-MM-DD HH:MM:SS
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_mvp_schema"
down_revision = None
branch_labels = None
depends_on = None
```

---

## Upgrade Operations (Exact Order)

## 1) Create `users`

- `id` UUID PK
- `email` VARCHAR(254) NOT NULL
- `full_name` VARCHAR(120) NOT NULL
- `password_hash` TEXT NOT NULL
- `is_active` BOOLEAN NOT NULL server default true
- `created_at`, `updated_at` TIMESTAMPTZ NOT NULL server default now()

Add constraints/indexes:
- PK on `id`
- Unique index on `lower(email)` for case-insensitive uniqueness

Implementation note:
- Use `op.create_index(..., [sa.text("lower(email)")], unique=True)` for PostgreSQL.

## 2) Create `projects`

- FK `owner_user_id -> users.id ON DELETE CASCADE`
- Add indexes:
  - `projects_owner_user_id_idx`
  - `projects_status_idx`

## 3) Create `documents`

- FK `project_id -> projects.id ON DELETE CASCADE`
- Add indexes:
  - `documents_project_id_idx`
  - `documents_processing_status_idx`

## 4) Create `scope_analyses`

- FK `document_id -> documents.id ON DELETE CASCADE`
- `document_id` should be unique (one analysis row per document in MVP)
- `scope_json` should be JSONB on PostgreSQL

Add indexes:
- `scope_analyses_document_id_idx`
- GIN index on `scope_json` (`scope_analyses_scope_json_gin`)

## 5) Create `wbs_runs`

- FK `project_id -> projects.id ON DELETE CASCADE`
- FK `source_document_id -> documents.id ON DELETE SET NULL`
- Add indexes:
  - `wbs_runs_project_id_idx`
  - `wbs_runs_generation_status_idx`

## 6) Create `wbs_items`

- FK `wbs_run_id -> wbs_runs.id ON DELETE CASCADE`
- Unique constraint on `(wbs_run_id, wbs_number)`
- Check constraint `level IN (1, 2)`

Add indexes:
- `wbs_items_wbs_run_id_idx`
- `wbs_items_sort_order_idx` on `(wbs_run_id, sort_order)`

---

## Downgrade Operations (Reverse Order)

Drop in this order to satisfy FK dependencies:

1. `wbs_items`
2. `wbs_runs`
3. `scope_analyses`
4. `documents`
5. `projects`
6. `users`

Also drop named indexes and constraints if created separately.

---

## Example Upgrade Skeleton

```python
def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("users_email_lower_uk", "users", [sa.text("lower(email)")], unique=True)

    # create projects
    # create documents
    # create scope_analyses
    # create wbs_runs
    # create wbs_items
```

---

## Validation Checklist for Migration PR

- `uv run alembic upgrade head` succeeds on local DB
- `uv run alembic downgrade -1` succeeds
- `uv run alembic upgrade head` succeeds again (idempotent migration path)
- All expected tables and indexes exist
- Unique lowercased email constraint works
- FK delete behavior matches spec (`CASCADE`/`SET NULL`)

---

## Notes on Auth Integration

When moving auth from in-memory service to DB-backed service:

- `register_user` writes to `users`
- `login_user` queries by normalized email (lowercased)
- `get_current_user` resolves `sub` claim to `users.id`
- Continue using Argon2 hash utility from [src/schedule_builder/utils/hashing.py](src/schedule_builder/utils/hashing.py)

This keeps API behavior unchanged while introducing persistence.
