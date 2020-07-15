"""
Internationalization / Localization helpers
===========================================

"""
import ast
import locale
import os
from typing import Dict, Union, Optional, Any, Sequence

from ae.core import stack_variables, try_eval  # type: ignore


__version__ = '0.0.2'


MsgType = Union[str, Dict[str, str]]
LanguageMessages = Dict[str, MsgType]


MSG_FILE_SUFFIX = 'i18n.msg'                                #: message text files containing

DOMAIN_LANGUAGES: Dict[str, str] = dict()                   #: associate a language to each domain
LOADED_LANGUAGES: Dict[str, LanguageMessages] = dict()      #: message text translations of all loaded languages

LANGUAGE, ENCODING = locale.getdefaultlocale()


def add_domain(domain: str, language: str):
    """ add/register new domain associated to the passed language.

    :param domain:      domain id, e.g. the id of an app or a user.
    :param language:    language to translate to for the passed domain.
    """
    global DOMAIN_LANGUAGES
    DOMAIN_LANGUAGES[domain] = language


def load_language_texts(language: str, domain: str = '', file_paths: Sequence[str] = ('loc', )):
    """ load translatable message texts for the given language and optional domain.

    :param language:    language to load.
    :param domain:      optional domain id, e.g. the id of an app or a user. if passed
                        then a message file with the domain name as prefix will be preferred.
    :param file_paths:  tuple of location folder root paths to search for message text files.
    """
    def file_to_dict(file_name: str):
        """ check passed file name (file_name) and if exists then load, parse and compile file content into a dict. """
        if os.path.exists(file_name):
            with open(file_name) as file_handle:  # refactor with de.core.file_content into ae.core
                file_content = file_handle.read()
            if file_content:
                lang_messages = ast.literal_eval(file_content)
                if lang_messages:
                    global LOADED_LANGUAGES
                    if language not in LOADED_LANGUAGES:
                        LOADED_LANGUAGES[language] = dict()
                    LOADED_LANGUAGES[language].update(lang_messages)

    for path in file_paths:
        path = os.path.join(path, language)
        file_to_dict(os.path.join(path, MSG_FILE_SUFFIX))
        if domain:
            file_to_dict(os.path.join(path, domain + '_' + MSG_FILE_SUFFIX))

    if domain not in DOMAIN_LANGUAGES:
        add_domain(domain, language)


def get_text(text: str, count: Optional[int] = None, domain: str = '') -> str:
    """ translate passed text string into the current language.

    :param text:        text message to be translated.
    :param count:       pass int value if the translated text has variants for their pluralization.
                        The count value will be converted into an amount/pluralize key by the
                        function :func:`plural_key`.
    :param domain:      domain id, identifying a configured/registered language.
    :return:            translated text message or the value passed into :paramref:`~get_text.text`
                        if no translation text got found for the current language.
    """
    lang = DOMAIN_LANGUAGES.get(domain, LANGUAGE)
    if lang in LOADED_LANGUAGES:
        translations = LOADED_LANGUAGES[lang]
        if text in translations:
            trans = translations[text]
            if isinstance(trans, str):
                text = trans
            else:
                key = plural_key(count) if count is not None else 'any'
                text = trans.get(key, text)
    return text


_ = get_text         #: alias of :func:`get_text`.


def get_f_string(f_string: str, count: Optional[int] = None, domain: str = '',
                 glo_vars: Optional[Dict[str, Any]] = None, loc_vars: Optional[Dict[str, Any]] = None
                 ) -> str:
    """ translate passed f-string into a f-string of the current language.

    :param f_string:    f-string to be translated and evaluated.
    :param count:       pass if the translated text changes on pluralization (see :func:`get_text`).
                        If passed then the value of this argument will be provided/overwritten in the
                        globals as a variable with the name `count`.
    :param domain:      domain id, identifying a configured/registered language.
    :param glo_vars:    global variables used in the conversion of the f-string expression to a string.
    :param loc_vars:    local variables used in the conversion of the f-string expression to a string.
    :return:            translated text message or the evaluated string result of the expression passed into
                        :paramref:`~get_text.f_string` if no translation text got found for the current language.
                        All syntax errors and exceptions occurring in the conversion of the f-string will be
                        ignored and the original or translated f_string value will be returned in these cases.
    """
    f_string = get_text(f_string, count=count, domain=domain)

    if not glo_vars and not loc_vars:
        glo_vars, loc_vars, _ = stack_variables(min_depth=3, max_depth=3)

    if count is not None:
        assert isinstance(glo_vars, dict)       # mypy
        glo_vars['count'] = count

    return try_eval('f"' + f_string + '"', ignored_exceptions=(Exception, ), glo_vars=glo_vars, loc_vars=loc_vars) \
        or f_string


f_ = get_f_string       #: alias of :func:`get_f_string`.


def plural_key(count: int) -> str:
    """ convert number in count into a dict key for to access the correct plural form.

    :param count:       number of items used in the current context.
    :return:            dict key within the MsgType part of the translation data structure.
    """
    if count == 0:
        key = 'zero'
    elif count == 1:
        key = 'one'
    elif count > 1:
        key = 'many'
    else:
        key = 'negative'

    return key
