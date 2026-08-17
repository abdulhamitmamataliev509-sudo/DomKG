import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

# Иштелүү үчүн гана белгилүү алсыз dev-секреттер.
# Production'до ЭЧ КАЧАН колдонулбайт — ал жерде env'ден келиши милдеттүү.
DEV_SECRET_KEY = "dev-only-insecure-secret-key-change-me"
DEV_JWT_SECRET_KEY = "dev-only-insecure-jwt-secret-key-change-me"


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _parse_origins(value: str):
    return [o.strip() for o in value.split(",") if o.strip()]


class Config:
    # Секреттер — prod'то create_app ичинде текшерилет (fail-fast)
    SECRET_KEY = os.getenv("SECRET_KEY") or None
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or None

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # PostgreSQL connection (.env файлынан алынат, берилбесе default)
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "domkg_db")

    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL")
        or f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # --- JWT өмүр мөөнөтү ---
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "30"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "7"))
    )

    # --- Rate limiting ---
    RATELIMIT_ENABLED = _env_bool("RATELIMIT_ENABLED", True)
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATE_LIMIT_LOGIN = os.getenv("RATE_LIMIT_LOGIN", "10 per minute")
    RATE_LIMIT_REGISTER = os.getenv("RATE_LIMIT_REGISTER", "5 per minute")

    # --- Email тастыктоо (кийинки фаза) ---
    REQUIRE_EMAIL_VERIFICATION = _env_bool("REQUIRE_EMAIL_VERIFICATION", False)

    # --- CORS: уруксат берилген origin'дер (virgin "*" эмес) ---
    CORS_ORIGINS = _parse_origins(
        os.getenv("CORS_ORIGINS", "http://localhost:5501,http://127.0.0.1:5501")
    )
    CORS_ALLOW_CREDENTIALS = _env_bool("CORS_ALLOW_CREDENTIALS", False)

    # --- Swagger / API doc ---
    SWAGGER_ENABLED = _env_bool("SWAGGER_ENABLED", False)


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    FLASK_ENV = "development"
    # Иштелүү конфигурациясы — ачык dev-секреттер гана (prod'тордо милдеттүү эмес)
    SECRET_KEY = os.getenv("SECRET_KEY") or DEV_SECRET_KEY
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or DEV_JWT_SECRET_KEY
    SWAGGER_ENABLED = _env_bool("SWAGGER_ENABLED", True)


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    FLASK_ENV = "testing"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"
    # Тесттерде limiter storage'и туура иштөөсү үчүн enabled, бирок чоң лимиттер
    RATELIMIT_ENABLED = True
    RATE_LIMIT_LOGIN = "1000 per minute"
    RATE_LIMIT_REGISTER = "1000 per minute"
    SWAGGER_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    FLASK_ENV = "production"
    # Секреттер env'ден келиши керек — validate_environment башталышта текшерет
    SECRET_KEY = os.getenv("SECRET_KEY") or None
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or None
    # Redis production'до сунушталат — env аркылуу коюлат
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI") or "redis://localhost:6379/0"
    RATE_LIMIT_LOGIN = os.getenv("RATE_LIMIT_LOGIN", "5 per minute")
    RATE_LIMIT_REGISTER = os.getenv("RATE_LIMIT_REGISTER", "3 per minute")
    SWAGGER_ENABLED = False


config_by_name = {
    "dev": DevelopmentConfig,
    "development": DevelopmentConfig,
    "test": TestingConfig,
    "testing": TestingConfig,
    "prod": ProductionConfig,
    "production": ProductionConfig,
}


def validate_environment(config_name: str):
    """Production үчүн эрте (fail-fast) коопсуздук текшерүүсү.

    - SECRET_KEY / JWT_SECRET_KEY милдеттүү (белгилүү dev-default эмес)
    - Production DEBUG/TESTING кошулбайт
    Ката болсо RuntimeError — сервер башталбайт.
    """
    cfg = config_by_name.get(config_name, DevelopmentConfig)
    if getattr(cfg, "FLASK_ENV", config_name) != "production":
        return cfg

    secrets = {"SECRET_KEY": os.getenv("SECRET_KEY"), "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY")}
    bad = [
        name
        for name, value in secrets.items()
        if not value or value in (DEV_SECRET_KEY, DEV_JWT_SECRET_KEY)
    ]
    if bad:
        raise RuntimeError(
            "Production requires secure environment variables: "
            + ", ".join(bad)
            + ". Do not use dev/default secrets."
        )
    if getattr(cfg, "DEBUG", False) or getattr(cfg, "TESTING", False):
        raise RuntimeError("Production must have DEBUG=False and TESTING=False.")
    return cfg