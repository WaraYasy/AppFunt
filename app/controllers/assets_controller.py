"""Controlador para la vista de Activos (inventario de hardware)."""
from flask import Blueprint, abort, flash, redirect, render_template, session, url_for
from flask_login import login_required

from app.database import SessionLocal
from app.forms import EditarActivoForm, NuevoActivoForm
from app.i18n import DEFAULT_LOCALE, translate
from app.models.assets import Asset, AssetCategoria
from app.models.persona import PersonaUbicacion
from app.repositories.asset_repository import AssetRepository
from app.repositories.persona_repository import PersonaRepository
from app.template_helpers import asset_icon, person_initials
from app.validacion import ValidationError

assets_bp = Blueprint("assets", __name__)

# Categorías con acceso rápido mediante pastillas de filtro en la vista,
# junto con la clave de traducción de su etiqueta.
CATEGORIAS_FILTRO = [
    (AssetCategoria.PORTATIL, "assets.filter_portatil"),
    (AssetCategoria.SERVIDOR, "assets.filter_servidor"),
    (AssetCategoria.REDES, "assets.filter_redes"),
    (AssetCategoria.PERIFERICO, "assets.filter_periferico"),
]

SIN_ASIGNAR = ""  # valor del <option>/campo id_persona que representa "sin custodio"


@assets_bp.before_request
@login_required
def _requerir_login():
    pass


def _locale() -> str:
    return session.get("locale", DEFAULT_LOCALE)


def _limpio(valor: str | None) -> str | None:
    """Recorta espacios y convierte vacío -> None. `valor` puede llegar None
    (campo Optional ausente del formdata), por eso no se puede asumir str."""
    return (valor or "").strip() or None


def _guardar(db, form, accion) -> bool:
    """Ejecuta `accion` (una llamada al repositorio). Si el modelo rechaza
    algún dato (@validates, ver app/validacion.py), engancha el error al
    campo correspondiente del form en vez de dejar que reviente en un 500 —
    es la red de seguridad para lo que WTForms no llegó a filtrar antes."""
    try:
        accion()
    except ValidationError as exc:
        db.rollback()  # descarta cualquier setattr() ya aplicado antes del que falló
        campo_form = getattr(form, exc.campo, None)
        if campo_form is not None:
            campo_form.errors.append(exc.mensaje)
        else:
            flash(f"{exc.campo}: {exc.mensaje}", "error")
        return False
    return True


def _serializar_asset(asset: Asset) -> dict:
    """Convierte un Asset (y su custodio, si tiene) en un dict listo para el panel lateral."""
    custodio = asset.custodio
    return {
        "id": asset.id,
        "codigo": asset.codigo,
        "nombre": asset.nombre,
        "categoria": asset.categoria,
        "icono": asset_icon(asset),
        "asignado": bool(asset.id_persona),
        "estado": asset.estado,
        "numeroSerie": asset.numero_serie,
        "cpu": asset.cpu,
        "ram": asset.ram,
        "almacenamiento": asset.almacenamiento,
        "sistemaOperativo": asset.sistema_operativo,
        "ubicacion": asset.ubicacion,
        "idPersona": asset.id_persona or "",
        "custodio": (
            {
                "nombre": f"{custodio.nombre} {custodio.apellido}",
                "iniciales": person_initials(custodio),
                "departamento": custodio.departamento,
                "ubicacion": custodio.ubicacion,
            }
            if custodio
            else None
        ),
    }


def _choices_id_persona(persona_repo: PersonaRepository) -> list[tuple[str, str]]:
    """Choices de custodio, comunes al form de alta y al de edición."""
    locale = _locale()
    return [(SIN_ASIGNAR, translate("assets.modal_field_assignment_empty", locale))] + [
        (persona.id, f"{persona.nombre} {persona.apellido}") for persona in persona_repo.get_all()
    ]


def _choices_ubicacion() -> list[tuple[str, str]]:
    """Ubicación cerrada: mismas sedes que Persona (ver PersonaUbicacion),
    para que la ubicación de un activo siempre sea una sede real y
    consistente con las de la gente, no texto libre inventado."""
    vacio = translate("assets.field_not_specified", _locale())
    return [("", vacio)] + [(sede, sede) for sede in PersonaUbicacion.OPCIONES]


def _preparar_form_nuevo(form: NuevoActivoForm, persona_repo: PersonaRepository) -> None:
    form.categoria.choices = [(categoria, categoria) for categoria in AssetCategoria.OPCIONES]
    form.ubicacion.choices = _choices_ubicacion()
    form.id_persona.choices = _choices_id_persona(persona_repo)


