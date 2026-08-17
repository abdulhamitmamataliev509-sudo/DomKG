from decimal import Decimal

from marshmallow import RAISE, Schema, ValidationError, fields, validate

from app.models import Category, City, District, Property, User


class BaseSchema(Schema):
    class Meta:
        unknown = RAISE


class UserCreateSchema(BaseSchema):
    email = fields.Email(required=True, error_messages={"required": "email is required"})
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, max=128),
        error_messages={"required": "password is required"},
    )
    first_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "first_name is required"},
    )
    last_name = fields.String(load_default=None, validate=validate.Length(max=100))
    phone = fields.String(load_default=None, validate=validate.Length(max=20))


class UserLoginSchema(BaseSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1, max=128))


class PaginationSchema(BaseSchema):
    limit = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))
    offset = fields.Integer(load_default=0, validate=validate.Range(min=0))


class CategorySchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    parent_id = fields.Integer(load_default=None, allow_none=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    slug = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(load_default=None, allow_none=True)
    sort_order = fields.Integer(load_default=0, validate=validate.Range(min=0))
    is_active = fields.Boolean(load_default=True)


class CitySchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    slug = fields.String(required=True, validate=validate.Length(min=1, max=120))
    is_active = fields.Boolean(load_default=True)
    sort_order = fields.Integer(load_default=0, validate=validate.Range(min=0))


class DistrictSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    city_id = fields.Integer(required=True, validate=validate.Range(min=1))
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    slug = fields.String(required=True, validate=validate.Length(min=1, max=120))
    is_active = fields.Boolean(load_default=True)
    sort_order = fields.Integer(load_default=0, validate=validate.Range(min=0))


class PropertyBaseSchema(BaseSchema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default=None, allow_none=True)
    deal_type = fields.String(
        load_default="sale",
        validate=validate.OneOf(Property.DEAL_TYPES),
    )
    property_type = fields.String(
        load_default="apartment",
        validate=validate.OneOf(Property.PROPERTY_TYPES),
    )
    price = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0))
    price_per_m2 = fields.Decimal(load_default=None, allow_none=True, as_string=False, validate=validate.Range(min=0))
    currency = fields.String(load_default="KGS", validate=validate.OneOf(Property.CURRENCIES))
    category_id = fields.Integer(required=True, validate=validate.Range(min=1))
    city_id = fields.Integer(required=True, validate=validate.Range(min=1))
    district_id = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1))
    rooms = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1))
    floor = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=0))
    floor_total = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=0))
    bathrooms = fields.Integer(load_default=1, allow_none=True, validate=validate.Range(min=0))
    year_built = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1900, max=2100))
    has_parking = fields.Boolean(load_default=False)
    has_balcony = fields.Boolean(load_default=False)
    has_furniture = fields.Boolean(load_default=False)
    area_total = fields.Decimal(load_default=None, allow_none=True, as_string=False, validate=validate.Range(min=0))
    area_living = fields.Decimal(load_default=None, allow_none=True, as_string=False, validate=validate.Range(min=0))
    area_kitchen = fields.Decimal(load_default=None, allow_none=True, as_string=False, validate=validate.Range(min=0))
    address = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
    latitude = fields.Decimal(load_default=None, allow_none=True, as_string=False, validate=validate.Range(min=-90, max=90))
    longitude = fields.Decimal(load_default=None, allow_none=True, as_string=False, validate=validate.Range(min=-180, max=180))
    status = fields.String(load_default="active", validate=validate.OneOf(Property.STATUSES))
    is_featured = fields.Boolean(load_default=False)


class PropertyCreateSchema(PropertyBaseSchema):
    pass


class PropertyUpdateSchema(BaseSchema):
    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    deal_type = fields.String(validate=validate.OneOf(Property.DEAL_TYPES))
    property_type = fields.String(validate=validate.OneOf(Property.PROPERTY_TYPES))
    price = fields.Decimal(as_string=False, validate=validate.Range(min=0))
    price_per_m2 = fields.Decimal(as_string=False, allow_none=True, validate=validate.Range(min=0))
    currency = fields.String(validate=validate.OneOf(Property.CURRENCIES))
    category_id = fields.Integer(validate=validate.Range(min=1))
    city_id = fields.Integer(validate=validate.Range(min=1))
    district_id = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    rooms = fields.Integer(validate=validate.Range(min=1))
    floor = fields.Integer(validate=validate.Range(min=0))
    floor_total = fields.Integer(validate=validate.Range(min=0))
    bathrooms = fields.Integer(validate=validate.Range(min=0))
    year_built = fields.Integer(validate=validate.Range(min=1900, max=2100))
    has_parking = fields.Boolean()
    has_balcony = fields.Boolean()
    has_furniture = fields.Boolean()
    area_total = fields.Decimal(as_string=False, validate=validate.Range(min=0))
    area_living = fields.Decimal(as_string=False, validate=validate.Range(min=0))
    area_kitchen = fields.Decimal(as_string=False, validate=validate.Range(min=0))
    address = fields.String(validate=validate.Length(max=255))
    latitude = fields.Decimal(as_string=False, validate=validate.Range(min=-90, max=90))
    longitude = fields.Decimal(as_string=False, validate=validate.Range(min=-180, max=180))
    status = fields.String(validate=validate.OneOf(Property.STATUSES))
    is_featured = fields.Boolean()


class FavoriteCreateSchema(BaseSchema):
    property_id = fields.Integer(required=True, validate=validate.Range(min=1))


class ReportResolveSchema(BaseSchema):
    status = fields.String(required=True, validate=validate.OneOf(["resolved", "dismissed"]))
    resolution_note = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class UserResponseSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    email = fields.String(dump_only=True)
    phone = fields.String(dump_only=True, allow_none=True)
    first_name = fields.String(dump_only=True)
    last_name = fields.String(dump_only=True, allow_none=True)
    role = fields.String(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    avatar_url = fields.String(dump_only=True, allow_none=True)
    created_at = fields.String(dump_only=True)


class PropertyResponseSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    title = fields.String(dump_only=True)
    description = fields.String(dump_only=True, allow_none=True)
    deal_type = fields.String(dump_only=True)
    property_type = fields.String(dump_only=True)
    price = fields.Decimal(dump_only=True)
    price_per_m2 = fields.Decimal(dump_only=True, allow_none=True)
    currency = fields.String(dump_only=True)
    owner_id = fields.Integer(dump_only=True)
    category_id = fields.Integer(dump_only=True)
    city_id = fields.Integer(dump_only=True)
    district_id = fields.Integer(dump_only=True, allow_none=True)
    rooms = fields.Integer(dump_only=True, allow_none=True)
    floor = fields.Integer(dump_only=True, allow_none=True)
    floor_total = fields.Integer(dump_only=True, allow_none=True)
    area_total = fields.Decimal(dump_only=True, allow_none=True)
    address = fields.String(dump_only=True, allow_none=True)
    latitude = fields.Decimal(dump_only=True, allow_none=True)
    longitude = fields.Decimal(dump_only=True, allow_none=True)
    status = fields.String(dump_only=True)
    is_featured = fields.Boolean(dump_only=True)
    view_count = fields.Integer(dump_only=True)
    published_at = fields.String(dump_only=True, allow_none=True)
    created_at = fields.String(dump_only=True)


def normalize_email(value):
    if value is None:
        return None
    return str(value).strip().lower()


def format_validation_error(exc):
    if isinstance(exc, ValidationError):
        return exc.messages
    return {"error": "Validation failed"}
