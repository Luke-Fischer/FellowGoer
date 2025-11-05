from flask import jsonify, request
from sqlalchemy import and_, or_
from models import db
from models.user import User
from models.chat import Chat, ChatParticipant, Message
from utils.auth import token_required


def register_routes(app):
    """Register chat-related endpoints"""

    @app.route('/api/chats', methods=['GET'])
    @token_required
    def get_user_chats(user_id):
        """Get all chats for the current user"""
        try:
            # Get all chats where the user is a participant
            chat_participants = ChatParticipant.query.filter_by(user_id=user_id).all()
            chat_ids = [cp.chat_id for cp in chat_participants]

            if not chat_ids:
                return jsonify({'chats': []}), 200

            # Get the chats
            chats = Chat.query.filter(Chat.id.in_(chat_ids)).order_by(Chat.updated_at.desc()).all()

            return jsonify({
                'chats': [chat.to_dict(current_user_id=user_id) for chat in chats]
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/chats', methods=['POST'])
    @token_required
    def create_or_get_chat(user_id):
        """Create a new chat or get existing chat with a user"""
        try:
            data = request.get_json()
            other_user_id = data.get('other_user_id')

            if not other_user_id:
                return jsonify({'error': 'other_user_id is required'}), 400

            if other_user_id == user_id:
                return jsonify({'error': 'Cannot create chat with yourself'}), 400

            # Check if other user exists
            other_user = User.query.get(other_user_id)
            if not other_user:
                return jsonify({'error': 'User not found'}), 404

            # Check if a chat already exists between these users
            # Find chats where both users are participants
            user_chats = db.session.query(ChatParticipant.chat_id).filter_by(user_id=user_id).all()
            user_chat_ids = [c[0] for c in user_chats]

            if user_chat_ids:
                existing_chat = db.session.query(Chat).join(
                    ChatParticipant, ChatParticipant.chat_id == Chat.id
                ).filter(
                    and_(
                        Chat.id.in_(user_chat_ids),
                        ChatParticipant.user_id == other_user_id
                    )
                ).first()

                if existing_chat:
                    return jsonify({
                        'chat': existing_chat.to_dict(current_user_id=user_id),
                        'created': False
                    }), 200

            # Create new chat
            new_chat = Chat()
            db.session.add(new_chat)
            db.session.flush()  # Get the chat ID

            # Add participants
            participant1 = ChatParticipant(chat_id=new_chat.id, user_id=user_id)
            participant2 = ChatParticipant(chat_id=new_chat.id, user_id=other_user_id)
            db.session.add(participant1)
            db.session.add(participant2)

            db.session.commit()

            return jsonify({
                'chat': new_chat.to_dict(current_user_id=user_id),
                'created': True
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/chats/<int:chat_id>', methods=['GET'])
    @token_required
    def get_chat(user_id, chat_id):
        """Get a specific chat"""
        try:
            # Check if user is a participant in this chat
            participant = ChatParticipant.query.filter_by(
                chat_id=chat_id,
                user_id=user_id
            ).first()

            if not participant:
                return jsonify({'error': 'Chat not found or access denied'}), 404

            chat = Chat.query.get(chat_id)
            if not chat:
                return jsonify({'error': 'Chat not found'}), 404

            return jsonify({'chat': chat.to_dict(current_user_id=user_id)}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/chats/<int:chat_id>/messages', methods=['GET'])
    @token_required
    def get_chat_messages(user_id, chat_id):
        """Get all messages in a chat"""
        try:
            # Check if user is a participant in this chat
            participant = ChatParticipant.query.filter_by(
                chat_id=chat_id,
                user_id=user_id
            ).first()

            if not participant:
                return jsonify({'error': 'Chat not found or access denied'}), 404

            # Get messages
            messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()

            return jsonify({
                'messages': [msg.to_dict() for msg in messages]
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/chats/<int:chat_id>/messages', methods=['POST'])
    @token_required
    def send_message(user_id, chat_id):
        """Send a message in a chat"""
        try:
            # Check if user is a participant in this chat
            participant = ChatParticipant.query.filter_by(
                chat_id=chat_id,
                user_id=user_id
            ).first()

            if not participant:
                return jsonify({'error': 'Chat not found or access denied'}), 404

            data = request.get_json()
            content = data.get('content', '').strip()

            if not content:
                return jsonify({'error': 'Message content is required'}), 400

            # Create message
            message = Message(
                chat_id=chat_id,
                sender_id=user_id,
                content=content
            )
            db.session.add(message)

            # Update chat's updated_at timestamp
            chat = Chat.query.get(chat_id)
            chat.updated_at = db.func.now()

            db.session.commit()

            return jsonify({
                'message': message.to_dict()
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
