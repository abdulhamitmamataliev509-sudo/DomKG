"""Шаар (City) жана район (District) моделдери.

Кыргызстандын шаар/район таксономиясы үчүн:
City -> District -> Property (1:N:N).
"""
from app.extensions import db
from app.models.base import TimestampMixin


class City(TimestampMixin, db.Model):
    """Шаар же облус (мас: Бишкек, Ош, Чүй облусу)."""

    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    # ---- Relationships ----
    districts = db.relationship(
        "District",
        back_populates="city",
        cascade="all, delete-orphan",
    )
    properties = db.relationship("Property", back_populates="city", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<City {self.id} {self.name}>"


class District(TimestampMixin, db.Model):
    """Шаар ичиндеги район (мас: Бишкек — Свердловский, Ленинский)."""

    __tablename__ = "districts"

    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(
        db.Integer,
        db.ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    # ---- Relationships ----
    city = db.relationship("City", back_populates="districts")
    properties = db.relationship("Property", back_populates="district", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<District {self.id} {self.name}>"