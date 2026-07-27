"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-27

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')  # for gen_random_uuid()

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("github_handle", sa.String(100), nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("role", sa.Enum("user", "premium", "admin", name="user_role"), nullable=False, server_default="user"),
        sa.Column("ai_credits", sa.Integer, nullable=False, server_default="50"),
        sa.Column("is_email_verified", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("is_banned", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("oauth_provider", sa.String(20), nullable=True),
        sa.Column("oauth_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("oauth_provider", "oauth_id", name="uq_users_oauth_identity"),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_username", "users", ["username"])

    # --- projects ---
    op.create_table(
        "projects",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("platform", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_projects_user_id", "projects", ["user_id"])

    # --- writeups ---
    op.create_table(
        "writeups",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", pg.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("file_type", sa.Enum("md", "pdf", "txt", "docx", name="file_type"), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=False),
        sa.Column("raw_content", sa.Text, nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "completed", "failed", name="writeup_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "visibility",
            sa.Enum("private", "public", name="writeup_visibility"),
            nullable=False,
            server_default="private",
        ),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("platform", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_writeups_user_id", "writeups", ["user_id"])
    op.create_index("idx_writeups_project_id", "writeups", ["project_id"])
    op.create_index("idx_writeups_status", "writeups", ["status"])
    op.create_index("idx_writeups_visibility", "writeups", ["visibility"])
    op.create_index("idx_writeups_created_at", "writeups", ["created_at"])
    op.execute(
        "CREATE INDEX idx_writeups_raw_content_fts ON writeups "
        "USING GIN (to_tsvector('english', coalesce(raw_content, '')))"
    )

    # --- summaries ---
    op.create_table(
        "summaries",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("writeup_id", pg.UUID(as_uuid=True), sa.ForeignKey("writeups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("executive_summary", sa.Text, nullable=True),
        sa.Column("vulnerability_type", sa.Text, nullable=True),
        sa.Column("exploitation_steps", sa.Text, nullable=True),
        sa.Column("detection_opportunities", sa.Text, nullable=True),
        sa.Column("blue_team_perspective", sa.Text, nullable=True),
        sa.Column("red_team_perspective", sa.Text, nullable=True),
        sa.Column("prevention", sa.Text, nullable=True),
        sa.Column("technologies_used", pg.JSONB, nullable=True),
        sa.Column("owasp_mappings", pg.JSONB, nullable=True),
        sa.Column("similar_htb_machines", pg.JSONB, nullable=True),
        sa.Column("similar_thm_rooms", pg.JSONB, nullable=True),
        sa.Column("interview_questions", pg.JSONB, nullable=True),
        sa.Column("learning_roadmap", sa.Text, nullable=True),
        sa.Column("important_notes", sa.Text, nullable=True),
        sa.Column("llm_provider_used", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("writeup_id", name="uq_summaries_writeup_id"),
    )
    op.create_index("idx_summaries_technologies_used", "summaries", ["technologies_used"], postgresql_using="gin")

    # --- techniques ---
    op.create_table(
        "techniques",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("writeup_id", pg.UUID(as_uuid=True), sa.ForeignKey("writeups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("evidence_snippet", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="ck_techniques_confidence_range"),
    )
    op.create_index("idx_techniques_writeup_id", "techniques", ["writeup_id"])
    op.create_index("idx_techniques_name", "techniques", ["name"])

    # --- commands ---
    op.create_table(
        "commands",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("writeup_id", pg.UUID(as_uuid=True), sa.ForeignKey("writeups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("command_text", sa.Text, nullable=False),
        sa.Column("tool_name", sa.String(100), nullable=True),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("sequence_order", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_index("idx_commands_writeup_id", "commands", ["writeup_id"])

    # --- mitre_mappings ---
    op.create_table(
        "mitre_mappings",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("writeup_id", pg.UUID(as_uuid=True), sa.ForeignKey("writeups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("technique_id", pg.UUID(as_uuid=True), sa.ForeignKey("techniques.id", ondelete="CASCADE"), nullable=True),
        sa.Column("mitre_technique_id", sa.String(20), nullable=False),
        sa.Column("mitre_tactic", sa.String(100), nullable=True),
        sa.Column("mitre_technique_name", sa.String(200), nullable=True),
    )
    op.create_index("idx_mitre_writeup_id", "mitre_mappings", ["writeup_id"])
    op.create_index("idx_mitre_technique_id", "mitre_mappings", ["mitre_technique_id"])

    # --- cves (decision #10: dedicated table, not JSONB) ---
    op.create_table(
        "cves",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("cve_id", sa.String(30), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("severity_score", sa.Float, nullable=True),
        sa.Column("severity_label", sa.String(20), nullable=True),
        sa.Column("published_date", sa.Date, nullable=True),
        sa.Column("reference_urls", pg.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("cve_id", name="uq_cves_cve_id"),
    )
    op.create_index("idx_cves_cve_id", "cves", ["cve_id"])

    op.create_table(
        "writeup_cves",
        sa.Column("writeup_id", pg.UUID(as_uuid=True), sa.ForeignKey("writeups.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("cve_id", pg.UUID(as_uuid=True), sa.ForeignKey("cves.id", ondelete="CASCADE"), primary_key=True),
    )

    # --- learning_paths ---
    op.create_table(
        "learning_paths",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("ordered_topics", pg.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_learning_paths_user_id", "learning_paths", ["user_id"])

    # --- flashcards ---
    op.create_table(
        "flashcards",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("writeup_id", pg.UUID(as_uuid=True), sa.ForeignKey("writeups.id", ondelete="CASCADE"), nullable=True),
        sa.Column(
            "learning_path_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("learning_paths.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.CheckConstraint(
            "writeup_id IS NOT NULL OR learning_path_id IS NOT NULL", name="ck_flashcards_has_parent"
        ),
    )
    op.create_index("idx_flashcards_writeup_id", "flashcards", ["writeup_id"])
    op.create_index("idx_flashcards_learning_path_id", "flashcards", ["learning_path_id"])

    # --- flashcard_reviews ---
    op.create_table(
        "flashcard_reviews",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("flashcard_id", pg.UUID(as_uuid=True), sa.ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ease_factor", sa.Integer, nullable=False, server_default="250"),
        sa.Column("interval_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("flashcard_id", "user_id", name="uq_flashcard_review_per_user"),
    )
    op.create_index("idx_flashcard_reviews_next_review", "flashcard_reviews", ["next_review_at"])

    # --- quizzes ---
    op.create_table(
        "quizzes",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("writeup_id", pg.UUID(as_uuid=True), sa.ForeignKey("writeups.id", ondelete="CASCADE"), nullable=True),
        sa.Column(
            "learning_path_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("learning_paths.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("mode", sa.Enum("quiz", "exam", name="quiz_mode"), nullable=False, server_default="quiz"),
        sa.Column("questions", pg.JSONB, nullable=False),
    )
    op.create_index("idx_quizzes_writeup_id", "quizzes", ["writeup_id"])
    op.create_index("idx_quizzes_learning_path_id", "quizzes", ["learning_path_id"])

    # --- quiz_attempts ---
    op.create_table(
        "quiz_attempts",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("quiz_id", pg.UUID(as_uuid=True), sa.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("answers", pg.JSONB, nullable=False),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_quiz_attempts_score_range"),
    )
    op.create_index("idx_quiz_attempts_user_id", "quiz_attempts", ["user_id"])
    op.create_index("idx_quiz_attempts_quiz_id", "quiz_attempts", ["quiz_id"])

    # --- history ---
    op.create_table(
        "history",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("writeup_id", pg.UUID(as_uuid=True), sa.ForeignKey("writeups.id", ondelete="CASCADE"), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_history_user_id", "history", ["user_id"])
    op.create_index("idx_history_created_at", "history", ["created_at"])

    # --- bookmarks ---
    op.create_table(
        "bookmarks",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "entity_type",
            sa.Enum("writeup", "flashcard", "learning_path", name="bookmark_entity_type"),
            nullable=False,
        ),
        sa.Column("entity_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "entity_type", "entity_id", name="uq_bookmark_per_entity"),
    )

    # --- notifications ---
    op.create_table(
        "notifications",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_notifications_user_id_is_read", "notifications", ["user_id", "is_read"])

    # --- subscriptions (Stripe-ready, decision #12) ---
    op.create_table(
        "subscriptions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan", sa.Enum("free", "premium", name="subscription_plan"), nullable=False, server_default="free"),
        sa.Column(
            "status",
            sa.Enum("active", "canceled", "past_due", name="subscription_status"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_subscriptions_user_id"),
    )

    # --- api_keys ---
    op.create_table(
        "api_keys",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False),
        sa.Column("label", sa.String(100), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("key_hash", name="uq_api_keys_key_hash"),
    )
    op.create_index("idx_api_keys_user_id", "api_keys", ["user_id"])

    # --- sessions ---
    op.create_table(
        "sessions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("refresh_token_hash", sa.String(255), nullable=False),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("refresh_token_hash", name="uq_sessions_refresh_token_hash"),
    )
    op.create_index("idx_sessions_user_id", "sessions", ["user_id"])
    op.create_index("idx_sessions_refresh_token_hash", "sessions", ["refresh_token_hash"])

    # --- chat_messages ---
    op.create_table(
        "chat_messages",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("writeup_id", pg.UUID(as_uuid=True), sa.ForeignKey("writeups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Enum("user", "assistant", name="chat_role"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_chat_messages_writeup_id_created_at", "chat_messages", ["writeup_id", "created_at"])


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("sessions")
    op.drop_table("api_keys")
    op.drop_table("subscriptions")
    op.drop_table("notifications")
    op.drop_table("bookmarks")
    op.drop_table("history")
    op.drop_table("quiz_attempts")
    op.drop_table("quizzes")
    op.drop_table("flashcard_reviews")
    op.drop_table("flashcards")
    op.drop_table("learning_paths")
    op.drop_table("writeup_cves")
    op.drop_table("cves")
    op.drop_table("mitre_mappings")
    op.drop_table("commands")
    op.drop_table("techniques")
    op.drop_table("summaries")
    op.drop_table("writeups")
    op.drop_table("projects")
    op.drop_table("users")

    for enum_name in [
        "chat_role",
        "subscription_status",
        "subscription_plan",
        "bookmark_entity_type",
        "quiz_mode",
        "writeup_visibility",
        "writeup_status",
        "file_type",
        "user_role",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
