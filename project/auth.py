from flask import Blueprint, render_template, redirect, session, url_for, request, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user

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
    session['user_id'] = user.id 
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
    session['user_id'] = user.id 
    return redirect(url_for('main.clientDashboard'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    return redirect(url_for('main.index'))