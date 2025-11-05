from flask import jsonify, request
from models import db
from models.transit import Route
from models.user_route import UserRoute
from utils.auth import token_required


def register_routes(app):
    """Register route management endpoints"""

    @app.route('/api/routes', methods=['GET'])
    @token_required
    def get_all_routes(user_id):
        """Get all available GO Transit routes"""
        try:
            routes = Route.query.order_by(Route.route_short_name).all()
            return jsonify({
                'routes': [route.to_dict() for route in routes]
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/routes', methods=['GET'])
    @token_required
    def get_user_routes(user_id):
        """Get current user's selected routes"""
        try:
            user_routes = UserRoute.query.filter_by(user_id=user_id).all()
            return jsonify({
                'routes': [ur.to_dict() for ur in user_routes]
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/routes', methods=['POST'])
    @token_required
    def add_user_route(user_id):
        """Add a route to user's selection"""
        try:
            data = request.get_json()
            route_id = data.get('route_id')

            if not route_id:
                return jsonify({'error': 'route_id is required'}), 400

            # Check if route exists
            route = Route.query.get(route_id)
            if not route:
                return jsonify({'error': 'Route not found'}), 404

            # Check if user already has this route
            existing = UserRoute.query.filter_by(
                user_id=user_id,
                route_id=route_id
            ).first()

            if existing:
                return jsonify({'error': 'Route already added'}), 409

            # Add the route
            user_route = UserRoute(user_id=user_id, route_id=route_id)
            db.session.add(user_route)
            db.session.commit()

            return jsonify({
                'message': 'Route added successfully',
                'route': user_route.to_dict()
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/routes/<int:user_route_id>', methods=['DELETE'])
    @token_required
    def delete_user_route(user_id, user_route_id):
        """Remove a route from user's selection"""
        try:
            user_route = UserRoute.query.filter_by(
                id=user_route_id,
                user_id=user_id
            ).first()

            if not user_route:
                return jsonify({'error': 'Route not found'}), 404

            db.session.delete(user_route)
            db.session.commit()

            return jsonify({'message': 'Route removed successfully'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
