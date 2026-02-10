from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import stripe
import json
from app.models import (
    db, Payment, Invoice, PaymentSchedule, Booking, Property, 
    Notification, User
)
from app.utils.email import send_email
from app.utils.invoice_generator import generate_invoice_pdf

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

# Initialize Stripe
stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')


# ==================== PAYMENT PROCESSING ====================

@payments_bp.route('/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent():
    """Create a payment intent for Stripe"""
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')
        amount = data.get('amount')
        
        if not booking_id or not amount:
            return jsonify({'error': 'Missing booking_id or amount'}), 400
        
        booking = Booking.query.get_or_404(booking_id)
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            metadata={
                'booking_id': booking_id,
                'user_id': current_user.id
            },
            description=f'Payment for booking #{booking_id}'
        )
        
        return jsonify({
            'clientSecret': intent['client_secret'],
            'paymentIntentId': intent['id']
        })
    
    except stripe.error.CardError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/confirm-payment', methods=['POST'])
@login_required
def confirm_payment():
    """Confirm payment after Stripe processing"""
    try:
        data = request.get_json()
        payment_intent_id = data.get('paymentIntentId')
        booking_id = data.get('booking_id')
        
        # Retrieve payment intent
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent['status'] == 'succeeded':
            # Create payment record
            payment = Payment(
                user_id=current_user.id,
                booking_id=booking_id,
                amount=intent['amount'] / 100,  # Convert back to dollars
                currency=intent['currency'].upper(),
                payment_method='stripe',
                stripe_payment_intent_id=payment_intent_id,
                status='completed',
                completed_at=datetime.utcnow(),
                description=f'Payment via Stripe for booking #{booking_id}'
            )
            
            db.session.add(payment)
            
            # Update booking if fully paid
            booking = Booking.query.get(booking_id)
            if booking:
                booking.status = 'approved'
                
                # Create notification
                notification = Notification(
                    user_id=booking.user_id,
                    title='Payment Confirmed',
                    message=f'Your booking for {booking.property.title} has been confirmed!',
                    notification_type='payment',
                    related_payment_id=payment.id,
                    related_booking_id=booking_id
                )
                db.session.add(notification)
                
                # Send confirmation email
                send_email(
                    recipient=booking.user.email,
                    subject=f'Payment Confirmation - Booking #{booking_id}',
                    template='payment_confirmation',
                    user=booking.user,
                    booking=booking,
                    payment=payment
                )
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Payment confirmed successfully',
                'paymentId': payment.id
            })
        
        return jsonify({'error': 'Payment was not successful'}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            current_app.config.get('STRIPE_WEBHOOK_SECRET', '')
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle different event types
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Handle succeeded payment
        booking_id = payment_intent['metadata'].get('booking_id')
        # Update payment status if needed
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata'].get('booking_id')
        # Handle failed payment
        booking = Booking.query.get(booking_id)
        if booking:
            booking.status = 'pending'
            db.session.commit()
    
    return jsonify({'success': True})


@payments_bp.route('/paypal-checkout', methods=['POST'])
@login_required
def paypal_checkout():
    """Create PayPal checkout"""
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')
        amount = data.get('amount')
        
        if not booking_id or not amount:
            return jsonify({'error': 'Missing booking_id or amount'}), 400
        
        booking = Booking.query.get_or_404(booking_id)
        
        # Create payment record with pending status
        payment = Payment(
            user_id=current_user.id,
            booking_id=booking_id,
            amount=amount,
            currency='USD',
            payment_method='paypal',
            status='pending',
            description=f'Payment via PayPal for booking #{booking_id}'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'paymentId': payment.id,
            'amount': amount
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== INVOICE MANAGEMENT ====================

@payments_bp.route('/invoices', methods=['GET'])
@login_required
def view_invoices():
    """View user's invoices"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', None)
    
    query = Invoice.query.filter_by(user_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    invoices = query.order_by(Invoice.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('invoices/list.html', invoices=invoices)


@payments_bp.route('/invoice/<int:invoice_id>', methods=['GET'])
@login_required
def view_invoice(invoice_id):
    """View invoice details"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Check authorization
    if invoice.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to view this invoice', 'danger')
        return redirect(url_for('payments.view_invoices'))
    
    return render_template('invoices/detail.html', invoice=invoice)


@payments_bp.route('/invoice/<int:invoice_id>/download', methods=['GET'])
@login_required
def download_invoice(invoice_id):
    """Download invoice as PDF"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Check authorization
    if invoice.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to download this invoice', 'danger')
        return redirect(url_for('payments.view_invoices'))
    
    if not invoice.pdf_file:
        # Generate PDF if not already generated
        invoice.pdf_file = generate_invoice_pdf(invoice)
        db.session.commit()
    
    # Return PDF file
    return redirect(f'/static/uploads/{invoice.pdf_file}')


@payments_bp.route('/invoice/<int:invoice_id>/mark-paid', methods=['POST'])
@login_required
def mark_invoice_paid(invoice_id):
    """Mark invoice as paid"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Check authorization
    if invoice.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        invoice.status = 'paid'
        invoice.paid_date = datetime.utcnow()
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            invoice_id=invoice_id,
            amount=invoice.amount,
            currency=invoice.currency,
            payment_method='manual',
            status='completed',
            completed_at=datetime.utcnow(),
            description=f'Manual payment for invoice #{invoice.invoice_number}'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Invoice marked as paid'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/create-recurring-invoice', methods=['POST'])
@login_required
def create_recurring_invoice():
    """Create a recurring invoice"""
    try:
        data = request.get_json()
        
        invoice = Invoice(
            user_id=current_user.id,
            invoice_number=f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            description=data.get('description'),
            amount=data.get('amount'),
            currency=data.get('currency', 'USD'),
            invoice_type=data.get('invoice_type', 'rent'),
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=int(data.get('days_until_due', 30))),
            is_recurring=True,
            recurrence_pattern=data.get('recurrence_pattern', 'monthly'),
            status='draft'
        )
        
        # Set next due date based on recurrence pattern
        if invoice.recurrence_pattern == 'monthly':
            invoice.next_due_date = invoice.due_date + timedelta(days=30)
        elif invoice.recurrence_pattern == 'quarterly':
            invoice.next_due_date = invoice.due_date + timedelta(days=90)
        elif invoice.recurrence_pattern == 'yearly':
            invoice.next_due_date = invoice.due_date + timedelta(days=365)
        
        db.session.add(invoice)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'invoiceId': invoice.id,
            'message': 'Recurring invoice created successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== PAYMENT SCHEDULING ====================

