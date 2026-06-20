"""create initial mvp schema

Revision ID: d49fe5886470
Revises:
Create Date: 2026-06-19 23:50:45.496721

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d49fe5886470"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("users_email_lower_uk", "users", [sa.text("lower(email)")], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=32), server_default=sa.text("'draft'"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_projects"),
    )
    op.create_index("projects_owner_user_id_idx", "projects", ["owner_user_id"], unique=False)
    op.create_index("projects_status_idx", "projects", ["status"], unique=False)

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column(
            "processing_status",
            sa.String(length=32),
            server_default=sa.text("'uploaded'"),
            nullable=False,
        ),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
    )
    op.create_index("documents_project_id_idx", "documents", ["project_id"], unique=False)
    op.create_index(
        "documents_processing_status_idx", "documents", ["processing_status"], unique=False
    )

    op.create_table(
        "scope_analyses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("scope_json", sa.JSON(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_scope_analyses"),
        sa.UniqueConstraint("document_id", name="uq_scope_analyses_document_id"),
    )
    op.create_index(
        "scope_analyses_document_id_idx", "scope_analyses", ["document_id"], unique=False
    )

    op.create_table(
        "wbs_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("source_document_id", sa.String(length=36), nullable=True),
        sa.Column(
            "generation_status",
            sa.String(length=32),
            server_default=sa.text("'generated'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_wbs_runs"),
    )
    op.create_index("wbs_runs_project_id_idx", "wbs_runs", ["project_id"], unique=False)
    op.create_index(
        "wbs_runs_generation_status_idx", "wbs_runs", ["generation_status"], unique=False
    )

    op.create_table(
        "wbs_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("wbs_run_id", sa.String(length=36), nullable=False),
        sa.Column("wbs_number", sa.String(length=24), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("parent_wbs_number", sa.String(length=24), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("level IN (1, 2)", name="ck_wbs_items_level_mvp"),
        sa.ForeignKeyConstraint(["wbs_run_id"], ["wbs_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_wbs_items"),
        sa.UniqueConstraint("wbs_run_id", "wbs_number", name="uq_wbs_items_run_number"),
    )
    op.create_index("wbs_items_wbs_run_id_idx", "wbs_items", ["wbs_run_id"], unique=False)
    op.create_index(
        "wbs_items_sort_order_idx", "wbs_items", ["wbs_run_id", "sort_order"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("wbs_items_sort_order_idx", table_name="wbs_items")
    op.drop_index("wbs_items_wbs_run_id_idx", table_name="wbs_items")
    op.drop_table("wbs_items")

    op.drop_index("wbs_runs_generation_status_idx", table_name="wbs_runs")
    op.drop_index("wbs_runs_project_id_idx", table_name="wbs_runs")
    op.drop_table("wbs_runs")

    op.drop_index("scope_analyses_document_id_idx", table_name="scope_analyses")
    op.drop_table("scope_analyses")

    op.drop_index("documents_processing_status_idx", table_name="documents")
    op.drop_index("documents_project_id_idx", table_name="documents")
    op.drop_table("documents")

    op.drop_index("projects_status_idx", table_name="projects")
    op.drop_index("projects_owner_user_id_idx", table_name="projects")
    op.drop_table("projects")

    op.drop_index("users_email_lower_uk", table_name="users")
    op.drop_table("users")
