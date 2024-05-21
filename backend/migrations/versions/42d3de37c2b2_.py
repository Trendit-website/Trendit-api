"""empty message

Revision ID: 42d3de37c2b2
Revises: 6a1a1e0f7d52
Create Date: 2024-05-21 09:38:22.120345

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42d3de37c2b2'
down_revision = '6a1a1e0f7d52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Create the new ENUM type
    sociallinksstatus_enum = sa.Enum('IDLE', 'PENDING', 'VERIFIED', 'REJECTED', name='sociallinksstatus')
    sociallinksstatus_enum.create(op.get_bind())

    with op.batch_alter_table('pricing', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(length=250),
               nullable=True)

    # Alter columns with USING clause for the enum conversion
    op.execute("ALTER TABLE social_links ALTER COLUMN google_verified TYPE sociallinksstatus USING CASE WHEN google_verified THEN 'VERIFIED'::sociallinksstatus ELSE 'IDLE'::sociallinksstatus END")
    op.execute("ALTER TABLE social_links ALTER COLUMN facebook_verified TYPE sociallinksstatus USING CASE WHEN facebook_verified THEN 'VERIFIED'::sociallinksstatus ELSE 'IDLE'::sociallinksstatus END")
    op.execute("ALTER TABLE social_links ALTER COLUMN instagram_verified TYPE sociallinksstatus USING CASE WHEN instagram_verified THEN 'VERIFIED'::sociallinksstatus ELSE 'IDLE'::sociallinksstatus END")
    op.execute("ALTER TABLE social_links ALTER COLUMN tiktok_verified TYPE sociallinksstatus USING CASE WHEN tiktok_verified THEN 'VERIFIED'::sociallinksstatus ELSE 'IDLE'::sociallinksstatus END")
    op.execute("ALTER TABLE social_links ALTER COLUMN x_verified TYPE sociallinksstatus USING CASE WHEN x_verified THEN 'VERIFIED'::sociallinksstatus ELSE 'IDLE'::sociallinksstatus END")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Revert columns back to BOOLEAN
    op.execute("ALTER TABLE social_links ALTER COLUMN google_verified TYPE BOOLEAN USING CASE WHEN google_verified = 'VERIFIED' THEN TRUE ELSE FALSE END")
    op.execute("ALTER TABLE social_links ALTER COLUMN facebook_verified TYPE BOOLEAN USING CASE WHEN facebook_verified = 'VERIFIED' THEN TRUE ELSE FALSE END")
    op.execute("ALTER TABLE social_links ALTER COLUMN instagram_verified TYPE BOOLEAN USING CASE WHEN instagram_verified = 'VERIFIED' THEN TRUE ELSE FALSE END")
    op.execute("ALTER TABLE social_links ALTER COLUMN tiktok_verified TYPE BOOLEAN USING CASE WHEN tiktok_verified = 'VERIFIED' THEN TRUE ELSE FALSE END")
    op.execute("ALTER TABLE social_links ALTER COLUMN x_verified TYPE BOOLEAN USING CASE WHEN x_verified = 'VERIFIED' THEN TRUE ELSE FALSE END")

    with op.batch_alter_table('pricing', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(length=250),
               nullable=True)

    # Drop the ENUM type
    sociallinksstatus_enum = sa.Enum('IDLE', 'PENDING', 'VERIFIED', 'REJECTED', name='sociallinksstatus')
    sociallinksstatus_enum.drop(op.get_bind())
    # ### end Alembic commands ###
