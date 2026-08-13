"""Жарнамаларды көрүү журналы (View) модели."""
from app.extensions import db
from app.models.base import TimestampMixin, utcnow


class View(TimestampMixin, db.Model):
    """Жарнаманын бир көрүлүшү (аналитика үчүн).

    Анонимдүү көрүүлөр да сакталат (user_id NULL болушу мүмкүн),
    IP жана user-agent учуру менен жазылат.
    """

    __tablename__ = "views"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 узундугуна жетет
    user_agent = db.Column(db.String(255), nullable=True)
    viewed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    # ---- Relationships ----
    property = db.relationship("Property", back_populates="views")
    user = db.relationship("User", back_populates="views")

    def __repr__(self) -> str:
        return f"<View {self.id} property={self.property_id}>"