"""Funciones auxiliares expuestas a las plantillas Jinja."""
from app.models.assets import Asset, AssetCategoria
from app.models.users import Users

ASSET_ICONS = {
    AssetCategoria.PORTATIL: "laptop",
    AssetCategoria.SOBREMESA: "desktop_windows",
    AssetCategoria.SERVIDOR: "dns",
    AssetCategoria.REDES: "hub",
    AssetCategoria.MOVIL: "smartphone",
    AssetCategoria.PERIFERICO: "keyboard",
    AssetCategoria.OTRO: "devices_other",
}


def estado_dot_class(asset: Asset) -> str:
    """Clase CSS para el indicador de estado de un asset en listados."""
    if asset.id_user:
        return "movement-item__dot--assigned"
    if asset.estado == "Disponible":
        return "movement-item__dot--available"
    return ""


def asset_icon(asset: Asset) -> str:
    """Icono de Material Symbols asociado a la categoría del asset."""
    return ASSET_ICONS.get(asset.categoria, "devices_other")


def asset_status_modifier(asset: Asset) -> str:
    """Modificador CSS ('assigned' | 'available' | 'neutral') según el estado del asset."""
    if asset.id_user:
        return "assigned"
    if asset.estado == "Disponible":
        return "available"
    return "neutral"


def user_initials(user: Users | None) -> str:
    """Iniciales de un usuario para mostrar en un avatar. '—' si no hay usuario."""
    if not user:
        return "—"
    iniciales = (user.nombre[:1] + user.apellido[:1]).upper()
    return iniciales or "—"


def init_app(app):
    app.jinja_env.globals["estado_dot_class"] = estado_dot_class
    app.jinja_env.globals["asset_icon"] = asset_icon
    app.jinja_env.globals["asset_status_modifier"] = asset_status_modifier
    app.jinja_env.globals["user_initials"] = user_initials
