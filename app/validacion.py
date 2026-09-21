"""Reusable model-level validations, meant to be used with @validates.

This is a second validation layer, independent from the one in forms.py.
WTForms validates what comes from the web form (with nice per-field
messages). This layer lives in the model and runs no matter where the
data comes from — the form, a script, a test, or a future API. It makes
sure inconsistent data never gets saved, no matter who writes it.

The functions here aren't the @validates methods themselves. Each model
defines one @validates("field") method per column (SQLAlchemy doesn't
allow more than one validator per column), and that method calls
whichever combination of rules applies to that field.

Controllers catch ValidationError and show it as an error on that
specific form field. It should never turn into a 500, since forms.py
already filters most of this beforehand — this layer is the safety net
for data that doesn't go through the web form.
"""

from email_validator import EmailNotValidError, validate_email


class ValidationError(ValueError):
    """Validation error for a model field.

    Carries the field name (`campo`) along with the message, so whoever
    catches the exception (the controller) can show it next to the right
    form field instead of as a generic error.
    """

    def __init__(self, campo: str, mensaje: str):
        super().__init__(mensaje)
        self.campo = campo
        self.mensaje = mensaje


def validar_longitud(instancia, campo: str, valor: str | None) -> str | None:
    """Reject a string longer than the declared column width.

    Reads the max length directly from instancia.__table__ instead of
    repeating it by hand: if the model's String(N) changes later, this
    validation updates itself.
    """
    if valor is None:
        return valor
    columna = instancia.__table__.columns[campo]
    maximo = getattr(columna.type, "length", None)
    if maximo and len(valor) > maximo:
        raise ValidationError(campo, f"No puede superar los {maximo} caracteres.")
    return valor


def validar_no_vacio(campo: str, valor: str | None) -> str:
    """Raise ValidationError if the value is empty or blank.

    Returns the value stripped of surrounding whitespace.
    """
    if not valor or not valor.strip():
        raise ValidationError(campo, "Este campo es obligatorio.")
    return valor.strip()


def validar_opciones(campo: str, valor: str | None, opciones: list[str]) -> str | None:
    """Check that the value is one of `opciones`, for enum-like fields.

    Empty or None is allowed through — whether the field is required is
    decided by validar_no_vacio, not by this function.
    """
    if valor and valor not in opciones:
        raise ValidationError(campo, f"Valor inválido: {valor!r}.")
    return valor


def validar_email(campo: str, valor: str | None) -> str | None:
    """Return None if `valor` is empty, otherwise validate and normalize it.

    Raises ValidationError if the email is not valid.
    """
    if not valor:
        return valor
    try:
        return validate_email(valor, check_deliverability=False).normalized
    except EmailNotValidError as exc:
        raise ValidationError(campo, str(exc)) from exc
