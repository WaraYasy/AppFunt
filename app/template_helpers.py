"""Funciones auxiliares expuestas a las plantillas Jinja."""
from app.models.assets import Asset


def estado_dot_class(asset: Asset) -> str:
    """Clase CSS para el indicador de estado de un asset en listados."""
    if asset.id_user:
        return "movement-item__dot--assigned"
    if asset.estado == "Disponible":
        return "movement-item__dot--available"
    return ""


def init_app(app):
    app.jinja_env.globals["estado_dot_class"] = estado_dot_class
