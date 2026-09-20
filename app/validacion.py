"""Validaciones reutilizables a nivel de modelo, para usar con @validates.

Esta es una segunda capa de validación, independiente de la de forms.py.
WTForms valida lo que llega por el formulario web (con mensajes lindos por
campo); esta capa vive en el modelo y corre pase lo que pase el dato llegue
por el form, un script, un test o una futura API — es la que garantiza que
nunca queda guardado un dato inconsistente, no importa quién escriba.

Las funciones de acá no son en sí los @validates: cada modelo define un
método @validates("campo") por columna (SQLAlchemy no permite más de un
validador por columna) y ese método llama a la combinación de reglas que
le correspondan a ese campo.

Los controladores atrapan ValidationError y la muestran como error de ese
campo puntual en el formulario — nunca debería llegar a convertirse en un
500, porque forms.py ya filtra casi todo esto antes; esta capa es la red
de seguridad para lo que no pasa por el form web.
"""
from email_validator import EmailNotValidError, validate_email


class ValidationError(ValueError):
    """Error de validación de un campo de modelo.

    Lleva el nombre del campo (`campo`) además del mensaje, para que quien
    atrapa la excepción (el controlador) pueda mostrarla junto al campo
    correcto del formulario en vez de como un error genérico.
    """

    def __init__(self, campo: str, mensaje: str):
        super().__init__(mensaje)
        self.campo = campo
        self.mensaje = mensaje


def validar_longitud(instancia, campo: str, valor: str | None) -> str | None:
    """Rechaza un string más largo que el ancho de columna declarado.

    Lee el máximo directamente de instancia.__table__ en vez de repetirlo
    a mano: si el día de mañana se cambia el String(N) del modelo, esta
    validación se actualiza sola.
    """
    if valor is None:
        return valor
    columna = instancia.__table__.columns[campo]
    maximo = getattr(columna.type, "length", None)
    if maximo and len(valor) > maximo:
        raise ValidationError(campo, f"No puede superar los {maximo} caracteres.")
    return valor


def validar_no_vacio(campo: str, valor: str | None) -> str:
    if not valor or not valor.strip():
        raise ValidationError(campo, "Este campo es obligatorio.")
    return valor.strip()


def validar_opciones(campo: str, valor: str | None, opciones: list[str]) -> str | None:
    """Para campos tipo enum (categoría, modalidad): si viene un valor,
    tiene que ser uno de los válidos. Vacío/None se deja pasar — que sea
    obligatorio o no lo decide validar_no_vacio, no esta función."""
    if valor and valor not in opciones:
        raise ValidationError(campo, f"Valor inválido: {valor!r}.")
    return valor


def validar_email(campo: str, valor: str | None) -> str | None:
    if not valor:
        return valor
    try:
        return validate_email(valor, check_deliverability=False).normalized
    except EmailNotValidError as exc:
        raise ValidationError(campo, str(exc)) from exc
