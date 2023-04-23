"""Initial migration.

Revision ID: ef30cba0bb8c
Revises: d257cfd04645
Create Date: 2023-04-22 07:47:11.513398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef30cba0bb8c'
down_revision = 'd257cfd04645'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)

    op.create_table('message',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('sender_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('receiver_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['receiver_id'], ['user.id'], name='message_receiver_id_fkey'),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], name='message_sender_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='message_pkey')
    )
    # ### end Alembic commands ###