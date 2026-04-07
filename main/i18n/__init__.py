"""
Server-side internationalization engine for ShipAI.
Provides t() translation function and language management.
"""
from flask import session, request, redirect

from main.i18n.en import translations as en_translations
from main.i18n.ru import translations as ru_translations
from main.i18n.kz import translations as kz_translations

LANGUAGES = {
    'en': en_translations,
    'ru': ru_translations,
    'kz': kz_translations,
}
DEFAULT_LANGUAGE = 'en'


def get_locale():
    """Get current language from: URL param > session > default."""
    lang = request.args.get('lang')
    if lang and lang in LANGUAGES:
        session['lang'] = lang
        return lang
    lang = session.get('lang')
    if lang and lang in LANGUAGES:
        return lang
    return DEFAULT_LANGUAGE


def t(key, **kwargs):
    """Translate a key to the current language.

    Falls back to English, then to the raw key.
    Supports f-string style formatting: t('flash_code_sent', email='user@example.com')
    """
    lang = get_locale()
    translations = LANGUAGES.get(lang, LANGUAGES[DEFAULT_LANGUAGE])
    text = translations.get(key)
    if text is None:
        text = LANGUAGES[DEFAULT_LANGUAGE].get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            pass
    return text


class LazyTranslation:
    """Lazy translation wrapper for WTForms validators.
    Translates when converted to string (at validation time, within request context).
    """
    def __init__(self, key, **kwargs):
        self.key = key
        self.kwargs = kwargs

    def __str__(self):
        return t(self.key, **self.kwargs)

    def __repr__(self):
        return str(self)

    def __mod__(self, other):
        return str(self) % other

    def __html__(self):
        return str(self)


def lazy_t(key, **kwargs):
    """Return a lazy translation object for use in WTForms validators."""
    return LazyTranslation(key, **kwargs)


def init_i18n(app):
    """Register i18n with the Flask app."""

    @app.before_request
    def set_language():
        lang = request.args.get('lang')
        if lang and lang in LANGUAGES:
            session['lang'] = lang

    @app.context_processor
    def inject_i18n():
        return {
            't': t,
            'current_lang': get_locale(),
        }
