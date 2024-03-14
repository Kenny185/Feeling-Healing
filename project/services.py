from flask import Blueprint, redirect, url_for, request, flash, abort
from .models import Service, Subscription, Booking, AvailableTimeSlot
from . import db
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import pytz

services = Blueprint('services', __name__)

def create_available_time_slots():
    available_time_slots = []
    current_time = datetime.now()
    start_time = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
    for day in range(7):
        for hour in range(9, 17, 2):
            time_slot = start_time + timedelta(days=day, hours=hour - start_time.hour)
            if time_slot > current_time:
                available_time_slots.append(time_slot)
            else:
                continue
    return available_time_slots

       

@services.route('/add_service', methods=['POST'])
@login_required
def add_service():
    # Check if current user is a staff and authorized to add services
    if current_user.role == 'staff':
        name = request.form.get('name')
        description = request.form.get('description')
        new_service = Service(name=name, description=description, is_active=True)
        db.session.add(new_service)
        db.session.commit()
        flash('New service added successfully!', 'success')
    else:
        flash('You do not have permission to perform this action.', 'danger')
    return redirect(url_for('main.staffDashboard'))

@services.route('/subscribe_to_service/<int:service_id>', methods=['POST'])
@login_required
def subscribe_to_service(service_id):
    if current_user.role != 'client':
        abort(403)  # Ensures only clients can subscribe to services
    service = Service.query.get_or_404(service_id)
    # Check if the user is already subscribed to avoid duplicates
    existing_subscription = Subscription.query.filter_by(user_id=current_user.id, service_id=service_id).first()
    if not existing_subscription:
        new_subscription = Subscription(user_id=current_user.id, service_id=service_id)
        db.session.add(new_subscription)
        db.session.commit()
        flash('You have successfully subscribed to the service.', 'success')
    else:
        flash('You are already subscribed to this service.', 'info')
    return redirect(url_for('main.clientDashboard'))

@services.route('/book_individual_session/<int:service_id>', methods=['POST'])
@login_required
def book_individual_session(service_id):
    available_time_slots = AvailableTimeSlot.query.filter_by(service_id=service_id).all()
    utc = pytz.utc
    
     # timezone_offset = int(request.form['timezone_offset'])
    chosen_time_str = request.form['time_slot']
    chosen_time = datetime.strptime(chosen_time_str, '%Y-%m-%d %H:%M:%S')
    # chosen_time += timedelta(minutes=timezone_offset)
    # utc_time = chosen_time.astimezone(utc)
    if chosen_time not in [slot.time_slot for slot in available_time_slots]:
        flash('Selected time slot is not available.', 'danger')
        return redirect(url_for('main.clientDashboard'))
    
    conflicting_bookings = Booking.query.filter_by(service_id=service_id, time_slot=chosen_time).first()
    if conflicting_bookings:
        flash('That slot is already booked!', 'danger')
        return redirect(url_for('main.clientDashboard'))
    
    new_booking = Booking(user_id=current_user.id, service_id=service_id, time_slot=chosen_time)
    db.session.add(new_booking)
    db.session.commit()
    
    available_time_slots = [slot for slot in available_time_slots if slot.time_slot != chosen_time]
        
    flash('Booking successful!', 'success')
    return redirect(url_for('main.clientDashboard', available_time_slots=available_time_slots ))
