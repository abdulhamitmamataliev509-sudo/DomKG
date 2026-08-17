from sqlalchemy.exc import IntegrityError

from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import TokenBlocklist, User
from app.schemas import UserCreateSchema, UserLoginSchema, normalize_email
from app.services import ServiceError


class AuthService:
    @staticmethod
    def register(data):
        payload = UserCreateSchema().load(data)
        email = normalize_email(payload["email"])
        password = payload["password"]
        first_name = (payload.get("first_name") or "").strip()
        if User.query.filter_by(email=email).first():
            raise ServiceError("This email is already registered", 409, "CONFLICT")

        user = User(
            email=email,
            phone=(payload.get("phone") or "").strip() or None,
            first_name=first_name,
            last_name=(payload.get("last_name") or "").strip() or None,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ServiceError("This email is already registered", 409, "CONFLICT")

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {"user": AuthService.user_public_dict(user), "access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def login(data):
        payload = UserLoginSchema().load(data)
        email = normalize_email(payload["email"])
        password = payload["password"]
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            raise ServiceError("Email or password is incorrect", 401, "UNAUTHORIZED")
        if not user.is_active:
            raise ServiceError("Email or password is incorrect", 401, "UNAUTHORIZED")

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {"user": AuthService.user_public_dict(user), "access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def user_public_dict(user):
        return {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_verified": user.is_verified,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    @staticmethod
    def revoke_token(jti, token_type, user_id, expires_at):
        if jti and not TokenBlocklist.query.filter_by(jti=jti).first():
            db.session.add(
                TokenBlocklist(
                    jti=jti,
                    token_type=token_type,
                    user_id=user_id,
                    expires_at=expires_at,
                )
            )

    @staticmethod
    def refresh_access(user):
        if user is None or not user.is_active:
            raise ServiceError("Account is inactive or missing", 401, "UNAUTHORIZED")
        return {"access_token": create_access_token(identity=str(user.id))}
