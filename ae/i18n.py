"""
Internationalization / Localization helpers
===========================================

On importing this portion it will automatically determine the default locale of
your operating system and user configuration. Additionally it will check the
current working directory for a folder with the name `loc` and if it exists
load the translatable message texts for the determined language accordingly.

For to determine or to change the default language and message text encoding the
functions :func:default_language` and :func:`default_encoding` are provided
by this portion.

For to specify other locale folders you can use the function :func:`add_paths`,
which is calling :func:`init_installed_languages` for to prepare the loading
of additional translations.

In any locale folder have to exist one sub-folder with a name of the
language code (e.g. 'en_US') for each supported language. In each of these
sub-folders there have to be a message translation file (named as specified
by the constant :data:`MSG_FILE_SUFFIX`).

Additional languages have to be explicitly loaded with the function
:func:`load_language_texts`.


translatable message texts and f-strings
----------------------------------------

Simple message texts can be enclosed in the code of your application with the
:func:`get_text` function, which can also be imported with the underscore alias
from this module (the function :func:`_`)::

    from ae.i18n import _

    message = _("any translatable message displayed to the app user.")
    print(message)          # prints the translated message text

For more complex messages with placeholders you can use the :func:`get_f_string`
function or its short alias :func:`f_`::

    from ae.i18n import f_

    my_var = 69
    print(f_("The value of my_var is {my_var}."))

Translatable message can also be provided in various pluralization forms.
For to get a pluralized message you have to pass the :paramref:`~get_text.count`
keyword argument of :func:`get_text` (or :func:`get_f_string`)::

    print(_("child", count=1))     # translated into "child" (in english) or e.g. "Kind" in german
    print(_("child", count=3))     # translated into "children" (in english) or e.g. "Kinder" in german

    print(f_("you have {count] children", count=1))  # -> "you have 1 child" or e.g. "Sie haben 1 Kind"
    print(f_("you have {count] children", count=3))  # -> "you have 3 children" or e.g. "Sie haben 3 Kinder"

You can load several languages into your app run-time. For to get the translation for a language
that is not the current default language you have to pass the :paramref:`~get_text.language` keyword argument
with the desired language code onto the call of :func:`get_text` (or :func:`get_f_string`)::

    print(_("message", language='es_ES'))   # returns the spanish translation text of "message"
    print(_("message", language='de_DE'))   # returns the german translation text of "message"

The helper function :func:`translation` can be used for to determine if a translation exists for
a message text.
"""
import ast
import locale
import os
from typing import Any, Dict, List, Optional, Union

from ae.core import stack_variables, try_eval           # type: ignore


__version__ = '0.0.8'


MsgType = Union[str, Dict[str, str]]                    #: type of message translations within :data:`MSG_FILE_SUFFIX`
LanguageMessages = Dict[str, MsgType]                   #: type of the data structure storing the loaded messages


MSG_FILE_SUFFIX = 'Msg.txt'                             #: file name containing translated texts of a language/locale
DEF_LANGUAGE = 'en_US'                                  #: language code of the messages in your app code
DEF_ENCODING = 'UTF-8'                                  #: encoding of the messages in your app code

_LANG, _ENC = locale.getdefaultlocale()
if not _LANG:
    _LANG = DEF_LANGUAGE     # pragma: no cover
if not _ENC:
    _ENC = DEF_ENCODING      # pragma: no cover
default_locale: List[str] = [_LANG, _ENC]               #: language and encoding code of the current language/locale
del _LANG, _ENC

locale_paths: List[str] = ['loc', ]                     #: file paths for to search for locale configurations/messages
installed_languages: List[str] = list()                 #: list of all languages found in the :data:`local_paths`
loaded_languages: Dict[str, LanguageMessages] = dict()  #: message text translations of all loaded languages


def add_paths(*file_paths: str, reset: bool = False):
    """ add/register new file paths for to search for language and region configurations.

    The list of installed translation languages will automatically be updated.

    :param file_paths:  tuple of locale folder root paths. Each folder path is containing
                        sub-folders for each supported language/locale. The name of each
                        sub is the language code of the locale (e.g. es_ES for Spain).
    :param reset:       pass True for to clear all previously added paths.
    """
    global locale_paths
    if reset:
        # faster than locale_paths[:] = [] (https://stackoverflow.com/questions/850795/different-ways-of-clearing-lists)
        locale_paths *= 0
    locale_paths.extend(file_paths)
    init_installed_languages()


def default_language(new_lang: str = '') -> str:
    """ get and optionally set the default language code.

    :param new_lang:    new default language code to be set. Kept unchanged if not passed.
    :return:            old default language (or current one if :paramref:`~default_language.new_lang` get not passed).
    """
    old_lang = default_locale[0]
    if new_lang:
        default_locale[0] = new_lang
        if new_lang in installed_languages and new_lang not in loaded_languages:
            load_language_texts(new_lang)
    return old_lang


def default_encoding(new_enc: str = '') -> str:
    """ get and optionally set the default message text encoding.

    :param new_enc:     new default encoding to be set. Kept unchanged if not passed.
    :return:            old default encoding (current one if :paramref:`~default_encoding.new_enc` get not passed).
    """
    old_enc = default_locale[1]
    if new_enc:
        default_locale[1] = new_enc
    return old_enc


