# extensions.py
# Este archivo centraliza la inicialización de extensiones como SQLAlchemy
# y define decoradores globales para evitar importaciones circulares.

from flask_sqlalchemy import SQLAlchemy
from flask import session, redirect, url_for, flash
from functools import wraps # Necesario para el decorador @wraps

# Crea una instancia de SQLAlchemy que será usada por toda la aplicación.
db = SQLAlchemy()

# Define el decorador login_required aquí para que sea importable por los blueprints
def login_required(f):
    """
    Decorador que requiere que el usuario esté logueado para acceder a una ruta.
    Si no está logueado, lo redirige a la página de login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            # Redirige a la ruta global de login definida en app.py
            flash('Por favor, inicia sesión para acceder a esta página.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function