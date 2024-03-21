from io import BytesIO
from flask import Blueprint, Flask,  make_response, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import User, Service, Subscription, Booking
from . import db

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
        'clients': (lambda: User.query.all(), ['Name', 'Email']),
        'subscribed_services': (lambda: Subscription.query.all(), ['User', 'Service']),
        'booked_sessions': (lambda: Booking.query.all(), ['Client', 'Service', 'Time Slot']),
    }
    if report_type not in report_data_functions:
        return "Invalid report type"
    
    data, headers = report_data_functions[report_type]
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 750, f"{report_type.capitalize()} Report")
    pdf.setFont("Helvetica", 10)

    row_height = 720
    for header in headers:
        pdf.drawString(headers.index(header) * 200 + 50, row_height, header)
    row_height -= 20

    for item in data():
        if report_type == 'services':
            pdf.drawString(50, row_height, item.name)
            pdf.drawString(250, row_height, item.description)
        elif report_type == 'clients':
            pdf.drawString(50, row_height, item.name)
            pdf.drawString(250, row_height, item.email)
        elif report_type == 'subscribed_services':
            pdf.drawString(50, row_height, item.user.name)
            pdf.drawString(250, row_height, item.service.name)
        elif report_type == 'booked_sessions':
            booking = Booking.query.filter_by(id=item.id).join(Service).first()
            if booking:
                pdf.drawString(50, row_height, booking.user.name)
                pdf.drawString(250, row_height, booking.service.name)
                pdf.drawString(450, row_height, str(booking.time_slot))  # Assuming time_slot is a string
        row_height -= 20

    pdf.save()
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={report_type}_report.pdf'

    return response

