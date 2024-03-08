from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user 
from . import db
from .models import Service, User, Subscription

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main.html')

@main.route('/ClientDashboard')
@login_required
def clientDashboard():
    if current_user.role != 'client':
        abort(403)  # Forbids access if the current user is not a client
    subscribed_services = [subscription.service for subscription in current_user.subscriptions]
    return render_template('clientDashboard.html', name=current_user.name, 
                           active_page='clientDashboard', services=subscribed_services)

@main.route('/StaffDashboard')
@login_required
def staffDashboard():
    if current_user.role != 'staff':
        abort(403)  # Forbids access if the current user is not staff
    return render_template('staffDashboard.html', name=current_user.name, active_page='staffDashboard')

@main.route('/profile')
@login_required
def profile():
    return render_template('services.html', name=current_user.name, active_page='services')


@main.route('/about')
def about():
    return render_template('about.html', active_page='about')

@main.route('/services')
def services():
    all_services = Service.query.all()
    return render_template('services.html', active_page='services', services=all_services)

@main.route('/home')
def home():
    return render_template('main.html', active_page='home')

@main.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact')



