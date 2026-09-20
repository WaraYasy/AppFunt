"""Controlador para la vista de Activos (inventario de hardware)."""
from flask import Blueprint, redirect, render_template, session, url_for

from app.database import SessionLocal
from app.forms import NuevoActivoForm
from app.i18n import DEFAULT_LOCALE, translate
from app.models.assets import Asset, AssetCategoria
from app.repositories.asset_repository import AssetRepository
from app.repositories.personal_repository import PersonalRepository
from app.template_helpers import asset_icon, person_initials

assets_bp = Blueprint("assets", __name__)

# Categorías con acceso rápido mediante pastillas de filtro en la vista,
# junto con la clave de traducción de su etiqueta.
CATEGORIAS_FILTRO = [
    (AssetCategoria.PORTATIL, "assets.filter_portatil"),
    (AssetCategoria.SERVIDOR, "assets.filter_servidor"),
    (AssetCategoria.REDES, "assets.filter_redes"),
    (AssetCategoria.PERIFERICO, "assets.filter_periferico"),
]

SIN_ASIGNAR = ""  # valor del <option>/campo id_personal que representa "sin custodio"


def _serializar_asset(asset: Asset) -> dict:
    """Convierte un Asset (y su custodio, si tiene) en un dict listo para el panel lateral."""
    custodio = asset.custodio
    return {
        "id": asset.id,
        "codigo": asset.codigo,
        "nombre": asset.nombre,
        "categoria": asset.categoria,
        "icono": asset_icon(asset),
        "asignado": bool(asset.id_personal),
        "estado": asset.estado,
        "numeroSerie": asset.numero_serie,
        "cpu": asset.cpu,
        "ram": asset.ram,
        "almacenamiento": asset.almacenamiento,
        "sistemaOperativo": asset.sistema_operativo,
        "garantia": asset.garantia,
        "custodio": (
            {
                "nombre": f"{custodio.nombre} {custodio.apellido}",
                "iniciales": person_initials(custodio),
                "rol": custodio.rol,
                "departamento": custodio.departamento,
                "ubicacion": custodio.ubicacion,
            }
            if custodio
            else None
        ),
    }


def _preparar_formulario(form: NuevoActivoForm, personal_repo: PersonalRepository) -> None:
    """Completa los choices de un NuevoActivoForm con datos de la base."""
    locale = session.get("locale", DEFAULT_LOCALE)
    form.categoria.choices = [(categoria, categoria) for categoria in AssetCategoria.OPCIONES]
    form.id_personal.choices = [
        (SIN_ASIGNAR, translate("assets.modal_field_assignment_empty", locale))
    ] + [
        (persona.id, f"{persona.nombre} {persona.apellido}" + (f" ({persona.rol})" if persona.rol else ""))
        for persona in personal_repo.get_all()
    ]


def _contexto_index(form: NuevoActivoForm | None = None) -> dict:
    db = SessionLocal()
    asset_repo = AssetRepository(db)
    personal_repo = PersonalRepository(db)

    if form is None:
        form = NuevoActivoForm()
    _preparar_formulario(form, personal_repo)

    assets = asset_repo.get_all()
    total_assets = len(assets)
    total_disponibles = asset_repo.count_disponibles()
    total_asignados = asset_repo.count_asignados()
    porcentaje_asignados = (
        round(total_asignados / total_assets * 100) if total_assets else 0
    )

    conteo_por_categoria = dict(asset_repo.count_by_categoria())
    filtros_categoria = [
        {
            "valor": categoria,
            "label_key": label_key,
            "total": conteo_por_categoria.get(categoria, 0),
        }
        for categoria, label_key in CATEGORIAS_FILTRO
    ]

    return {
        "assets": assets,
        "assets_json": [_serializar_asset(asset) for asset in assets],
        "total_assets": total_assets,
        "total_disponibles": total_disponibles,
        "total_asignados": total_asignados,
        "porcentaje_asignados": porcentaje_asignados,
        "filtros_categoria": filtros_categoria,
        "form": form,
        "abrir_modal_nuevo": False,
    }


@assets_bp.route("/activos")
def index():
    return render_template("assets.html", **_contexto_index())


@assets_bp.route("/activos/nuevo", methods=["POST"])
def crear():
    db = SessionLocal()
    asset_repo = AssetRepository(db)
    personal_repo = PersonalRepository(db)

    form = NuevoActivoForm()
    _preparar_formulario(form, personal_repo)

    if form.validate_on_submit():
        if form.numero_serie.data and asset_repo.existe_numero_serie(form.numero_serie.data):
            form.numero_serie.errors.append("assets.error_duplicate_serial")
        else:
            asset_repo.create(
                nombre=form.nombre.data.strip(),
                categoria=form.categoria.data,
                numero_serie=form.numero_serie.data.strip() or None,
                ubicacion=form.ubicacion.data.strip() or None,
                id_personal=form.id_personal.data or None,
            )
            return redirect(url_for("assets.index"))

    contexto = _contexto_index(form=form)
    contexto["abrir_modal_nuevo"] = True
    return render_template("assets.html", **contexto), 400
