"""dummy migration"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b58c4dc79f6a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
