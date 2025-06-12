import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
import math
from sqlalchemy import func, desc

# Importar el formulario que definiremos en forms.py
from forms import MotoForm

# --- Configuración de la Aplicación Flask ---
app = Flask(__name__)

# Clave secreta para seguridad de sesiones y formularios WTForms
# ¡IMPORTANTE! CAMBIA ESTA CLAVE EN UN ENTORNO DE PRODUCCIÓN
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_key_change_this_in_production_1234567890')

# Configuración de la base de datos SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'motos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    imagen_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Moto {self.nombre} {self.modelo}>'

# --- Funciones Auxiliares para Archivos ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- DEFINICIÓN DE MARCAS PARA EL FILTRO ---
ALL_AVAILABLE_BRANDS = sorted([
    "Harley-Davidson", "Kawasaki", "Yamaha", "Honda", "Triumph", "Suzuki",
    "Ducati", "BMW", "Royal Enfield", "Benelli", "CFMoto", "Hero", "Keeway",
    "KTM", "Motomel", "Serna", "Super Soco", "TVS", "UM", "Vespa"
])

# --- Rutas de la Aplicación ---
@app.route('/')
def index():
    motos_carrusel = []
    try:
        # **CAMBIO DE LÓGICA:** Obtener las últimas 8 motos añadidas (las de mayor ID)
        # Esto proporcionará una muestra más variada y reciente para el carrusel de la página de inicio.
        motos_carrusel = Moto.query.order_by(desc(Moto.id)).limit(8).all()
        
        # Opcional: Si deseas un orden diferente (ej. aleatorio o por marca/precio)
        # import random
        # random.shuffle(motos_carrusel) 

    except Exception as e:
        print(f"Error al cargar motos para el carrusel: {e}")
        motos_carrusel = []
    
    return render_template('index.html', motos_carrusel=motos_carrusel)

@app.route('/catalogo-completo')
def catalogo_completo():
    query = Moto.query

    search_query = request.args.get('search_query', '').strip()
    brand_filter = request.args.get('brand_filter', '').strip()
    year_filter = request.args.get('year_filter', '').strip()
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Moto.nombre.ilike(search_pattern)) |
            (Moto.marca.ilike(search_pattern)) |
            (Moto.modelo.ilike(search_pattern))
        )
    
    if brand_filter:
        query = query.filter(Moto.marca == brand_filter)

    if year_filter and year_filter.isdigit():
        query = query.filter(Moto.año == int(year_filter))

    if price_min is not None:
        query = query.filter(Moto.precio >= price_min)

    if price_max is not None:
        query = query.filter(Moto.precio <= price_max)

    filtered_motos = query.all()
    total_motos = len(filtered_motos)

    page = request.args.get('page', 1, type=int)
    per_page = 9
    total_pages = math.ceil(total_motos / per_page)
    
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    elif total_pages == 0:
        page = 1

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_motos = filtered_motos[start_index:end_index]

    available_brands = ALL_AVAILABLE_BRANDS 
    available_years = sorted(list(set(moto.año for moto in db.session.query(Moto.año).distinct())), reverse=True)

    return render_template('catalogo_completo.html', 
                            motos=paginated_motos,
                            page=page,
                            total_pages=total_pages,
                            search_query=search_query,
                            brand_filter=brand_filter,
                            year_filter=year_filter,
                            price_min=price_min,
                            price_max=price_max,
                            available_brands=available_brands,
                            available_years=available_years
                        )

@app.route('/moto/<int:moto_id>')
def moto_detalle(moto_id):
    moto = db.session.get(Moto, moto_id)
    if not moto:
        flash('Motocicleta no encontrada.', 'danger')
        return redirect(url_for('catalogo_completo'))
    return render_template('moto_detalle.html', moto=moto)

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

