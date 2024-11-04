"""create sensor_readings_table

Revision ID: 9943741abfd8
Revises: 
Create Date: 2024-11-01 06:51:13.532484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9943741abfd8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sensor_readings',
        sa.Column('equipment_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('equipment_id', 'timestamp')
    )
    
    op.create_index('idx_equipment_timestamp', 'sensor_readings', ['equipment_id', 'timestamp'])
    op.create_index('idx_timestamp', 'sensor_readings', ['timestamp'])


def downgrade() -> None:
    op.drop_index('idx_timestamp')
    op.drop_index('idx_equipment_timestamp')
    op.drop_table('sensor_readings')
