"""Helper functions exposed to Jinja templates."""

from app.models.assets import Asset, AssetCategoria
from app.models.persona import Persona

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
    """Return the CSS class for an asset's status dot in the movements list.

    Kept separate from asset_status_modifier because the two views use
    different class naming: this one returns a full BEM class
    (`movement-item__dot--...`), the other a bare modifier word meant to
    be combined with a different block name.
    """
    if asset.id_persona:
        return "movement-item__dot--assigned"
    if asset.estado == "Disponible":
        return "movement-item__dot--available"
    return ""


def asset_icon(asset: Asset) -> str:
    """Return the Material Symbols icon name for the asset's category."""
    return ASSET_ICONS.get(asset.categoria, "devices_other")


def asset_status_modifier(asset: Asset) -> str:
    """Return a bare CSS modifier ('assigned' | 'available' | 'neutral') for the asset card.

    See estado_dot_class for why this isn't reused there instead.
    """
    if asset.id_persona:
        return "assigned"
    if asset.estado == "Disponible":
        return "available"
    return "neutral"


def person_initials(persona: Persona | None) -> str:
    """Return a Persona's initials for an avatar. Returns '—' if `persona` is None."""
    if not persona:
        return "—"
    iniciales = (persona.nombre[:1] + persona.apellido[:1]).upper()
    return iniciales or "—"


def init_app(app):
    app.jinja_env.globals["estado_dot_class"] = estado_dot_class
    app.jinja_env.globals["asset_icon"] = asset_icon
    app.jinja_env.globals["asset_status_modifier"] = asset_status_modifier
    app.jinja_env.globals["person_initials"] = person_initials
