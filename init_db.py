# init_db.py
# Script para inicializar la base de datos de tu aplicación Flask en Render.
# Crea las tablas de la base de datos si no existen y las puebla con datos de ejemplo.

import os
from datetime import datetime
from app import app, db, User, Moto, Invoice # Asegúrate de que 'app' sea tu instancia de Flask
                                             # y que User, Moto, Invoice sean tus modelos de SQLAlchemy

# Configuración de la base de datos para este script
# Render puede proporcionar una DATABASE_URL (ej. para PostgreSQL),
# pero si usas SQLite, asegúrate de que la ruta sea relativa al proyecto.
# En Render, el directorio /opt/render/project/src/ es la raíz de tu proyecto.
basedir = os.path.abspath(os.path.dirname(__file__))
# Si Render proporciona una URL de base de datos (por ejemplo, para PostgreSQL), úsala.
# De lo contrario, usa SQLite en el archivo 'motos.db' en la raíz del proyecto.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
                                        'sqlite:///' + os.path.join(basedir, 'motos.db')

# Desactiva la señal de modificación para ahorrar memoria (recomendado para SQLAlchemy Flask)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Con el contexto de la aplicación, interactúa con la base de datos
with app.app_context():
    # Crea todas las tablas definidas en tus modelos (User, Moto, Invoice)
    db.create_all()
    print("DB Init: Tablas de la base de datos creadas (o ya existían).")

    # Verifica si el usuario 'admin' ya existe, si no, lo crea
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin')
        # Configura la contraseña del admin. ¡Cámbiala por una segura!
        admin_user.set_password('Th1Nk3R23524') # <--- CAMBIA ESTA CONTRASEÑA por la real de tu admin
        db.session.add(admin_user)
        db.session.commit()
        print("DB Init: Usuario 'admin' creado.")
    else:
        print("DB Init: El usuario 'admin' ya existe. (No se recreó)")

    # Verifica si hay motos en la base de datos, si no, añade datos de ejemplo
    if not Moto.query.first():
        print("DB Init: Base de datos de motos vacía, añadiendo datos de ejemplo...")
        sample_motos = [
            Moto(marca="Benelli", modelo="Leoncino 500", año=2023, precio=6999.00, descripcion="Una scrambler moderna con diseño italiano y un motor bicilíndrico emocionante.", imagen_url="images/uploads/benelli-leoncino-500.png"),
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
        print("DB Init: Datos de ejemplo de motos añadidos a la base de datos.")
    else:
        print("DB Init: La base de datos de motos ya contiene datos.")

    # Verifica si hay facturas en la base de datos, si no, añade datos de ejemplo
    if not Invoice.query.first():
        print("DB Init: Base de datos de facturas vacía, añadiendo datos de ejemplo de facturas...")
        sample_invoices = [
            Invoice(
                invoice_number="INV-20250615-0001",
                customer_name="Juan Pérez",
                customer_address="Calle Falsa 123, Ciudad",
                customer_email="juan.perez@example.com",
                invoice_date=datetime(2025, 6, 15).date(),
                items_description="1x Honda CB1000R, 1x Casco Integral",
                subtotal_amount=13500.00,
                tax_rate=0.16,
                tax_amount=2160.00,
                total_amount=15660.00,
                notes="Entrega a domicilio coordinada."
            ),
            Invoice(
                invoice_number="INV-20250614-0002",
                customer_name="María Gómez",
                customer_address="Av. Siempre Viva 742, Pueblo",
                customer_email="maria.gomez@example.com",
                invoice_date=datetime(2025, 6, 14).date(),
                items_description="1x Kawasaki Z900RS",
                subtotal_amount=11999.00,
                tax_rate=0.16,
                tax_amount=1919.84,
                total_amount=13918.84,
                notes="Cliente recurrente, descuento especial."
            )
        ]
        db.session.add_all(sample_invoices)
        db.session.commit()
        print("DB Init: Datos de ejemplo de facturas añadidos a la base de datos.")
    else:
        print("DB Init: La base de datos de facturas ya contiene datos.")
