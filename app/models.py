from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    
    # Role: 'admin', 'landlord', 'student', 'general'
    role = db.Column(db.String(20), nullable=False, default='general')
    
    # Profile information
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Payment & Financial
    stripe_customer_id = db.Column(db.String(255))
    paypal_customer_id = db.Column(db.String(255))
    bank_account = db.Column(db.String(255))  # Encrypted
    
    # Relationships
    properties = db.relationship('Property', backref='landlord', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True, cascade='all, delete-orphan')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy=True, cascade='all, delete-orphan')
    wishlists = db.relationship('Wishlist', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='user', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Property(db.Model):
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Property details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    property_type = db.Column(db.String(50), nullable=False)  # apartment, house, room, etc.
    
    # Location
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)  # For map integration
    longitude = db.Column(db.Float)  # For map integration
    
    # Details
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    total_rooms = db.Column(db.Integer, nullable=False)
    available_rooms = db.Column(db.Integer, nullable=False)
    price_per_month = db.Column(db.Float, nullable=False)
    
    # Amenities (stored as comma-separated values)
    amenities = db.Column(db.Text)  # wifi, parking, kitchen, etc.
    
    # Images (stored as comma-separated file paths)
    images = db.Column(db.Text)
    
    # Status
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='property', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='property', lazy=True, cascade='all, delete-orphan')
    availabilities = db.relationship('PropertyAvailability', backref='property', lazy=True, cascade='all, delete-orphan')
    leases = db.relationship('Lease', backref='property', lazy=True, cascade='all, delete-orphan')
    wishlists = db.relationship('Wishlist', backref='property', lazy=True, cascade='all, delete-orphan')
    
    def get_average_rating(self):
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)
    
    def get_images_list(self):
        if self.images:
            return self.images.split(',')
        return []
    
    def get_amenities_list(self):
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []
    
    def get_occupancy_rate(self):
        """Calculate occupancy rate for analytics"""
        total_days = 365
        booked_days = 0
        for booking in self.bookings:
            if booking.status in ['approved', 'completed']:
                delta = booking.check_out_date - booking.check_in_date
                booked_days += delta.days
        return (booked_days / total_days * 100) if total_days > 0 else 0
    
    def __repr__(self):
        return f'<Property {self.title}>'


class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Booking details
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date)  # Can be null for long-term rentals
    num_rooms = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    
    # Status: 'pending', 'approved', 'rejected', 'cancelled', 'completed'
    status = db.Column(db.String(20), default='pending')
    
    # Additional information
    message = db.Column(db.Text)  # Message from tenant to landlord
    response = db.Column(db.Text)  # Response from landlord
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lease = db.relationship('Lease', uselist=False, backref='booking')
    payments = db.relationship('Payment', backref='booking')
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Review content
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    comment = db.Column(db.Text, nullable=False)
    
    # Helpful votes
    helpful_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id} - {self.rating} stars>'


# ==================== PAYMENT & FINANCIAL MODELS ====================

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    
    # Payment details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Payment method: 'stripe', 'paypal', 'bank_transfer', 'cash'
    payment_method = db.Column(db.String(50), nullable=False)
    
    # Payment status: 'pending', 'completed', 'failed', 'refunded'
    status = db.Column(db.String(20), default='pending')
    
    # Transaction IDs from payment processors
    stripe_payment_intent_id = db.Column(db.String(255))
    paypal_transaction_id = db.Column(db.String(255))
    
    # Description
    description = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.amount} {self.currency}>'


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'))
    
    # Invoice details
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Invoice type: 'rent', 'deposit', 'utility', 'maintenance', etc.
    invoice_type = db.Column(db.String(50), nullable=False)
    
    # Dates
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    paid_date = db.Column(db.DateTime)
    
    # Status: 'draft', 'sent', 'viewed', 'partial', 'paid', 'overdue', 'cancelled'
    status = db.Column(db.String(20), default='draft')
    
    # File path for PDF
    pdf_file = db.Column(db.String(255))
    
    # Payment scheduling
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(50))  # 'monthly', 'quarterly', 'yearly'
    next_due_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='invoice')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


class PaymentSchedule(db.Model):
    __tablename__ = 'payment_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    
    # Schedule details
    total_amount = db.Column(db.Float, nullable=False)
    payment_frequency = db.Column(db.String(50), nullable=False)  # 'monthly', 'weekly', 'bi-weekly'
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Dates
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    next_payment_date = db.Column(db.DateTime, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PaymentSchedule {self.id}>'


# ==================== COMMUNICATION MODELS ====================

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Message content
    subject = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    
    # Conversation tracking
    parent_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    parent_message = db.relationship('Message', remote_side=[id], backref='replies')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id} to {self.recipient_id}>'


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Notification content
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'booking', 'payment', 'lease', 'message', etc.
    
    # Link to related resource
    related_booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    related_payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))
    related_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.notification_type}>'


# ==================== AVAILABILITY & SCHEDULING MODELS ====================

class PropertyAvailability(db.Model):
    __tablename__ = 'property_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Date range
    date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Type of unavailability: 'blocked', 'maintenance', 'cleaning'
    unavailability_reason = db.Column(db.String(100))
    
    # Notes
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PropertyAvailability {self.property_id} on {self.date}>'


