from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
from app.models import db, Message, Notification, User, Booking
from app.utils.email import send_email

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')

# Store active connections
active_users = {}


@messages_bp.route('/', methods=['GET'])
@login_required
def inbox():
    """View user's inbox"""
    page = request.args.get('page', 1, type=int)
    
    # Get all conversations
    received_messages = Message.query.filter_by(
        recipient_id=current_user.id
    ).order_by(Message.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('messages/inbox.html', messages=received_messages)


@messages_bp.route('/conversation/<int:user_id>', methods=['GET'])
@login_required
def view_conversation(user_id):
    """View conversation with specific user"""
    other_user = User.query.get_or_404(user_id)
    
    # Get all messages in conversation
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # Mark received messages as read
    unread_messages = Message.query.filter_by(
        recipient_id=current_user.id,
        sender_id=user_id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    
    return render_template(
        'messages/conversation.html',
        other_user=other_user,
        messages=messages
    )


@messages_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Send a message"""
    try:
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        
        if not recipient_id or not content:
            return jsonify({'error': 'Missing recipient_id or content'}), 400
        
        recipient = User.query.get_or_404(recipient_id)
        
        # Create message
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=content
        )
        
        db.session.add(message)
        
        # Create notification for recipient
        notification = Notification(
            user_id=recipient_id,
            title='New Message',
            message=f'{current_user.full_name} sent you a message',
            notification_type='message',
            related_message_id=message.id
        )
        db.session.add(notification)
        
        db.session.commit()
        
        # Emit to recipient if online
        if recipient_id in active_users:
            emit('new_message', {
                'sender_id': current_user.id,
                'sender_name': current_user.full_name,
                'message': content,
                'timestamp': message.created_at.isoformat()
            }, room=active_users[recipient_id])
        
        return jsonify({
            'success': True,
            'messageId': message.id,
            'timestamp': message.created_at.isoformat()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/message/<int:message_id>/read', methods=['PUT'])
@login_required
def mark_as_read(message_id):
    """Mark message as read"""
    try:
        message = Message.query.get_or_404(message_id)
        
        # Check authorization
        if message.recipient_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        message.is_read = True
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/message/<int:message_id>/delete', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """Delete a message"""
    try:
        message = Message.query.get_or_404(message_id)
        
        # Check authorization
        if message.sender_id != current_user.id and message.recipient_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(message)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Get list of conversations"""
    try:
        # Get unique users in conversations
        messages = Message.query.filter(
            (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
        ).order_by(Message.created_at.desc()).all()
        
        conversations = {}
        for msg in messages:
            other_user_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
            
            if other_user_id not in conversations:
                other_user = User.query.get(other_user_id)
                conversations[other_user_id] = {
                    'user_id': other_user_id,
                    'user_name': other_user.full_name,
                    'last_message': msg.content,
                    'last_message_time': msg.created_at.isoformat(),
                    'unread_count': Message.query.filter_by(
                        sender_id=other_user_id,
                        recipient_id=current_user.id,
                        is_read=False
                    ).count()
                }
        
        return jsonify({
            'success': True,
            'conversations': list(conversations.values())
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/send-booking-inquiry/<int:property_id>', methods=['POST'])
@login_required
def send_booking_inquiry(property_id):
    """Send inquiry message to landlord about property"""
    try:
        from app.models import Property
        
        property = Property.query.get_or_404(property_id)
        data = request.get_json()
        
        # Create message
        message = Message(
            sender_id=current_user.id,
            recipient_id=property.landlord_id,
            subject=f'Inquiry about {property.title}',
            content=data.get('message', '')
        )
        
        db.session.add(message)
        
        # Create notification for landlord
        notification = Notification(
            user_id=property.landlord_id,
            title='New Property Inquiry',
            message=f'{current_user.full_name} is interested in {property.title}',
            notification_type='message'
        )
        db.session.add(notification)
        
        db.session.commit()
        
        # Send email to landlord
        send_email(
            recipient=property.landlord.email,
            subject=f'New Inquiry - {property.title}',
            template='property_inquiry',
            tenant=current_user,
            property=property,
            message=data.get('message', '')
        )
        
        return jsonify({
            'success': True,
            'messageId': message.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== SOCKET.IO EVENTS ====================

def register_message_events(socketio):
    """Register socket.io events for real-time messaging"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle user connection"""
        from flask import session
        if current_user.is_authenticated:
            active_users[current_user.id] = request.sid
            emit('user_connected', {
                'user_id': current_user.id,
                'username': current_user.username
            }, broadcast=True)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnection"""
        if current_user.is_authenticated:
            active_users.pop(current_user.id, None)
            emit('user_disconnected', {
                'user_id': current_user.id
            }, broadcast=True)
    
    @socketio.on('join_conversation')
    def join_conversation(data):
        """Join conversation room"""
        conversation_id = f"conv_{min(current_user.id, data['other_user_id'])}_{max(current_user.id, data['other_user_id'])}"
        join_room(conversation_id)
        emit('user_joined', {
            'user_id': current_user.id,
            'username': current_user.username
        }, room=conversation_id)
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle real-time message sending"""
        recipient_id = data['recipient_id']
        content = data['content']
        
        # Create message in database
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=content
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Emit to both users
        conversation_id = f"conv_{min(current_user.id, recipient_id)}_{max(current_user.id, recipient_id)}"
        
        emit('message_received', {
            'sender_id': current_user.id,
            'sender_name': current_user.full_name,
            'content': content,
            'timestamp': message.created_at.isoformat(),
            'message_id': message.id
        }, room=conversation_id)
    
    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing notification"""
        recipient_id = data['recipient_id']
        conversation_id = f"conv_{min(current_user.id, recipient_id)}_{max(current_user.id, recipient_id)}"
        
        emit('user_typing', {
            'user_id': current_user.id,
            'username': current_user.username
        }, room=conversation_id, skip_sid=request.sid)
    
    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """Handle stop typing notification"""
        recipient_id = data['recipient_id']
        conversation_id = f"conv_{min(current_user.id, recipient_id)}_{max(current_user.id, recipient_id)}"
        
        emit('user_stop_typing', {
            'user_id': current_user.id
        }, room=conversation_id, skip_sid=request.sid)
