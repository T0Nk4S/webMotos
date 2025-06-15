from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Length # Añadido Length
from flask_wtf.file import FileAllowed

# Función de validación personalizada para el año
def validate_year(form, field):
    # Esta validación es redundante si ya se usa NumberRange, pero la mantengo si la quieres por alguna razón específica.
    if field.data and (field.data < 1900 or field.data > 2100):
        raise ValidationError('El año debe ser un valor entre 1900 y 2100.')

class MotoForm(FlaskForm):
    # ELIMINADO: nombre = StringField('Nombre', validators=[DataRequired(message="El nombre de la moto es requerido.")])
    
    marca = StringField('Marca', validators=[
        DataRequired(message="La marca es requerida."),
        Length(min=2, max=100, message="La marca debe tener entre 2 y 100 caracteres.") # AÑADIDO/AJUSTADO Length
    ])
    modelo = StringField('Modelo', validators=[
        DataRequired(message="El modelo es requerido."),
        Length(min=2, max=100, message="El modelo debe tener entre 2 y 100 caracteres.") # AÑADIDO/AJUSTADO Length
    ])

    # Añadimos la validación personalizada para el año
    año = IntegerField('Año', validators=[
        DataRequired(message="El año es requerido."),
        NumberRange(min=1900, max=2100, message="El año debe estar entre 1900 y 2100."),
        validate_year # Aquí se añade la validación personalizada (si la quieres mantener)
    ])

    precio = FloatField('Precio', validators=[
        DataRequired(message="El precio es requerido."),
        NumberRange(min=0.01, message="El precio debe ser mayor que cero.")
    ])
    descripcion = TextAreaField('Descripción', validators=[
        Length(max=500, message="La descripción no puede exceder los 500 caracteres.") # AÑADIDO: Límite de longitud para descripción
    ])

    imagen = FileField('Imagen de la Moto', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Solo se permiten imágenes (jpg, jpeg, png, gif).')
    ])

    submit = SubmitField('Guardar Moto')