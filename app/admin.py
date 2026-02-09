from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash
from app.models import User, Property, Booking, Review

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        flash('You must be an admin to access this page.', 'danger')
        return redirect(url_for('main.index'))


class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        flash('You must be an admin to access this page.', 'danger')
        return redirect(url_for('main.index'))


class UserAdminView(SecureModelView):
    column_list = ['id', 'username', 'email', 'full_name', 'role', 'is_active', 'created_at']
    column_searchable_list = ['username', 'email', 'full_name']
    column_filters = ['role', 'is_active', 'is_verified']
    column_editable_list = ['is_active', 'is_verified', 'role']
    form_excluded_columns = ['password_hash', 'properties', 'bookings', 'reviews']


class PropertyAdminView(SecureModelView):
    column_list = ['id', 'title', 'city', 'price_per_month', 'landlord', 'is_available', 'created_at']
    column_searchable_list = ['title', 'city', 'address']
    column_filters = ['city', 'property_type', 'is_available', 'is_featured']
    column_editable_list = ['is_available', 'is_featured']
    form_excluded_columns = ['bookings', 'reviews']


class BookingAdminView(SecureModelView):
    column_list = ['id', 'user', 'property', 'status', 'total_price', 'created_at']
    column_filters = ['status']
    column_editable_list = ['status']


class ReviewAdminView(SecureModelView):
    column_list = ['id', 'user', 'property', 'rating', 'created_at']
    column_filters = ['rating']


def setup_admin(app, db):
    admin = Admin(
        app, 
        name='Rental Booking Admin', 
        template_mode='bootstrap4',
        index_view=SecureAdminIndexView()
    )
    
    admin.add_view(UserAdminView(User, db.session))
    admin.add_view(PropertyAdminView(Property, db.session))
    admin.add_view(BookingAdminView(Booking, db.session))
    admin.add_view(ReviewAdminView(Review, db.session))
    
    return admin
