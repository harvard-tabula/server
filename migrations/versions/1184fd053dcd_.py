"""empty message

Revision ID: 1184fd053dcd
Revises: 880f88839a57
Create Date: 2017-03-04 22:32:22.185647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1184fd053dcd'
down_revision = '880f88839a57'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('department',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name_long', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('course', sa.Column('course_id', sa.Integer(), nullable=True))
    op.add_column('course', sa.Column('department', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'course', 'department', ['department'], ['id'])
    op.drop_column('course', 'code')
    op.alter_column('user_history', 'user_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('user_profile', 'user_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_profile', 'user_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('user_history', 'user_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.add_column('course', sa.Column('code', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'course', type_='foreignkey')
    op.drop_column('course', 'department')
    op.drop_column('course', 'course_id')
    op.drop_table('department')
    # ### end Alembic commands ###
