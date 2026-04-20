"""
User profile and account routes blueprint
"""
import os
import hashlib
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from main.models import db, User, MedicalMetrics, MedicalDocument, LabResult
from main.forms import UpdateProfileForm, MedicalMetricsForm, MedicalDocumentUploadForm, ChangePasswordForm
from main.i18n import t

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
    form = ChangePasswordForm()
    return render_template('settings.html', form=form)


@user_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash(t('wrong_current_password'), 'error')
            return redirect(url_for('user.settings'))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash(t('password_changed'), 'success')
        return redirect(url_for('user.settings'))
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'error')
    return redirect(url_for('user.settings'))


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
        flash(t('flash_profile_updated'), 'success')
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
        flash(t('flash_medical_saved'), 'success')
        return redirect(url_for('user.medical_card'))

    # Get latest confirmed lab results
    latest_doc = MedicalDocument.query.filter_by(
        user_id=current_user.id, status='confirmed'
    ).order_by(MedicalDocument.confirmed_at.desc()).first()
    lab_results = latest_doc.lab_results if latest_doc else []

    # Generate recommendations
    from main.utils.health_analyzer import analyze_health, analyze_lab_results
    from main.utils.groq_client import generate_health_tips

    analysis = analyze_health(metrics) if metrics else None
    lab_analysis = analyze_lab_results(lab_results) if lab_results else None
    health_tips = None
    if lab_results:
        health_tips = generate_health_tips(lab_results, metrics)

    return render_template('medical_card.html', user=current_user, form=form,
                           metrics=metrics, lab_results=lab_results,
                           analysis=analysis, lab_analysis=lab_analysis,
                           health_tips=health_tips)


@user_bp.route('/medical-analysis')
@login_required
def medical_analysis():
    """Medical analysis page with health recommendations"""
    from main.utils.health_analyzer import analyze_health, analyze_lab_results
    from main.utils.groq_client import generate_health_tips

    metrics = MedicalMetrics.query.filter_by(user_id=current_user.id).first()
    analysis = analyze_health(metrics) if metrics else None

    # Get latest confirmed lab results
    latest_doc = MedicalDocument.query.filter_by(
        user_id=current_user.id, status='confirmed'
    ).order_by(MedicalDocument.confirmed_at.desc()).first()

    lab_results = latest_doc.lab_results if latest_doc else []
    lab_analysis = analyze_lab_results(lab_results) if lab_results else None

    # Generate AI health tips if we have lab data
    health_tips = None
    if lab_results:
        health_tips = generate_health_tips(lab_results, metrics)

    return render_template('medical_analysis.html', user=current_user,
                           analysis=analysis, metrics=metrics,
                           lab_results=lab_results, lab_analysis=lab_analysis,
                           health_tips=health_tips)


@user_bp.route('/lab-upload', methods=['GET', 'POST'])
@login_required
def lab_upload():
    """Upload medical documents for lab value extraction"""
    form = MedicalDocumentUploadForm()

    if form.validate_on_submit():
        raw_text = None
        filename = None
        file_path = None
        input_type = 'text'

        # Handle PDF upload
        if form.document.data:
            f = form.document.data
            filename = secure_filename(f.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_dir, f'{current_user.id}_{int(datetime.utcnow().timestamp())}_{filename}')
            f.save(file_path)
            input_type = 'pdf'

            # Extract text from PDF
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    raw_text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
            except Exception as e:
                flash(t('flash_pdf_error', error=str(e)), 'danger')
                return redirect(url_for('user.lab_upload'))

        # Handle pasted text
        elif form.text_input.data and form.text_input.data.strip():
            raw_text = form.text_input.data.strip()
            input_type = 'text'
        else:
            flash(t('flash_upload_required'), 'warning')
            return redirect(url_for('user.lab_upload'))

        if not raw_text or len(raw_text.strip()) < 10:
            flash(t('flash_not_enough_text'), 'warning')
            return redirect(url_for('user.lab_upload'))

        # Check for duplicate content
        content_hash = hashlib.sha256(raw_text.strip().encode('utf-8')).hexdigest()
        existing = MedicalDocument.query.filter_by(
            user_id=current_user.id, content_hash=content_hash
        ).first()
        if existing:
            # Clean up uploaded file if any
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            flash(t('flash_duplicate_doc'), 'warning')
            return redirect(url_for('user.lab_upload'))

        # Create document record
        doc = MedicalDocument(
            user_id=current_user.id,
            filename=filename,
            file_path=file_path,
            input_type=input_type,
            raw_text=raw_text,
            content_hash=content_hash,
            status='pending',
        )
        db.session.add(doc)
        db.session.commit()

        return redirect(url_for('user.lab_results', doc_id=doc.id))

    # Get past uploads
    documents = MedicalDocument.query.filter_by(
        user_id=current_user.id
    ).order_by(MedicalDocument.created_at.desc()).all()

    return render_template('lab_upload.html', form=form, documents=documents)


