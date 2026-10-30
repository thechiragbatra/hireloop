"""Create owner-scoped Hireloop records."""

import sqlalchemy as sa
from alembic import op

revision = "0001_create_records"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "hireloop_records"
    if not inspector.has_table(table_name):
        op.create_table(
            table_name,
            sa.Column("id", sa.String(length=255), nullable=False),
            sa.Column("kind", sa.String(length=32), nullable=False),
            sa.Column("owner_id", sa.String(length=255), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    indexes = {item["name"] for item in inspector.get_indexes(table_name)}
    if "ix_hireloop_records_kind" not in indexes:
        op.create_index("ix_hireloop_records_kind", table_name, ["kind"])
    if "ix_hireloop_records_owner_id" not in indexes:
        op.create_index("ix_hireloop_records_owner_id", table_name, ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_hireloop_records_owner_id", table_name="hireloop_records")
    op.drop_index("ix_hireloop_records_kind", table_name="hireloop_records")
    op.drop_table("hireloop_records")
