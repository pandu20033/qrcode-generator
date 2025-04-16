from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
from models import User
from extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('qr.dashboard'))

    if request.method == 'POST':
        if not request.is_json:
            return jsonify({'error': 'Invalid request format'}), 400

        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(name=data['name'], email=data['email'], password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'Registration successful'}), 201

    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('qr.dashboard'))

    if request.method == 'POST':
        if not request.is_json:
            return jsonify({'error': 'Invalid request format'}), 400

        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()

        if user and bcrypt.check_password_hash(user.password_hash, data['password']):
            login_user(user)
            return jsonify({'message': 'Login successful'}), 200

        return jsonify({'error': 'Invalid email or password'}), 401

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
