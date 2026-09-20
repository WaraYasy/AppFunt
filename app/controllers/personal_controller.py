"""Controlador para la vista de Personal (directorio de colaboradores)."""
from flask import Blueprint, abort, flash, redirect, render_template, session, url_for
from flask_login import login_required

from app.database import SessionLocal
from app.forms import EditarColaboradorForm, NuevoColaboradorForm
from app.i18n import DEFAULT_LOCALE, translate
from app.models.assets import Asset
from app.models.personal import Personal, PersonalDepartamento, PersonalModalidad, PersonalUbicacion
from app.repositories.asset_repository import AssetRepository
from app.repositories.personal_repository import PersonalRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.template_helpers import asset_icon, person_initials
from app.validacion import ValidationError

personal_bp = Blueprint("personal", __name__)


@personal_bp.before_request
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


def _serializar_asset_asignado(asset: Asset) -> dict:
    return {
        "id": asset.id,
        "nombre": asset.nombre,
        "categoria": asset.categoria,
        "icono": asset_icon(asset),
        "numeroSerie": asset.numero_serie,
        "codigo": asset.codigo,
    }


def _serializar_persona(persona: Personal, ids_con_cuenta: set[str]) -> dict:
    return {
        "id": persona.id,
        "codigo": persona.codigo,
        "nombre": f"{persona.nombre} {persona.apellido}",
        "iniciales": person_initials(persona),
        "email": persona.email,
        "departamento": persona.departamento,
        "ubicacion": persona.ubicacion,
        "modalidad": persona.modalidad,
        "incorporacion": persona.created.strftime("%d/%m/%Y"),
        "tieneActivos": bool(persona.assets),
        "cantidadActivos": len(persona.assets),
        "activos": [_serializar_asset_asignado(asset) for asset in persona.assets],
        "tieneCuenta": persona.id in ids_con_cuenta,
    }


def _preparar_formulario(form) -> None:
    """Completa los choices (departamento, ubicación, modalidad) de un
    formulario de Personal. Alta y edición comparten estos tres campos."""
    locale = _locale()
    vacio = translate("personal.field_not_specified", locale)
    form.departamento.choices = [("", vacio)] + [
        (depto, depto) for depto in PersonalDepartamento.OPCIONES
    ]
    form.ubicacion.choices = [("", vacio)] + [
        (sede, sede) for sede in PersonalUbicacion.OPCIONES
    ]
    form.modalidad.choices = [("", vacio)] + [
        (modalidad, modalidad) for modalidad in PersonalModalidad.OPCIONES
    ]


def _contexto_index(
    form_nuevo: NuevoColaboradorForm | None = None,
    form_editar: EditarColaboradorForm | None = None,
    abrir_modal_nuevo: bool = False,
    id_editar_abierto: str | None = None,
) -> dict:
    db = SessionLocal()
    personal_repo = PersonalRepository(db)
    usuario_repo = UsuarioRepository(db)

    if form_nuevo is None:
        form_nuevo = NuevoColaboradorForm()
    _preparar_formulario(form_nuevo)

    if form_editar is None:
        form_editar = EditarColaboradorForm(prefix="editar-")
    _preparar_formulario(form_editar)

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

    ids_con_cuenta = usuario_repo.ids_personal_con_cuenta()

    return {
        "personal": personal,
        "personal_json": [_serializar_persona(persona, ids_con_cuenta) for persona in personal],
        "total_empleados": total_empleados,
        "con_activos": con_activos,
        "sin_activos": sin_activos,
        "porcentaje_con_activos": porcentaje_con_activos,
        "filtros_personal": filtros_personal,
        "form": form_nuevo,
        "form_editar": form_editar,
        "abrir_modal_nuevo": abrir_modal_nuevo,
        "id_editar_abierto": id_editar_abierto,
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
        elif _guardar(
            db,
            form,
            lambda: personal_repo.create(
                nombre=form.nombre.data.strip(),
                apellido=form.apellido.data.strip(),
                email=_limpio(form.email.data),
                departamento=form.departamento.data or None,
                ubicacion=form.ubicacion.data or None,
                modalidad=form.modalidad.data or None,
            ),
        ):
            flash(translate("personal.flash_created", _locale()), "success")
            return redirect(url_for("personal.index"))

    contexto = _contexto_index(form_nuevo=form)
    contexto["abrir_modal_nuevo"] = True
    return render_template("personal.html", **contexto), 400


@personal_bp.route("/personal/<id_persona>/editar", methods=["POST"])
def editar(id_persona):
    db = SessionLocal()
    personal_repo = PersonalRepository(db)

    persona = personal_repo.get_by_id(id_persona)
    if persona is None:
        abort(404)

    form = EditarColaboradorForm(prefix="editar-")
    _preparar_formulario(form)

    if form.validate_on_submit():
        # nombre/apellido no se pueden editar (ver forms.py).
        if form.email.data and personal_repo.existe_email(form.email.data, excluir_id=persona.id):
            form.email.errors.append("personal.error_duplicate_email")
        elif _guardar(
            db,
            form,
            lambda: personal_repo.update(
                persona,
                email=_limpio(form.email.data),
                departamento=form.departamento.data or None,
                ubicacion=form.ubicacion.data or None,
                modalidad=form.modalidad.data or None,
            ),
        ):
            flash(translate("personal.flash_updated", _locale()), "success")
            return redirect(url_for("personal.index"))

    contexto = _contexto_index(form_editar=form)
    contexto["id_editar_abierto"] = persona.id
    return render_template("personal.html", **contexto), 400


@personal_bp.route("/personal/<id_persona>/eliminar", methods=["POST"])
def eliminar(id_persona):
    db = SessionLocal()
    personal_repo = PersonalRepository(db)
    usuario_repo = UsuarioRepository(db)

    persona = personal_repo.get_by_id(id_persona)
    if persona is None:
        abort(404)

    nombre = f"{persona.nombre} {persona.apellido}"

    # Si tiene una cuenta de acceso vinculada, no se borra: en MySQL la FK
    # (Usuario.id_personal, sin ondelete) rechazaría el DELETE igual, pero acá
    # lo cortamos antes con un mensaje claro en vez de dejar que explote un
    # IntegrityError sin capturar. La cuenta se borra aparte, a mano.
    if usuario_repo.get_by_personal(persona.id) is not None:
        flash(translate("personal.error_has_account", _locale()).format(nombre=nombre), "error")
        return redirect(url_for("personal.index"))

    huerfanos = personal_repo.delete(persona)

    if huerfanos:
        mensaje = translate("personal.flash_deleted_with_orphans", _locale()).format(
            nombre=nombre, n=huerfanos
        )
        flash(mensaje, "warning")
    else:
        mensaje = translate("personal.flash_deleted", _locale()).format(nombre=nombre)
        flash(mensaje, "success")

    return redirect(url_for("personal.index"))


@personal_bp.route("/personal/<id_persona>/activos/<id_asset>/quitar", methods=["POST"])
def quitar_activo(id_persona, id_asset):
    """Desasigna un activo puntual de esta persona (no lo elimina: el activo
    queda sin custodio, disponible). Se llama desde el drawer de Personal,
    con confirmación previa del lado del cliente."""
    db = SessionLocal()
    asset_repo = AssetRepository(db)

    asset = asset_repo.get_by_id(id_asset)
    if asset is None or asset.id_personal != id_persona:
        abort(404)

    nombre_asset = asset.nombre
    asset_repo.update(asset, id_personal=None)
    flash(translate("personal.flash_asset_unassigned", _locale()).format(nombre=nombre_asset), "success")
    return redirect(url_for("personal.index"))
