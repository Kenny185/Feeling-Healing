from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Service, Subscription, Booking, AvailableTimeSlot
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import pytz
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html', active_page='login')

@auth.route('/signup')
def signup():
    return render_template('signup.html', active_page='signup')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    role = request.form.get('role')
    
    if not email or not name or not password:
        flash('Kindly fill all the details')
        return redirect(url_for('auth.signup'))
    
    user = User.query.filter_by(email=email).first() 
    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'), role=role)
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    if new_user.role == 'client':
        return redirect(url_for('auth.clientLogin'))
    elif new_user.role == 'staff':
        return redirect(url_for('auth.staffLogin'))
        
@auth.route('/StaffLogin')
def staffLogin():
    return render_template('staffLogin.html', active_page='login')

@auth.route('/StaffLogin', methods=['POST'])
def staff_login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    if not email or not password:
        flash('Please check your details')
        return redirect(url_for('auth.staffLogin'))
    
    user = User.query.filter_by(email=email).first()
    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password)or user.role != 'staff':
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.staffLogin'))    
    # if the user doesn't exist or password is wrong, reload the page
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.staffDashboard'))

@auth.route('/ClientLogin')
def clientLogin():
    return render_template('clientLogin.html', active_page='login')

@auth.route('/ClientLogin', methods=['POST'])
def client_login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    if not email or not password:
        flash('Please check your details')
        return redirect(url_for('auth.clientLogin'))
    
    user = User.query.filter_by(email=email).first()
    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password)or user.role != 'client':
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.clientLogin'))    
    # if the user doesn't exist or password is wrong, reload the page
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.clientDashboard'))

@auth.route('/add_service', methods=['POST'])
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

@auth.route('/subscribe_to_service/<int:service_id>', methods=['POST'])
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

@auth.route('/book_individual_session/<int:service_id>', methods=['POST'])
@login_required
def book_individual_session(service_id):
    utc = pytz.utc
    available_time_slots = []
    start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    for day in range(7):
        for hour in range(9, 17, 2):  # Assuming 9 AM to 5 PM schedule
            time_slot = start_time + timedelta(days=day, hours=hour-start_time.hour)
            available_time_slots.append(time_slot.strptime('%Y-%m-%d %H:%M'))
            # Assume 'time_slot' is a string like "2023-07-21 14:00"
    service = Service.query.get(service_id)
    for slot in available_time_slots:
         if not available_slot:  # Check if the time slot is not already added
            available_slot = AvailableTimeSlot(service_id=service.id, time_slot=slot)
            db.session.add(available_slot)
    db.session.commit()
    timezone_offset = int(request.form['timezone_offset'])
    chosen_time = request.form['time_slot']
    chosen_time = datetime.strptime(chosen_time, '%Y-%m-%d %H:%M')
    chosen_time += timedelta(minutes=timezone_offset)
    utc_time = chosen_time.astimezone(utc)
    conflicting_bookings = Booking.query.filter_by(service_id=service_id, time_slot=utc_time).first()
    if conflicting_bookings:
        flash('That slot is already booked!', 'danger')
    new_booking = Booking(user_id=current_user.id, service_id=service_id, time_slot=utc_time)
    db.session.add(new_booking)
    db.session.commit()
    flash('Booking successful!', 'success')
    return redirect(url_for('main.clientDashboard', available_time_slots=available_time_slots ))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))