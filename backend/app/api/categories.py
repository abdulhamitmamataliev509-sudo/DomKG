"""Категориялар Blueprint'и — /api/categories."""
from flask import Blueprint, request

from app.models import Category
from app.utils.http import error, success

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


def _category_dict(cat, include_children=False):
    """Category моделинин көрүнүшү."""
    data = {
        "id": cat.id,
        "parent_id": cat.parent_id,
        "name": cat.name,
        "slug": cat.slug,
        "description": cat.description,
        "sort_order": cat.sort_order,
        "is_active": cat.is_active,
    }
    if include_children and cat.children:
        data["children"] = [_category_dict(c) for c in cat.children]
    return data


@categories_bp.get("/ping")
def categories_ping():
    """
    Сервистин ден соолугун текшерүү.

    Blueprint'тин иштээрин ырастоочу эң жөнөкөй эндпоинт.
    ---
    tags:
      - categories
    summary: Categories сервисинин ден соолугун текшерүү
    description: Жөнөкөй ping чакуу — categories blueprint'инин катталгандыгын көрсөтөт.
    responses:
      200:
        description: Сервис иштеп жатат
        schema:
          type: object
          properties:
            service:
              type: string
              example: categories
            status:
              type: string
              example: ok
      500:
        description: Сервер катасы
        schema:
          type: object
          properties:
            status:
              type: string
    """
    return success({"service": "categories", "status": "ok"})


@categories_bp.get("")
def list_categories():
    """
    Категориялардын тизмеси.

    Башкы (parent) категориялар баракталат; `tree=true` берилсе
    суб-категориялар дагы түзүлөт.
    ---
    tags:
      - categories
    summary: Категориялардын тизмеси (дарак/тизме)
    parameters:
      - name: tree
        in: query
        type: boolean
        required: false
        default: false
        description: true болсо child категориялар менен дарак
    responses:
      200:
        description: Категориялардын тизмеси
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  slug:
                    type: string
      500:
        description: Сервер катасы
        schema:
          type: object
          properties:
            status:
              type: string
    """
    tree = request.args.get("tree") == "true"
    categories = Category.query.filter_by(parent_id=None, is_active=True).all()
    return success([_category_dict(c, include_children=tree) for c in categories])


@categories_bp.get("/<int:category_id>")
def get_category(category_id):
    """
    Жеке категориянын маалыматы.

    Берилген `category_id` менен категория кайтарылат.
    ---
    tags:
      - categories
    summary: Жеке категория
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
        description: Категориянын ID
    responses:
      200:
        description: Категория табылды
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                slug:
                  type: string
      404:
        description: Категория табылган жок
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      500:
        description: Сервер катасы
        schema:
          type: object
          properties:
            status:
              type: string
    """
    category = Category.query.get(category_id)
    if not category:
        return error("Категория табылган жок", 404)
    return success(_category_dict(category, include_children=True))