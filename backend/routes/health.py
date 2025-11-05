from flask import jsonify


def register_routes(app):
    """Register health check routes"""

    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy'}), 200
