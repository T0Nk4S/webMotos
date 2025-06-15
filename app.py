import os
import math
import re
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# --- Importaciones para generación de PDF ---
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO
# --- Fin de importaciones de PDF ---

# Importar el formulario que definiremos en forms.py
from forms import MotoForm # <-- Este archivo también cambiará

# --- Configuración de la Aplicación Flask ---
app = Flask(__name__)

# Clave secreta para seguridad de sesiones y formularios WTForms
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
    # nombre = db.Column(db.String(100), nullable=False) # <-- ELIMINADO: Campo 'nombre'
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    año = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        # Ahora representará usando marca y modelo
        return f'<Moto {self.marca} {self.modelo}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- Funciones Auxiliares para Archivos ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_unique_filename(marca, modelo, original_extension):
    base_name = f"{marca}-{modelo}"
    base_name = re.sub(r'[^a-zA-Z0-9_\-]', '', base_name).lower()
    base_name = re.sub(r'[-_]+', '-', base_name)
    base_name = base_name.strip('-').strip('_')

    new_filename = f"{base_name}.{original_extension}"
    safe_filename = secure_filename(new_filename)

    counter = 1
    final_filename = safe_filename
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], final_filename)):
        name_part, ext_part = os.path.splitext(safe_filename)
        final_filename = f"{name_part}-{counter}{ext_part}"
        counter += 1
    return final_filename


# --- DEFINICIÓN DE MARCAS PARA EL FILTRO ---
ALL_AVAILABLE_BRANDS = sorted([
    "Harley-Davidson", "Kawasaki", "Yamaha", "Honda", "Triumph", "Suzuki",
    "Ducati", "BMW", "Royal Enfield", "Benelli", "CFMoto", "Hero", "Keeway",
    "KTM", "Motomel", "Serna", "Super Soco", "TVS", "UM", "Vespa"
])

# --- Función Decorador para proteger rutas ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Por favor, inicia sesión para acceder a esta página.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rutas de la Aplicación ---
@app.route('/')
def index():
    motos_carrusel = []
    try:
        motos_carrusel = Moto.query.order_by(desc(Moto.id)).limit(8).all()
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
            # (Moto.nombre.ilike(search_pattern)) | # <-- ELIMINADO de la búsqueda
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

