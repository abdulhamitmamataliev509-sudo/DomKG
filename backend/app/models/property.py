"""Кыймылсыз мүлк объектилери: Property, PropertyImage, Favorite."""
from datetime import datetime, timezone

from app.extensions import db
from app.models.base import TimestampMixin


class Property(TimestampMixin, db.Model):
    """Кыймылсыз мүлк жарнамасы (батир/үй/жер/коммерциялык)."""

    __tablename__ = "properties"

    # Бюджеттин турү жана физикалык тип — фронтендеги фильтрлерге жардам
    DEAL_TYPES = ("sale", "rent")          # сатуу / ижара
    PROPERTY_TYPES = ("apartment", "house", "land", "commercial")
    CURRENCIES = ("KGS", "USD")
    STATUSES = ("draft", "moderation", "active", "sold", "rented", "archived")

    id = db.Column(db.Integer, primary_key=True)

    # ---- Ээси жана жайгашкан жери (FK) ----
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    city_id = db.Column(
        db.Integer,
        db.ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    district_id = db.Column(
        db.Integer,
        db.ForeignKey("districts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ---- Башкы маалымат ----
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deal_type = db.Column(db.String(10), nullable=False, default="sale")
    property_type = db.Column(db.String(20), nullable=False, default="apartment")
    price = db.Column(db.Numeric(14, 2), nullable=False)
    price_per_m2 = db.Column(db.Numeric(14, 2), nullable=True)  # автоматтык эсептөөгө болот
    currency = db.Column(db.String(3), nullable=False, default="KGS")

    # ---- Өлчөмдөр (м²) ----
    area_total = db.Column(db.Numeric(10, 2), nullable=True)
    area_living = db.Column(db.Numeric(10, 2), nullable=True)
    area_kitchen = db.Column(db.Numeric(10, 2), nullable=True)

    # ---- Физикалык мүнөздөмөлөр ----
    rooms = db.Column(db.Integer, nullable=True)
    floor = db.Column(db.Integer, nullable=True)
    floor_total = db.Column(db.Integer, nullable=True)
    bathrooms = db.Column(db.Integer, nullable=True, default=1)
    year_built = db.Column(db.Integer, nullable=True)
    has_parking = db.Column(db.Boolean, nullable=False, default=False)
    has_balcony = db.Column(db.Boolean, nullable=False, default=False)
    has_furniture = db.Column(db.Boolean, nullable=False, default=False)

    # ---- Координаттар / дарек ----
    address = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Numeric(9, 6), nullable=True)
    longitude = db.Column(db.Numeric(9, 6), nullable=True)

    # ---- Статус / жайылтуу ----
    status = db.Column(db.String(20), nullable=False, default="draft", index=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    published_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Издөө фильтрлери үчүн бириккен индекс (status + deal_type)
    __table_args__ = (
        db.Index("ix_properties_status_deal", "status", "deal_type"),
    )

    # ---- Relationships ----
    owner = db.relationship("User", back_populates="properties")
    category = db.relationship("Category", back_populates="properties")
    city = db.relationship("City", back_populates="properties")
    district = db.relationship("District", back_populates="properties")

    images = db.relationship(
        "PropertyImage",
        back_populates="property",
        cascade="all, delete-orphan",
        order_by="PropertyImage.sort_order",
    )
    favorites = db.relationship(
        "Favorite",
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    views = db.relationship(
        "View",
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    reports = db.relationship("Report", back_populates="property", lazy="dynamic")
    messages = db.relationship("Message", back_populates="property", lazy="dynamic")

    def increment_view(self) -> None:
        """Жарнаманын көрүү эсептегичин көбөйтөт."""
        self.view_count = (self.view_count or 0) + 1

    def publish(self) -> None:
        """Жарнаманы 'active' статуска чыгарып, убактысын белгилейт."""
        self.status = "active"
        self.published_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<Property {self.id} {self.title!r}>"


class PropertyImage(TimestampMixin, db.Model):
    """Жарнаманын сүрөтү. 1 жарнамага көп сүрөт туура келет."""

    __tablename__ = "property_images"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200), nullable=True)
    is_primary = db.Column(db.Boolean, nullable=False, default=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    # ---- Relationships ----
    property = db.relationship("Property", back_populates="images")

    def __repr__(self) -> str:
        return f"<PropertyImage {self.id} ({self.sort_order})>"


class Favorite(TimestampMixin, db.Model):
    """Колдонуучунун тандоосу (избранное).

    Бир колдонуучу бир мүлктү бир гана жолу избранное кошо алат.
    """

    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
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

    __table_args__ = (
        db.UniqueConstraint("user_id", "property_id", name="uq_favorites_user_property"),
    )

    # ---- Relationships ----
    user = db.relationship("User", back_populates="favorites")
    property = db.relationship("Property", back_populates="favorites")

    def __repr__(self) -> str:
        return f"<Favorite user={self.user_id} property={self.property_id}>"