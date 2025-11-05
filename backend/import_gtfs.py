"""
Script to import GTFS data from text files into the database.
Run this script to populate the Routes, Stops, Trips, and StopTimes tables.
"""

import csv
import os
from datetime import datetime
from app import app
from models import db
from models.transit import Route, Stop, Trip, StopTime


def parse_time(time_str):
    """Parse GTFS time format (HH:MM:SS) which can exceed 24 hours"""
    if not time_str or time_str.strip() == '':
        return None

    parts = time_str.strip().split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])

    # GTFS allows hours > 24 for trips that go past midnight
    # We'll normalize to 24-hour format
    hours = hours % 24

    return datetime.strptime(f"{hours:02d}:{minutes:02d}:{seconds:02d}", "%H:%M:%S").time()


def import_routes(data_dir):
    """Import routes from routes.txt"""
    print("Importing routes...")
    count = 0

    with open(os.path.join(data_dir, 'routes.txt'), 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            route = Route(
                route_id=row['route_id'],
                agency_id=row['agency_id'],
                route_short_name=row['route_short_name'],
                route_long_name=row['route_long_name'],
                route_type=int(row['route_type']),
                route_color=row.get('route_color'),
                route_text_color=row.get('route_text_color')
            )
            db.session.add(route)
            count += 1

            if count % 10 == 0:
                db.session.commit()

    db.session.commit()
    print(f"[OK] Imported {count} routes")


def import_stops(data_dir):
    """Import stops from stops.txt"""
    print("Importing stops...")
    count = 0

    with open(os.path.join(data_dir, 'stops.txt'), 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stop = Stop(
                stop_id=row['stop_id'],
                stop_name=row['stop_name'],
                stop_lat=float(row['stop_lat']),
                stop_lon=float(row['stop_lon']),
                zone_id=row.get('zone_id'),
                stop_url=row.get('stop_url'),
                location_type=int(row['location_type']) if row.get('location_type') else None,
                parent_station=row.get('parent_station'),
                wheelchair_boarding=int(row['wheelchair_boarding']) if row.get('wheelchair_boarding') else None,
                stop_code=row.get('stop_code')
            )
            db.session.add(stop)
            count += 1

            if count % 50 == 0:
                db.session.commit()

    db.session.commit()
    print(f"[OK] Imported {count} stops")


def import_trips(data_dir):
    """Import trips from trips.txt"""
    print("Importing trips...")
    count = 0

    with open(os.path.join(data_dir, 'trips.txt'), 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trip = Trip(
                trip_id=row['trip_id'],
                route_id=row['route_id'],
                service_id=row['service_id'],
                trip_headsign=row.get('trip_headsign'),
                trip_short_name=row.get('trip_short_name'),
                direction_id=int(row['direction_id']) if row.get('direction_id') else None,
                block_id=row.get('block_id'),
                shape_id=row.get('shape_id'),
                wheelchair_accessible=int(row['wheelchair_accessible']) if row.get('wheelchair_accessible') else None,
                bikes_allowed=int(row['bikes_allowed']) if row.get('bikes_allowed') else None,
                route_variant=row.get('route_variant')
            )
            db.session.add(trip)
            count += 1

            if count % 500 == 0:
                db.session.commit()
                print(f"  {count} trips imported...")

    db.session.commit()
    print(f"[OK] Imported {count} trips")


def import_stop_times(data_dir):
    """Import stop times from stop_times.txt (WARNING: This is a large file!)"""
    print("Importing stop times (this may take a while)...")
    count = 0

    with open(os.path.join(data_dir, 'stop_times.txt'), 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            arrival_time = parse_time(row['arrival_time'])
            departure_time = parse_time(row['departure_time'])

            if arrival_time and departure_time:
                stop_time = StopTime(
                    trip_id=row['trip_id'],
                    stop_id=row['stop_id'],
                    arrival_time=arrival_time,
                    departure_time=departure_time,
                    stop_sequence=int(row['stop_sequence']),
                    pickup_type=int(row['pickup_type']) if row.get('pickup_type') else 0,
                    drop_off_type=int(row['drop_off_type']) if row.get('drop_off_type') else 0,
                    stop_headsign=row.get('stop_headsign')
                )
                db.session.add(stop_time)
                count += 1

                if count % 1000 == 0:
                    db.session.commit()
                    print(f"  {count} stop times imported...")

    db.session.commit()
    print(f"[OK] Imported {count} stop times")


def main():
    """Main import function"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found at {data_dir}")
        return

    print("\n" + "="*60)
    print("GO Transit GTFS Data Import")
    print("="*60 + "\n")

    with app.app_context():
        # Check if data already exists
        existing_routes = Route.query.count()
        if existing_routes > 0:
            print(f"[INFO] Database already contains {existing_routes} routes.")
            print("Clearing existing data...")
            StopTime.query.delete()
            Trip.query.delete()
            Stop.query.delete()
            Route.query.delete()
            db.session.commit()
            print("[OK] Cleared existing data\n")

        # Import data
        try:
            import_routes(data_dir)
            import_stops(data_dir)
            import_trips(data_dir)
            import_stop_times(data_dir)

            print("\n" + "="*60)
            print("[SUCCESS] Import completed successfully!")
            print("="*60 + "\n")

            # Show summary
            print("Database summary:")
            print(f"  Routes: {Route.query.count()}")
            print(f"  Stops: {Stop.query.count()}")
            print(f"  Trips: {Trip.query.count()}")
            print(f"  Stop Times: {StopTime.query.count()}")
            print()

        except Exception as e:
            print(f"\n[ERROR] Error during import: {e}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    main()
