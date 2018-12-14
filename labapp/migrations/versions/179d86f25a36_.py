"""empty message

Revision ID: 179d86f25a36
Revises: 44176926ed58
Create Date: 2018-12-13 14:33:15.863743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '179d86f25a36'
down_revision = '44176926ed58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recorder',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('uid', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('location_description', sa.String(length=100), nullable=True),
    sa.Column('current_series_uid', sa.String(length=36), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recorder_uid'), 'recorder', ['uid'], unique=True)
    op.create_table('recording_parameters',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('uid', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('samplerate', sa.Integer(), nullable=True),
    sa.Column('channels', sa.Integer(), nullable=True),
    sa.Column('duration', sa.Numeric(precision=10, scale=7, asdecimal=False), nullable=True),
    sa.Column('amplification', sa.Numeric(precision=10, scale=7, asdecimal=False), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uid')
    )
    op.create_table('series',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('uid', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('parameters_uid', sa.String(length=36), nullable=True),
    sa.Column('recorder_uid', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['parameters_uid'], ['recording_parameters.uid'], ),
    sa.ForeignKeyConstraint(['recorder_uid'], ['recorder.uid'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uid')
    )
    op.create_table('record',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('uid', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    sa.Column('filepath', sa.String(length=200), nullable=True),
    sa.Column('series_uid', sa.String(length=36), nullable=True),
    sa.Column('label_uid', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['label_uid'], ['label.uid'], ),
    sa.ForeignKeyConstraint(['series_uid'], ['series.uid'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('record')
    op.drop_table('series')
    op.drop_table('recording_parameters')
    op.drop_index(op.f('ix_recorder_uid'), table_name='recorder')
    op.drop_table('recorder')
    # ### end Alembic commands ###