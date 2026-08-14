"""Администратор Blueprint'и — /api/admin.

Статистика жана арыздарды (reports) башкаруу эндпоинттери.
"""
from datetime import datetime, timezone

from flask import Blueprint, request

from app.extensions import db
from app.models import Property, Report, User, View
from app.utils.http import error, iso, success

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/ping")
def admin_ping():
    """
    Сервистин ден соолугун текшерүү.

    Blueprint'тин иштээрин ырастоочу эң жөнөкөй эндпоинт.
    ---
    tags:
      - admin
    summary: Admin сервисинин ден соолугун текшерүү
    description: Жөнөкөй ping чакуу — admin blueprint'инин катталгандыгын көрсөтөт.
    responses:
      200:
        description: Сервис иштеп жатат
        schema:
          type: object
          properties:
            service:
              type: string
              example: admin
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
    return success({"service": "admin", "status": "ok"})


@admin_bp.get("/stats")
def stats():
    """
    Платформанын жалпы статистикасы.

    Колдонуучу, жарнама, көрүү жана ачык арыздардын саны.
    ---
    tags:
      - admin
    summary: Платформа статистикасы
    responses:
      200:
        description: Статистика ийгиликтүү алынды
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: object
              properties:
                total_users:
                  type: integer
                total_properties:
                  type: integer
                active_properties:
                  type: integer
                total_views:
                  type: integer
                pending_reports:
                  type: integer
      401:
        description: Админ укугу керек (киришүү талап)
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
    data = {
        "total_users": User.query.count(),
        "total_properties": Property.query.count(),
        "active_properties": Property.query.filter_by(status="active").count(),
        "total_views": View.query.count(),
        "pending_reports": Report.query.filter_by(status="pending").count(),
    }
    return success(data)


@admin_bp.get("/reports")
def list_reports():
    """
    Арыздардын тизмеси.

    `status` аргументи менен (pending/resolved/...) фильтрленет.
    ---
    tags:
      - admin
    summary: Арыздардын тизмеси
    parameters:
      - name: status
        in: query
        type: string
        required: false
        enum: [pending, reviewed, resolved, dismissed]
        description: Арыздын статусу (эгер берилбесе — бардыгы)
    responses:
      200:
        description: Арыздардын тизмеси
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
                  property_id:
                    type: integer
                  reason:
                    type: string
                  status:
                    type: string
      401:
        description: Админ укугу керек
        schema:
          type: object
          properties:
            status:
              type: string
      500:
        description: Сервер катасы
        schema:
          type: object
          properties:
            status:
              type: string
    """
    query = Report.query
    if request.args.get("status"):
        query = query.filter(Report.status == request.args["status"])
    reports = query.order_by(Report.created_at.desc()).all()
    return success(
        [
            {
                "id": r.id,
                "property_id": r.property_id,
                "reporter_id": r.reporter_id,
                "reason": r.reason,
                "description": r.description,
                "status": r.status,
                "resolved_at": iso(r.resolved_at),
                "created_at": iso(r.created_at),
            }
            for r in reports
        ]
    )


@admin_bp.patch("/reports/<int:report_id>")
def resolve_report(report_id):
    """
    Арызды чечүү.

    `resolved_by` (админ ID), `status` (resolved/dismissed) жана
    `resolution_note` кабыл алынат.
    ---
    tags:
      - admin
    summary: Арызды чечүү/жабуу
    parameters:
      - name: report_id
        in: path
        type: integer
        required: true
        description: Арыздын ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - resolved_by
          properties:
            resolved_by:
              type: integer
              description: Админ колдонуучунун ID
            status:
              type: string
              enum: [resolved, dismissed]
              default: resolved
            resolution_note:
              type: string
    responses:
      200:
        description: Арыз чечилди
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
            data:
              type: object
              properties:
                id:
                  type: integer
                status:
                  type: string
      400:
        description: Валидация катасы
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      404:
        description: Арыз табылган жок
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
    report = Report.query.get(report_id)
    if not report:
        return error("Арыз табылган жок", 404)

    data = request.get_json(silent=True) or {}
    admin_id = data.get("resolved_by")
    if not admin_id:
        return error("resolved_by талап кылынат", 400)

    status = data.get("status", "resolved")
    if status not in ("resolved", "dismissed"):
        return error("status 'resolved' же 'dismissed' болушу керек", 400)

    report.resolve(admin_id, status=status, note=data.get("resolution_note"))
    db.session.commit()
    return success(
        {"id": report.id, "status": report.status},
        message="Арыз чечилди",
    )