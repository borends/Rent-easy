from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.message import Message
from app.models.user import User
from app import db
from datetime import datetime
from sqlalchemy import or_

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/')
@login_required
def index():
    # Получаем список чатов
    chats = db.session.query(User).distinct().join(Message, 
        or_(
            (Message.sender_id == User.id) & (Message.recipient_id == current_user.id),
            (Message.recipient_id == User.id) & (Message.sender_id == current_user.id)
        )
    ).all()
    return render_template('chat/index.html', chats=chats)

@bp.route('/<int:user_id>')
@login_required
def chat(user_id):
    try:
        other_user = User.query.get_or_404(user_id)
        messages = Message.query.filter(
            or_(
                (Message.sender_id == current_user.id) & (Message.recipient_id == user_id),
                (Message.recipient_id == current_user.id) & (Message.sender_id == user_id)
            )
        ).order_by(Message.created_at.asc()).all()
        
        # Получаем список всех чатов для сайдбара
        chats = db.session.query(User).distinct().join(Message, 
            or_(
                (Message.sender_id == User.id) & (Message.recipient_id == current_user.id),
                (Message.recipient_id == User.id) & (Message.sender_id == current_user.id)
            )
        ).all()
        
        return render_template('chat/chat.html', 
                             other_user=other_user, 
                             messages=messages, 
                             chats=chats)
    except Exception as e:
        current_app.logger.error(f"Error in chat route: {str(e)}")
        return str(e), 500

@bp.route('/<int:user_id>/send', methods=['POST'])
@login_required
def send_message(user_id):
    print(f"\n=== New message request ===")
    print(f"From user: {current_user.id} to user: {user_id}")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data or 'message' not in data:
            print("Error: No message in request data")
            return jsonify({'error': 'No message provided'}), 400
        
        message_text = data['message'].strip()
        if not message_text:
            print("Error: Empty message")
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        print(f"Creating message with text: {message_text}")
        
        message = Message(
            sender_id=current_user.id,
            recipient_id=user_id,
            body=message_text,
            created_at=datetime.utcnow()
        )
        
        db.session.add(message)
        db.session.commit()
        
        response_data = {
            'id': message.id,
            'sender_id': message.sender_id,
            'recipient_id': message.recipient_id,
            'body': message.body,
            'created_at': message.created_at.isoformat()
        }
        
        print(f"Message saved successfully. Response data: {response_data}")
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        current_app.logger.error(f"Error sending message: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:user_id>/messages')
@login_required
def get_messages(user_id):
    try:
        since = request.args.get('since')
        query = Message.query.filter(
            or_(
                (Message.sender_id == current_user.id) & (Message.recipient_id == user_id),
                (Message.recipient_id == current_user.id) & (Message.sender_id == user_id)
            )
        )
        
        if since:
            try:
                since_date = datetime.fromisoformat(since)
                query = query.filter(Message.created_at > since_date)
            except ValueError:
                pass
        
        messages = query.order_by(Message.created_at.asc()).all()
        
        return jsonify([{
            'id': message.id,
            'sender_id': message.sender_id,
            'recipient_id': message.recipient_id,
            'body': message.body,
            'created_at': message.created_at.isoformat()
        } for message in messages])
        
    except Exception as e:
        current_app.logger.error(f"Error getting messages: {str(e)}")
        return jsonify({'error': str(e)}), 500