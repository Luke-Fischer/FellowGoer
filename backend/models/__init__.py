from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to register them with SQLAlchemy
from models.user import User
from models.transit import Route, Stop, Trip, StopTime
from models.user_route import UserRoute
from models.chat import Chat, ChatParticipant, Message
