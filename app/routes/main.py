from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Property, Review, Booking, User
from app import db
from sqlalchemy import or_, and_
import random

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get featured properties and random properties
    featured_properties = Property.query.filter_by(is_available=True, is_featured=True).limit(6).all()
    
    # Get random properties if not enough featured
    all_properties = Property.query.filter_by(is_available=True).all()
    if len(all_properties) > 0:
        random.shuffle(all_properties)
        display_properties = all_properties[:12]
    else:
        display_properties = []
    
    # Get some recent reviews
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(6).all()
    
    return render_template('index.html', 
                         properties=display_properties, 
                         featured_properties=featured_properties,
                         reviews=recent_reviews)


@main_bp.route('/properties')
def properties():
    # Get filter parameters
    city = request.args.get('city', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    bedrooms = request.args.get('bedrooms', type=int)
    property_type = request.args.get('property_type', '')
    
    # Build query
    query = Property.query.filter_by(is_available=True)
    
    if city:
        query = query.filter(Property.city.ilike(f'%{city}%'))
    
    if min_price:
        query = query.filter(Property.price_per_month >= min_price)
    
    if max_price:
        query = query.filter(Property.price_per_month <= max_price)
    
    if bedrooms:
        query = query.filter(Property.bedrooms >= bedrooms)
    
    if property_type:
        query = query.filter(Property.property_type == property_type)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 12
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    properties_list = pagination.items
    
    # Get unique cities for filter
    cities = db.session.query(Property.city).distinct().all()
    cities = [c[0] for c in cities]
    
    return render_template('properties/list.html', 
                         properties=properties_list,
                         pagination=pagination,
                         cities=cities)


@main_bp.route('/property/<int:id>')
def property_detail(id):
    property = Property.query.get_or_404(id)
    reviews = Review.query.filter_by(property_id=id).order_by(Review.created_at.desc()).all()
    
    # Check if user has already booked this property
    has_booked = False
    if current_user.is_authenticated:
        has_booked = Booking.query.filter_by(
            user_id=current_user.id, 
            property_id=id
        ).first() is not None
    
    return render_template('properties/detail.html', 
                         property=property, 
                         reviews=reviews,
                         has_booked=has_booked)


@main_bp.route('/property/<int:id>/book', methods=['GET', 'POST'])
@login_required
def book_property(id):
    if current_user.role == 'landlord':
        flash('Landlords cannot book properties.', 'warning')
        return redirect(url_for('main.property_detail', id=id))
    
    property = Property.query.get_or_404(id)
    
    if not property.is_available or property.available_rooms <= 0:
        flash('This property is not available for booking.', 'danger')
        return redirect(url_for('main.property_detail', id=id))
    
    if request.method == 'POST':
        check_in_date = request.form.get('check_in_date')
        num_rooms = int(request.form.get('num_rooms', 1))
        message = request.form.get('message', '')
        
        if num_rooms > property.available_rooms:
            flash(f'Only {property.available_rooms} rooms available.', 'danger')
            return redirect(url_for('main.book_property', id=id))
        
        # Calculate total price (assuming monthly rent)
        total_price = property.price_per_month * num_rooms
        
        booking = Booking(
            user_id=current_user.id,
            property_id=property.id,
            check_in_date=check_in_date,
            num_rooms=num_rooms,
            total_price=total_price,
            message=message,
            status='pending'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        flash('Booking request submitted successfully! The landlord will review your request.', 'success')
        return redirect(url_for('main.my_bookings'))
    
    return render_template('properties/book.html', property=property)


@main_bp.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('bookings/my_bookings.html', bookings=bookings)


@main_bp.route('/booking/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_booking(id):
    booking = Booking.query.get_or_404(id)
    
    if booking.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.my_bookings'))
    
    if booking.status == 'approved':
        # Return available rooms
        property = Property.query.get(booking.property_id)
        property.available_rooms += booking.num_rooms
    
    booking.status = 'cancelled'
    db.session.commit()
    
    flash('Booking cancelled successfully.', 'info')
    return redirect(url_for('main.my_bookings'))


@main_bp.route('/property/<int:id>/review', methods=['GET', 'POST'])
@login_required
def add_review(id):
    property = Property.query.get_or_404(id)
    
    # Check if user has booked this property
    has_booking = Booking.query.filter_by(
        user_id=current_user.id,
        property_id=id,
        status='approved'
    ).first()
    
    if not has_booking:
        flash('You can only review properties you have booked.', 'warning')
        return redirect(url_for('main.property_detail', id=id))
    
    # Check if user already reviewed
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        property_id=id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this property.', 'info')
        return redirect(url_for('main.property_detail', id=id))
    
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        title = request.form.get('title', '')
        comment = request.form.get('comment')
        
        review = Review(
            user_id=current_user.id,
            property_id=property.id,
            rating=rating,
            title=title,
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('main.property_detail', id=id))
    
    return render_template('reviews/add.html', property=property)
