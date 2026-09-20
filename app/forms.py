"""Formularios (Flask-WTF) para las altas de Activos y Personal.

Los choices de campos dependientes de datos (categoría, custodio, modalidad)
se completan en el controlador antes de validar, no acá: este módulo no
toca la base de datos.

Los campos no llevan `label` en español: el texto visible se pasa desde
la plantilla vía `t()` (ver macros/forms.html), para que el formulario
respete el idioma activo igual que el resto de la UI.
"""
from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, StringField
from wtforms.validators import DataRequired, Email, Length, Optional


class NuevoActivoForm(FlaskForm):
    nombre = StringField(
        validators=[DataRequired(message="forms.error_required"), Length(max=100)],
    )
    categoria = RadioField(validators=[DataRequired(message="forms.error_required")])
    numero_serie = StringField(validators=[Optional(), Length(max=60)])
    ubicacion = StringField(validators=[Optional(), Length(max=120)])
    id_personal = SelectField(validators=[Optional()])


class NuevoColaboradorForm(FlaskForm):
    nombre = StringField(validators=[DataRequired(message="forms.error_required"), Length(max=45)])
    apellido = StringField(validators=[DataRequired(message="forms.error_required"), Length(max=45)])
    email = StringField(validators=[Optional(), Email(message="forms.error_email"), Length(max=120)])
    rol = StringField(validators=[Optional(), Length(max=80)])
    departamento = StringField(validators=[Optional(), Length(max=80)])
    ubicacion = StringField(validators=[Optional(), Length(max=120)])
    modalidad = RadioField(validators=[Optional()], default="")
