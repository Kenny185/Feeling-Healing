from flask import Blueprint, redirect, url_for, request, flash, abort
from .models import Service, Subscription, Booking, AvailableTimeSlot
from . import db
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import pytz

services = Blueprint('services', __name__)

def create_available_time_slots():
    available_time_slots = []
    start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    for day in range(7):
        for hour in range(9, 17, 2):  # Assuming 9 AM to 5 PM schedule
            time_slot = start_time + timedelta(days=day, hours=hour-start_time.hour)
            available_time_slots.append(time_slot)
            # Assume 'time_slot' is a string like "2023-07-21 14:00"
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
    available_time_slots = create_available_time_slots()
    utc = pytz.utc
    
    # avail_time_slots = AvailableTimeSlot.available_time_slots(service_id)
    # for slot in avail_time_slots:
    #     if not slot:  # Check if the time slot is not already added
    #         # available_slot = AvailableTimeSlot.available_time_slots(service_id=service.id, time_slot=slot)
    #         db.session.add(slot)
    #         db.session.commit()
    # timezone_offset = int(request.form['timezone_offset'])
    chosen_time_str = request.form['time_slot']
    chosen_time = datetime.strptime(chosen_time_str, '%Y-%m-%d %H:%M')
    # chosen_time += timedelta(minutes=timezone_offset)
    # utc_time = chosen_time.astimezone(utc)
    conflicting_bookings = Booking.query.filter_by(service_id=service_id, time_slot=chosen_time).first()
    if conflicting_bookings:
        flash('That slot is already booked!', 'danger')
    new_booking = Booking(user_id=current_user.id, service_id=service_id, time_slot=chosen_time)
    db.session.add(new_booking)
    db.session.commit()
    flash('Booking successful!', 'success')
    return redirect(url_for('main.clientDashboard', available_time_slots=available_time_slots ))
