"""create phone number for user col

Revision ID: a08d61bd1f9a
Revises: 
Create Date: 2022-09-24 20:33:46.663672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a08d61bd1f9a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("phone_number", sa.String(), nullable=True))


def downgrade():
    op.drop_column("users", "phone_number")
