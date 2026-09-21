"""Forms (Flask-WTF) for creating and editing Assets and Personas.

Choices for data-dependent fields (category, custodian, department,
location, work mode) are filled in by the controller before validation,
not here: this module never touches the database.

Fields don't get a Spanish `label`: the visible text comes from the
template via `t()` (see macros/forms.html), so the form follows the
active language just like the rest of the UI.

Edit forms do NOT inherit from the create forms: they expose fewer
fields on purpose. An asset's name/category/serial number (and a
Persona's name/last name) are identity data set once, at creation, and
they shouldn't change afterward — that's why they only exist in the
create form, never in the edit one.
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, RadioField, SelectField, StringField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    username = StringField(
        validators=[DataRequired(message="forms.error_required"), Length(max=45)]
    )
    password = PasswordField(validators=[DataRequired(message="forms.error_required")])
    remember = BooleanField()


class NuevoActivoForm(FlaskForm):
    nombre = StringField(
        validators=[DataRequired(message="forms.error_required"), Length(max=100)],
    )
    categoria = RadioField(validators=[DataRequired(message="forms.error_required")])
    numero_serie = StringField(validators=[Optional(), Length(max=60)])
    ubicacion = SelectField(validators=[Optional()])
    id_persona = SelectField(validators=[Optional()])


class EditarActivoForm(FlaskForm):
    """Only what makes sense to change over time.

    Location, who has it, and its technical specs. Name/category/serial
    aren't exposed here (see the module docstring).
    """

    ubicacion = SelectField(validators=[Optional()])
    id_persona = SelectField(validators=[Optional()])
    cpu = StringField(validators=[Optional(), Length(max=120)])
    ram = StringField(validators=[Optional(), Length(max=60)])
    almacenamiento = StringField(validators=[Optional(), Length(max=120)])
    sistema_operativo = StringField(validators=[Optional(), Length(max=80)])


class NuevoColaboradorForm(FlaskForm):
    nombre = StringField(
        validators=[DataRequired(message="forms.error_required"), Length(max=45)]
    )
    apellido = StringField(
        validators=[DataRequired(message="forms.error_required"), Length(max=45)]
    )
    email = StringField(
        validators=[Optional(), Email(message="forms.error_email"), Length(max=120)]
    )
    departamento = SelectField(validators=[Optional()])
    ubicacion = SelectField(validators=[Optional()])
    modalidad = RadioField(validators=[Optional()], default="")


class EditarColaboradorForm(FlaskForm):
    """Only what makes sense to change: contact and organizational data.

    Name/last name aren't exposed here (see the module docstring).
    """

    email = StringField(
        validators=[Optional(), Email(message="forms.error_email"), Length(max=120)]
    )
    departamento = SelectField(validators=[Optional()])
    ubicacion = SelectField(validators=[Optional()])
    modalidad = RadioField(validators=[Optional()], default="")
