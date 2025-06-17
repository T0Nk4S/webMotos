# routes/main.py
# Contiene las rutas del Blueprint 'main_bp' para la parte pública de la aplicación.

import math
from flask import Blueprint, render_template, request, url_for, flash, redirect # <--- ¡Añadir 'redirect' aquí!
from sqlalchemy import desc
# IMPORTANTE: Importa 'db' y 'login_required' desde extensions.py
from extensions import db, login_required
from models import Moto # Importa el modelo Moto desde el módulo models.py

# Define el Blueprint para las rutas principales (públicas)
main_bp = Blueprint('main_bp', __name__)

# --- DEFINICIÓN DE MARCAS PARA EL FILTRO ---
ALL_AVAILABLE_BRANDS = sorted([
    "Harley-Davidson", "Kawasaki", "Yamaha", "Honda", "Triumph", "Suzuki",
    "Ducati", "BMW", "Royal Enfield", "Benelli", "CFMoto", "Hero", "Keeway",
    "KTM", "Motomel", "Serna", "Super Soco", "TVS", "UM", "Vespa"
])

@main_bp.route('/')
def index():
    """
    Ruta para la página de inicio que muestra un carrusel de motos.
    """
    motos_carrusel = []
    try:
        motos_carrusel = Moto.query.order_by(desc(Moto.id)).limit(8).all()
    except Exception as e:
        print(f"Error al cargar motos para el carrusel: {e}")
        motos_carrusel = []
            
    return render_template('index.html', motos_carrusel=motos_carrusel)

@main_bp.route('/catalogo-completo')
def catalogo_completo():
    """
    Ruta para el catálogo completo de motos con filtros y paginación.
    Permite buscar por marca y modelo, filtrar por marca, año y rango de precio.
    """
    query = Moto.query

    search_query = request.args.get('search_query', '').strip()
    brand_filter = request.args.get('brand_filter', '').strip()
    year_filter = request.args.get('year_filter', '').strip()
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
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

@main_bp.route('/moto/<int:moto_id>')
def moto_detalle(moto_id):
    """
    Ruta para ver los detalles de una moto específica.
    """
    moto = db.session.get(Moto, moto_id)
    if not moto:
        flash('Motocicleta no encontrada.', 'danger')
        return redirect(url_for('main_bp.catalogo_completo'))
    return render_template('moto_detalle.html', moto=moto)