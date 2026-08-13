"""Колдонуучу (User) жана Админ (Admin) моделдери."""
from app.extensions import db
from app.models.base import TimestampMixin


class User(TimestampMixin, db.Model):
    """Платформанын катталган колдонуучусу (сатуучу / сатып алуучу)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    # user | admin | ... кайсы роль экени
    role = db.Column(db.String(20), nullable=False, default="user")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    avatar_url = db.Column(db.String(500), nullable=True)

    # ---- Relationships ----
    properties = db.relationship(
        "Property",
        back_populates="owner",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    favorites = db.relationship(
        "Favorite",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    admin_profile = db.relationship(
        "Admin",
        back_populates="user",
        uselist=False,  # 1:1
        cascade="all, delete-orphan",
    )
    sent_messages = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        lazy="dynamic",
    )
    received_messages = db.relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        back_populates="receiver",
        lazy="dynamic",
    )
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    submitted_reports = db.relationship(
        "Report",
        foreign_keys="Report.reporter_id",
        back_populates="reporter",
        lazy="dynamic",
    )
    views = db.relationship("View", back_populates="user", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User {self.id} {self.email}>"


class Admin(TimestampMixin, db.Model):
    """Платформанын администратору. User менен 1:1 байланышат."""

    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    # super_admin | moderator | support
    role = db.Column(db.String(30), nullable=False, default="moderator")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # ---- Relationships ----
    user = db.relationship("User", back_populates="admin_profile")
    resolved_reports = db.relationship(
        "Report",
        foreign_keys="Report.resolved_by",
        back_populates="resolver",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Admin {self.id} {self.role}>"