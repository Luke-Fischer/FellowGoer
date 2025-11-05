from models import db
from datetime import datetime


class UserRoute(db.Model):
    """Model for storing user's selected routes"""

    __tablename__ = 'user_routes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    route_id = db.Column(db.String(50), db.ForeignKey('routes.route_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure a user can't add the same route twice
    __table_args__ = (
        db.UniqueConstraint('user_id', 'route_id', name='unique_user_route'),
    )

    # Relationships
    user = db.relationship('User', backref=db.backref('user_routes', lazy='dynamic'))
    route = db.relationship('Route', backref=db.backref('user_routes', lazy='dynamic'))

    def __repr__(self):
        return f'<UserRoute user_id={self.user_id} route_id={self.route_id}>'

    def to_dict(self):
        """Convert user route object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'route_id': self.route_id,
            'created_at': self.created_at.isoformat(),
            'route': self.route.to_dict() if self.route else None
        }
