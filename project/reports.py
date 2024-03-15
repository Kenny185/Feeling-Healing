from io import BytesIO
from flask import Blueprint, Flask, send_file, make_response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from .models import User, Service, Subscription, Booking
from . import db

reports = Blueprint('reports', __name__)

@reports.route('/services_report')
def services_report():
    services = Service.query.all()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("Services Report", styles['Title']))
    data = [["Service Name", "Description"]]
    for service in services:
        data.append([service.name, service.description])
        
    table = Table(data)
    elements.append(table)
    doc.build(elements)
    return send_file(buffer, as_attachment=True, attachment_filename='services-report.pdf')

@reports.route('/clients_report')
def download_clients_report():
    # Fetch clients data from your database
    clients = User.query.filter(User.role != 'staff').all()
    # Create PDF document
    buffer = BytesIO()
    doc = SimpleDocTemplate("clients_report.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    # Add heading
    elements.append(Paragraph("Clients Report", styles['Title']))
    # Add clients data in a table
    data = [["Client Name", "Email"]]
    for client in clients:
        data.append([client.name, client.email])

    table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                              ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                              ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                              ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                              ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                              ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                              ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table = Table(data)
    table.setStyle(table_style)
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    response = make_response(buffer.getvalue())

    # Set the content type and attachment filename
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=clients_report.pdf'

    return response
# Function to generate PDF report for services linked to specific client
# def generate_services_linked_to_client_report(client_id):
#     # Fetch client's data and associated services from your database
#     client = Client.query.get(client_id)
#     services = client.services  # Assuming there's a relationship between Client and Service models

    # Create PDF document
    # Add client's information and associated services to the PDF document
    # Customize layout, styling, and save the PDF file

# Function to generate PDF report for sessions booked for different services
def generate_sessions_report():
    # Fetch booked sessions data with service details from your database
    sessions = Booking.query.join(Service).all()

    # Create PDF document
    # Add session details along with service information to the PDF document
    # Customize layout, styling, and save the PDF file

# Routes to download the generated PDF files
# @reports.route('/download_clients_report')
# def download_clients_report():
#     generate_clients_report()
#     return send_file("clients_report.pdf", as_attachment=True)

# @reports.route('/download_services_linked_to_client_report/<int:client_id>')
# def download_services_linked_to_client_report(client_id):
#     generate_services_linked_to_client_report(client_id)
#     return send_file("services_linked_to_client_report.pdf", as_attachment=True)

@reports.route('/download_sessions_report')
def download_sessions_report():
    generate_sessions_report()
    return send_file("sessions_report.pdf", as_attachment=True)


#  <div>
#             <form action="{{ url_for('reports.download_services_linked_to_client_report', client_id=client_id) }}" method="get">
#                 <button type="submit"> Download Services Linked to Client Report </button>
#             </form>
#         </div>
#         <div>
#             <a href="{{ url_for('reports.download_sessions_report') }}" download>
#                 <button> Download Sessions Report </button>
#             </a>
#         </div>
# <div class="reports">
#         <h1>Download Reports</h1>
#         <div>
#             <a href="{{ url_for('reports.download_clients_report') }}" download>
#             <button>Download Clients Report</button>
#             </a>
#         </div>
       
#     </div>