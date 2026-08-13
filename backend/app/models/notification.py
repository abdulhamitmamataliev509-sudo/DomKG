"""Колдонуучуга жөнөтүлгөн эскертмелер (Notification) модели."""
from app.extensions import db
from app.models.base import TimestampMixin


class Notification(TimestampMixin, db.Model):
    """Пайдалануучуга жөнөтүлгөн түртүү/эскертме.

    Типтерге мисал: message, favorite, report, system.
    """

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # message | favorite | report | system
    type = db.Column(db.String(30), nullable=False, default="system")
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Баяндама менен байланыштыруучу байланыштыруучу талаалар (опционал)
    property_id = db.Column(
        db.Integer, db.ForeignKey("properties.id", ondelete="SET NULL"), nullable=True
    )
    message_id = db.Column(
        db.Integer, db.ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )

    # ---- Relationships ----
    user = db.relationship("User", back_populates="notifications")
    property = db.relationship("Property", viewonly=True)
    message = db.relationship("Message", viewonly=True)

    def mark_as_read(self) -> None:
        """Эскертмени окулган деп белгилейт."""
        from app.models.base import utcnow

        if not self.is_read:
            self.is_read = True
            self.read_at = utcnow()

    def __repr__(self) -> str:
        return f"<Notification {self.id} type={self.type} user={self.user_id}>"