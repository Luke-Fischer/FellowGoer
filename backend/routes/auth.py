from flask import request, jsonify
from models import db
from models.user import User


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

            # Create new user (storing password as plain text for now)
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            return jsonify({
                'message': 'User created successfully',
                'user': new_user.to_dict()
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
                return jsonify({'error': 'User does not exist'}), 401

            # Check password (plain text comparison for now)
            if user.password != password:
                return jsonify({'error': 'Invalid credentials'}), 401

            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict()
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
