from flask_mail import Mail, Message
from flask import render_template_string, current_app
from threading import Thread

mail = Mail()

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        mail.send(msg)


def send_email(recipient, subject, template, **kwargs):
    """Send email with template"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient] if isinstance(recipient, str) else recipient,
            html=render_template_string(template, **kwargs),
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        # Send asynchronously using threading
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_booking_confirmation_email(user, booking):
    """Send booking confirmation email"""
    subject = f'Booking Confirmation - {booking.property.title}'
    
    html_content = f"""
    <h2>Booking Confirmation</h2>
    <p>Hi {user.full_name},</p>
    <p>Your booking for <strong>{booking.property.title}</strong> has been confirmed!</p>
    
    <h3>Booking Details:</h3>
    <ul>
        <li><strong>Property:</strong> {booking.property.title}</li>
        <li><strong>Address:</strong> {booking.property.address}, {booking.property.city}</li>
        <li><strong>Check-in:</strong> {booking.check_in_date}</li>
        <li><strong>Check-out:</strong> {booking.check_out_date}</li>
        <li><strong>Total Price:</strong> ${booking.total_price:.2f}</li>
    </ul>
    
    <p>Thank you for booking with Amahle Rentals!</p>
    """
    
    return send_email(user.email, subject, html_content)


def send_payment_reminder_email(user, invoice):
    """Send payment reminder email"""
    subject = f'Payment Reminder - Invoice #{invoice.invoice_number}'
    
    html_content = f"""
    <h2>Payment Reminder</h2>
    <p>Hi {user.full_name},</p>
    <p>This is a reminder that your payment is due:</p>
    
    <h3>Invoice Details:</h3>
    <ul>
        <li><strong>Invoice Number:</strong> {invoice.invoice_number}</li>
        <li><strong>Amount:</strong> ${invoice.amount:.2f}</li>
        <li><strong>Due Date:</strong> {invoice.due_date.strftime('%Y-%m-%d')}</li>
        <li><strong>Description:</strong> {invoice.description}</li>
    </ul>
    
    <p>Please make your payment by the due date to avoid late fees.</p>
    """
    
    return send_email(user.email, subject, html_content)


def send_lease_expiration_alert(user, lease):
    """Send lease expiration alert email"""
    from datetime import datetime
    days_until_expiration = (lease.end_date - datetime.utcnow()).days
    
    subject = f'Lease Expiration Alert - {days_until_expiration} days remaining'
    
    html_content = f"""
    <h2>Lease Expiration Alert</h2>
    <p>Hi {user.full_name},</p>
    <p>Your lease will expire in {days_until_expiration} days.</p>
    
    <h3>Lease Details:</h3>
    <ul>
        <li><strong>Lease Number:</strong> {lease.lease_number}</li>
        <li><strong>Property:</strong> {lease.property.title}</li>
        <li><strong>Expiration Date:</strong> {lease.end_date.strftime('%Y-%m-%d')}</li>
        <li><strong>Auto Renewal:</strong> {'Yes' if lease.auto_renew else 'No'}</li>
    </ul>
    
    <p>Please contact your landlord if you wish to renew or terminate your lease.</p>
    """
    
    return send_email(user.email, subject, html_content)


def send_new_booking_request_email(landlord, booking):
    """Send new booking request email to landlord"""
    subject = f'New Booking Request - {booking.property.title}'
    
    html_content = f"""
    <h2>New Booking Request</h2>
    <p>Hi {landlord.full_name},</p>
    <p>You have received a new booking request!</p>
    
    <h3>Booking Details:</h3>
    <ul>
        <li><strong>Property:</strong> {booking.property.title}</li>
        <li><strong>Tenant:</strong> {booking.user.full_name}</li>
        <li><strong>Tenant Email:</strong> {booking.user.email}</li>
        <li><strong>Check-in:</strong> {booking.check_in_date}</li>
        <li><strong>Rooms:</strong> {booking.num_rooms}</li>
        <li><strong>Total Price:</strong> R{booking.total_price:.2f}</li>
        <li><strong>Message:</strong> {booking.message if booking.message else 'No message provided'}</li>
    </ul>
    
    <p>Please log in to your dashboard to approve or reject this booking.</p>
    """
    
    return send_email(landlord.email, subject, html_content)


def send_booking_approved_email(user, booking, response=''):
    """Send booking approved email to tenant"""
    subject = f'Booking Approved - {booking.property.title}'
    
    html_content = f"""
    <h2 style="color: #28a745;">✓ Booking Approved!</h2>
    <p>Hi {user.full_name},</p>
    <p>Great news! Your booking has been approved by the landlord.</p>
    
    <h3>Booking Details:</h3>
    <ul>
        <li><strong>Property:</strong> {booking.property.title}</li>
        <li><strong>Address:</strong> {booking.property.address}, {booking.property.city}</li>
        <li><strong>Check-in:</strong> {booking.check_in_date}</li>
        <li><strong>Rooms:</strong> {booking.num_rooms}</li>
        <li><strong>Total Price:</strong> R{booking.total_price:.2f}</li>
    </ul>
    
    {f'<h3>Message from Landlord:</h3><p>{response}</p>' if response else ''}
    
    <p>The landlord will contact you shortly with further details.</p>
    <p>Thank you for using Amahle Rentals!</p>
    """
    
    return send_email(user.email, subject, html_content)


def send_booking_rejected_email(user, booking, response=''):
    """Send booking rejected email to tenant"""
    subject = f'Booking Update - {booking.property.title}'
    
    html_content = f"""
    <h2>Booking Update</h2>
    <p>Hi {user.full_name},</p>
    <p>Unfortunately, your booking request for <strong>{booking.property.title}</strong> could not be approved at this time.</p>
    
    {f'<h3>Reason:</h3><p>{response}</p>' if response else ''}
    
    <p>Don't worry! We have many other great properties available.</p>
    <p><a href="http://127.0.0.1:5000/properties" style="display: inline-block; padding: 10px 20px; background-color: #0d6efd; color: white; text-decoration: none; border-radius: 5px;">Browse Other Properties</a></p>
    
    <p>Thank you for using Amahle Rentals!</p>
    """
    
    return send_email(user.email, subject, html_content)


def send_new_message_notification(recipient, sender, message_preview):
    """Send new message notification email"""
    subject = f'New Message from {sender.full_name}'
    
    html_content = f"""
    <h2>New Message</h2>
    <p>Hi {recipient.full_name},</p>
    <p>You have received a new message from <strong>{sender.full_name}</strong>:</p>
    
    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #0d6efd; margin: 20px 0;">
        <p>{message_preview[:200]}{'...' if len(message_preview) > 200 else ''}</p>
    </div>
    
    <p><a href="http://127.0.0.1:5000/messages" style="display: inline-block; padding: 10px 20px; background-color: #0d6efd; color: white; text-decoration: none; border-radius: 5px;">View Message</a></p>
    
    <p>Thank you for using Amahle Rentals!</p>
    """
    
    return send_email(recipient.email, subject, html_content)


def send_rent_reminder_email(user, property, days_until_due=7):
    """Send rent payment reminder email"""
    subject = f'Rent Payment Reminder - {property.title}'
    
    html_content = f"""
    <h2>Rent Payment Reminder</h2>
    <p>Hi {user.full_name},</p>
    <p>This is a friendly reminder that your rent payment is due in {days_until_due} days.</p>
    
    <h3>Payment Details:</h3>
    <ul>
        <li><strong>Property:</strong> {property.title}</li>
        <li><strong>Amount Due:</strong> R{property.price_per_month:.2f}</li>
        <li><strong>Due Date:</strong> {days_until_due} day(s)</li>
    </ul>
    
    <p>Please ensure your payment is made on time to avoid any late fees.</p>
    <p>If you have already made the payment, please disregard this message.</p>
    
    <p>Thank you!</p>
    """
    
    return send_email(user.email, subject, html_content)


def send_welcome_email(user):
    """Send welcome email to new users"""
    subject = 'Welcome to Amahle Rentals!'
    
    html_content = f"""
    <h1 style="color: #0d6efd;">Welcome to Amahle Rentals!</h1>
    <p>Hi {user.full_name},</p>
    <p>Thank you for joining Amahle Rentals - your trusted platform for finding the perfect accommodation.</p>
    
    <h3>Getting Started:</h3>
    {'<p>As a landlord, you can now start listing your properties and connecting with quality tenants.</p>' if user.role == 'landlord' else '<p>You can now browse available properties and submit booking requests.</p>'}
    
    <div style="margin: 30px 0;">
        <a href="http://127.0.0.1:5000/properties" style="display: inline-block; padding: 12px 30px; background-color: #0d6efd; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px;">Browse Properties</a>
        {'<a href="http://127.0.0.1:5000/landlord/property/add" style="display: inline-block; padding: 12px 30px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px;">Add Property</a>' if user.role == 'landlord' else ''}
    </div>
    
    <p>If you have any questions, feel free to contact us.</p>
    <p>Happy house hunting!</p>
    """
    
    return send_email(user.email, subject, html_content)

