from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField, FileField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Length, Optional, Email
from flask_wtf.file import FileAllowed
from wtforms.widgets import DateInput

def validate_year(form, field):
    if field.data and (field.data < 1900 or field.data > 2100):
        raise ValidationError('El año debe ser un valor entre 1900 y 2100.')

class MotoForm(FlaskForm):
    marca = StringField('Marca', validators=[
        DataRequired(message="La marca es requerida."),
        Length(min=2, max=100, message="La marca debe tener entre 2 y 100 caracteres.")
    ])
    modelo = StringField('Modelo', validators=[
        DataRequired(message="El modelo es requerido."),
        Length(min=2, max=100, message="El modelo debe tener entre 2 y 100 caracteres.")
    ])

    año = IntegerField('Año', validators=[
        DataRequired(message="El año es requerido."),
        NumberRange(min=1900, max=2100, message="El año debe estar entre 1900 y 2100."),
        validate_year
    ])

    precio = FloatField('Precio', validators=[
        DataRequired(message="El precio es requerido."),
        NumberRange(min=0.01, message="El precio debe ser mayor que cero.")
    ])
    descripcion = TextAreaField('Descripción', validators=[
        Length(max=500, message="La descripción no puede exceder los 500 caracteres."),
        Optional()
    ])

    imagen = FileField('Imagen de la Moto', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Solo se permiten imágenes (jpg, jpeg, png, gif).'),
        Optional()
    ])

    submit = SubmitField('Guardar Moto')

class InvoiceForm(FlaskForm):
    customer_name = StringField('Nombre del Cliente', validators=[DataRequired(message="El nombre del cliente es requerido."), Length(max=150)])
    customer_address = TextAreaField('Dirección del Cliente', validators=[Optional(), Length(max=500)])
    customer_email = StringField('Email del Cliente', validators=[Optional(), Email(message="Email inválido."), Length(max=150)])
    invoice_date = DateField('Fecha de Factura', validators=[DataRequired(message="La fecha es requerida.")], format='%Y-%m-%d', widget=DateInput())
    items_description = TextAreaField('Descripción de Artículos', validators=[DataRequired(message="La descripción de los artículos es requerida."), Length(max=1000)])
    subtotal_amount = FloatField('Subtotal', validators=[DataRequired(message="El subtotal es requerido."), NumberRange(min=0)])
    tax_rate = FloatField('Tasa de Impuesto (%)', validators=[DataRequired(message="La tasa de impuesto es requerida."), NumberRange(min=0, max=100)], default=0.0)
    tax_amount = FloatField('Monto de Impuesto', validators=[DataRequired(message="El monto de impuesto es requerido."), NumberRange(min=0)], default=0.0)
    total_amount = FloatField('Total', validators=[DataRequired(message="El total es requerido."), NumberRange(min=0)])
    notes = TextAreaField('Notas Adicionales', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Guardar Factura')