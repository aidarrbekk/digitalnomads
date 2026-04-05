"""
Authentication routes blueprint
Handles: signup, login, logout, OTP verification, password reset
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer

from main.models import db, User
from main.forms import SignUpForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, VerifyOTPForm
from main.utils.email_otp import generate_otp, send_otp_email
from main.utils.email_templates import (
    create_email_message, send_email,
    get_confirmation_email_template, get_password_reset_email_template
)

auth_bp = Blueprint('auth', __name__)


def generate_confirmation_token(email: str) -> str:
    """Generate email verification token"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    salt = current_app.config.get('SECURITY_PASSWORD_SALT', 'email-confirm-salt')
    return serializer.dumps(email, salt=salt)


def verify_confirmation_token(token: str, max_age: int = 86400) -> str | None:
    """Verify email token and return email if valid"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    salt = current_app.config.get('SECURITY_PASSWORD_SALT', 'email-confirm-salt')
    try:
        email = serializer.loads(token, salt=salt, max_age=max_age)
        return email
    except Exception:
        return None


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sign up - collect user info and send OTP"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    form = SignUpForm()
    if form.validate_on_submit():
        otp = generate_otp()
        session['pending_signup'] = {
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data,
            'otp': otp
        }
        session.permanent = True
        send_otp_email(form.email.data, otp)
        flash(f'Code sent to {form.email.data}. Check your inbox.', 'success')
        return redirect(url_for('auth.verify_otp'))

    return render_template('signup.html', form=form)


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """Verify OTP and create account"""
    if 'pending_signup' not in session:
        flash('Please start registration.', 'warning')
        return redirect(url_for('auth.signup'))

    form = VerifyOTPForm()
    pending_data = session['pending_signup']

    if form.validate_on_submit():
        if form.otp.data == pending_data['otp']:
            user = User(
                username=pending_data['username'],
                email=pending_data['email'],
                email_verified=True
            )
            user.set_password(pending_data['password'])
            db.session.add(user)
            db.session.commit()
            session.pop('pending_signup', None)

            flash('Email verified! Account created. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid code. Try again.', 'danger')
            return redirect(url_for('auth.verify_otp'))

    return render_template('verify_otp.html', form=form, email=pending_data.get('email', ''))


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP code"""
    if 'pending_signup' not in session:
        flash('Please start registration.', 'warning')
        return redirect(url_for('auth.signup'))

    pending_data = session['pending_signup']
    send_otp_email(pending_data['email'], pending_data['otp'])
    flash(f'Code resent to {pending_data["email"]}', 'success')
    return redirect(url_for('auth.verify_otp'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        ident = form.identifier.data.strip()
        user = User.query.filter_by(username=ident).first()
        if not user:
            user = User.query.filter_by(email=ident).first()

        if not user or not user.check_password(form.password.data):
            flash('Invalid credentials', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Account disabled', 'danger')
            return redirect(url_for('auth.login'))

        if not user.email_verified:
            token = generate_confirmation_token(user.email)
            try:
                html, plain = get_confirmation_email_template(
                    url_for('auth.confirm_email', token=token, _external=True)
                )
                msg = create_email_message('Confirm Your Account', user.email, html, plain)
                send_email(msg)
            except Exception as e:
                current_app.logger.error(f'Failed to send confirmation email: {e}')

            flash('Email not verified. Confirmation sent. Check inbox.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('user.dashboard'))

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))


@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    """Email confirmation"""
    email = verify_confirmation_token(token)

    if not email:
        flash('Confirmation link invalid or expired.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.signup'))

    if user.email_verified:
        flash('Account already confirmed.', 'info')
        return redirect(url_for('auth.login'))

    user.verify_email()
    db.session.commit()
    flash('Email confirmed! Thank you.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-confirmation', methods=['GET', 'POST'])
def resend_confirmation():
    """Resend confirmation email"""
    if current_user.is_authenticated:
        if current_user.email_verified:
            flash('Email already confirmed.', 'info')
            return redirect(url_for('user.dashboard'))

        token = generate_confirmation_token(current_user.email)
        try:
            html, plain = get_confirmation_email_template(
                url_for('auth.confirm_email', token=token, _external=True)
            )
            msg = create_email_message('Confirm Your Account', current_user.email, html, plain)
            send_email(msg)
        except Exception as e:
            current_app.logger.error(f'Failed to send confirmation: {e}')

        flash('Confirmation email sent.', 'success')
        return redirect(url_for('user.profile'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        if user and not user.email_verified:
            token = generate_confirmation_token(user.email)
            try:
                html, plain = get_confirmation_email_template(
                    url_for('auth.confirm_email', token=token, _external=True)
                )
                msg = create_email_message('Confirm Your Account', user.email, html, plain)
                send_email(msg)
            except Exception as e:
                current_app.logger.error(f'Failed to send confirmation: {e}')

        flash('Confirmation email sent if account exists.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('resend_confirmation.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_confirmation_token(user.email)
            try:
                html, plain = get_password_reset_email_template(
                    url_for('auth.reset_password', token=token, _external=True)
                )
                msg = create_email_message('Reset Your Password', user.email, html, plain)
                send_email(msg)
            except Exception as e:
                current_app.logger.error(f'Failed to send reset email: {e}')

        flash('Password reset instructions sent if account exists.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    email = verify_confirmation_token(token, max_age=3600)
    if not email:
        flash('Reset link invalid or expired.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password reset successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', form=form)
