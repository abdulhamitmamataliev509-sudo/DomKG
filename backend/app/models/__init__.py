"""Бардык SQLAlchemy моделдеринин экспорту.

Бул пакетти импорттоо бардык моделдерди метадатада каттайт,
андыктан `db.create_all()` жана Alembic миграциялары
аппараттык таблицалардын баарын билет.
"""
from app.models.base import TimestampMixin, utcnow
from app.models.user import User, Admin
from app.models.category import Category
from app.models.city import City, District
from app.models.property import Property, PropertyImage, Favorite
from app.models.message import Message
from app.models.notification import Notification
from app.models.report import Report
from app.models.view import View

__all__ = [
    # base helpers
    "TimestampMixin",
    "utcnow",
    # entities
    "User",
    "Admin",
    "Category",
    "City",
    "District",
    "Property",
    "PropertyImage",
    "Favorite",
    "Message",
    "Notification",
    "Report",
    "View",
]