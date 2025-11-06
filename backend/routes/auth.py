from flask import request, jsonify
from models import db
from models.user import User
from utils.auth import generate_token


def register_routes(app):
    """Register authentication routes"""

    @app.route('/api/signup', methods=['POST'])
    def signup():
        """User signup endpoint"""
        try:
            data = request.get_json()

            # Validate input
            if not data or not data.get('username') or not data.get('email') or not data.get('password'):
                return jsonify({'error': 'Missing required fields'}), 400

            username = data['username']
            email = data['email']
            password = data['password']

            # Check if user already exists
            if User.query.filter_by(username=username).first():
                return jsonify({'error': 'Username already exists'}), 409

            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already exists'}), 409

            # Create new user with hashed password
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Generate JWT token
            token = generate_token(new_user.id, app.config['SECRET_KEY'])

            return jsonify({
                'message': 'User created successfully',
                'user': new_user.to_dict(),
                'token': token
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/login', methods=['POST'])
    def login():
        """User login endpoint"""
        try:
            data = request.get_json()

            # Validate input
            if not data or not data.get('username') or not data.get('password'):
                return jsonify({'error': 'Missing username or password'}), 400

            username = data['username']
            password = data['password']

            # Find user
            user = User.query.filter_by(username=username).first()

            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401

            # Check password using bcrypt
            if not user.check_password(password):
                return jsonify({'error': 'Invalid credentials'}), 401

            # Generate JWT token
            token = generate_token(user.id, app.config['SECRET_KEY'])

            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict(),
                'token': token
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
