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
    assets_por_categoria = asset_repo.count_by_categoria()

    return render_template(
        "index.html",
        total_empleados=total_empleados,
        total_assets=total_assets,
        assets_por_categoria=assets_por_categoria,
    )