class Lease(db.Model):
    __tablename__ = 'leases'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Lease details
    lease_number = db.Column(db.String(50), unique=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Financial terms
    monthly_rent = db.Column(db.Float, nullable=False)
    security_deposit = db.Column(db.Float)
    
    # Status: 'draft', 'active', 'renewal_pending', 'completed', 'terminated'
    status = db.Column(db.String(20), default='draft')
    
    # Renewal info
    auto_renew = db.Column(db.Boolean, default=False)
    renewal_notice_days = db.Column(db.Integer, default=30)
    next_renewal_date = db.Column(db.DateTime)
    
    # Document
    lease_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Lease {self.lease_number}>'


# ==================== WISHLIST MODEL ====================

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Notes
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Wishlist {self.user_id} - {self.property_id}>'


# ==================== DOCUMENT MODELS ====================

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Document details
    name = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # 'lease', 'agreement', 'invoice', 'proof'
    
    # File information
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(50))
    
    # Signing information
    is_signed = db.Column(db.Boolean, default=False)
    docusign_envelope_id = db.Column(db.String(255))
    signed_by_landlord = db.Column(db.Boolean, default=False)
    signed_by_tenant = db.Column(db.Boolean, default=False)
    signed_date = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # 'draft', 'pending_signature', 'signed', 'archived'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.name}>'


# ==================== ANALYTICS MODELS ====================

class PropertyAnalytics(db.Model):
    __tablename__ = 'property_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Date for analytics
    analytics_date = db.Column(db.Date, nullable=False)
    
    # Metrics
    total_views = db.Column(db.Integer, default=0)
    total_inquiries = db.Column(db.Integer, default=0)
    total_bookings = db.Column(db.Integer, default=0)
    occupancy_rate = db.Column(db.Float, default=0)
    revenue = db.Column(db.Float, default=0)
    average_rating = db.Column(db.Float, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PropertyAnalytics {self.property_id} on {self.analytics_date}>'


class SystemAnalytics(db.Model):
    __tablename__ = 'system_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Date for analytics
    analytics_date = db.Column(db.Date, nullable=False)
    
    # User metrics
    total_users = db.Column(db.Integer, default=0)
    new_users = db.Column(db.Integer, default=0)
    active_users = db.Column(db.Integer, default=0)
    
    # Property metrics
    total_properties = db.Column(db.Integer, default=0)
    new_properties = db.Column(db.Integer, default=0)
    available_properties = db.Column(db.Integer, default=0)
    
    # Booking metrics
    total_bookings = db.Column(db.Integer, default=0)
    pending_bookings = db.Column(db.Integer, default=0)
    completed_bookings = db.Column(db.Integer, default=0)
    
    # Revenue metrics
    total_revenue = db.Column(db.Float, default=0)
    total_transactions = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemAnalytics on {self.analytics_date}>'


# ==================== RECOMMENDATION MODEL ====================

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Preferences
    min_price = db.Column(db.Float)
    max_price = db.Column(db.Float)
    preferred_cities = db.Column(db.Text)  # Comma-separated
    preferred_amenities = db.Column(db.Text)  # Comma-separated
    preferred_property_types = db.Column(db.Text)  # Comma-separated
    min_bedrooms = db.Column(db.Integer)
    max_bedrooms = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPreference {self.user_id}>'


# ==================== ADMIN & GOVERNANCE MODELS ====================

class UserActivityLog(db.Model):
    __tablename__ = 'user_activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for anonymous actions
    
    # Activity details
    action = db.Column(db.String(100), nullable=False)  # 'login', 'view_property', 'create_booking', etc.
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    
    # Related resources
    resource_type = db.Column(db.String(50))  # 'property', 'booking', 'user', etc.
    resource_id = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserActivityLog {self.action} by {self.user_id}>'


class ReportAbuse(db.Model):
    __tablename__ = 'report_abuse'
    
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # What is being reported
    reported_type = db.Column(db.String(50), nullable=False)  # 'property', 'user', 'review', 'booking'
    reported_id = db.Column(db.Integer, nullable=False)
    
    # Report details
    reason = db.Column(db.String(100), nullable=False)  # 'spam', 'fraud', 'inappropriate', 'harassment', etc.
    description = db.Column(db.Text, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # 'pending', 'investigating', 'resolved', 'dismissed'
    admin_notes = db.Column(db.Text)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reports_made')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='reports_resolved')
    
    def __repr__(self):
        return f'<ReportAbuse {self.reported_type} #{self.reported_id}>'


class UserSuspension(db.Model):
    __tablename__ = 'user_suspensions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    suspended_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Suspension details
    reason = db.Column(db.Text, nullable=False)
    duration_days = db.Column(db.Integer)  # None = permanent
    
    # Dates
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    lifted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    lifted_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='suspensions')
    admin = db.relationship('User', foreign_keys=[suspended_by], backref='suspensions_issued')
    lifter = db.relationship('User', foreign_keys=[lifted_by], backref='suspensions_lifted')
    
    def __repr__(self):
        return f'<UserSuspension user={self.user_id} by={self.suspended_by}>'

