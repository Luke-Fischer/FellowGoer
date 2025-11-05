from models import db
from datetime import datetime


class Chat(db.Model):
    """Model for chat conversations between users"""

    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = db.relationship('Message', back_populates='chat', lazy='dynamic')
    participants = db.relationship('ChatParticipant', back_populates='chat', lazy='dynamic')

    def __repr__(self):
        return f'<Chat {self.id}>'

    def to_dict(self, current_user_id=None):
        """Convert chat object to dictionary"""
        participants_list = [p.to_dict() for p in self.participants.all()]

        # Get the other participant (not the current user)
        other_participant = None
        if current_user_id:
            for p in participants_list:
                if p['user_id'] != current_user_id:
                    other_participant = p
                    break

        # Get the last message
        last_message = self.messages.order_by(Message.created_at.desc()).first()

        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'participants': participants_list,
            'other_participant': other_participant,
            'last_message': last_message.to_dict() if last_message else None,
            'unread_count': 0  # TODO: Implement unread count
        }


class ChatParticipant(db.Model):
    """Model for users participating in a chat"""

    __tablename__ = 'chat_participants'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure a user can't join the same chat twice
    __table_args__ = (
        db.UniqueConstraint('chat_id', 'user_id', name='unique_chat_participant'),
    )

    # Relationships
    chat = db.relationship('Chat', back_populates='participants')
    user = db.relationship('User', backref=db.backref('chat_participants', lazy='dynamic'))

    def __repr__(self):
        return f'<ChatParticipant chat_id={self.chat_id} user_id={self.user_id}>'

    def to_dict(self):
        """Convert chat participant object to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.user.username,
            'joined_at': self.joined_at.isoformat()
        }


class Message(db.Model):
    """Model for messages in a chat"""

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    chat = db.relationship('Chat', back_populates='messages')
    sender = db.relationship('User', backref=db.backref('messages', lazy='dynamic'))

    # Index for efficient queries
    __table_args__ = (
        db.Index('idx_chat_created', 'chat_id', 'created_at'),
    )

    def __repr__(self):
        return f'<Message {self.id} from user {self.sender_id}>'

    def to_dict(self):
        """Convert message object to dictionary"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'sender_id': self.sender_id,
            'sender_username': self.sender.username,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }
