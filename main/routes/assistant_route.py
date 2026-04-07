import sys
import os
import logging

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required

from main.i18n import t

# Use safe wrapper for med_bot
from main.utils.med_bot_wrapper import answer_question, is_rag_available

# Create blueprint
assistant_bp = Blueprint('assistant', __name__, url_prefix='/assistant')

logger = logging.getLogger('assistant')

RAG_AVAILABLE = is_rag_available()

@assistant_bp.route('/')
@login_required
def assistant_page():
    """Assistant main page"""
    return render_template('assistant_page.html')

@assistant_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """API endpoint for chat messages"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({
            'error': 'No message provided',
            'success': False
        }), 400
    
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({
            'error': 'Empty message',
            'success': False
        }), 400
    
    if len(user_message) > 1000:
        return jsonify({
            'error': 'Message too long (max 1000 characters)',
            'success': False
        }), 400
    
    try:
        # Get answer from RAG engine (wrapper handles all errors)
        response = answer_question(user_message)
        
        # Store conversation in session (for tracking)
        if 'assistant_history' not in session:
            session['assistant_history'] = []
        
        session['assistant_history'].append({
            'user': user_message,
            'assistant': response
        })
        session.modified = True
        
        return jsonify({
            'response': response,
            'success': True
        })
    
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({
            'error': t('assistant_error'),
            'response': t('assistant_error'),
            'success': False
        }), 500

@assistant_bp.route('/api/clear-history', methods=['POST'])
@login_required
def clear_history():
    """Clear chat history"""
    session.pop('assistant_history', None)
    session.modified = True
    return jsonify({'success': True})

@assistant_bp.route('/api/history', methods=['GET'])
@login_required
def get_history():
    """Get chat history"""
    history = session.get('assistant_history', [])
    return jsonify({'history': history})