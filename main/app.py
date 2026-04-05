"""
Digital Nomads Flask Application
Medical information management with authentication, anatomy education, and AI assistant
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template
from flask_login import LoginManager

from main.config import config
from main.models import db, User


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create database tables and seed data
    with app.app_context():
        db.create_all()
        from main.seed_data import seed_database
        seed_database(db)

    # Register email OTP module
    from main.utils.email_otp import set_app as set_email_app
    set_email_app(app)

    # Core routes
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    # Register blueprints
    from main.routes.auth import auth_bp
    from main.routes.user import user_bp
    from main.routes.medical import medical_bp
    from main.routes.assistant_route import assistant_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(medical_bp)
    app.register_blueprint(assistant_bp)

    return app


app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(debug=True)
