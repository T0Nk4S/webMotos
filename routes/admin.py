# routes/admin.py
# Contiene las rutas del Blueprint 'admin_bp' para la gestión de motocicletas (CRUD).

import os
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from models import Moto # Importa el modelo Moto desde models.py
from forms import MotoForm # Importa el formulario MotoForm desde forms.py
# IMPORTANTE: Importa 'db' y 'login_required' desde extensions.py
from extensions import db, login_required # <--- CAMBIO AQUÍ
from utils.pdf_generator import export_pdf_motos as generate_catalog_pdf

admin_bp = Blueprint('admin_bp', __name__)

# --- Funciones Auxiliares para Manejo de Archivos ---
def allowed_file(filename, app_config):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app_config['ALLOWED_EXTENSIONS']

def generate_unique_filename(marca, modelo, original_extension, upload_folder):
    base_name = f"{marca}-{modelo}"
    base_name = re.sub(r'[^a-zA-Z0-9_\-]', '', base_name).lower()
    base_name = re.sub(r'[-_]+', '-', base_name)
    base_name = base_name.strip('-').strip('_')

    new_filename = f"{base_name}.{original_extension}"
    safe_filename = secure_filename(new_filename)

    counter = 1
    final_filename = safe_filename
    while os.path.exists(os.path.join(upload_folder, final_filename)):
        name_part, ext_part = os.path.splitext(safe_filename)
        final_filename = f"{name_part}-{counter}{ext_part}"
        counter += 1
    return final_filename

# --- Rutas de Gestión de Motos (CRUD) ---

@admin_bp.route('/motos')
@login_required
def admin_motos():
    motos = Moto.query.all()
    form = MotoForm()
    return render_template('admin_motos.html', motos=motos, form=form)

@admin_bp.route('/add_moto', methods=['GET', 'POST'])
@login_required
def add_moto():
    form = MotoForm()
    if form.validate_on_submit():
        imagen_url_db = None
        if form.imagen.data:
            original_filename = form.imagen.data.filename
            if allowed_file(original_filename, current_app.config):
                imagen_filename = generate_unique_filename(form.marca.data, form.modelo.data, 
                                                           original_filename.rsplit('.', 1)[1].lower(),
                                                           current_app.config['UPLOAD_FOLDER'])
                
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], imagen_filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                form.imagen.data.save(file_path)
                imagen_url_db = f'images/uploads/{imagen_filename}'
            else:
                flash('Tipo de archivo no permitido para la imagen.', 'danger')
                return render_template('add_edit_moto.html', form=form, moto=None)
        
        nueva_moto = Moto(
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
        return redirect(url_for('admin_bp.admin_motos'))

    return render_template('add_edit_moto.html', form=form, moto=None)

@admin_bp.route('/edit_moto/<int:moto_id>', methods=['GET', 'POST'])
@login_required
def edit_moto(moto_id):
    moto = db.session.get(Moto, moto_id)
    if not moto:
        flash(f'La moto con ID {moto_id} no fue encontrada.', 'danger')
        return redirect(url_for('admin_bp.admin_motos'))

    form = MotoForm(obj=moto)

    if form.validate_on_submit():
        if form.imagen.data:
            original_filename = form.imagen.data.filename
            if allowed_file(original_filename, current_app.config):
                if moto.imagen_url and moto.imagen_url.startswith('images/uploads/'):
                    image_path_to_delete = os.path.join(current_app.root_path, 'static', moto.imagen_url)
                    if os.path.exists(image_path_to_delete):
                        try:
                            os.remove(image_path_to_delete)
                            print(f"Old image removed: {image_path_to_delete}")
                        except OSError as e:
                            print(f"Error removing old image {image_path_to_delete}: {e}")
                    else:
                        print(f"Advertencia: La imagen antigua '{moto.imagen_url}' no existe en el disco.")

                imagen_filename = generate_unique_filename(form.marca.data, form.modelo.data, 
                                                           original_filename.rsplit('.', 1)[1].lower(),
                                                           current_app.config['UPLOAD_FOLDER'])
                
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], imagen_filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                form.imagen.data.save(file_path)
                moto.imagen_url = f'images/uploads/{imagen_filename}'
            else:
                flash('Tipo de archivo no permitido para la nueva imagen.', 'danger')
                return render_template('add_edit_moto.html', form=form, moto=moto)

        moto.marca = form.marca.data
        moto.modelo = form.modelo.data
        moto.año = form.año.data
        moto.precio = form.precio.data
        moto.descripcion = form.descripcion.data

        db.session.commit()
        flash('¡Moto actualizada exitosamente!', 'success')
        return redirect(url_for('admin_bp.admin_motos'))
    return render_template('add_edit_moto.html', form=form, moto=moto)

@admin_bp.route('/delete_moto/<int:moto_id>', methods=['POST'])
@login_required
def delete_moto(moto_id):
    moto = db.session.get(Moto, moto_id)
    if not moto:
        flash(f'La moto con ID {moto_id} no fue encontrada.', 'danger')
        return redirect(url_for('admin_bp.admin_motos'))

    if moto.imagen_url:
        if moto.imagen_url.startswith('images/uploads/'):
            image_path = os.path.join(current_app.root_path, 'static', moto.imagen_url)
            
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

    return redirect(url_for('admin_bp.admin_motos'))

@admin_bp.route('/export_pdf_motos')
@login_required
def export_pdf_motos_route():
    from flask import send_file
    pdf_buffer = generate_catalog_pdf(current_app, db)
    pdf_buffer.seek(0)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name='catalogo_motos_motoshop.pdf',
        mimetype='application/pdf'
    )