# --- RUTAS DE ADMINISTRACIÓN (Con Login Required) ---

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'logged_in' in session and session['logged_in']:
        flash('Ya has iniciado sesión.', 'info')
        return redirect(url_for('admin_motos'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['logged_in'] = True
            flash('¡Inicio de sesión exitoso! Bienvenido, Administrador.', 'success')
            return redirect(url_for('admin_motos'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('logged_in', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))

@app.route('/admin_motos')
@login_required
def admin_motos():
    motos = Moto.query.all()
    form = MotoForm()
    return render_template('admin_motos.html', motos=motos, form=form)

@app.route('/add_moto', methods=['GET', 'POST'])
@login_required
def add_moto():
    form = MotoForm()
    if form.validate_on_submit():
        imagen_filename = None
        if form.imagen.data:
            original_filename = form.imagen.data.filename
            if allowed_file(original_filename):
                # Usar marca y modelo para el nombre de archivo
                imagen_filename = generate_unique_filename(form.marca.data, form.modelo.data, original_filename.rsplit('.', 1)[1].lower())
                
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                form.imagen.data.save(file_path)
                imagen_url_db = f'images/uploads/{imagen_filename}'
            else:
                flash('Tipo de archivo no permitido para la imagen.', 'danger')
                return render_template('add_edit_moto.html', form=form, moto=None)
        else:
            imagen_url_db = None

        nueva_moto = Moto(
            # nombre=form.nombre.data, # <-- ELIMINADO de la creación
            marca=form.marca.data,
            modelo=form.modelo.data,
            año=form.año.data,
            precio=form.precio.data,
            descripcion=form.descripcion.data,
            imagen_url=imagen_url_db
        )
        db.session.add(nueva_moto)
        db.session.commit()
        flash('¡Moto añadida exitosamente!', 'success')
        return redirect(url_for('admin_motos'))

    return render_template('add_edit_moto.html', form=form, moto=None)

@app.route('/edit_moto/<int:moto_id>', methods=['GET', 'POST'])
@login_required
def edit_moto(moto_id):
    moto = db.session.get(Moto, moto_id)
    if not moto:
        flash(f'La moto con ID {moto_id} no fue encontrada.', 'danger')
        return redirect(url_for('admin_motos'))

    form = MotoForm(obj=moto)

    if form.validate_on_submit():
        if form.imagen.data:
            original_filename = form.imagen.data.filename
            if allowed_file(original_filename):
                if moto.imagen_url and moto.imagen_url.startswith('images/uploads/'):
                    image_path_to_delete = os.path.join(app.root_path, 'static', moto.imagen_url)
                    if os.path.exists(image_path_to_delete):
                        try:
                            os.remove(image_path_to_delete)
                            print(f"Old image removed: {image_path_to_delete}")
                        except OSError as e:
                            print(f"Error removing old image {image_path_to_delete}: {e}")
                    else:
                        print(f"Advertencia: La imagen antigua '{moto.imagen_url}' no existe en el disco.")

                # Usar marca y modelo para el nuevo nombre de archivo
                imagen_filename = generate_unique_filename(form.marca.data, form.modelo.data, original_filename.rsplit('.', 1)[1].lower())
                
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                form.imagen.data.save(file_path)
                moto.imagen_url = f'images/uploads/{imagen_filename}'
            else:
                flash('Tipo de archivo no permitido para la nueva imagen.', 'danger')
                return render_template('add_edit_moto.html', form=form, moto=moto)

        # moto.nombre = form.nombre.data # <-- ELIMINADO de la actualización
        moto.marca = form.marca.data
        moto.modelo = form.modelo.data
        moto.año = form.año.data
        moto.precio = form.precio.data
        moto.descripcion = form.descripcion.data

        db.session.commit()
        flash('¡Moto actualizada exitosamente!', 'success')
        return redirect(url_for('admin_motos'))
    return render_template('add_edit_moto.html', form=form, moto=moto)

@app.route('/delete_moto/<int:moto_id>', methods=['POST'])
@login_required
def delete_moto(moto_id):
    moto = db.session.get(Moto, moto_id)
    if not moto:
        flash(f'La moto con ID {moto_id} no fue encontrada.', 'danger')
        return redirect(url_for('admin_motos'))

    if moto.imagen_url:
        if moto.imagen_url.startswith('images/uploads/'):
            image_path = os.path.join(app.root_path, 'static', moto.imagen_url)
            
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"Image deleted successfully: {image_path}")
                except OSError as e:
                    print(f"ERROR deleting image {image_path}: {e}")
                    flash(f"Error al eliminar la imagen del servidor: {e}", 'danger')
            else:
                print(f"Advertencia: El archivo de imagen no existe en el disco: {image_path}")
                flash("Advertencia: La imagen asociada no se encontró en el servidor, solo se eliminó la entrada de la base de datos.", 'info')
        else:
            print(f"Advertencia: La imagen {moto.imagen_url} no está en la carpeta de uploads, no se intentó eliminar del disco.")

    db.session.delete(moto)
    db.session.commit()
    flash('¡Moto eliminada exitosamente!', 'success')

    return redirect(url_for('admin_motos'))

# --- FUNCIÓN: Exportar Catálogo a PDF ---
@app.route('/export_pdf_motos')
@login_required
def export_pdf_motos():
    motos = Moto.query.order_by(Moto.marca, Moto.modelo).all()

    motos_by_brand = {}
    for moto in motos:
        if moto.marca not in motos_by_brand:
            motos_by_brand[moto.marca] = []
        motos_by_brand[moto.marca].append(moto)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch/2, leftMargin=inch/2, topMargin=inch/2, bottomMargin=inch/2)
    
    Story = []
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='TitleStyle',
                             fontSize=30,
                             leading=36,
                             alignment=1,
                             spaceAfter=24,
                             fontName='Helvetica-Bold',
                             textColor=colors.HexColor('#2C3E50')))

    styles.add(ParagraphStyle(name='SubtitleStyle',
                             fontSize=14,
                             leading=18,
                             alignment=1,
                             spaceAfter=20,
                             fontName='Helvetica-Oblique',
                             textColor=colors.gray))

    styles.add(ParagraphStyle(name='BrandHeader',
                             fontSize=22,
                             leading=26,
                             spaceBefore=25,
                             spaceAfter=15,
                             fontName='Helvetica-BoldOblique',
                             textColor=colors.HexColor('#E74C3C'),
                             alignment=0))

    styles.add(ParagraphStyle(name='MotoDetailHeader',
                             fontSize=12,
                             leading=14,
                             fontName='Helvetica-Bold',
                             textColor=colors.black))
    
    styles.add(ParagraphStyle(name='MotoDetailText',
                             fontSize=10,
                             leading=12,
                             fontName='Helvetica'))

    styles.add(ParagraphStyle(name='DescriptionStyle',
                             fontSize=9,
                             leading=11,
                             spaceAfter=8,
                             fontName='Helvetica-Oblique',
                             textColor=colors.HexColor('#34495E')))

    Story.append(Paragraph("Catálogo Completo de Motocicletas", styles['TitleStyle']))
    Story.append(Paragraph("Presentado por MotoShop - Su fuente de pasión sobre ruedas", styles['SubtitleStyle']))
    Story.append(Spacer(1, 0.3 * inch))

    for brand in sorted(motos_by_brand.keys()):
        Story.append(Paragraph(f"Marca: {brand}", styles['BrandHeader']))
        Story.append(Spacer(1, 0.1 * inch))

        col_widths = [1.2 * inch, 2.0 * inch, 0.8 * inch, 2.5 * inch]

        table_headers = [
            Paragraph("Imagen", styles['MotoDetailHeader']),
            # CAMBIO: Usamos 'Marca / Modelo / Año' en lugar de 'Nombre'
            Paragraph("Moto (Marca / Modelo / Año)", styles['MotoDetailHeader']),
            Paragraph("Precio", styles['MotoDetailHeader']),
            Paragraph("Descripción", styles['MotoDetailHeader'])
        ]
        data = [table_headers]
        
        for moto in motos_by_brand[brand]:
            img_element = ""
            image_absolute_path = os.path.join(app.root_path, 'static', moto.imagen_url) if moto.imagen_url else ''
            
            img_width = 1.0 * inch
            img_height = 0.75 * inch

            if moto.imagen_url and os.path.exists(image_absolute_path):
                try:
                    img = Image(image_absolute_path, img_width, img_height)
                    img_element = img
                except Exception as e:
                    print(f"Error al cargar imagen para PDF '{image_absolute_path}': {e}")
                    img_element = Paragraph("<i>No image found</i>", styles['MotoDetailText'])
            else:
                placeholder_path = os.path.join(app.root_path, 'static', 'images', 'placeholder.jpg')
                if os.path.exists(placeholder_path):
                    try:
                        img = Image(placeholder_path, img_width, img_height)
                        img_element = img
                    except Exception as e:
                        print(f"Error al cargar placeholder para PDF '{placeholder_path}': {e}")
                        img_element = Paragraph("<i>No image</i>", styles['MotoDetailText'])
                else:
                    img_element = Paragraph("<i>No image</i>", styles['MotoDetailText'])

            # CAMBIO: Construir la información de la moto con Marca y Modelo
            moto_info = Paragraph(
                f"<b>{moto.marca}</b><br/>"
                f"{moto.modelo}<br/>"
                f"Año: {moto.año}",
                styles['MotoDetailText']
            )

            precio_info = Paragraph(f"${moto.precio:,.2f}", styles['MotoDetailText'])

            desc_info = Paragraph(moto.descripcion if moto.descripcion else "Sin descripción.", styles['DescriptionStyle'])
            
            data.append([
                img_element,
                moto_info,
                precio_info,
                desc_info
            ])

        table = Table(data, colWidths=col_widths)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#ECF0F1')]),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            
            ('ALIGN', (0,1), (0,-1), 'CENTER'),
            ('ALIGN', (1,1), (1,-1), 'LEFT'),
            ('ALIGN', (2,1), (2,-1), 'RIGHT'),
            ('ALIGN', (3,1), (3,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        Story.append(table)
        Story.append(Spacer(1, 0.5 * inch))

    doc.build(Story)
    
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='catalogo_motos_motoshop.pdf',
        mimetype='application/pdf'
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created if they didn't exist.")

        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin')
            admin_user.set_password('Th1Nk3R23524')
            db.session.add(admin_user)
            db.session.commit()
            print("----------------------------------------------------------------------")
            print("ATTENTION: 'admin' user created with password 'Th1Nk3R23524'!")
            print("        CHANGE THESE CREDENTIALS IN THE CODE FOR PRODUCTION.")
            print("----------------------------------------------------------------------")
        else:
            print("The 'admin' user already exists.")

        if not Moto.query.first():
            print("Motorcycle database empty, adding sample data...")
            sample_motos = [
                # CAMBIO: Los datos de ejemplo ya no tienen el campo 'nombre'
                Moto(marca="Benelli", modelo="Leoncino 500", año=2023, precio=6999.00, descripcion="Una scrambler moderna con diseño italiano y un motor bicilíndrico emocionante.", imagen_url="images/uploads/benelli-leoncino-500.png"), # Nombre de archivo ajustado
                Moto(marca="CFMoto", modelo="650NK", año=2024, precio=6499.00, descripcion="Naked de media cilindrada, potente y ágil, con un estilo agresivo.", imagen_url="images/uploads/cfmoto-650nk.png"),
                Moto(marca="Hero", modelo="Xtreme 160R", año=2023, precio=2500.00, descripcion="Moto deportiva urbana con un rendimiento ágil y eficiente para el día a día.", imagen_url="images/uploads/hero-xtreme-160r.png"),
                Moto(marca="Honda", modelo="CB1000R", año=2024, precio=12999.00, descripcion="Neo Sports Café, una naked de diseño minimalista con el potente motor de la Fireblade.", imagen_url="images/uploads/honda-cb1000r.png"),
                Moto(marca="Kawasaki", modelo="Z900RS", año=2023, precio=11999.00, descripcion="Un tributo moderno a la Z1 original, con un estilo retro y un rendimiento de vanguardia.", imagen_url="images/uploads/kawasaki-z900rs.png"),
                Moto(marca="Keeway", modelo="K-Light 202", año=2022, precio=3199.00, descripcion="Cruiser compacta con un estilo clásico y fácil manejo para la ciudad.", imagen_url="images/uploads/keeway-k-light-202.png"),
                Moto(marca="KTM", modelo="1290 Super Duke R", año=2024, precio=19999.00, descripcion="La 'Bestia' de KTM, una hypernaked con un motor V-Twin brutal y componentes de alta gama.", imagen_url="images/uploads/ktm-1290-super-duke-r.png"),
                Moto(marca="Motomel", modelo="Skua 250", año=2023, precio=3499.00, descripcion="Una moto trail versátil, diseñada para afrontar terrenos variados con comodidad y robustez.", imagen_url="images/uploads/motomel-skua-250.png"),
                Moto(marca="Royal Enfield", modelo="Continental GT 650", año=2024, precio=7499.00, descripcion="Cafe racer clásica con un diseño atemporal y un motor bicilíndrico suave.", imagen_url="images/uploads/royal-enfield-continental-gt-650.png"),
                Moto(marca="Serna", modelo="RX400", año=2023, precio=4200.00, descripcion="Trail de aventura, robusta y preparada para explorar cualquier camino, con un buen equilibrio entre carretera y off-road.", imagen_url="images/uploads/serna-rx400.png"),
                Moto(marca="Super Soco", modelo="TC Max", año=2024, precio=5499.00, descripcion="Motocicleta eléctrica de estilo urbano y prestaciones sorprendentes, ideal para la movilidad sostenible.", imagen_url="images/uploads/super-soco-tc-max.png"),
                Moto(marca="Suzuki", modelo="GSX-R1000R", año=2023, precio=16000.00, descripcion="Superbike pura, diseñada para ofrecer el máximo rendimiento en pista y una experiencia de conducción inigualable.", imagen_url="images/uploads/suzuki-gsx-r1000r.png"),
                Moto(marca="TVS", modelo="Apache RR 310", año=2024, precio=4500.00, descripcion="Sportbike carenada con un diseño agresivo y tecnología inspirada en las carreras.", imagen_url="images/uploads/tvs-apache-rr-310.png"),
                Moto(marca="UM", modelo="DSR Adventure 200", año=2023, precio=3800.00, descripcion="Una motocicleta de doble propósito diseñada para la aventura, con un rendimiento sólido en carretera y fuera de ella.", imagen_url="images/uploads/um-dsr-adventure-200.png"),
                Moto(marca="Vespa", modelo="GTS 300 SuperTech", año=2024, precio=8500.00, descripcion="El scooter más potente de Vespa, combina la conectividad y la tecnología con el icónico estilo italiano.", imagen_url="images/uploads/vespa-gts-300-supertech.png"),
                Moto(marca="Ducati", modelo="Panigale V4 R", año=2024, precio=42995.00, descripcion="La Panigale V4 R es la expresión máxima de la deportividad Ducati, con un motor de 998 cc derivado de MotoGP.", imagen_url="images/uploads/ducati-panigale-v4-r.png"),
                Moto(marca="BMW", modelo="S 1000 RR", año=2024, precio=18995.00, descripcion="La BMW S 1000 RR es una superbike de alto rendimiento, diseñada para la pista pero igualmente impresionante en carretera.", imagen_url="images/uploads/bmw-s-1000-rr.png"),
                Moto(marca="Triumph", modelo="Speed Triple 1200 RS", año=2024, precio=18500.00, descripcion="La Speed Triple 1200 RS es la naked deportiva definitiva de Triumph, con un rendimiento explosivo y tecnología avanzada.", imagen_url="images/uploads/triumph-speed-triple-1200-rs.png"),
                Moto(marca="Yamaha", modelo="YZF-R1M", año=2024, precio=26999.00, descripcion="La Yamaha YZF-R1M es la versión más exclusiva de la R1, con componentes de competición y telemetría avanzada.", imagen_url="images/uploads/yamaha-yzf-r1m.png"),
                Moto(marca="Harley-Davidson", modelo="Nightster Special", año=2024, precio=14999.00, descripcion="La Harley-Davidson Nightster Special combina la tradición cruiser con un motor Revolution Max 975T de última generación.", imagen_url="images/uploads/harley-davidson-nightster-special.png")
            ]
            db.session.add_all(sample_motos)
            db.session.commit()
            print("Sample motorcycle data added to the database.")

    app.run(debug=True)