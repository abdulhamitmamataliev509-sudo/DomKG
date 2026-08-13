"""Жалпы ORM микс-класстары жана жардамчылар.

Бардык моделдерде кайталанган талаалар (id, created_at, updated_at)
бир жерде топтолду — DRY принциби.
"""
from datetime import datetime, timezone

from app.extensions import db


def utcnow() -> datetime:
    """UTC убакытын кайтарат — timestamps үчүн default."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Түзүлгөн жана өзгөртүлгөн убакыт талаалары."""

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )