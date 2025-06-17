# routes/invoices.py
# Contiene las rutas del Blueprint 'invoices_bp' para la gestión de facturas (CRUD).

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Invoice # Importa el modelo Invoice desde models.py
from forms import InvoiceForm # Importa el formulario InvoiceForm desde forms.py
# IMPORTANTE: Importa 'db' y 'login_required' desde extensions.py
from extensions import db, login_required # <--- CAMBIO AQUÍ
from datetime import datetime

invoices_bp = Blueprint('invoices_bp', __name__)

@invoices_bp.route('/')
@login_required
def admin_invoices():
    invoices = Invoice.query.order_by(Invoice.invoice_date.desc()).all()
    return render_template('admin_invoices.html', invoices=invoices)

@invoices_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_invoice():
    form = InvoiceForm()
    if form.validate_on_submit():
        last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
        last_id = last_invoice.id if last_invoice else 0
        new_invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{last_id + 1:04d}"

        nueva_factura = Invoice(
            invoice_number=new_invoice_number,
            customer_name=form.customer_name.data,
            customer_address=form.customer_address.data,
            customer_email=form.customer_email.data,
            invoice_date=form.invoice_date.data,
            items_description=form.items_description.data,
            subtotal_amount=form.subtotal_amount.data,
            tax_rate=form.tax_rate.data,
            tax_amount=form.tax_amount.data,
            total_amount=form.total_amount.data,
            notes=form.notes.data
        )
        db.session.add(nueva_factura)
        db.session.commit()
        flash('¡Factura creada exitosamente!', 'success')
        return redirect(url_for('invoices_bp.admin_invoices'))
    return render_template('add_edit_invoice.html', form=form, invoice=None)

@invoices_bp.route('/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice:
        flash('Factura no encontrada.', 'danger')
        return redirect(url_for('invoices_bp.admin_invoices'))
    return render_template('view_invoice.html', invoice=invoice)

@invoices_bp.route('/<int:invoice_id>/print')
@login_required
def print_invoice(invoice_id):
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice:
        flash('Factura no encontrada.', 'danger')
        return redirect(url_for('invoices_bp.admin_invoices'))
    return render_template('invoice_template.html', invoice=invoice)