def init_installed_languages():
    """ reset and rescan the configured/supported languages found in the currently set :data:`locale_paths`.
    """
    global installed_languages
    installed_languages *= 0

    for path in locale_paths:
        if os.path.exists(path):
            installed_languages.extend(
                dir_entry.name for dir_entry in os.scandir(path)
                if dir_entry.is_dir() and os.path.exists(os.path.join(dir_entry.path, MSG_FILE_SUFFIX)))


def load_language_texts(language: str, encoding: str = '', domain: str = '', reset: bool = False):
    """ load translatable message texts for the given language and optional domain.

    :param language:    language code to load.
    :param encoding:    encoding to use for to load message file.
    :param domain:      optional domain id, e.g. the id of an app, attached process or a user. if passed
                        then it will be used as prefix for the message file name to be loaded.
    :param reset:       pass True for to clear all previously added language/locale messages.
    """
    global loaded_languages
    if reset:
        loaded_languages.clear()
    if language not in loaded_languages:
        loaded_languages[language] = dict()
    if not encoding:
        encoding = default_locale[1]

    for path in locale_paths:
        file_name = os.path.join(path, language, f'{domain}{MSG_FILE_SUFFIX}')
        if not os.path.exists(file_name):
            continue
        with open(file_name, encoding=encoding) as file_handle:  # refactor with de.core.file_content into ae.core
            file_content = file_handle.read()
        if file_content:
            lang_messages = ast.literal_eval(file_content)
            if lang_messages:
                loaded_languages[language].update(lang_messages)


def get_text(text: str, count: Optional[int] = None, key_suffix: str = '', language: str = '') -> str:
    """ translate passed text string into the current language.

    :param text:        text message to be translated.
    :param count:       pass int value if the translated text has variants for their pluralization.
                        The count value will be converted into an amount/pluralize key by the
                        function :func:`plural_key`.
    :param key_suffix:  suffix to the key used if the translation is a dict.
    :param language:    language code to load (def=current language code in 1st item of :data:`default_locale`).
    :return:            translated text message or the value passed into :paramref:`~get_text.text`
                        if no translation text got found for the current language.
    """
    trans = translation(text, language=language)
    if isinstance(trans, str):
        text = trans
    elif trans is not None:
        text = trans.get(plural_key(count) + key_suffix, text)
    return text


_ = get_text         #: alias of :func:`get_text`.


def get_f_string(f_str: str, count: Optional[int] = None, key_suffix: str = '', language: str = '',
                 glo_vars: Optional[Dict[str, Any]] = None, loc_vars: Optional[Dict[str, Any]] = None
                 ) -> str:
    """ translate passed f-string into a message string of the passed / default language.

    :param f_str:       f-string to be translated and evaluated.
    :param count:       pass if the translated text changes on pluralization (see :func:`get_text`).
                        If passed then the value of this argument will be provided/overwritten in the
                        globals as a variable with the name `count`.
    :param key_suffix:  suffix to the key used if the translation is a dict.
    :param language:    language code to load (def=current language code in 1st item of :data:`default_locale`).
    :param glo_vars:    global variables used in the conversion of the f-string expression to a string.
    :param loc_vars:    local variables used in the conversion of the f-string expression to a string.
    :return:            translated text message or the evaluated string result of the expression passed into
                        :paramref:`~get_text.f_string` if no translation text got found for the current language.
                        All syntax errors and exceptions occurring in the conversion of the f-string will be
                        ignored and the original or translated f_string value will be returned in these cases.
    """
    f_str = get_text(f_str, count=count, key_suffix=key_suffix, language=language)

    ret = ''
    if '{' in f_str and '}' in f_str:  # performance optimization: skip f-string evaluation if no placeholders
        if not glo_vars and not loc_vars:
            glo_vars, loc_vars, _ = stack_variables(max_depth=3)

        if count is not None:
            if glo_vars is None:
                glo_vars = dict()
            glo_vars['count'] = count

        ret = try_eval('f"""' + f_str + '"""', ignored_exceptions=(Exception, ), glo_vars=glo_vars, loc_vars=loc_vars)

    return ret or f_str


f_ = get_f_string       #: alias of :func:`get_f_string`.


def plural_key(count: Optional[int]) -> str:
    """ convert number in count into a dict key for to access the correct plural form.

    :param count:       number of items used in the current context or None (resulting in empty string).
    :return:            dict key (prefix) within the MsgType part of the translation data structure.
    """
    if count is None:
        key = ''
    elif count == 0:
        key = 'zero'
    elif count == 1:
        key = 'one'
    elif count > 1:
        key = 'many'
    else:
        key = 'negative'

    return key


def translation(text: str, language: str = '') -> Optional[Union[str, MsgType]]:
    """ determine translation for passed text string and language.

    :param text:        text message to be translated.
    :param language:    language code to load (def=current language code in 1st item of :data:`default_locale`).
    :return:            None if not found else translation message or dict with plural forms.
    """
    if not language:
        language = default_locale[0]

    if language in loaded_languages:
        translations = loaded_languages[language]
        if text in translations:
            return translations[text]
    return None


# load and set the system/os locale/language/encoding as the app defaults at startup (import)
init_installed_languages()
if default_locale[0] in installed_languages:  # pragma: no cover
    load_language_texts(default_locale[0], encoding=default_locale[1])
