from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes import auth, health, routes, chats

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Register routes
auth.register_routes(app)
health.register_routes(app)
routes.register_routes(app)
chats.register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
