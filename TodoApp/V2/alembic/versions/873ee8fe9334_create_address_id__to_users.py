"""create address_id_ to users

Revision ID: 873ee8fe9334
Revises: 4f94b81e3830
Create Date: 2022-09-24 21:20:56.653382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "873ee8fe9334"
down_revision = "4f94b81e3830"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("address_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "address_users_fk",
        source_table="users",
        referent_table="address",
        local_cols=["address_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint("address_users_fk", table_name="users")
    op.drop_column("users", "address_id")
