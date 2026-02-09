from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db, User

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.landlord import landlord_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(landlord_bp)
    
    # Setup admin
    from app.admin import setup_admin
    setup_admin(app, db)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d'):
        if value is None:
            return ""
        return value.strftime(format)
    
    return app
