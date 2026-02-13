import os
import sys

# Ensure project root is on sys.path so `from main...` imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, redirect, url_for, flash, request, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from email.message import EmailMessage
from main.config import config
from main.models import db, User
from main.forms import SignUpForm, LoginForm, UpdateProfileForm
import os
import smtplib

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    salt = current_app.config.get('SECURITY_PASSWORD_SALT', 'email-confirm-salt')
    return serializer.dumps(email, salt=salt)

def send_confirmation_email(email, token):
    """Send email confirmation link with HTML template"""
    msg = EmailMessage()
    msg['Subject'] = 'Confirm Your ShipAI Account'
    msg['From'] = current_app.config.get('MAIL_DEFAULT_SENDER', 'ShipAI <noreply@shipai.com>')
    msg['To'] = email
    
    link = url_for('confirm_email', token=token, _external=True)
    
    # HTML email body
    html_body = f'''
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0d6efd;">Welcome to ShipAI!</h2>
                
                <p>Thanks for signing up. Please confirm your email address to complete your registration.</p>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background-color: #0d6efd; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        Confirm Email Address
                    </a>
                </p>
                
                <p>Or copy and paste this link in your browser:</p>
                <p style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; word-break: break-all;">
                    {link}
                </p>
                
                <p>This link will expire in 24 hours.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    If you didn't sign up for ShipAI, please ignore this email.
                </p>
                
                <p style="font-size: 12px; color: #666;">
                    Best regards,<br>
                    The ShipAI Team
                </p>
            </div>
        </body>
    </html>
    '''
    
    msg.set_content('Please confirm your email address by clicking the link above.', subtype='plain')
    msg.add_alternative(html_body, subtype='html')
    
    # Get mail config
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = current_app.config.get('MAIL_PORT', 587)
    mail_user = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)

    if not mail_server or not mail_port:
        raise RuntimeError('Mail server not configured (MAIL_SERVER and MAIL_PORT required)')

    with smtplib.SMTP(mail_server, mail_port, timeout=10) as server:
        # Start TLS if requested
        if mail_use_tls:
            try:
                server.starttls()
            except Exception as e:
                current_app.logger.warning(f'TLS failed: {e}')

        # Login if credentials provided
        if mail_user and mail_password:
            try:
                server.login(mail_user, mail_password)
            except smtplib.SMTPAuthenticationError as e:
                current_app.logger.error(f'SMTP auth failed: {e}')
                raise

        server.send_message(msg)

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Routes
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """Sign up page and form handling"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = SignUpForm()
        if form.validate_on_submit():
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            # generate confirmation token and send email
            token = generate_confirmation_token(user.email)
            try:
                send_confirmation_email(user.email, token)
            except Exception as e:
                current_app.logger.error(f'Failed to send confirmation email to {user.email}: {e}')
            
            flash('Account created! A confirmation email has been sent to your inbox. Please click the link to verify your email.', 'success')
            return redirect(url_for('login'))

        return render_template('signup.html', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page and form handling"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            ident = form.identifier.data.strip()
            user = User.query.filter_by(username=ident).first()
            if user is None:
                user = User.query.filter_by(email=ident).first()

            if user is None or not user.check_password(form.password.data):
                flash('Invalid username/email or password', 'danger')
                return redirect(url_for('login'))

            if not user.is_active:
                flash('Your account has been disabled', 'danger')
                return redirect(url_for('login'))

            if not user.email_verified:
                # resend confirmation
                token = generate_confirmation_token(user.email)
                try:
                    send_confirmation_email(user.email, token)
                except Exception as e:
                    current_app.logger.error(f'Failed to resend confirmation email to {user.email}: {e}')
                
                flash('Your email is not verified. A confirmation email has been sent. Please check your inbox.', 'warning')
                return redirect(url_for('login'))

            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))

        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout user"""
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('home'))

    @app.route('/profile')
    @login_required
    def profile():
        """Simple profile view"""
        return render_template('profile.html', user=current_user)

    @app.route('/settings')
    @login_required
    def settings():
        """Settings page placeholder"""
        return render_template('settings.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard"""
        return render_template('dashboard.html', user=current_user)
    
    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        """Edit user profile"""
        form = UpdateProfileForm()
        form.set_user_id(current_user.id)
        
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.bio = form.bio.data
            current_user.country = form.country.data
            
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('dashboard'))
        
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
            form.first_name.data = current_user.first_name
            form.last_name.data = current_user.last_name
            form.bio.data = current_user.bio
            form.country.data = current_user.country
        
        return render_template('edit_profile.html', form=form)

    @app.route('/confirm/<token>')
    def confirm_email(token):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        salt = app.config.get('SECURITY_PASSWORD_SALT', 'email-confirm-salt')
        try:
            email = serializer.loads(token, salt=salt, max_age=60*60*24)
        except Exception:
            flash('The confirmation link is invalid or has expired.', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Invalid user for confirmation.', 'danger')
            return redirect(url_for('signup'))

        if user.email_verified:
            flash('Account already confirmed. Please login.', 'info')
            return redirect(url_for('login'))

        user.verify_email()
        db.session.commit()
        flash('Your account has been confirmed. Thank you!', 'success')
        return redirect(url_for('login'))

    @app.route('/resend-confirmation', methods=['GET', 'POST'])
    def resend_confirmation():
        """Resend confirmation email"""
        if current_user.is_authenticated:
            if current_user.email_verified:
                flash('Your email is already verified.', 'info')
                return redirect(url_for('dashboard'))
            # User is logged in but not verified — resend
            token = generate_confirmation_token(current_user.email)
            try:
                send_confirmation_email(current_user.email, token)
            except Exception as e:
                current_app.logger.error(f'Failed to resend confirmation email to {current_user.email}: {e}')
            
            flash('A confirmation email has been sent to your inbox.', 'success')
            return redirect(url_for('profile'))

        # For unauthenticated users (on login page)
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            user = User.query.filter_by(email=email).first()
            if user:
                if user.email_verified:
                    flash('This email is already verified.', 'info')
                else:
                    token = generate_confirmation_token(user.email)
                    try:
                        send_confirmation_email(user.email, token)
                    except Exception as e:
                        current_app.logger.error(f'Failed to send confirmation email to {user.email}: {e}')
                    
                    flash('A confirmation email has been sent to your email address.', 'success')
            else:
                flash('Email not found.', 'danger')
            return redirect(url_for('login'))

        # GET — show resend form
        return render_template('resend_confirmation.html')
    
    return app

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(debug=True)