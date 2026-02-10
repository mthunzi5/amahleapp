from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import Property, Booking
from datetime import datetime, timedelta
from sqlalchemy import and_

calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')


@calendar_bp.route('/property/<int:property_id>')
@login_required
def property_calendar(property_id):
    """Show availability calendar for a property"""
    property = Property.query.get_or_404(property_id)
    
    # Check if user is the landlord
    is_owner = current_user.id == property.landlord_id
    
    return render_template('calendar/property.html', property=property, is_owner=is_owner)


@calendar_bp.route('/api/property/<int:property_id>/bookings')
@login_required
def get_property_bookings(property_id):
    """Get bookings for calendar (API endpoint)"""
    property = Property.query.get_or_404(property_id)
    
    # Get all approved bookings for this property
    bookings = Booking.query.filter_by(
        property_id=property_id,
        status='approved'
    ).all()
    
    events = []
    for booking in bookings:
        # Check if user is landlord or the booking owner
        is_owner = current_user.id == property.landlord_id
        is_booker = current_user.id == booking.user_id
        
        event = {
            'id': booking.id,
            'title': f'{booking.num_rooms} room(s) booked',
            'start': booking.check_in_date.isoformat() if hasattr(booking.check_in_date, 'isoformat') else str(booking.check_in_date),
            'end': (booking.check_in_date + timedelta(days=30)).isoformat() if hasattr(booking.check_in_date, 'isoformat') else str(booking.check_in_date),
            'color': '#28a745',
            'extendedProps': {
                'rooms': booking.num_rooms,
                'price': float(booking.total_price),
                'status': booking.status
            }
        }
        
        # Add tenant info only for landlord
        if is_owner:
            event['extendedProps']['tenant'] = booking.user.full_name
            event['extendedProps']['tenant_email'] = booking.user.email
            event['extendedProps']['tenant_phone'] = booking.user.phone
        
        # Add message if user is involved
        if is_owner or is_booker:
            event['extendedProps']['message'] = booking.message
        
        events.append(event)
    
    return jsonify(events)


@calendar_bp.route('/my-calendar')
@login_required
def my_calendar():
    """Show all bookings for current user"""
    if current_user.role == 'landlord':
        # Get all properties
        properties = Property.query.filter_by(landlord_id=current_user.id).all()
        property_ids = [p.id for p in properties]
        
        # Get all bookings for these properties
        bookings = Booking.query.filter(
            Booking.property_id.in_(property_ids),
            Booking.status == 'approved'
        ).all()
    else:
        # Get user's bookings
        bookings = Booking.query.filter_by(
            user_id=current_user.id,
            status='approved'
        ).all()
    
    return render_template('calendar/my_calendar.html', bookings=bookings)


@calendar_bp.route('/api/my-bookings')
@login_required
def get_my_bookings():
    """Get user's bookings for calendar (API endpoint)"""
    if current_user.role == 'landlord':
        # Get all properties
        properties = Property.query.filter_by(landlord_id=current_user.id).all()
        property_ids = [p.id for p in properties]
        
        # Get all bookings for these properties
        bookings = Booking.query.filter(
            Booking.property_id.in_(property_ids),
            Booking.status == 'approved'
        ).all()
    else:
        # Get user's bookings
        bookings = Booking.query.filter_by(
            user_id=current_user.id,
            status='approved'
        ).all()
    
    events = []
    for booking in bookings:
        is_landlord = current_user.role == 'landlord'
        
        event = {
            'id': booking.id,
            'title': f'{booking.property.title} - {booking.num_rooms} room(s)',
            'start': booking.check_in_date.isoformat() if hasattr(booking.check_in_date, 'isoformat') else str(booking.check_in_date),
            'end': (booking.check_in_date + timedelta(days=30)).isoformat() if hasattr(booking.check_in_date, 'isoformat') else str(booking.check_in_date),
            'color': '#0d6efd' if is_landlord else '#28a745',
            'extendedProps': {
                'property': booking.property.title,
                'property_address': f'{booking.property.address}, {booking.property.city}',
                'rooms': booking.num_rooms,
                'price': float(booking.total_price),
                'status': booking.status
            }
        }
        
        if is_landlord:
            event['extendedProps']['tenant'] = booking.user.full_name
            event['extendedProps']['tenant_email'] = booking.user.email
        
        events.append(event)
    
    return jsonify(events)
