"""Сатып алуучу менен сатуучунун ортосундагы билдирүү (Message) модели."""
from app.extensions import db
from app.models.base import TimestampMixin


class Message(TimestampMixin, db.Model):
    """Колдонуучулар ортосундагы жеке билдирүү (жарнамага байланыштуу)."""

    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # ---- Relationships ----
    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages",
    )
    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_messages",
    )
    property = db.relationship("Property", back_populates="messages")

    def mark_as_read(self) -> None:
        """Билдирүүнү окулган деп белгилейт."""
        from app.models.base import utcnow

        if not self.is_read:
            self.is_read = True
            self.read_at = utcnow()

    def __repr__(self) -> str:
        return f"<Message {self.id} {self.sender_id}->{self.receiver_id}>"