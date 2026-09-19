from flask import Blueprint, render_template

from app.database import SessionLocal
from app.repositories.asset_repository import AssetRepository
from app.repositories.user_repository import UserRepository

base_bp = Blueprint("base", __name__)


@base_bp.route("/")
def index():
    db = SessionLocal()
    asset_repo = AssetRepository(db)
    user_repo = UserRepository(db)

    total_empleados = user_repo.count_all()
    total_assets = asset_repo.count_all()
    total_disponibles = asset_repo.count_disponibles()
    total_asignados = asset_repo.count_asignados()
    assets_recientes = asset_repo.get_recientes(limite=4)

    porcentaje_asignados = (
        round(total_asignados / total_assets * 100) if total_assets else 0
    )

    return render_template(
        "index.html",
        total_empleados=total_empleados,
        total_assets=total_assets,
        total_disponibles=total_disponibles,
        total_asignados=total_asignados,
        porcentaje_asignados=porcentaje_asignados,
        assets_recientes=assets_recientes,
    )