@user_bp.route('/lab-results/<int:doc_id>', methods=['GET', 'POST'])
@login_required
def lab_results(doc_id):
    """Review and confirm extracted lab results"""
    doc = MedicalDocument.query.get_or_404(doc_id)
    if doc.user_id != current_user.id:
        flash(t('flash_access_denied'), 'danger')
        return redirect(url_for('user.lab_upload'))

    # Extract lab values if still pending
    if doc.status == 'pending':
        from main.utils.groq_client import extract_lab_values

        result = extract_lab_values(doc.raw_text)

        if result.get('error'):
            doc.status = 'failed'
            doc.error_message = result['error']
            db.session.commit()
            flash(result['error'], 'warning')
        else:
            doc.ai_summary = result.get('summary', '')
            doc.status = 'extracted'

            for lr_data in result.get('lab_results', []):
                lab = LabResult(
                    document_id=doc.id,
                    user_id=current_user.id,
                    test_name=lr_data.get('test_name', ''),
                    test_name_ru=lr_data.get('test_name_ru', ''),
                    value=lr_data.get('value'),
                    unit=lr_data.get('unit', ''),
                    reference_range_low=lr_data.get('reference_range_low'),
                    reference_range_high=lr_data.get('reference_range_high'),
                    reference_range_text=lr_data.get('reference_range_text', ''),
                    status=lr_data.get('status', 'normal'),
                    category=lr_data.get('category', 'other'),
                )
                db.session.add(lab)

            db.session.commit()

    # Handle user confirmation (POST)
    if request.method == 'POST' and doc.status == 'extracted':
        # Update lab results from form data
        for lab in doc.lab_results:
            val = request.form.get(f'value_{lab.id}')
            if val:
                try:
                    lab.value = float(val)
                except (ValueError, TypeError):
                    pass
            unit = request.form.get(f'unit_{lab.id}')
            if unit:
                lab.unit = unit
            lab.is_confirmed = True

        doc.status = 'confirmed'
        doc.confirmed_at = datetime.utcnow()

        # Auto-delete the uploaded file and clear raw text (no longer needed)
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        doc.file_path = None
        doc.raw_text = None

        db.session.commit()

        flash(t('flash_lab_confirmed'), 'success')
        return redirect(url_for('user.medical_card'))

    return render_template('lab_results_review.html', doc=doc)


@user_bp.route('/lab-upload/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id):
    """Delete an uploaded medical document"""
    doc = MedicalDocument.query.get_or_404(doc_id)
    if doc.user_id != current_user.id:
        flash(t('flash_access_denied'), 'danger')
        return redirect(url_for('user.lab_upload'))

    # Delete file from disk
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.session.delete(doc)
    db.session.commit()
    flash(t('flash_doc_deleted'), 'success')
    return redirect(url_for('user.lab_upload'))
