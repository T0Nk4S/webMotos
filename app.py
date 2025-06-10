import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

# Importar el formulario que definiremos en forms.py
from forms import MotoForm

# --- Configuración de la Aplicación Flask ---
app = Flask(__name__)

# Clave secreta para seguridad de sesiones y formularios WTForms
# ¡IMPORTANTE! CAMBIA ESTA CLAVE EN UN ENTORNO DE PRODUCCIÓN
# Genera una clave aleatoria larga y compleja, por ejemplo, usando:
# import secrets
# secrets.token_hex(32)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_key_change_this_in_production_1234567890')

# Configuración de la base de datos SQLite
# Utiliza os.path.abspath para asegurar que la ruta a la DB es absoluta
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'motos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactiva el seguimiento de modificaciones de objetos
db = SQLAlchemy(app)

# Configuración para subida de imágenes
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'images', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Inicializar CSRFProtect
csrf = CSRFProtect(app)

# --- Modelo de la Base de Datos ---
class Moto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    año = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(200), nullable=True)  # Ruta relativa a static/

    def __repr__(self):
        return f'<Moto {self.nombre} {self.modelo}>'

# --- Funciones Auxiliares para Archivos ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- Rutas de la Aplicación ---
@app.route('/')
def index():
    try:
        motos_carrusel = Moto.query.limit(5).all()
    except Exception as e:
        print(f"Error al cargar motos para el carrusel: {e}")
        motos_carrusel = []
    return render_template('index.html', motos_carrusel=motos_carrusel)

@app.route('/catalogo-completo')
def catalogo_completo():
    all_motos = Moto.query.all()
    return render_template('catalogo_completo.html', motos=all_motos)

@app.route('/admin')
def admin_motos():
    motos = Moto.query.all()
    return render_template('admin_motos.html', motos=motos)

@app.route('/add-moto', methods=['GET', 'POST'])
def add_moto():
    form = MotoForm()
    if form.validate_on_submit():
        imagen_filename = None
        if form.imagen.data:
            if allowed_file(form.imagen.data.filename):
                filename = secure_filename(form.imagen.data.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.imagen.data.save(file_path)
                imagen_filename = f'images/uploads/{filename}'
            else:
                flash('Tipo de archivo no permitido para la imagen.', 'danger')
                return render_template('add_edit_moto.html', form=form, moto=None)

        nueva_moto = Moto(
            nombre=form.nombre.data,
            marca=form.marca.data,
            modelo=form.modelo.data,
            año=form.año.data,
            precio=form.precio.data,
            descripcion=form.descripcion.data,
            imagen_url=imagen_filename
        )
        db.session.add(nueva_moto)
        db.session.commit()
        flash('¡Moto añadida exitosamente!', 'success')
        return redirect(url_for('admin_motos'))

    return render_template('add_edit_moto.html', form=form, moto=None)

# --- Inicio de la Aplicación ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tablas de la base de datos creadas si no existían.")

    app.run(debug=True)