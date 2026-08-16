"""Revoked JWT токендердин денлисти (TokenBlocklist).

Raw JWT сакталбайт — жекече ``jti`` идентификатору гана, минималдуу
маалымат менен. Access жана refresh токендер revoked деп белгиленет.
"""
from app.extensions import db
from app.models.base import TimestampMixin


class TokenBlocklist(TimestampMixin, db.Model):
    """JWT jti денлист — revoked токендер ушул жерде сакталат."""

    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(64), unique=True, nullable=False, index=True)
    # access | refresh
    token_type = db.Column(db.String(20), nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # ---- Relationships ----
    user = db.relationship(
        "User",
        backref=db.backref("blocked_tokens", lazy="dynamic"),
    )

    def __repr__(self) -> str:
        return f"<TokenBlocklist {self.jti} ({self.token_type})>"