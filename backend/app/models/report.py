"""Жарнамага арыз берүү (Report) модели."""
from datetime import datetime, timezone

from app.extensions import db
from app.models.base import TimestampMixin, utcnow


class Report(TimestampMixin, db.Model):
    """Арыз (жалган/мыйзамсыз жарнама же мазмун боюнча шикаят).

    Статусу: pending -> reviewed / resolved / dismissed
    """

    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reason = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # pending | reviewed | resolved | dismissed
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    resolved_by = db.Column(
        db.Integer,
        db.ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    resolution_note = db.Column(db.Text, nullable=True)

    # ---- Relationships ----
    reporter = db.relationship(
        "User", foreign_keys=[reporter_id], back_populates="submitted_reports"
    )
    property = db.relationship("Property", back_populates="reports")
    resolver = db.relationship("Admin", foreign_keys=[resolved_by], back_populates="resolved_reports")

    def resolve(self, admin_id: int, status: str = "resolved", note: str = None) -> None:
        """Арызды администратор тарабынан жабык деп белгилейт."""
        self.status = status
        self.resolved_by = admin_id
        self.resolved_at = datetime.now(timezone.utc)
        self.resolution_note = note

    def __repr__(self) -> str:
        return f"<Report {self.id} status={self.status} property={self.property_id}>"