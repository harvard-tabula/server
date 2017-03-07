"""empty message

Revision ID: 45bfc6421311
Revises: 2f91c2bb4ef1
Create Date: 2017-03-07 19:47:31.824393

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45bfc6421311'
down_revision = '2f91c2bb4ef1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('category', sa.String(length=20), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tags',
    sa.Column('user_profile_id', sa.Integer(), nullable=True),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['user_profile_id'], ['user_profile.id'], )
    )
    op.drop_table('milestones')
    op.drop_table('milestone')
    op.drop_table('interest')
    op.drop_table('interests')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('interests',
    sa.Column('user_profile_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('interest_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['interest_id'], ['interest.id'], name='interests_interest_id_fkey'),
    sa.ForeignKeyConstraint(['user_profile_id'], ['user_profile.id'], name='interests_user_profile_id_fkey')
    )
    op.create_table('interest',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='interest_pkey'),
    sa.UniqueConstraint('name', name='interest_name_key')
    )
    op.create_table('milestone',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('milestone_id_seq'::regclass)"), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='milestone_pkey'),
    sa.UniqueConstraint('name', name='milestone_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('milestones',
    sa.Column('milestone_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_profile_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['milestone_id'], ['milestone.id'], name='milestones_milestone_id_fkey'),
    sa.ForeignKeyConstraint(['user_profile_id'], ['user_profile.id'], name='milestones_user_profile_id_fkey')
    )
    op.drop_table('tags')
    op.drop_table('tag')
    # ### end Alembic commands ###
