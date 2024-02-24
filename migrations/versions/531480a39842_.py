"""empty message

Revision ID: 531480a39842
Revises: 7dc82f7cc2ba
Create Date: 2024-02-24 13:24:13.467314

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '531480a39842'
down_revision = '7dc82f7cc2ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inbox_rules', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=150), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inbox_rules', schema=None) as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###
