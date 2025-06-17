# utils/pdf_generator.py
# Contiene la lógica para generar el catálogo de motos en formato PDF.

import os
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

# Importa el modelo Moto para hacer consultas.
# La instancia de db se pasa como argumento desde el blueprint.
from models import Moto

def export_pdf_motos(app_instance, db_instance):
    """
    Genera un documento PDF del catálogo de motos, ordenado por marca,
    e incluye detalles e imágenes para cada moto.

    Args:
        app_instance: La instancia de la aplicación Flask (current_app).
        db_instance: La instancia de SQLAlchemy (db).

    Returns:
        Un objeto BytesIO que contiene el PDF generado.
    """
    # Se requiere un contexto de aplicación para acceder a la base de datos.
    # El blueprint pasa 'current_app' y 'db', por lo que podemos usarlos aquí.
    with app_instance.app_context():
        motos = db_instance.session.query(Moto).order_by(Moto.marca, Moto.modelo).all()

    # Agrupa las motos por marca para una mejor organización en el PDF.
    motos_by_brand = {}
    for moto in motos:
        if moto.marca not in motos_by_brand:
            motos_by_brand[moto.marca] = []
        motos_by_brand[moto.marca].append(moto)

    # Crea un buffer en memoria para almacenar el PDF generado.
    buffer = BytesIO()
    # Define las propiedades del documento PDF (tamaño de página, márgenes).
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch/2, leftMargin=inch/2, topMargin=inch/2, bottomMargin=inch/2)
    
    # Lista para almacenar los elementos del Story (contenido del PDF).
    Story = []
    # Obtiene los estilos de párrafo predefinidos de ReportLab.
    styles = getSampleStyleSheet()

    # --- Estilos Personalizados para el PDF ---
    styles.add(ParagraphStyle(name='TitleStyle',
                             fontSize=30,
                             leading=36,
                             alignment=1, # Centrado
                             spaceAfter=24,
                             fontName='Helvetica-Bold',
                             textColor=colors.HexColor('#2C3E50'))) # Azul oscuro

    styles.add(ParagraphStyle(name='SubtitleStyle',
                             fontSize=14,
                             leading=18,
                             alignment=1, # Centrado
                             spaceAfter=20,
                             fontName='Helvetica-Oblique', # Cursiva
                             textColor=colors.gray))

    styles.add(ParagraphStyle(name='BrandHeader',
                             fontSize=22,
                             leading=26,
                             spaceBefore=25, # Espacio antes de cada nueva marca
                             spaceAfter=15,
                             fontName='Helvetica-BoldOblique', # Negrita y cursiva
                             textColor=colors.HexColor('#E74C3C'), # Rojo
                             alignment=0)) # Alineado a la izquierda

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
                             textColor=colors.HexColor('#34495E'))) # Gris oscuro para la descripción

    # --- Construcción del Contenido del PDF ---

    # Título principal del catálogo
    Story.append(Paragraph("Catálogo Completo de Motocicletas", styles['TitleStyle']))
    Story.append(Paragraph("Presentado por MotoShop - Su fuente de pasión sobre ruedas", styles['SubtitleStyle']))
    Story.append(Spacer(1, 0.3 * inch)) # Espacio vertical

    # Itera sobre cada marca de motos (ordenadas alfabéticamente)
    for brand in sorted(motos_by_brand.keys()):
        Story.append(Paragraph(f"Marca: {brand}", styles['BrandHeader'])) # Encabezado para la marca
        Story.append(Spacer(1, 0.1 * inch))

        # Define los anchos de las columnas para la tabla de motos.
        # Imagen, Moto (Marca/Modelo/Año), Precio, Descripción
        col_widths = [1.2 * inch, 2.0 * inch, 0.8 * inch, 2.5 * inch]

        # Define los encabezados de la tabla.
        table_headers = [
            Paragraph("Imagen", styles['MotoDetailHeader']),
            Paragraph("Moto (Marca / Modelo / Año)", styles['MotoDetailHeader']),
            Paragraph("Precio", styles['MotoDetailHeader']),
            Paragraph("Descripción", styles['MotoDetailHeader'])
        ]
        data = [table_headers] # La primera fila de la tabla son los encabezados.

        # Itera sobre cada moto dentro de la marca actual.
        for moto in motos_by_brand[brand]:
            img_element = "" # Elemento de imagen para la celda de la tabla
            # Construye la ruta absoluta de la imagen.
            image_absolute_path = os.path.join(app_instance.root_path, 'static', moto.imagen_url) if moto.imagen_url else ''
            
            # Dimensiones deseadas para la imagen en la tabla.
            img_width = 1.0 * inch
            img_height = 0.75 * inch

            # Intenta cargar la imagen si la URL existe y el archivo es accesible.
            if moto.imagen_url and os.path.exists(image_absolute_path):
                try:
                    # Crea un objeto Image de ReportLab.
                    img = Image(image_absolute_path, img_width, img_height)
                    img_element = img
                except Exception as e:
                    # En caso de error al cargar la imagen, muestra un texto.
                    print(f"Error al cargar imagen para PDF '{image_absolute_path}': {e}")
                    img_element = Paragraph("<i>No image found</i>", styles['MotoDetailText'])
            else:
                # Si no hay imagen o el archivo no existe, usa una imagen de placeholder.
                placeholder_path = os.path.join(app_instance.root_path, 'static', 'images', 'placeholder.jpg')
                if os.path.exists(placeholder_path):
                    try:
                        img = Image(placeholder_path, img_width, img_height)
                        img_element = img
                    except Exception as e:
                        print(f"Error al cargar placeholder para PDF '{placeholder_path}': {e}")
                        img_element = Paragraph("<i>No image</i>", styles['MotoDetailText'])
                else:
                    img_element = Paragraph("<i>No image</i>", styles['MotoDetailText'])

            # Construye el contenido de las celdas de la tabla para cada moto.
            moto_info = Paragraph(
                f"<b>{moto.marca}</b><br/>" # Marca en negrita
                f"{moto.modelo}<br/>"       # Modelo
                f"Año: {moto.año}",         # Año
                styles['MotoDetailText']
            )

            precio_info = Paragraph(f"${moto.precio:,.2f}", styles['MotoDetailText']) # Precio formateado

            desc_info = Paragraph(moto.descripcion if moto.descripcion else "Sin descripción.", styles['DescriptionStyle'])
            
            # Añade la fila de datos de la moto a la tabla.
            data.append([
                img_element,
                moto_info,
                precio_info,
                desc_info
            ])

        # Crea el objeto Table con los datos y anchos de columna definidos.
        table = Table(data, colWidths=col_widths)
        
        # --- Estilo de la Tabla ---
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3498DB')), # Color de fondo del encabezado
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), # Color del texto del encabezado
            ('ALIGN', (0,0), (-1,-1), 'CENTER'), # Alineación general del contenido de las celdas
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alineación vertical general
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # Fuente del encabezado
            ('BOTTOMPADDING', (0,0), (-1,0), 12), # Relleno inferior del encabezado
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')), # Bordes de la tabla
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#ECF0F1')]), # Colores de fondo alternos para filas
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            
            # Alineaciones específicas para columnas de datos
            ('ALIGN', (0,1), (0,-1), 'CENTER'), # Imágenes centradas
            ('ALIGN', (1,1), (1,-1), 'LEFT'),   # Información de la moto a la izquierda
            ('ALIGN', (2,1), (2,-1), 'RIGHT'),  # Precio a la derecha
            ('ALIGN', (3,1), (3,-1), 'LEFT'),   # Descripción a la izquierda
            ('VALIGN', (0,0), (-1,-1), 'TOP'), # Alineación vertical superior para todas las celdas (especialmente importante para descripciones largas)
        ]))
        Story.append(table) # Añade la tabla al Story
        Story.append(Spacer(1, 0.5 * inch)) # Espacio después de cada tabla de marca

    doc.build(Story) # Construye el documento PDF a partir del Story
    
    # Mueve el puntero del buffer al inicio para que el archivo pueda ser leído.
    buffer.seek(0)
    
    # Devuelve el buffer. La ruta de Flask que llama a esta función se encargará de enviarlo.
    return buffer