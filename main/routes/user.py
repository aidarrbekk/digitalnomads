"""
User profile and account routes blueprint
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from main.models import db, User, MedicalMetrics
from main.forms import UpdateProfileForm, MedicalMetricsForm

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile')
@login_required
def profile():
    """User profile view"""
    return render_template('profile.html', user=current_user)


@user_bp.route('/settings')
@login_required
def settings():
    """User settings page"""
    return render_template('settings.html')


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return render_template('dashboard.html', user=current_user)


@user_bp.route('/profile/edit', methods=['GET', 'POST'])
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
        flash('Ваш профиль был обновлен!', 'success')
        return redirect(url_for('user.dashboard'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.bio.data = current_user.bio
        form.country.data = current_user.country

    return render_template('edit_profile.html', form=form)


@user_bp.route('/medical-card', methods=['GET', 'POST'])
@login_required
def medical_card():
    """Medical card page - user's medical information"""
    # Get or create medical metrics for current user
    metrics = MedicalMetrics.query.filter_by(user_id=current_user.id).first()
    if not metrics:
        metrics = MedicalMetrics(user_id=current_user.id)
        db.session.add(metrics)
        db.session.commit()

    form = MedicalMetricsForm()

    if request.method == 'GET':
        # Populate form with existing data
        form.height_cm.data = metrics.height_cm
        form.weight_kg.data = metrics.weight_kg
        form.blood_type.data = metrics.blood_type or ''
        form.blood_pressure_systolic.data = metrics.blood_pressure_systolic
        form.blood_pressure_diastolic.data = metrics.blood_pressure_diastolic
        form.heart_rate.data = metrics.heart_rate
        form.temperature_c.data = metrics.temperature_c
        form.oxygen_saturation.data = metrics.oxygen_saturation
        form.allergies.data = metrics.allergies
        form.chronic_conditions.data = metrics.chronic_conditions
        form.medications.data = metrics.medications
        form.surgeries.data = metrics.surgeries
        form.emergency_contact_name.data = metrics.emergency_contact_name
        form.emergency_contact_phone.data = metrics.emergency_contact_phone
        form.emergency_contact_relation.data = metrics.emergency_contact_relation

    if form.validate_on_submit():
        # Update medical metrics
        metrics.height_cm = form.height_cm.data
        metrics.weight_kg = form.weight_kg.data
        metrics.blood_type = form.blood_type.data
        metrics.blood_pressure_systolic = form.blood_pressure_systolic.data
        metrics.blood_pressure_diastolic = form.blood_pressure_diastolic.data
        metrics.heart_rate = form.heart_rate.data
        metrics.temperature_c = form.temperature_c.data
        metrics.oxygen_saturation = form.oxygen_saturation.data
        metrics.allergies = form.allergies.data
        metrics.chronic_conditions = form.chronic_conditions.data
        metrics.medications = form.medications.data
        metrics.surgeries = form.surgeries.data
        metrics.emergency_contact_name = form.emergency_contact_name.data
        metrics.emergency_contact_phone = form.emergency_contact_phone.data
        metrics.emergency_contact_relation = form.emergency_contact_relation.data

        db.session.commit()
        flash('Медицинская информация успешно сохранена!', 'success')
        return redirect(url_for('user.medical_card'))

    return render_template('medical_card.html', user=current_user, form=form, metrics=metrics)


@user_bp.route('/medical-analysis')
@login_required
def medical_analysis():
    """Medical analysis page"""
    return render_template('medical_analysis.html', user=current_user)
