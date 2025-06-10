from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from flask_wtf.file import FileAllowed  # Para validación de archivos

# Función de validación personalizada para el año
def validate_year(form, field):
    if field.data and (field.data < 1900 or field.data > 2100):  # Rango de años razonable
        raise ValidationError('El año debe ser un valor entre 1900 y 2100.')

class MotoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message="El nombre de la moto es requerido.")])
    marca = StringField('Marca', validators=[DataRequired(message="La marca es requerida.")])
    modelo = StringField('Modelo', validators=[DataRequired(message="El modelo es requerido.")])

    # Añadimos la validación personalizada para el año
    año = IntegerField('Año', validators=[
        DataRequired(message="El año es requerido."),
        NumberRange(min=1900, max=2100, message="El año debe estar entre 1900 y 2100."),
        validate_year  # Aquí se añade la validación personalizada
    ])

    precio = FloatField('Precio', validators=[
        DataRequired(message="El precio es requerido."),
        NumberRange(min=0.01, message="El precio debe ser mayor que cero.")
    ])
    descripcion = TextAreaField('Descripción')

    # El campo de imagen es opcional para la edición, por eso no tiene FileRequired().
    # Si quieres que sea obligatorio al añadir, podrías añadir FileRequired() aquí
    # o manejar esa lógica en la ruta 'add_moto'.
    imagen = FileField('Imagen de la Moto', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Solo se permiten imágenes (jpg, jpeg, png, gif).')
    ])

    submit = SubmitField('Guardar Moto')