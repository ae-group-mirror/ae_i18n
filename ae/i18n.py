"""
Internationalization / Localization helpers
===========================================

"""
import locale
import os
from typing import Dict, Union, Optional, Any

from ae.core import stack_variables                                                 # type: ignore


__version__ = '0.0.1'


MSG_FILE_SUFFIX = 'i18n.msg'

_DOMAIN_LANGUAGES: Dict[str, str] = dict()
_LOADED_LANGUAGES: Dict[str, Dict[str, Union[str, Dict[str, str]]]] = dict()
_LANGUAGE, _ENCODING = locale.getdefaultlocale()


def add_domain(domain: str, language: str):
    """ add/register new domain associated to the passed language.

    :param domain:      domain id, e.g. the id of an app or a user.
    :param language:    language to translate to for the passed domain.
    """
    global _DOMAIN_LANGUAGES
    _DOMAIN_LANGUAGES[domain] = language


def load_language_texts(language: str, domain: str = ''):
    """ load translatable message texts for the given language and optional domain.

    :param language:    language to load.
    :param domain:      optional domain id, e.g. the id of an app or a user. if passed
                        then a message file with the domain name as prefix will be preferred.
    """
    if domain not in _DOMAIN_LANGUAGES:
        add_domain(domain, language)

    file_name = os.path.join('loc', language)
    if os.path.exists(os.path.join(file_name, domain + '_' + MSG_FILE_SUFFIX)):
        file_name = os.path.join(file_name, domain + '_' + MSG_FILE_SUFFIX)
    else:
        file_name = os.path.join(file_name, MSG_FILE_SUFFIX)
    with open(file_name) as file_handle:        # refactor with de.core.file_content into ae.core
        file_content = file_handle.read()

    global _LOADED_LANGUAGES
    _LOADED_LANGUAGES[language] = eval(file_content)


def get_text(text: str, count: int = 1, domain: str = '') -> str:
    """ translate passed text string into the current language.

    :param text:        text message to be translated.
    :param count:       pass int value if the translated text changes on pluralization (default=1).
    :param domain:      domain id, identifying a configured/registered language.
    :return:            translated text message or the value passed into :paramref:`~get_text.text`
                        if no translation text got found for the current language.
    """
    lang = _DOMAIN_LANGUAGES.get(domain, _LANGUAGE)
    if lang in _LOADED_LANGUAGES:
        translations = _LOADED_LANGUAGES[lang]
        if text in translations:
            trans = translations[text]
            if isinstance(trans, dict):
                if count == 0:
                    key = 'zero'
                elif count == 1:
                    key = 'one'
                elif count > 1:
                    key = 'many'
                elif count < 0:
                    key = 'negative'
                else:
                    key = 'any'
                text = trans.get(key, text)
            else:
                text = trans
    return text


_ = get_text         #: alias of :func:`get_text`.


def get_f_string(f_string: str, count: int = 1, domain: str = '',
                 g_vars: Optional[Dict[str, Any]] = None, l_vars: Optional[Dict[str, Any]] = None
                 ) -> str:
    """ translate passed f-string into a f-string of the current language.

    :param f_string:    f-string to be translated and evaluated.
    :param count:       pass if the translated text changes on pluralization (see :func:`get_text`).
    :param domain:      domain id, identifying a configured/registered language.
    :param g_vars:      global variables used in the conversion of the f-string expression to a string.
    :param l_vars:      local variables used in the conversion of the f-string expression to a string.
    :return:            translated text message or the evaluated string result of the expression passed into
                        :paramref:`~get_text.f_string` if no translation text got found for the current language.
    """
    f_string = get_text(f_string, count=count, domain=domain)
    if not g_vars and not l_vars:
        g_vars, l_vars, _ = stack_variables(max_depth=1)
    return eval(f"f'{f_string}'", g_vars, l_vars)


f_ = get_f_string       #: alias of :func:`get_f_string`.