@app.route('/edit-moto/<int:moto_id>', methods=['GET', 'POST'])
def edit_moto(moto_id):
    moto = db.session.get(Moto, moto_id)
    if not moto:
        flash(f'La moto con ID {moto_id} no fue encontrada.', 'danger')
        return redirect(url_for('admin_motos'))

    form = MotoForm(obj=moto)

    if form.validate_on_submit():
        if form.imagen.data:
            if allowed_file(form.imagen.data.filename):
                if moto.imagen_url and os.path.exists(os.path.join(app.root_path, 'static', moto.imagen_url)):
                    try:
                        os.remove(os.path.join(app.root_path, 'static', moto.imagen_url))
                    except OSError as e:
                        print(f"Error al eliminar la imagen antigua: {e}")

                filename = secure_filename(form.imagen.data.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.imagen.data.save(file_path)
                moto.imagen_url = f'images/uploads/{filename}'
            else:
                flash('Tipo de archivo no permitido para la nueva imagen.', 'danger')
                return render_template('add_edit_moto.html', form=form, moto=moto)

        moto.nombre = form.nombre.data
        moto.marca = form.marca.data
        moto.modelo = form.modelo.data
        moto.año = form.año.data
        moto.precio = form.precio.data
        moto.descripcion = form.descripcion.data

        db.session.commit()
        flash('¡Moto actualizada exitosamente!', 'success')
        return redirect(url_for('admin_motos'))

    return render_template('add_edit_moto.html', form=form, moto=moto)

@app.route('/delete-moto/<int:moto_id>', methods=['POST'])
def delete_moto(moto_id):
    moto = db.session.get(Moto, moto_id)
    if not moto:
        flash(f'La moto con ID {moto_id} no fue encontrada.', 'danger')
        return redirect(url_for('admin_motos'))

    if moto.imagen_url:
        image_path = os.path.join(app.root_path, 'static', moto.imagen_url)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"Imagen eliminada: {image_path}")
            except OSError as e:
                print(f"Error al eliminar la imagen: {e}")

    db.session.delete(moto)
    db.session.commit()
    flash('¡Moto eliminada exitosamente!', 'success')

    return redirect(url_for('admin_motos'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tablas de la base de datos creadas si no existían.")

        if not Moto.query.first():
            print("Base de datos vacía, añadiendo datos de ejemplo...")
            sample_motos = [
                Moto(nombre="Leoncino 500", marca="Benelli", modelo="BJ500", año=2023, precio=6999.00, descripcion="Una scrambler moderna con diseño italiano y un motor bicilíndrico emocionante.", imagen_url="images/uploads/benelli.png"),
                Moto(nombre="650NK", marca="CFMoto", modelo="CF650NK", año=2024, precio=6499.00, descripcion="Naked de media cilindrada, potente y ágil, con un estilo agresivo.", imagen_url="images/uploads/cfmoto.png"),
                Moto(nombre="Xtreme 160R", marca="Hero", modelo="Xtreme160R", año=2023, precio=2500.00, descripcion="Moto deportiva urbana con un rendimiento ágil y eficiente para el día a día.", imagen_url="images/uploads/hero.png"),
                Moto(nombre="CB1000R", marca="Honda", modelo="CB1000R", año=2024, precio=12999.00, descripcion="Neo Sports Café, una naked de diseño minimalista con el potente motor de la Fireblade.", imagen_url="images/uploads/honda.png"),
                Moto(nombre="Z900RS", marca="Kawasaki", modelo="Z900RS", año=2023, precio=11999.00, descripcion="Un tributo moderno a la Z1 original, con un estilo retro y un rendimiento de vanguardia.", imagen_url="images/uploads/kawasaki.png"),
                Moto(nombre="K-Light 202", marca="Keeway", modelo="K-Light202", año=2022, precio=3199.00, descripcion="Cruiser compacta con un estilo clásico y fácil manejo para la ciudad.", imagen_url="images/uploads/keeway.png"),
                Moto(nombre="1290 Super Duke R", marca="KTM", modelo="1290 SDR", año=2024, precio=19999.00, descripcion="La 'Bestia' de KTM, una hypernaked con un motor V-Twin brutal y componentes de alta gama.", imagen_url="images/uploads/ktm.png"),
                Moto(nombre="Skua 250", marca="Motomel", modelo="Skua250", año=2023, precio=3499.00, descripcion="Una moto trail versátil, diseñada para afrontar terrenos variados con comodidad y robustez.", imagen_url="images/uploads/motomel.png"),
                Moto(nombre="Continental GT 650", marca="Royal Enfield", modelo="CGT650", año=2024, precio=7499.00, descripcion="Cafe racer clásica con un diseño atemporal y un motor bicilíndrico suave.", imagen_url="images/uploads/royalenfield.png"),
                Moto(nombre="RX400", marca="Serna", modelo="RX400", año=2023, precio=4200.00, descripcion="Trail de aventura, robusta y preparada para explorar cualquier camino, con un buen equilibrio entre carretera y off-road.", imagen_url="images/uploads/serna.png"),
                Moto(nombre="TC Max", marca="Super Soco", modelo="TCMax", año=2024, precio=5499.00, descripcion="Motocicleta eléctrica de estilo urbano y prestaciones sorprendentes, ideal para la movilidad sostenible.", imagen_url="images/uploads/supersoco.png"),
                Moto(nombre="GSX-R1000R", marca="Suzuki", modelo="GSX-R1000R", año=2023, precio=16000.00, descripcion="Superbike pura, diseñada para ofrecer el máximo rendimiento en pista y una experiencia de conducción inigualable.", imagen_url="images/uploads/suzuki.png"),
                Moto(nombre="Apache RR 310", marca="TVS", modelo="RR310", año=2024, precio=4500.00, descripcion="Sportbike carenada con un diseño agresivo y tecnología inspirada en las carreras.", imagen_url="images/uploads/tvs.png"),
                Moto(nombre="DSR Adventure 200", marca="UM", modelo="DSR200", año=2023, precio=3800.00, descripcion="Una motocicleta de doble propósito diseñada para la aventura, con un rendimiento sólido en carretera y fuera de ella.", imagen_url="images/uploads/um.png"),
                Moto(nombre="GTS 300 SuperTech", marca="Vespa", modelo="GTS300", año=2024, precio=8500.00, descripcion="El scooter más potente de Vespa, combina la conectividad y la tecnología con el icónico estilo italiano.", imagen_url="images/uploads/vespa.png"),
                Moto(nombre="Panigale V4 R", marca="Ducati", modelo="V4R", año=2024, precio=42995.00, descripcion="La Panigale V4 R es la expresión máxima de la deportividad Ducati, con un motor de 998 cc derivado de MotoGP.", imagen_url="images/uploads/ducati.png"),
                Moto(nombre="S 1000 RR", marca="BMW", modelo="S1000RR", año=2024, precio=18995.00, descripcion="La BMW S 1000 RR es una superbike de alto rendimiento, diseñada para la pista pero igualmente impresionante en carretera.", imagen_url="images/uploads/bmw.png"),
                Moto(nombre="Speed Triple 1200 RS", marca="Triumph", modelo="1200RS", año=2024, precio=18500.00, descripcion="La Speed Triple 1200 RS es la naked deportiva definitiva de Triumph, con un rendimiento explosivo y tecnología avanzada.", imagen_url="images/uploads/triumph.png"),
                Moto(nombre="YZF-R1M", marca="Yamaha", modelo="R1M", año=2024, precio=26999.00, descripcion="La Yamaha YZF-R1M es la versión más exclusiva de la R1, con componentes de competición y telemetría avanzada.", imagen_url="images/uploads/yamaha.png"),
                Moto(nombre="Nightster Special", marca="Harley-Davidson", modelo="RH975S", año=2024, precio=14999.00, descripcion="La Harley-Davidson Nightster Special combina la tradición cruiser con un motor Revolution Max 975T de última generación.", imagen_url="images/uploads/harley-davidson.png")
            ]
            db.session.add_all(sample_motos)
            db.session.commit()
            print("Datos de ejemplo añadidos a la base de datos.")

    app.run(debug=True)