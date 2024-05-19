from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd47374a6e1d8'
down_revision = '35998805e3fe'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('driver') as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('number_of_ratings', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rating', sa.Float(), nullable=True))

def downgrade():
    with op.batch_alter_table('driver') as batch_op:
        batch_op.drop_column('rating')
        batch_op.drop_column('number_of_ratings')
        batch_op.drop_column('status')
