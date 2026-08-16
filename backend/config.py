import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-change-in-prod')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-super-secret-key-change-in-prod')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # PostgreSQL connection (.env файлынан алынат, берилбесе default)
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'domkg_db')

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )

    # ------------------------------------------------------------------
    # JWT token өмүр мөөнөтү (Production үчүн маанилүү)
    #   access  : кыска — API'ге кирүү үчүн
    #   refresh : узак — access'ти жаңылоо үчүн
    # env өзгөрмөлөрү:
    #   JWT_ACCESS_TOKEN_EXPIRES_MINUTES (default 30)
    #   JWT_REFRESH_TOKEN_EXPIRES_DAYS   (default 7)
    # ------------------------------------------------------------------
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', '30'))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES_DAYS', '7'))
    )

    # ------------------------------------------------------------------
    # Rate limiting (flask-limiter)
    #   RATELIMIT_ENABLED       : true/false
    #   RATELIMIT_STORAGE_URI   : memory:// (dev) | redis://... (prod)
    #   RATE_LIMIT_LOGIN        : login чакуу чектөө
    #   RATE_LIMIT_REGISTER     : register чакуу чектөө
    # ------------------------------------------------------------------
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'memory://')
    RATE_LIMIT_LOGIN = os.getenv('RATE_LIMIT_LOGIN', '10 per minute')
    RATE_LIMIT_REGISTER = os.getenv('RATE_LIMIT_REGISTER', '5 per minute')

    # ------------------------------------------------------------------
    # Email тастыктоо
    #   REQUIRE_EMAIL_VERIFICATION=True болсо, is_verified=False колдонуучу
    #   кире албайт. Email жөнөтүү инфраструктурасы али жок — кийинки фазада.
    # ------------------------------------------------------------------
    REQUIRE_EMAIL_VERIFICATION = (
        os.getenv('REQUIRE_EMAIL_VERIFICATION', 'false').lower() == 'true'
    )


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Тесттерде storage туура иштеши үчүн enabled болот, бирок чоң лимиттер
    RATELIMIT_ENABLED = True
    RATE_LIMIT_LOGIN = '1000 per minute'
    RATE_LIMIT_REGISTER = '1000 per minute'


class ProductionConfig(Config):
    DEBUG = False
    # Production'до катуураак лимиттер (агрессивдүү эмес)
    RATE_LIMIT_LOGIN = os.getenv('RATE_LIMIT_LOGIN', '5 per minute')
    RATE_LIMIT_REGISTER = os.getenv('RATE_LIMIT_REGISTER', '3 per minute')


config_by_name = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig
}