# models.py
# Define los modelos de la base de datos para la aplicación MotoShop.

# IMPORTANTE: Importa 'db' desde el nuevo archivo 'extensions.py'
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Modelo para las motocicletas en el catálogo.
class Moto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    año = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Moto {self.marca} {self.modelo}>'

# Modelo para los usuarios (administradores en este caso).
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Modelo: Invoice (Factura)
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_address = db.Column(db.Text, nullable=True)
    customer_email = db.Column(db.String(150), nullable=True)
    items_description = db.Column(db.Text, nullable=False)
    subtotal_amount = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, nullable=False, default=0.0)
    tax_amount = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Invoice {self.invoice_number} - {self.customer_name}>'