def _preparar_form_editar(form: EditarActivoForm, persona_repo: PersonaRepository) -> None:
    form.ubicacion.choices = _choices_ubicacion()
    form.id_persona.choices = _choices_id_persona(persona_repo)


def _contexto_index(
    form_nuevo: NuevoActivoForm | None = None,
    form_editar: EditarActivoForm | None = None,
    abrir_modal_nuevo: bool = False,
    id_editar_abierto: str | None = None,
) -> dict:
    db = SessionLocal()
    asset_repo = AssetRepository(db)
    persona_repo = PersonaRepository(db)

    if form_nuevo is None:
        form_nuevo = NuevoActivoForm()
    _preparar_form_nuevo(form_nuevo, persona_repo)

    if form_editar is None:
        form_editar = EditarActivoForm(prefix="editar-")
    _preparar_form_editar(form_editar, persona_repo)

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

    personas_json = [
        {
            "id": persona.id,
            "nombre": f"{persona.nombre} {persona.apellido}",
            "iniciales": person_initials(persona),
            "departamento": persona.departamento,
        }
        for persona in persona_repo.get_all()
    ]

    return {
        "assets": assets,
        "assets_json": [_serializar_asset(asset) for asset in assets],
        "personas_json": personas_json,
        "total_assets": total_assets,
        "total_disponibles": total_disponibles,
        "total_asignados": total_asignados,
        "porcentaje_asignados": porcentaje_asignados,
        "filtros_categoria": filtros_categoria,
        "form": form_nuevo,
        "form_editar": form_editar,
        "abrir_modal_nuevo": abrir_modal_nuevo,
        "id_editar_abierto": id_editar_abierto,
    }


@assets_bp.route("/activos")
def index():
    return render_template("assets.html", **_contexto_index())


@assets_bp.route("/activos/nuevo", methods=["POST"])
def crear():
    db = SessionLocal()
    asset_repo = AssetRepository(db)
    persona_repo = PersonaRepository(db)

    form = NuevoActivoForm()
    _preparar_form_nuevo(form, persona_repo)

    if form.validate_on_submit():
        if form.numero_serie.data and asset_repo.existe_numero_serie(form.numero_serie.data):
            form.numero_serie.errors.append("assets.error_duplicate_serial")
        elif _guardar(
            db,
            form,
            lambda: asset_repo.create(
                nombre=form.nombre.data.strip(),
                categoria=form.categoria.data,
                numero_serie=_limpio(form.numero_serie.data),
                ubicacion=form.ubicacion.data or None,
                id_persona=form.id_persona.data or None,
            ),
        ):
            flash(translate("assets.flash_created", _locale()), "success")
            return redirect(url_for("assets.index"))

    contexto = _contexto_index(form_nuevo=form)
    contexto["abrir_modal_nuevo"] = True
    return render_template("assets.html", **contexto), 400


@assets_bp.route("/activos/<id_asset>/editar", methods=["POST"])
def editar(id_asset):
    db = SessionLocal()
    asset_repo = AssetRepository(db)
    persona_repo = PersonaRepository(db)

    asset = asset_repo.get_by_id(id_asset)
    if asset is None:
        abort(404)

    form = EditarActivoForm(prefix="editar-")
    _preparar_form_editar(form, persona_repo)

    if form.validate_on_submit():
        # nombre/categoría/número de serie no se pueden editar (ver forms.py),
        # así que no hace falta re-chequear duplicado de serie acá: no cambia.
        if _guardar(
            db,
            form,
            lambda: asset_repo.update(
                asset,
                ubicacion=form.ubicacion.data or None,
                id_persona=form.id_persona.data or None,
                cpu=_limpio(form.cpu.data),
                ram=_limpio(form.ram.data),
                almacenamiento=_limpio(form.almacenamiento.data),
                sistema_operativo=_limpio(form.sistema_operativo.data),
            ),
        ):
            flash(translate("assets.flash_updated", _locale()), "success")
            return redirect(url_for("assets.index"))

    contexto = _contexto_index(form_editar=form)
    contexto["id_editar_abierto"] = asset.id
    return render_template("assets.html", **contexto), 400


@assets_bp.route("/activos/<id_asset>/eliminar", methods=["POST"])
def eliminar(id_asset):
    db = SessionLocal()
    asset_repo = AssetRepository(db)

    asset = asset_repo.get_by_id(id_asset)
    if asset is None:
        abort(404)

    nombre = asset.nombre
    asset_repo.delete(asset)
    flash(translate("assets.flash_deleted", _locale()).format(nombre=nombre), "success")
    return redirect(url_for("assets.index"))