@payments_bp.route('/payment-schedules', methods=['GET'])
@login_required
def view_payment_schedules():
    """View payment schedules"""
    schedules = PaymentSchedule.query.filter_by(user_id=current_user.id).all()
    return render_template('payments/schedules.html', schedules=schedules)


@payments_bp.route('/create-payment-schedule', methods=['POST'])
@login_required
def create_payment_schedule():
    """Create a payment schedule"""
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')
        
        booking = Booking.query.get_or_404(booking_id)
        
        # Check authorization
        if booking.user_id != current_user.id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        schedule = PaymentSchedule(
            user_id=current_user.id,
            booking_id=booking_id,
            total_amount=data.get('total_amount'),
            payment_frequency=data.get('payment_frequency', 'monthly'),
            start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d'),
            end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d') if data.get('end_date') else None,
            next_payment_date=datetime.strptime(data.get('first_payment_date'), '%Y-%m-%d')
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'scheduleId': schedule.id,
            'message': 'Payment schedule created successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== FINANCIAL REPORTS ====================

@payments_bp.route('/reports/earnings', methods=['GET'])
@login_required
def earnings_report():
    """View earnings report for landlords"""
    if current_user.role != 'landlord' and current_user.role != 'admin':
        flash('You do not have permission to view earnings reports', 'danger')
        return redirect(url_for('main.index'))
    
    # Get all payments for user's properties
    properties = Property.query.filter_by(landlord_id=current_user.id).all()
    property_ids = [p.id for p in properties]
    
    # Calculate earnings
    total_earnings = 0
    monthly_earnings = {}
    
    if property_ids:
        payments = Payment.query.join(
            Booking, Booking.id == Payment.booking_id
        ).filter(
            Booking.property_id.in_(property_ids),
            Payment.status == 'completed'
        ).all()
        
        for payment in payments:
            total_earnings += payment.amount
            month_key = payment.completed_at.strftime('%Y-%m')
            monthly_earnings[month_key] = monthly_earnings.get(month_key, 0) + payment.amount
    
    return render_template(
        'reports/earnings.html',
        total_earnings=total_earnings,
        monthly_earnings=monthly_earnings,
        properties=properties
    )


@payments_bp.route('/reports/spending', methods=['GET'])
@login_required
def spending_report():
    """View spending report for tenants"""
    # Get all payments made by current user
    payments = Payment.query.filter_by(user_id=current_user.id, status='completed').all()
    
    total_spent = sum(p.amount for p in payments)
    monthly_spending = {}
    
    for payment in payments:
        month_key = payment.completed_at.strftime('%Y-%m')
        monthly_spending[month_key] = monthly_spending.get(month_key, 0) + payment.amount
    
    return render_template(
        'reports/spending.html',
        total_spent=total_spent,
        monthly_spending=monthly_spending,
        payments=payments
    )


@payments_bp.route('/reports/property/<int:property_id>', methods=['GET'])
@login_required
def property_revenue_report(property_id):
    """View revenue report for a specific property"""
    property = Property.query.get_or_404(property_id)
    
    # Check authorization
    if property.landlord_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to view this report', 'danger')
        return redirect(url_for('main.index'))
    
    # Calculate revenue metrics
    bookings = Booking.query.filter_by(property_id=property_id, status='completed').all()
    total_revenue = sum(b.total_price for b in bookings)
    
    monthly_revenue = {}
    for booking in bookings:
        month_key = booking.check_in_date.strftime('%Y-%m')
        monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + booking.total_price
    
    # Calculate occupancy
    occupancy_rate = property.get_occupancy_rate()
    
    return render_template(
        'reports/property_revenue.html',
        property=property,
        total_revenue=total_revenue,
        monthly_revenue=monthly_revenue,
        occupancy_rate=occupancy_rate,
        bookings=bookings
    )
