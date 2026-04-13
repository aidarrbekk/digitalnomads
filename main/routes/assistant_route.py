import sys
import os
import logging

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user

from main.i18n import t
from main.models import db, ChatMessage, ChatConversation, MedicalMetrics, UserHealthCondition, Prescription, Visit, Diagnosis

# Use safe wrapper for med_bot
from main.utils.med_bot_wrapper import answer_question, is_rag_available

# Create blueprint
assistant_bp = Blueprint('assistant', __name__, url_prefix='/assistant')

logger = logging.getLogger('assistant')

RAG_AVAILABLE = is_rag_available()


def _build_user_medical_context(user_id: int, conversation_id: int = None) -> str:
    """Build a medical context string from the user's medical card data."""
    parts = []

    # 1. Medical metrics (allergies, chronic conditions, current medications)
    metrics = MedicalMetrics.query.filter_by(user_id=user_id).first()
    if metrics:
        if metrics.allergies:
            parts.append(f"Аллергии пациента: {metrics.allergies}")
        if metrics.chronic_conditions:
            parts.append(f"Хронические заболевания: {metrics.chronic_conditions}")
        if metrics.medications:
            parts.append(f"Текущие лекарства: {metrics.medications}")
        if metrics.blood_type:
            parts.append(f"Группа крови: {metrics.blood_type}")

    # 2. Active health conditions
    conditions = UserHealthCondition.query.filter_by(
        user_id=user_id, status='active'
    ).all()
    if conditions:
        cond_names = [c.disease.name for c in conditions if c.disease]
        if cond_names:
            parts.append(f"Активные заболевания: {', '.join(cond_names)}")

    # 3. Recent diagnoses (last 5)
    recent_visits = Visit.query.filter_by(user_id=user_id).order_by(
        Visit.visit_date.desc()
    ).limit(5).all()
    diag_names = []
    rx_items = []
    for v in recent_visits:
        for d in v.diagnoses:
            diag_names.append(d.disease_name)
        for p in v.prescriptions:
            rx_items.append(f"{p.medication_name} ({p.dosage or ''} {p.frequency or ''})".strip())
    if diag_names:
        parts.append(f"Недавние диагнозы: {', '.join(diag_names[:10])}")
    if rx_items:
        parts.append(f"Назначенные препараты: {', '.join(rx_items[:10])}")

    # 4. Recent messages in this conversation (for continuity)
    if conversation_id:
        recent_msgs = ChatMessage.query.filter_by(
            user_id=user_id, conversation_id=conversation_id
        ).order_by(ChatMessage.created_at.desc()).limit(6).all()
    else:
        recent_msgs = ChatMessage.query.filter_by(user_id=user_id).order_by(
            ChatMessage.created_at.desc()
        ).limit(6).all()
    if recent_msgs:
        recent_msgs.reverse()
        history_lines = []
        for m in recent_msgs:
            role_label = "Пациент" if m.role == "user" else "Ассистент"
            content = m.content[:300] + "..." if len(m.content) > 300 else m.content
            history_lines.append(f"{role_label}: {content}")
        parts.append("Последние сообщения:\n" + "\n".join(history_lines))

    return "\n".join(parts) if parts else ""


@assistant_bp.route('/')
@login_required
def assistant_page():
    """Assistant main page"""
    return render_template('assistant_page.html')


# ── Conversation management ──────────────────────────────────────────────────

@assistant_bp.route('/api/conversations', methods=['GET'])
@login_required
def list_conversations():
    """List all conversations for current user"""
    convos = ChatConversation.query.filter_by(
        user_id=current_user.id
    ).order_by(ChatConversation.updated_at.desc()).all()

    return jsonify({'conversations': [{
        'id': c.id,
        'title': c.title,
        'updated_at': c.updated_at.isoformat() if c.updated_at else c.created_at.isoformat()
    } for c in convos]})


@assistant_bp.route('/api/conversations', methods=['POST'])
@login_required
def create_conversation():
    """Create a new conversation"""
    convo = ChatConversation(user_id=current_user.id, title='New Chat')
    db.session.add(convo)
    db.session.commit()
    return jsonify({'id': convo.id, 'title': convo.title, 'success': True})


@assistant_bp.route('/api/conversations/<int:convo_id>', methods=['DELETE'])
@login_required
def delete_conversation(convo_id):
    """Delete a conversation and its messages"""
    convo = ChatConversation.query.filter_by(
        id=convo_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(convo)
    db.session.commit()
    return jsonify({'success': True})


# ── Chat ─────────────────────────────────────────────────────────────────────

@assistant_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """API endpoint for chat messages"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided', 'success': False}), 400

    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'Empty message', 'success': False}), 400

    if len(user_message) > 1000:
        return jsonify({'error': 'Message too long (max 1000 characters)', 'success': False}), 400

    conversation_id = data.get('conversation_id')

    try:
        # Resolve or create conversation
        convo = None
        if conversation_id:
            convo = ChatConversation.query.filter_by(
                id=conversation_id, user_id=current_user.id
            ).first()
        if not convo:
            convo = ChatConversation(user_id=current_user.id, title=user_message[:60])
            db.session.add(convo)
            db.session.flush()

        # Auto-title: if conversation still has default title, use first message
        if convo.title == 'New Chat':
            convo.title = user_message[:60]

        # Build user medical context
        medical_context = _build_user_medical_context(current_user.id, convo.id)

        # Get answer from RAG engine with medical context
        response = answer_question(user_message, medical_context=medical_context)

        # Save messages
        db.session.add(ChatMessage(user_id=current_user.id, conversation_id=convo.id,
                                   role='user', content=user_message))
        db.session.add(ChatMessage(user_id=current_user.id, conversation_id=convo.id,
                                   role='assistant', content=response))
        db.session.commit()

        return jsonify({
            'response': response,
            'conversation_id': convo.id,
            'conversation_title': convo.title,
            'success': True
        })

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': t('assistant_error'),
            'response': t('assistant_error'),
            'success': False
        }), 500


@assistant_bp.route('/api/clear-history', methods=['POST'])
@login_required
def clear_history():
    """Clear all conversations for current user"""
    ChatConversation.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'success': True})


@assistant_bp.route('/api/history', methods=['GET'])
@login_required
def get_history():
    """Get chat history for a specific conversation"""
    conversation_id = request.args.get('conversation_id', type=int)
    if not conversation_id:
        return jsonify({'history': []})

    convo = ChatConversation.query.filter_by(
        id=conversation_id, user_id=current_user.id
    ).first()
    if not convo:
        return jsonify({'history': []})

    messages = ChatMessage.query.filter_by(
        conversation_id=conversation_id
    ).order_by(ChatMessage.created_at.asc()).all()

    history = []
    i = 0
    while i < len(messages):
        entry = {}
        if messages[i].role == 'user':
            entry['user'] = messages[i].content
            if i + 1 < len(messages) and messages[i + 1].role == 'assistant':
                entry['assistant'] = messages[i + 1].content
                i += 2
            else:
                i += 1
        else:
            entry['assistant'] = messages[i].content
            i += 1
        history.append(entry)

    return jsonify({'history': history})