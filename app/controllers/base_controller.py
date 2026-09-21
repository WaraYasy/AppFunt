"""Controller for the dashboard (home) page."""
from flask import Blueprint, render_template
from flask_login import login_required

from app.database import SessionLocal
from app.repositories.asset_repository import AssetRepository
from app.repositories.persona_repository import PersonaRepository

base_bp = Blueprint("base", __name__)


@base_bp.before_request
@login_required
def _requerir_login():
    """Require a logged-in admin for every route in this blueprint."""


@base_bp.route("/")
def index():
    db = SessionLocal()
    asset_repo = AssetRepository(db)
    persona_repo = PersonaRepository(db)

    total_empleados = persona_repo.count_all()
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
