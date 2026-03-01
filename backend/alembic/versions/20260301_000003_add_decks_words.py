"""add decks and words

Revision ID: 20260301_000003
Revises: 20260301_000002
Create Date: 2026-03-01 00:00:03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260301_000003"
down_revision: Union[str, None] = "20260301_000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "decks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_decks_id"), "decks", ["id"], unique=False)
    op.create_index(op.f("ix_decks_user_id"), "decks", ["user_id"], unique=False)

    op.create_table(
        "words",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("deck_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("word", sa.String(length=255), nullable=False),
        sa.Column("definition", sa.Text(), nullable=True),
        sa.Column("ease_factor", sa.Float(), server_default="2.5", nullable=False),
        sa.Column("interval", sa.Integer(), server_default="0", nullable=False),
        sa.Column("repetition", sa.Integer(), server_default="0", nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["deck_id"], ["decks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_words_deck_id"), "words", ["deck_id"], unique=False)
    op.create_index(op.f("ix_words_id"), "words", ["id"], unique=False)
    op.create_index(op.f("ix_words_user_id"), "words", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_words_user_id"), table_name="words")
    op.drop_index(op.f("ix_words_id"), table_name="words")
    op.drop_index(op.f("ix_words_deck_id"), table_name="words")
    op.drop_table("words")

    op.drop_index(op.f("ix_decks_user_id"), table_name="decks")
    op.drop_index(op.f("ix_decks_id"), table_name="decks")
    op.drop_table("decks")

