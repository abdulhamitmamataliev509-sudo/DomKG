from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Favorite, Property
from app.schemas import FavoriteCreateSchema
from app.services import ServiceError


class FavoriteService:
    @staticmethod
    def list_for_user(user):
        return Favorite.query.filter_by(user_id=user.id).order_by(Favorite.created_at.desc()).all()

    @staticmethod
    def add(user, data):
        payload = FavoriteCreateSchema().load(data)
        property_id = payload["property_id"]
        if not Property.query.get(property_id):
            raise ServiceError("Property not found", 404, "NOT_FOUND")
        if Favorite.query.filter_by(user_id=user.id, property_id=property_id).first():
            raise ServiceError("This property is already in your favorites", 409, "CONFLICT")

        favorite = Favorite(user_id=user.id, property_id=property_id)
        db.session.add(favorite)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ServiceError("This property is already in your favorites", 409, "CONFLICT")
        return favorite

    @staticmethod
    def remove(user, property_id):
        favorite = Favorite.query.filter_by(user_id=user.id, property_id=property_id).first()
        if not favorite:
            raise ServiceError("Favorite not found", 404, "NOT_FOUND")
        db.session.delete(favorite)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ServiceError("Unable to remove favorite", 409, "CONFLICT")
        return True
