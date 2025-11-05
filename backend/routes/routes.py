from flask import jsonify, request
from sqlalchemy import and_, func
from models import db
from models.user import User
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

    @app.route('/api/connect/users', methods=['GET'])
    @token_required
    def get_matching_users(user_id):
        """Get users who share at least one route with the current user"""
        try:
            # Get the current user's route IDs
            user_route_ids = db.session.query(UserRoute.route_id).filter_by(user_id=user_id).all()
            user_route_ids = [r[0] for r in user_route_ids]

            if not user_route_ids:
                return jsonify({'users': []}), 200

            # Find other users who have at least one matching route
            matching_users = db.session.query(
                User.id,
                User.username,
                User.email,
                func.count(UserRoute.route_id).label('shared_routes_count')
            ).join(
                UserRoute, UserRoute.user_id == User.id
            ).filter(
                and_(
                    User.id != user_id,  # Exclude current user
                    UserRoute.route_id.in_(user_route_ids)  # Match routes
                )
            ).group_by(
                User.id, User.username, User.email
            ).all()

            # Get detailed information for each matching user
            result = []
            for match in matching_users:
                # Get the shared routes
                shared_routes = db.session.query(Route).join(
                    UserRoute, UserRoute.route_id == Route.route_id
                ).filter(
                    and_(
                        UserRoute.user_id == match.id,
                        UserRoute.route_id.in_(user_route_ids)
                    )
                ).all()

                result.append({
                    'id': match.id,
                    'username': match.username,
                    'email': match.email,
                    'shared_routes_count': match.shared_routes_count,
                    'shared_routes': [route.to_dict() for route in shared_routes]
                })

            return jsonify({'users': result}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
