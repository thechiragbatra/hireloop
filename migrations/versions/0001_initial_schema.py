"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2025-10-25
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("data", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_profiles_user_id"), "profiles", ["user_id"], unique=False)

    op.create_table(
        "jobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("data", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_user_id"), "jobs", ["user_id"], unique=False)

    op.create_table(
        "applications",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("match_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(), nullable=False, server_default="saved"),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("resume_version", sa.String(), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_applications_user_id"), "applications", ["user_id"], unique=False)

    # Row Level Security policies
    op.execute("ALTER TABLE profiles ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE jobs ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE applications ENABLE ROW LEVEL SECURITY")

    op.execute(
        """
        CREATE POLICY profiles_user_isolation ON profiles
        FOR ALL USING (user_id = auth.uid() OR user_id IS NULL)
        """
    )
    op.execute(
        """
        CREATE POLICY jobs_user_isolation ON jobs
        FOR ALL USING (user_id = auth.uid() OR user_id IS NULL)
        """
    )
    op.execute(
        """
        CREATE POLICY applications_user_isolation ON applications
        FOR ALL USING (user_id = auth.uid() OR user_id IS NULL)
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS profiles_user_isolation ON profiles")
    op.execute("DROP POLICY IF EXISTS jobs_user_isolation ON jobs")
    op.execute("DROP POLICY IF EXISTS applications_user_isolation ON applications")
    op.drop_table("applications")
    op.drop_table("jobs")
    op.drop_table("profiles")
