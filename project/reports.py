from io import BytesIO
from flask import Blueprint, Flask,  make_response, jsonify
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import User, Service, Subscription, Booking
from . import db
from reportlab.platypus.tables import Table

reports = Blueprint('reports', __name__)

@reports.route('/reports/services')
def services_report():
    services = Service.query.all()
    services_data = [{'Name': service.name, 'Description': service.description} for service in services]
    return jsonify(services_data)

@reports.route('/reports/clients')
def clients_report():
    clients = User.query.filter_by(role='client').all()
    clients_data = [{'Name': client.name, 'Email': client.email} for client in clients]
    return jsonify(clients_data)

@reports.route('/reports/subscribed_services')
def subscribed_services_report():
    subscriptions = Subscription.query.all()
    subscribed_services_data = [{'User': subscription.user.name,
                                 'Service': subscription.service.name} for subscription in subscriptions]
    return jsonify(subscribed_services_data)

@reports.route('/reports/booked_sessions')
def booked_sessions_report():
    bookings = Booking.query.all()
    booked_sessions_data = [{'client': booking.user.name,
                             'service': booking.service.name if booking.service else 'N/A',
                             'time_slot': booking.time_slot} for booking in bookings]
    return jsonify(booked_sessions_data)

@reports.route('/reports/generate_pdf/<report_type>')
def generate_pdf(report_type):
    report_data_functions = {
        'services': (lambda: Service.query.all(), ['Name', 'Description']),
        'clients': (lambda: User.query.filter_by(role='client').all(), ['Name', 'Email']),
        'subscribed_services': (lambda: Subscription.query.all(), ['User', 'Service']),
        'booked_sessions': (lambda: Booking.query.all(), ['Client', 'Service', 'Time Slot']),
    }
    if report_type not in report_data_functions:
        return "Invalid report type"
    
    data, headers = report_data_functions[report_type]
    
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Add logo image
    logo_path = 'project/static/images/logo.jpeg'
    logo = Image(logo_path, width=100, height=50)
    elements.append(logo)
    elements.append(Spacer(1, 20)) 
    
    # Add report title
    title_style = getSampleStyleSheet()["Title"]
    title_text = f"{report_type.capitalize()} Report"
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 20))
    
    table_heading_style = [('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                           ('LEFTPADDING', (0, 0), (-1, -1), 10),
                           ('RIGHTPADDING', (0, 0), (-1, -1), 10), 
                           ('TOPPADDING', (0, 0), (-1, -1), 10), 
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]

    # Create style for table rows
    table_row_style = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                       ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                       ('LEFTPADDING', (0, 0), (-1, -1), 10),
                       ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                       ('TOPPADDING', (0, 0), (-1, -1), 10), 
                       ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]
    data_rows = []
    for item in data():
        row = []
        if report_type == 'services':
            row.append(Paragraph(item.name))
            row.append(Paragraph(item.description))
        elif report_type == 'clients':
            row.append(Paragraph(item.name))
            row.append(Paragraph(item.email))
        elif report_type == 'subscribed_services':
            row.append(Paragraph(item.user.name))
            row.append(Paragraph(item.service.name))
        elif report_type == 'booked_sessions':
            booking = Booking.query.filter_by(id=item.id).join(Service).first()
            if booking:
                row.append((booking.user.name))
                row.append(Paragraph(booking.service.name))
                row.append(Paragraph((booking.time_slot)))
        data_rows.append(row)
    
    # Create table
    table_style = [('GRID', (0, 0), (-1, -1), 1, 'BLACK')]
    table = Table([headers] + data_rows, style=table_heading_style + table_row_style, hAlign='CENTRE')
    elements.append(table)
    
    pdf.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={report_type}_report.pdf'

    return response