"""
Startup script for Render deployment
Checks if routes are imported, imports if needed, then starts the app
"""
import os
import subprocess
from app import app
from models import db
from models.transit import Route

def ensure_data_imported():
    """Check if routes exist, import if needed"""
    with app.app_context():
        route_count = Route.query.count()

        if route_count == 0:
            print("=" * 60)
            print("No routes found in database. Running GTFS import...")
            print("=" * 60)

            # Run the import script
            import import_gtfs
            import_gtfs.main()

            print("=" * 60)
            print("Data import completed!")
            print("=" * 60)
        else:
            print(f"Database already contains {route_count} routes. Skipping import.")

if __name__ == '__main__':
    # Ensure data is imported
    ensure_data_imported()

    # Start the Flask app with gunicorn
    port = int(os.environ.get('PORT', 5000))
    os.system(f'gunicorn --bind 0.0.0.0:{port} app:app')
