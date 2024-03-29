"""fix tables

Revision ID: 17dd4042d158
Revises: 1a8d71183df5
Create Date: 2023-04-24 18:16:17.833396

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '17dd4042d158'
down_revision = '1a8d71183df5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner', sa.String(length=50), nullable=False),
    sa.Column('card_number', sa.String(length=50), nullable=False),
    sa.Column('cvv', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_discount',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('exchange_code', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('district', sa.String(length=50), nullable=False),
    sa.Column('address', sa.String(length=50), nullable=False),
    sa.Column('postal_code', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('User_Discount')
    op.drop_table('payments')
    op.drop_table('User_Location')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User_Location',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"User_Location_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('district', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('address', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('postal_code', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='User_Location_pkey')
    )
    op.create_table('payments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('owner', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('card_number', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('cvv', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='payments_pkey')
    )
    op.create_table('User_Discount',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"User_Discount_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('exchange_code', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='User_Discount_pkey')
    )
    op.drop_table('user_location')
    op.drop_table('user_discount')
    op.drop_table('payment')
    # ### end Alembic commands ###
