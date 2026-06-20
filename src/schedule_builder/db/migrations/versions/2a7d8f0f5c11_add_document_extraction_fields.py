"""Add extracted document fields.

Revision ID: 2a7d8f0f5c11
Revises: d49fe5886470
Create Date: 2026-06-20 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2a7d8f0f5c11"
down_revision = "d49fe5886470"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("page_count", sa.Integer(), nullable=True))
    op.add_column(
        "documents",
        sa.Column("extracted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("documents", sa.Column("extraction_error", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "extraction_error")
    op.drop_column("documents", "extracted_at")
    op.drop_column("documents", "page_count")
    op.drop_column("documents", "extracted_text")
