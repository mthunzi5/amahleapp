from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Property, Booking, Review, ReportAbuse, UserSuspension, UserActivityLog
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin_governance', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You must be an admin to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin governance dashboard"""
    # Get statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    suspended_users = User.query.filter_by(is_active=False).count()
    
    total_properties = Property.query.count()
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status='pending').count()
    
    # Get pending reports
    pending_reports = ReportAbuse.query.filter_by(status='pending').count()
    
    # Recent activity
    recent_activity = UserActivityLog.query.order_by(UserActivityLog.created_at.desc()).limit(10).all()
    
    # Recent reports
    recent_reports = ReportAbuse.query.order_by(ReportAbuse.created_at.desc()).limit(5).all()
    
    return render_template('admin_governance/dashboard.html',
                         total_users=total_users,
                         active_users=active_users,
                         suspended_users=suspended_users,
                         total_properties=total_properties,
                         total_bookings=total_bookings,
                         pending_bookings=pending_bookings,
                         pending_reports=pending_reports,
                         recent_activity=recent_activity,
                         recent_reports=recent_reports)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management"""
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.full_name.ilike(f'%{search}%'))
        )
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'suspended':
        query = query.filter_by(is_active=False)
    
    users = query.order_by(User.created_at.desc()).all()
    
    return render_template('admin_governance/users.html', users=users)


@admin_bp.route('/user/<int:user_id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_user(user_id):
    """Suspend a user"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        flash('Cannot suspend an admin user.', 'danger')
        return redirect(url_for('admin_governance.users'))
    
    reason = request.form.get('reason', 'Policy violation')
    duration_days = request.form.get('duration_days', type=int)
    
    # Create suspension record
    suspension = UserSuspension(
        user_id=user_id,
        suspended_by=current_user.id,
        reason=reason,
        duration_days=duration_days,
        end_date=datetime.utcnow() + timedelta(days=duration_days) if duration_days else None
    )
    
    user.is_active = False
    
    db.session.add(suspension)
    db.session.commit()
    
    # Log activity
    log = UserActivityLog(
        user_id=current_user.id,
        action='suspend_user',
        description=f'Suspended user {user.username}',
        resource_type='user',
        resource_id=user_id
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'User {user.username} has been suspended.', 'success')
    return redirect(url_for('admin_governance.users'))


@admin_bp.route('/user/<int:user_id>/unsuspend', methods=['POST'])
@login_required
@admin_required
def unsuspend_user(user_id):
    """Unsuspend a user"""
    user = User.query.get_or_404(user_id)
    
    # Find active suspension
    suspension = UserSuspension.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()
    
    if suspension:
        suspension.is_active = False
        suspension.lifted_by = current_user.id
        suspension.lifted_at = datetime.utcnow()
    
    user.is_active = True
    
    db.session.commit()
    
    # Log activity
    log = UserActivityLog(
        user_id=current_user.id,
        action='unsuspend_user',
        description=f'Unsuspended user {user.username}',
        resource_type='user',
        resource_id=user_id
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'User {user.username} has been unsuspended.', 'success')
    return redirect(url_for('admin_governance.users'))


@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """View abuse reports"""
    status_filter = request.args.get('status', 'pending')
    
    query = ReportAbuse.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    reports = query.order_by(ReportAbuse.created_at.desc()).all()
    
    return render_template('admin_governance/reports.html', reports=reports, status_filter=status_filter)


@admin_bp.route('/report/<int:report_id>')
@login_required
@admin_required
def report_detail(report_id):
    """View report details"""
    report = ReportAbuse.query.get_or_404(report_id)
    
    # Get the reported resource
    reported_resource = None
    if report.reported_type == 'property':
        reported_resource = Property.query.get(report.reported_id)
    elif report.reported_type == 'user':
        reported_resource = User.query.get(report.reported_id)
    elif report.reported_type == 'review':
        reported_resource = Review.query.get(report.reported_id)
    elif report.reported_type == 'booking':
        reported_resource = Booking.query.get(report.reported_id)
    
    return render_template('admin_governance/report_detail.html', 
                         report=report, 
                         reported_resource=reported_resource)


@admin_bp.route('/report/<int:report_id>/resolve', methods=['POST'])
@login_required
@admin_required
def resolve_report(report_id):
    """Resolve an abuse report"""
    report = ReportAbuse.query.get_or_404(report_id)
    
    status = request.form.get('status', 'resolved')
    admin_notes = request.form.get('admin_notes', '')
    
    report.status = status
    report.admin_notes = admin_notes
    report.resolved_by = current_user.id
    report.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log activity
    log = UserActivityLog(
        user_id=current_user.id,
        action='resolve_report',
        description=f'Resolved report #{report_id} as {status}',
        resource_type='report',
        resource_id=report_id
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'Report #{report_id} has been marked as {status}.', 'success')
    return redirect(url_for('admin_governance.reports'))


@admin_bp.route('/activity-logs')
@login_required
@admin_required
def activity_logs():
    """View user activity logs"""
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action', '')
    
    query = UserActivityLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if action:
        query = query.filter_by(action=action)
    
    logs = query.order_by(UserActivityLog.created_at.desc()).limit(100).all()
    
    return render_template('admin_governance/activity_logs.html', logs=logs)
