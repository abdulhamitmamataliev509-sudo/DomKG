"""Жергиликтүү smoke-тест: моделдердин бардыгы туура катталып,
таблицалар эс тутумундагы sqlite'те түзүлө аларын жана
relationships иштешин текшерет."""
import sys

from app import create_app
from app.extensions import db
from app.models import (
    User,
    Category,
    City,
    District,
    Property,
    PropertyImage,
    Favorite,
    Message,
    Notification,
    Report,
    View,
)


def main() -> int:
    app = create_app("test")  # sqlite:///:memory: колдонулат

    with app.app_context():
        db.create_all()
        tables = sorted(db.metadata.tables.keys())
        print("\n=== DomKG tables ===")
        for t in tables:
            print(f"  - {t}")
        required = {
            "users", "admins", "categories", "cities", "districts",
            "properties", "property_images", "favorites",
            "messages", "notifications", "reports", "views",
        }
        missing = required - set(tables)
        if missing:
            print(f"\n[FAIL] Жетишпеген таблицалар: {sorted(missing)}")
            return 1

        # ---- Relationship sanity check ----
        user = User(
            email="seller@domkg.kg", phone="+996700000000",
            password_hash="fakehash", first_name="Айбек",
        )
        bot = User(
            email="buyer@domkg.kg", first_name="Нургул",
            password_hash="fakehash",
        )
        db.session.add_all([user, bot])

        category = Category(name="Батир", slug="apartment")
        city = City(name="Бишкек", slug="bishkek")
        district = District(name="Свердлов", slug="sverdlov", city=city)
        db.session.add_all([category, city, district])
        db.session.flush()

        prop = Property(
            title="2 бөлмөлүү батир", deal_type="sale", price=95000,
            owner=user, category=category, city=city, district=district,
        )
        db.session.add(prop)
        db.session.flush()

        prop.images.append(PropertyImage(image_url="/uploads/a.jpg", is_primary=True))
        prop.views.append(View(user=bot, ip_address="127.0.0.1"))
        db.session.add(Favorite(user=bot, property_id=prop.id))
        db.session.add(Message(sender=bot, receiver=user, property=prop, body="Салам!"))
        db.session.add(Notification(user=user, type="message", title="Жаңы билдирүү"))
        db.session.add(Report(reporter=bot, property=prop, reason="spam"))
        db.session.commit()

        # Текшерүүлөр
        assert prop.owner == user, "owner relationship бузулган"
        assert len(prop.images) == 1, "images relationship бузулган"
        assert len(prop.views.all()) == 1, "views relationship бузулган"
        assert len(prop.favorites.all()) == 1, "favorites relationship бузулган"
        assert prop.city.districts[0] == district, "city.districts бузулган"
        assert len(user.properties.all()) == 1, "user.properties бузулган"
        assert len(bot.sent_messages.all()) == 1, "sent_messages бузулган"
        assert len(user.received_messages.all()) == 1, "received_messages бузулган"
        assert len(user.notifications.all()) == 1, "notifications бузулган"
        assert len(bot.submitted_reports.all()) == 1, "reports бузулган"
        prop.increment_view()
        assert prop.view_count == 1, "increment_view иштебейт"

        print("\n[OK] Relationships да ийгиликтүү иштеп жатат.")
        db.session.rollback()
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())