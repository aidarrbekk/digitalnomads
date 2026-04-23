"""
Digital Nomads Flask Application
Medical information management with authentication, anatomy education, and AI assistant
"""
import logging
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, send_from_directory, redirect, url_for, flash, request
from flask_login import LoginManager

from main.config import config
from main.models import db, User
from main.i18n import init_i18n, t

logger = logging.getLogger(__name__)

_SYNC_INTERVAL = 12 * 60 * 60  # 12 hours in seconds


def _start_iteka_scheduler(app):
    """Run i-teka.kz sync in a background thread, repeating every 12 hours."""
    from main.utils.iteka_scraper import sync_iteka_data

    def _run():
        try:
            logger.info("Starting scheduled i-teka.kz data sync...")
            sync_iteka_data(app)
        except Exception as e:
            logger.error(f"i-teka sync failed: {e}")
        finally:
            timer = threading.Timer(_SYNC_INTERVAL, _run)
            timer.daemon = True
            timer.start()

    # Initial sync after 10 seconds (let the app start first)
    timer = threading.Timer(10, _run)
    timer.daemon = True
    timer.start()

from flask import Flask, render_template, send_from_directory, redirect, url_for, flash, request
from flask_login import LoginManager

from main.config import config
from main.models import db, User
from main.i18n import init_i18n, t


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Initialize i18n
    init_i18n(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.unauthorized_handler
    def unauthorized():
        flash(t('flash_login_required'), 'info')
        return redirect(url_for('auth.login', next=request.url))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create database tables and seed data
    with app.app_context():
        db.create_all()
        from main.seed_data import seed_database
        seed_database(db)

    # Create uploads directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

    @app.route('/download/privacy-policy')
    def download_privacy_policy():
        return send_from_directory(
            os.path.join(app.static_folder, 'docs'),
            'privacy_policy.txt',
            as_attachment=True,
            download_name='ShipAI_Privacy_Policy.txt'
        )

    @app.route('/download/terms')
    def download_terms():
        return send_from_directory(
            os.path.join(app.static_folder, 'docs'),
            'terms_of_service.txt',
            as_attachment=True,
            download_name='ShipAI_Terms_of_Service.txt'
        )

    # Register blueprints
    from main.routes.auth import auth_bp
    from main.routes.user import user_bp
    from main.routes.medical import medical_bp
    from main.routes.assistant_route import assistant_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(medical_bp)
    app.register_blueprint(assistant_bp)

    # Start background i-teka.kz sync scheduler (every 12 hours)
    if not app.config.get('TESTING'):
        _start_iteka_scheduler(app)

    return app


app = create_app(os.environ.get('FLASK_ENV', 'development'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
