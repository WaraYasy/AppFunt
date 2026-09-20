"""Formularios (Flask-WTF) para las altas/ediciones de Activos y Personal.

Los choices de campos dependientes de datos (categoría, custodio,
departamento, ubicación, modalidad) se completan en el controlador antes
de validar, no acá: este módulo no toca la base de datos.

Los campos no llevan `label` en español: el texto visible se pasa desde
la plantilla vía `t()` (ver macros/forms.html), para que el formulario
respete el idioma activo igual que el resto de la UI.

Los forms de edición NO heredan de los de alta: a propósito exponen menos
campos. Nombre/categoría/número de serie de un activo (y nombre/apellido
de una persona) son datos de identidad que se fijan una vez, al dar de
alta, y no tiene sentido que cambien después — por eso solo existen en
el form de alta, nunca en el de edición.
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, RadioField, SelectField, StringField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired(message="forms.error_required"), Length(max=45)])
    password = PasswordField(validators=[DataRequired(message="forms.error_required")])
    remember = BooleanField()


class NuevoActivoForm(FlaskForm):
    nombre = StringField(
        validators=[DataRequired(message="forms.error_required"), Length(max=100)],
    )
    categoria = RadioField(validators=[DataRequired(message="forms.error_required")])
    numero_serie = StringField(validators=[Optional(), Length(max=60)])
    ubicacion = SelectField(validators=[Optional()])
    id_personal = SelectField(validators=[Optional()])


class EditarActivoForm(FlaskForm):
    """Solo lo que tiene sentido que cambie con el tiempo: dónde está, quién
    lo tiene, y su ficha técnica. Nombre/categoría/serie no se exponen acá
    (ver docstring del módulo); garantía tampoco: no aporta lo suficiente
    como para justificar el campo."""

    ubicacion = SelectField(validators=[Optional()])
    id_personal = SelectField(validators=[Optional()])
    cpu = StringField(validators=[Optional(), Length(max=120)])
    ram = StringField(validators=[Optional(), Length(max=60)])
    almacenamiento = StringField(validators=[Optional(), Length(max=120)])
    sistema_operativo = StringField(validators=[Optional(), Length(max=80)])


class NuevoColaboradorForm(FlaskForm):
    nombre = StringField(validators=[DataRequired(message="forms.error_required"), Length(max=45)])
    apellido = StringField(validators=[DataRequired(message="forms.error_required"), Length(max=45)])
    email = StringField(validators=[Optional(), Email(message="forms.error_email"), Length(max=120)])
    departamento = SelectField(validators=[Optional()])
    ubicacion = SelectField(validators=[Optional()])
    modalidad = RadioField(validators=[Optional()], default="")


class EditarColaboradorForm(FlaskForm):
    """Solo lo que tiene sentido que cambie: contacto y datos organizativos.
    Nombre/apellido no se exponen acá (ver docstring del módulo)."""

    email = StringField(validators=[Optional(), Email(message="forms.error_email"), Length(max=120)])
    departamento = SelectField(validators=[Optional()])
    ubicacion = SelectField(validators=[Optional()])
    modalidad = RadioField(validators=[Optional()], default="")
