"""add review logs

Revision ID: 20260301_000004
Revises: 20260301_000003
Create Date: 2026-03-01 00:00:04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260301_000004"
down_revision: Union[str, None] = "20260301_000003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "review_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("word_id", sa.Integer(), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("prev_repetition", sa.Integer(), nullable=False),
        sa.Column("prev_interval", sa.Integer(), nullable=False),
        sa.Column("prev_ease_factor", sa.Float(), nullable=False),
        sa.Column("prev_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_repetition", sa.Integer(), nullable=False),
        sa.Column("next_interval", sa.Integer(), nullable=False),
        sa.Column("next_ease_factor", sa.Float(), nullable=False),
        sa.Column("next_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["word_id"], ["words.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_logs_id"), "review_logs", ["id"], unique=False)
    op.create_index(op.f("ix_review_logs_user_id"), "review_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_review_logs_word_id"), "review_logs", ["word_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_review_logs_word_id"), table_name="review_logs")
    op.drop_index(op.f("ix_review_logs_user_id"), table_name="review_logs")
    op.drop_index(op.f("ix_review_logs_id"), table_name="review_logs")
    op.drop_table("review_logs")

