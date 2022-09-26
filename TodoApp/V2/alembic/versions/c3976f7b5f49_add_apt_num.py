"""add apt_num

Revision ID: c3976f7b5f49
Revises: 873ee8fe9334
Create Date: 2022-09-25 18:08:04.361658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3976f7b5f49"
down_revision = "873ee8fe9334"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("address", sa.Column("apt_num", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("address", "apt_num")
