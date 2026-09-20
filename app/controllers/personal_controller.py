"""Controlador para la vista de Personal (directorio de colaboradores)."""
from flask import Blueprint, redirect, render_template, session, url_for

from app.database import SessionLocal
from app.forms import NuevoColaboradorForm
from app.i18n import DEFAULT_LOCALE, translate
from app.models.assets import Asset
from app.models.personal import Personal, PersonalModalidad
from app.repositories.personal_repository import PersonalRepository
from app.template_helpers import asset_icon, person_initials

personal_bp = Blueprint("personal", __name__)


def _serializar_asset_asignado(asset: Asset) -> dict:
    return {
        "id": asset.id,
        "nombre": asset.nombre,
        "categoria": asset.categoria,
        "icono": asset_icon(asset),
        "numeroSerie": asset.numero_serie,
        "codigo": asset.codigo,
    }


def _serializar_persona(persona: Personal) -> dict:
    return {
        "id": persona.id,
        "codigo": persona.codigo,
        "nombre": f"{persona.nombre} {persona.apellido}",
        "iniciales": person_initials(persona),
        "email": persona.email,
        "rol": persona.rol,
        "departamento": persona.departamento,
        "ubicacion": persona.ubicacion,
        "modalidad": persona.modalidad,
        "incorporacion": persona.created.strftime("%d/%m/%Y"),
        "tieneActivos": bool(persona.assets),
        "activos": [_serializar_asset_asignado(asset) for asset in persona.assets],
    }


def _preparar_formulario(form: NuevoColaboradorForm) -> None:
    """Completa los choices de un NuevoColaboradorForm."""
    locale = session.get("locale", DEFAULT_LOCALE)
    form.modalidad.choices = [("", translate("personal.modal_field_modality_empty", locale))] + [
        (modalidad, modalidad) for modalidad in PersonalModalidad.OPCIONES
    ]


def _contexto_index(form: NuevoColaboradorForm | None = None) -> dict:
    db = SessionLocal()
    personal_repo = PersonalRepository(db)

    if form is None:
        form = NuevoColaboradorForm()
    _preparar_formulario(form)

    personal = personal_repo.get_all()
    total_empleados = len(personal)
    con_activos = sum(1 for persona in personal if persona.assets)
    sin_activos = total_empleados - con_activos
    porcentaje_con_activos = (
        round(con_activos / total_empleados * 100) if total_empleados else 0
    )

    conteo_por_modalidad = dict(personal_repo.count_by_modalidad())

    filtros_personal = [
        {"valor": "all", "label_key": "personal.filter_all", "total": total_empleados},
        {"valor": "with_assets", "label_key": "personal.filter_with_assets", "total": con_activos},
        {"valor": "pending", "label_key": "personal.filter_pending", "total": sin_activos},
        {
            "valor": "remote",
            "label_key": "personal.filter_remote",
            "total": conteo_por_modalidad.get(PersonalModalidad.REMOTO, 0),
        },
        {
            "valor": "onsite",
            "label_key": "personal.filter_onsite",
            "total": conteo_por_modalidad.get(PersonalModalidad.PRESENCIAL, 0),
        },
    ]

    return {
        "personal": personal,
        "personal_json": [_serializar_persona(persona) for persona in personal],
        "total_empleados": total_empleados,
        "con_activos": con_activos,
        "sin_activos": sin_activos,
        "porcentaje_con_activos": porcentaje_con_activos,
        "filtros_personal": filtros_personal,
        "form": form,
        "abrir_modal_nuevo": False,
    }


@personal_bp.route("/personal")
def index():
    return render_template("personal.html", **_contexto_index())


@personal_bp.route("/personal/nuevo", methods=["POST"])
def crear():
    db = SessionLocal()
    personal_repo = PersonalRepository(db)

    form = NuevoColaboradorForm()
    _preparar_formulario(form)

    if form.validate_on_submit():
        if form.email.data and personal_repo.existe_email(form.email.data):
            form.email.errors.append("personal.error_duplicate_email")
        else:
            personal_repo.create(
                nombre=form.nombre.data.strip(),
                apellido=form.apellido.data.strip(),
                email=form.email.data.strip() or None,
                rol=form.rol.data.strip() or None,
                departamento=form.departamento.data.strip() or None,
                ubicacion=form.ubicacion.data.strip() or None,
                modalidad=form.modalidad.data or None,
            )
            return redirect(url_for("personal.index"))

    contexto = _contexto_index(form=form)
    contexto["abrir_modal_nuevo"] = True
    return render_template("personal.html", **contexto), 400
