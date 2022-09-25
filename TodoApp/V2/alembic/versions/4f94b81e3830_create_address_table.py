"""create address table

Revision ID: 4f94b81e3830
Revises: a08d61bd1f9a
Create Date: 2022-09-24 21:05:07.519519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4f94b81e3830"
down_revision = "a08d61bd1f9a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "address",
        sa.Column("id", sa.Integer(), nullable=True, primary_key=True),
        sa.Column("address1", sa.String(), nullable=False),
        sa.Column("address2", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("postcalcode", sa.String(), nullable=False),
    )


def downgrade():
    pass
