from models import db
from datetime import time


class Route(db.Model):
    """Model for GO Transit routes (trains and buses)"""

    __tablename__ = 'routes'

    route_id = db.Column(db.String(50), primary_key=True)
    agency_id = db.Column(db.String(10))
    route_short_name = db.Column(db.String(10), nullable=False)
    route_long_name = db.Column(db.String(100), nullable=False)
    route_type = db.Column(db.Integer, nullable=False)  # 2=train, 3=bus
    route_color = db.Column(db.String(6))
    route_text_color = db.Column(db.String(6))

    # Relationship to trips
    trips = db.relationship('Trip', back_populates='route', lazy='dynamic')

    def __repr__(self):
        return f'<Route {self.route_short_name} - {self.route_long_name}>'

    def to_dict(self):
        """Convert route object to dictionary"""
        return {
            'route_id': self.route_id,
            'route_short_name': self.route_short_name,
            'route_long_name': self.route_long_name,
            'route_type': 'train' if self.route_type == 2 else 'bus',
            'route_color': self.route_color,
            'route_text_color': self.route_text_color
        }


class Stop(db.Model):
    """Model for GO Transit stops/stations"""

    __tablename__ = 'stops'

    stop_id = db.Column(db.String(50), primary_key=True)
    stop_name = db.Column(db.String(200), nullable=False)
    stop_lat = db.Column(db.Float, nullable=False)
    stop_lon = db.Column(db.Float, nullable=False)
    zone_id = db.Column(db.String(10))
    stop_url = db.Column(db.String(255))
    location_type = db.Column(db.Integer)
    parent_station = db.Column(db.String(50))
    wheelchair_boarding = db.Column(db.Integer)
    stop_code = db.Column(db.String(20))

    # Relationship to stop times
    stop_times = db.relationship('StopTime', back_populates='stop', lazy='dynamic')

    def __repr__(self):
        return f'<Stop {self.stop_id} - {self.stop_name}>'

    def to_dict(self):
        """Convert stop object to dictionary"""
        return {
            'stop_id': self.stop_id,
            'stop_name': self.stop_name,
            'stop_lat': self.stop_lat,
            'stop_lon': self.stop_lon,
            'wheelchair_boarding': self.wheelchair_boarding,
            'stop_url': self.stop_url
        }


class Trip(db.Model):
    """Model for individual GO Transit trips (specific train/bus runs)"""

    __tablename__ = 'trips'

    trip_id = db.Column(db.String(50), primary_key=True)
    route_id = db.Column(db.String(50), db.ForeignKey('routes.route_id'), nullable=False)
    service_id = db.Column(db.String(50), nullable=False)
    trip_headsign = db.Column(db.String(100))
    trip_short_name = db.Column(db.String(50))
    direction_id = db.Column(db.Integer)  # 0=outbound, 1=inbound
    block_id = db.Column(db.String(50))
    shape_id = db.Column(db.String(50))
    wheelchair_accessible = db.Column(db.Integer)
    bikes_allowed = db.Column(db.Integer)
    route_variant = db.Column(db.String(10))

    # Relationships
    route = db.relationship('Route', back_populates='trips')
    stop_times = db.relationship('StopTime', back_populates='trip', lazy='dynamic',
                                 order_by='StopTime.stop_sequence')

    def __repr__(self):
        return f'<Trip {self.trip_id} - {self.trip_headsign}>'

    def to_dict(self):
        """Convert trip object to dictionary"""
        return {
            'trip_id': self.trip_id,
            'route_id': self.route_id,
            'service_id': self.service_id,
            'trip_headsign': self.trip_headsign,
            'direction_id': self.direction_id,
            'wheelchair_accessible': self.wheelchair_accessible == 1,
            'bikes_allowed': self.bikes_allowed == 1
        }


class StopTime(db.Model):
    """Model for scheduled stop times (when trips arrive at stops)"""

    __tablename__ = 'stop_times'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.String(50), db.ForeignKey('trips.trip_id'), nullable=False)
    stop_id = db.Column(db.String(50), db.ForeignKey('stops.stop_id'), nullable=False)
    arrival_time = db.Column(db.Time, nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    stop_sequence = db.Column(db.Integer, nullable=False)
    pickup_type = db.Column(db.Integer)
    drop_off_type = db.Column(db.Integer)
    stop_headsign = db.Column(db.String(100))

    # Relationships
    trip = db.relationship('Trip', back_populates='stop_times')
    stop = db.relationship('Stop', back_populates='stop_times')

    # Composite index for efficient queries
    __table_args__ = (
        db.Index('idx_trip_stop', 'trip_id', 'stop_sequence'),
        db.Index('idx_stop_time', 'stop_id', 'arrival_time'),
    )

    def __repr__(self):
        return f'<StopTime trip={self.trip_id} stop={self.stop_id} seq={self.stop_sequence}>'

    def to_dict(self):
        """Convert stop time object to dictionary"""
        return {
            'trip_id': self.trip_id,
            'stop_id': self.stop_id,
            'arrival_time': self.arrival_time.strftime('%H:%M:%S'),
            'departure_time': self.departure_time.strftime('%H:%M:%S'),
            'stop_sequence': self.stop_sequence
        }
