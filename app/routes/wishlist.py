from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Wishlist, Property
from datetime import datetime

wishlist_bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')


@wishlist_bp.route('/')
@login_required
def index():
    """View user's wishlist"""
    wishlists = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist/index.html', wishlists=wishlists)


@wishlist_bp.route('/add/<int:property_id>', methods=['POST'])
@login_required
def add(property_id):
    """Add property to wishlist"""
    property = Property.query.get_or_404(property_id)
    
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(
        user_id=current_user.id, 
        property_id=property_id
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'Already in wishlist'}), 400
    
    wishlist_item = Wishlist(
        user_id=current_user.id,
        property_id=property_id
    )
    
    db.session.add(wishlist_item)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'message': 'Added to wishlist'})
    
    flash('Property added to wishlist!', 'success')
    return redirect(request.referrer or url_for('main.properties'))


@wishlist_bp.route('/remove/<int:property_id>', methods=['POST', 'DELETE'])
@login_required
def remove(property_id):
    """Remove property from wishlist"""
    wishlist_item = Wishlist.query.filter_by(
        user_id=current_user.id, 
        property_id=property_id
    ).first_or_404()
    
    db.session.delete(wishlist_item)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'message': 'Removed from wishlist'})
    
    flash('Property removed from wishlist.', 'info')
    return redirect(request.referrer or url_for('wishlist.index'))


@wishlist_bp.route('/check/<int:property_id>')
@login_required
def check(property_id):
    """Check if property is in wishlist (for AJAX)"""
    exists = Wishlist.query.filter_by(
        user_id=current_user.id, 
        property_id=property_id
    ).first() is not None
    
    return jsonify({'in_wishlist': exists})


@wishlist_bp.route('/toggle/<int:property_id>', methods=['POST'])
@login_required
def toggle(property_id):
    """Toggle property in wishlist"""
    property = Property.query.get_or_404(property_id)
    
    wishlist_item = Wishlist.query.filter_by(
        user_id=current_user.id, 
        property_id=property_id
    ).first()
    
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({'success': True, 'in_wishlist': False, 'message': 'Removed from wishlist'})
    else:
        wishlist_item = Wishlist(
            user_id=current_user.id,
            property_id=property_id
        )
        db.session.add(wishlist_item)
        db.session.commit()
        return jsonify({'success': True, 'in_wishlist': True, 'message': 'Added to wishlist'})
