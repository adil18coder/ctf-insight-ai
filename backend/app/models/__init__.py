"""
Import every model here. Alembic's env.py imports this module (not individual
model files) so `Base.metadata` always reflects the complete schema — a model
file that isn't imported here is invisible to autogenerate and will silently
never get a migration.
"""
from app.models.api_key import APIKey
from app.models.bookmark import Bookmark, BookmarkEntityType
from app.models.chat_message import ChatMessage, ChatRole
from app.models.command import Command
from app.models.cve import CVE, WriteUpCVE
from app.models.flashcard import Flashcard
from app.models.flashcard_review import FlashcardReview
from app.models.history import History
from app.models.learning_path import LearningPath
from app.models.mitre import MitreMapping
from app.models.notification import Notification
from app.models.project import Project
from app.models.quiz import Quiz, QuizMode
from app.models.quiz_attempt import QuizAttempt
from app.models.session import Session
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.summary import Summary
from app.models.technique import Technique
from app.models.user import User, UserRole
from app.models.writeup import FileType, Visibility, WriteUp, WriteUpStatus

__all__ = [
    "APIKey",
    "Bookmark",
    "BookmarkEntityType",
    "ChatMessage",
    "ChatRole",
    "Command",
    "CVE",
    "WriteUpCVE",
    "Flashcard",
    "FlashcardReview",
    "History",
    "LearningPath",
    "MitreMapping",
    "Notification",
    "Project",
    "Quiz",
    "QuizMode",
    "QuizAttempt",
    "Session",
    "Subscription",
    "SubscriptionPlan",
    "SubscriptionStatus",
    "Summary",
    "Technique",
    "User",
    "UserRole",
    "FileType",
    "Visibility",
    "WriteUp",
    "WriteUpStatus",
]
