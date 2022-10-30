"""create_tables

Revision ID: 32edd08dd080
Revises: 
Create Date: 2022-10-27 12:07:29.901611

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32edd08dd080'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.VARCHAR(128)),
        sa.Column('firstName', sa.VARCHAR(32)),
        sa.Column('lastName', sa.VARCHAR(32)),
        sa.Column('email', sa.VARCHAR(128)),
        sa.Column('password', sa.VARCHAR(128)),
        sa.Column('phone', sa.VARCHAR(32)),
        sa.Column('birthDate', sa.Date),
        sa.Column('userStatus', sa.Enum('0', '1'), default='1')
    )

    op.create_table(
        'classroom',
        sa.Column('id',sa.Integer,primary_key=True),
        sa.Column('name', sa.VARCHAR(128)),
        sa.Column('classroomStatus', sa.Enum('available', 'pending', 'unavailable'), default='available'),
        sa.Column('capacity', sa.Integer)
    )

    op.create_table(
        'order_table',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('classroomId', sa.Integer, sa.ForeignKey("classroom.id")),
        sa.Column('userId', sa.Integer, sa.ForeignKey("user.id")),
        sa.Column('start_time', sa.DateTime),
        sa.Column('end_time', sa.DateTime),
        sa.Column('status', sa.Enum('placed', 'approved', 'denied'), default='placed')
    )


def downgrade() -> None:
    op.drop_table('order_table')
    op.drop_table('user')
    op.drop_table('classroom')


