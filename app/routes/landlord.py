from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Property, Booking, Review
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from app.utils.email import send_booking_approved_email, send_booking_rejected_email

landlord_bp = Blueprint('landlord', __name__, url_prefix='/landlord')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def landlord_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'landlord':
            flash('You must be a landlord to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@landlord_bp.route('/dashboard')
@login_required
@landlord_required
def dashboard():
    # Get landlord's properties
    properties = Property.query.filter_by(landlord_id=current_user.id).all()
    
    # Get pending bookings
    property_ids = [p.id for p in properties]
    pending_bookings = Booking.query.filter(
        Booking.property_id.in_(property_ids),
        Booking.status == 'pending'
    ).order_by(Booking.created_at.desc()).all()
    
    # Get statistics
    total_properties = len(properties)
    total_bookings = Booking.query.filter(Booking.property_id.in_(property_ids)).count()
    approved_bookings = Booking.query.filter(
        Booking.property_id.in_(property_ids),
        Booking.status == 'approved'
    ).count()
    
    # Calculate total revenue (from approved bookings)
    total_revenue = db.session.query(db.func.sum(Booking.total_price)).filter(
        Booking.property_id.in_(property_ids),
        Booking.status == 'approved'
    ).scalar() or 0
    
    return render_template('landlord/dashboard.html',
                         properties=properties,
                         pending_bookings=pending_bookings,
                         total_properties=total_properties,
                         total_bookings=total_bookings,
                         approved_bookings=approved_bookings,
                         total_revenue=total_revenue)


@landlord_bp.route('/properties')
@login_required
@landlord_required
def properties():
    properties = Property.query.filter_by(landlord_id=current_user.id).order_by(Property.created_at.desc()).all()
    return render_template('landlord/properties.html', properties=properties)


@landlord_bp.route('/property/add', methods=['GET', 'POST'])
@login_required
@landlord_required
def add_property():
    if request.method == 'POST':
        # Handle image uploads
        uploaded_files = request.files.getlist('images')
        image_paths = []
        
        if uploaded_files and uploaded_files[0].filename:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to prevent filename conflicts
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    image_paths.append(f"uploads/{filename}")
        
        property = Property(
            landlord_id=current_user.id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            property_type=request.form.get('property_type'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            province=request.form.get('province'),
            postal_code=request.form.get('postal_code'),
            bedrooms=int(request.form.get('bedrooms')),
            bathrooms=int(request.form.get('bathrooms')),
            total_rooms=int(request.form.get('total_rooms')),
            available_rooms=int(request.form.get('total_rooms')),  # Initially all rooms are available
            price_per_month=float(request.form.get('price_per_month')),
            amenities=request.form.get('amenities'),
            images=','.join(image_paths) if image_paths else None,
            is_available=True
        )
        
        db.session.add(property)
        db.session.commit()
        
        flash('Property added successfully!', 'success')
        return redirect(url_for('landlord.properties'))
    
    return render_template('landlord/add_property.html')


@landlord_bp.route('/property/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@landlord_required
def edit_property(id):
    property = Property.query.get_or_404(id)
    
    if property.landlord_id != current_user.id:
        flash('You can only edit your own properties.', 'danger')
        return redirect(url_for('landlord.properties'))
    
    if request.method == 'POST':
        # Handle new image uploads
        uploaded_files = request.files.getlist('images')
        new_image_paths = []
        
        if uploaded_files and uploaded_files[0].filename:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to prevent filename conflicts
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    new_image_paths.append(f"uploads/{filename}")
        
        # Keep existing images unless explicitly removed
        existing_images = property.get_images_list() if property.images else []
        removed_images = request.form.get('removed_images', '').split(',')
        removed_images = [img.strip() for img in removed_images if img.strip()]
        
        # Filter out removed images
        remaining_images = [img for img in existing_images if img not in removed_images]
        
        # Combine remaining and new images
        all_images = remaining_images + new_image_paths
        
        property.title = request.form.get('title')
        property.description = request.form.get('description')
        property.property_type = request.form.get('property_type')
        property.address = request.form.get('address')
        property.city = request.form.get('city')
        property.province = request.form.get('province')
        property.postal_code = request.form.get('postal_code')
        property.bedrooms = int(request.form.get('bedrooms'))
        property.bathrooms = int(request.form.get('bathrooms'))
        property.total_rooms = int(request.form.get('total_rooms'))
        property.price_per_month = float(request.form.get('price_per_month'))
        property.amenities = request.form.get('amenities')
        property.images = ','.join(all_images) if all_images else None
        property.is_available = request.form.get('is_available') == 'on'
        property.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Property updated successfully!', 'success')
        return redirect(url_for('landlord.properties'))
    
    return render_template('landlord/edit_property.html', property=property)


@landlord_bp.route('/property/<int:id>/delete', methods=['POST'])
@login_required
@landlord_required
def delete_property(id):
    property = Property.query.get_or_404(id)
    
    if property.landlord_id != current_user.id:
        flash('You can only delete your own properties.', 'danger')
        return redirect(url_for('landlord.properties'))
    
    # Check for active bookings
    active_bookings = Booking.query.filter_by(
        property_id=id,
        status='approved'
    ).count()
    
    if active_bookings > 0:
        flash('Cannot delete property with active bookings.', 'danger')
        return redirect(url_for('landlord.properties'))
    
    db.session.delete(property)
    db.session.commit()
    
    flash('Property deleted successfully.', 'success')
    return redirect(url_for('landlord.properties'))


@landlord_bp.route('/bookings')
@login_required
@landlord_required
def bookings():
    # Get all bookings for landlord's properties
    property_ids = [p.id for p in Property.query.filter_by(landlord_id=current_user.id).all()]
    bookings = Booking.query.filter(
        Booking.property_id.in_(property_ids)
    ).order_by(Booking.created_at.desc()).all()
    
    return render_template('landlord/bookings.html', bookings=bookings)


@landlord_bp.route('/booking/<int:id>/approve', methods=['POST'])
@login_required
@landlord_required
def approve_booking(id):
    booking = Booking.query.get_or_404(id)
    property = Property.query.get(booking.property_id)
    
    if property.landlord_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('landlord.bookings'))
    
    if property.available_rooms < booking.num_rooms:
        flash('Not enough rooms available for this booking.', 'danger')
        return redirect(url_for('landlord.bookings'))
    
    booking.status = 'approved'
    booking.response = request.form.get('response', '')
    property.available_rooms -= booking.num_rooms
    
    db.session.commit()
    
    # Send approval email to tenant
    try:
        send_booking_approved_email(booking.user, booking, booking.response)
    except Exception as e:
        print(f"Error sending approval email: {e}")
    
    flash('Booking approved successfully!', 'success')
    return redirect(url_for('landlord.bookings'))


@landlord_bp.route('/booking/<int:id>/reject', methods=['POST'])
@login_required
@landlord_required
def reject_booking(id):
    booking = Booking.query.get_or_404(id)
    property = Property.query.get(booking.property_id)
    
    if property.landlord_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('landlord.bookings'))
    
    booking.status = 'rejected'
    booking.response = request.form.get('response', '')
    
    db.session.commit()
    
    # Send rejection email to tenant
    try:
        send_booking_rejected_email(booking.user, booking, booking.response)
    except Exception as e:
        print(f"Error sending rejection email: {e}")
    
    flash('Booking rejected.', 'info')
    return redirect(url_for('landlord.bookings'))
