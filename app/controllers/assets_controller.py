"""Controlador para la vista de Activos (inventario de hardware)."""
from flask import Blueprint, render_template

from app.database import SessionLocal
from app.models.assets import Asset, AssetCategoria
from app.repositories.asset_repository import AssetRepository
from app.template_helpers import asset_icon, user_initials

assets_bp = Blueprint("assets", __name__)

# Categorías con acceso rápido mediante pastillas de filtro en la vista,
# junto con la clave de traducción de su etiqueta.
CATEGORIAS_FILTRO = [
    (AssetCategoria.PORTATIL, "assets.filter_portatil"),
    (AssetCategoria.SERVIDOR, "assets.filter_servidor"),
    (AssetCategoria.REDES, "assets.filter_redes"),
    (AssetCategoria.PERIFERICO, "assets.filter_periferico"),
]


def _serializar_asset(asset: Asset) -> dict:
    """Convierte un Asset (y su usuario, si tiene) en un dict listo para el panel lateral."""
    usuario = asset.usuario
    return {
        "id": asset.id,
        "codigo": asset.codigo,
        "nombre": asset.nombre,
        "categoria": asset.categoria,
        "icono": asset_icon(asset),
        "asignado": bool(asset.id_user),
        "estado": asset.estado,
        "numeroSerie": asset.numero_serie,
        "cpu": asset.cpu,
        "ram": asset.ram,
        "almacenamiento": asset.almacenamiento,
        "sistemaOperativo": asset.sistema_operativo,
        "garantia": asset.garantia,
        "usuario": (
            {
                "nombre": f"{usuario.nombre} {usuario.apellido}",
                "iniciales": user_initials(usuario),
                "rol": usuario.rol,
                "departamento": usuario.departamento,
                "ubicacion": usuario.ubicacion,
            }
            if usuario
            else None
        ),
    }


@assets_bp.route("/activos")
def index():
    db = SessionLocal()
    asset_repo = AssetRepository(db)

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

    return render_template(
        "assets.html",
        assets=assets,
        assets_json=[_serializar_asset(asset) for asset in assets],
        total_assets=total_assets,
        total_disponibles=total_disponibles,
        total_asignados=total_asignados,
        porcentaje_asignados=porcentaje_asignados,
        filtros_categoria=filtros_categoria,
    )
