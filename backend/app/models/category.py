"""Кыймылсыз мүлк категориясы (Category) модели — эки деңгээлдүү дарак."""
from app.extensions import db
from app.models.base import TimestampMixin


class Category(TimestampMixin, db.Model):
    """Мүлк категориясы: батир, үй, жер, коммерциялык ж.б.

    ``parent_id`` өзүнө-өзү байланыш аркылуу суб-категорияларды
    түзүүгө мүмкүндүк берет (мас: Категория -> Жаңы курулуш).
    """

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # ---- Relationships ----
    parent = db.relationship(
        "Category",
        remote_side=[id],  # өзүнө-өзү: parent тармагы
        back_populates="children",
    )
    children = db.relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    properties = db.relationship(
        "Property",
        back_populates="category",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Category {self.id} {self.name}>"