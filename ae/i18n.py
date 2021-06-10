"""
internationalization / localization helpers
===========================================

on importing this portion it will automatically determine the default locale (language) and encoding of your operating
system and user configuration.

the functions :func:`default_language` and :func:`default_encoding` - provided by this portion - are determining or
changing the default language and translation texts encoding.

additional languages will be automatically loaded by the function :func:`load_language_texts`.


translation texts locale paths
------------------------------

multiple paths can be provided by your app as well as any python package and namespace portion to store translation
texts. by default they are situated in a sub-folder with the name `loc` underneath of your app/package root folder. to
load them call the function :func:`register_package_translations` from the module using the locale texts.

.. hint:: see e.g. the ae namespace portion :mod:`ae.gui_help` loading package/module specific translation messages.

.. hint::
    the :meth:`~ae.gui_app.on_app_build` app event is used by :mod:`~ae.gui_help` to load the app-specific translation
    texts on app startup.

to specify additional locale folders you can use the function :func:`register_translations_path`.

in a locale folder have to exist at least one sub-folder with a name of the language code for each supported language
(e.g. 'loc/en' for english).

in each of these sub-folders at least one message translation file with a file name ending in the string specified by
the constant :data:`MSG_FILE_SUFFIX` has to exist.


translatable message texts and f-strings
----------------------------------------

simple message text strings can be enclosed in the code of your application with the :func:`get_text` function provided
by this portion/module::

    from ae.i18n import get_text

    message = get_text("any translatable message displayed to the app user.")
    print(message)          # prints the translated message text

for more complex messages with placeholders you can use the :func:`get_f_string` function::

    from ae.i18n import get_f_string

    my_var = 69
    print(get_f_string("The value of my_var is {my_var}."))

translatable message can also be provided in various pluralization forms. to get a pluralized message you have to pass
the :paramref:`~get_text.count` keyword argument of :func:`get_text`::

    print(get_text("child", count=1))     # translated into "child" (in english) or e.g. "Kind" in german
    print(get_text("child", count=3))     # -> "children" (in english) or e.g. "Kinder" (in german)

for pluralized message translated by the :func:`get_f_string` function, the count value have to be passed in the `count`
item of the :paramref:`~get_f_string.loc_vars`::

    print(get_f_string("you have {count] children", loc_vars=dict(count=1)))
    # -> "you have 1 child" or e.g. "Sie haben 1 Kind"
    print(get_f_string("you have {count] children", loc_vars={'count': 3}))
    # -> "you have 3 children" or "Sie haben 3 Kinder"

you can load several languages into your app run-time. to get the translation for a language that is not the current
default language you have to pass the :paramref:`~get_text.language` keyword argument with the desired language code
onto the call of :func:`get_text` (or :func:`get_f_string`)::

    print(get_text("message", language='es'))   # returns the spanish translation text of "message"
    print(get_text("message", language='de'))   # returns the german translation text of "message"

the helper function :func:`translation` can be used to determine if a translation exists for a message text.

.. hint::
    the ae portion :mod:`ae.kivy_app` is implementing translation messages for kv files and provides additional
    helper functions and methods.
"""
import ast
import locale
import os
from typing import Any, Dict, List, Optional, Union

from ae.base import os_platform                                                 # type: ignore
from ae.files import read_file_text                                             # type: ignore
from ae.paths import norm_path, Collector                                       # type: ignore
from ae.inspector import stack_var, stack_vars, try_eval                        # type: ignore


__version__ = '0.1.23'


MsgType = Union[str, Dict[str, str]]                        #: type of message literals in translation text files
LanguageMessages = Dict[str, MsgType]                       #: type of the data structure storing the loaded messages


DEF_ENCODING = 'UTF-8'                                      #: encoding of the messages in your app code
DEF_LANGUAGE = 'en'                                         #: language code of the messages in your app code

INSTALLED_LANGUAGES: List[str] = list()                     # list of language codes found in :data:`TRANSLATIONS_PATHS`

LOADED_TRANSLATIONS: Dict[str, LanguageMessages] = dict()   #: message text translations of all loaded languages

MSG_FILE_SUFFIX = 'Msg.txt'                                 #: name suffix of translation text files

TRANSLATIONS_PATHS: List[str] = list()                      #: file paths to search for translations


if os_platform == 'android':                                                                        # pragma: no cover
    from jnius import autoclass                                                                     # type: ignore

    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    # noinspection PyBroadException
    try:
        # copied from https://github.com/HelloZeroNet/ZeroNet-kivy/blob/master/src/platform_android.py
        _LANG = mActivity.getResources().getConfiguration().locale.toString()   # deprecated since API level 24
    except Exception:
        # noinspection PyBroadException
        try:
            _LANG = mActivity.getResources().getConfiguration().getLocales().get(0).toString()
        except Exception:
            _LANG = ''
    _ENC = ''
else:
    _LANG, _ENC = locale.getdefaultlocale()  # type: ignore # mypy is not seeing the not _LANG checks (next code line)
if not _LANG:
    _LANG = DEF_LANGUAGE     # pragma: no cover
elif '_' in _LANG:
    _LANG = _LANG.split('_')[0]
if not _ENC:
    _ENC = DEF_ENCODING      # pragma: no cover
default_locale: List[str] = [_LANG, _ENC]                   #: language and encoding code of the current language/locale
del _LANG, _ENC


def default_encoding(new_enc: str = '') -> str:
    """ get and optionally set the default message text encoding.

    :param new_enc:             new default encoding to be set. kept unchanged if not passed.
    :return:                    old default encoding (current if :paramref:`~default_encoding.new_enc` get not passed).
    """
    old_enc = default_locale[1]
    if new_enc:
        default_locale[1] = new_enc
    return old_enc


def default_language(new_lang: str = '') -> str:
    """ get and optionally set the default language code.

    :param new_lang:            new default language code to be set. kept unchanged if not passed.
    :return:                    old default language (or current one if :paramref:`~default_language.new_lang`
                                get not passed).
    """
    old_lang = default_locale[0]
    if new_lang:
        default_locale[0] = new_lang
        if new_lang not in LOADED_TRANSLATIONS:
            load_language_texts(new_lang)
    return old_lang


def get_text(text: str, count: Optional[int] = None, key_suffix: str = '', language: str = '') -> str:
    """ translate passed text string into the current language.

    :param text:                text message to be translated.
    :param count:               pass int value if the translated text has variants for their pluralization. the count
                                value will be converted into an amount/pluralize key by the function :func:`plural_key`.
    :param key_suffix:          suffix to the key used if the translation is a dict.
    :param language:            language code to load (def=current language code in 1st item of :data:`default_locale`).
    :return:                    translated text message or the value passed into :paramref:`~get_text.text` if no
                                translation text got found for the current language.
    """
    trans = translation(text, language=language)
    if isinstance(trans, str):
        text = trans
    elif trans is not None:
        text = trans.get(plural_key(count) + key_suffix, text)
    return text


def get_f_string(f_str: str, key_suffix: str = '', language: str = '',
                 glo_vars: Optional[Dict[str, Any]] = None, loc_vars: Optional[Dict[str, Any]] = None
                 ) -> str:
    """ translate passed f-string into a message string of the passed / default language.

    :param f_str:               f-string to be translated and evaluated.
    :param key_suffix:          suffix to the key used if the translation is a dict.
    :param language:            language code to load (def=current language code in 1st item of :data:`default_locale`).
    :param glo_vars:            global variables used in the conversion of the f-string expression to a string. the
                                globals() of the caller of the callee will be available too and get overwritten by the
                                items of this argument.
    :param loc_vars:            local variables used in the conversion of the f-string expression to a string. the
                                locals() of the caller of the callee will be available too and get overwritten by the
                                items of this argument. pass a numeric value in the `count` item of this dict for
                                pluralized translated texts (see also :paramref:`~get_text.count` parameter of the
                                function :func:`get_text`).
    :return:                    translated text message including evaluated and formatted variables/expressions of the
                                f-string passed-in :paramref:`~get_f_string.f_str`. if no translation text got found for
                                the current language then the original text message will be returned. any syntax errors
                                and exceptions occurring in the conversion of the f-string are silently ignored.
    """
    count = loc_vars.get('count') if isinstance(loc_vars, dict) else None
    f_str = get_text(f_str, count=count, key_suffix=key_suffix, language=language)

    ret = ''
    if '{' in f_str and '}' in f_str:  # performance optimization: skip f-string evaluation if no placeholders
        g_vars, l_vars, _ = stack_vars(max_depth=1)
        if glo_vars is not None:
            g_vars.update(glo_vars)
        if loc_vars is not None:
            l_vars.update(loc_vars)

        ret = try_eval('f"""' + f_str + '"""', ignored_exceptions=(Exception, ), glo_vars=g_vars, loc_vars=l_vars)

    return ret or f_str


def load_language_file(file_name: str, encoding: str, language: str):
    """ load file content encoded with the given encoding into the specified language.

    :param file_name:           file name, inclusive path and extension to load.
    :param encoding:            encoding id string.
    :param language:            language id string.
    """
    content = read_file_text(file_name, encoding=encoding)
    if content:
        lang_messages = ast.literal_eval(content)
        if lang_messages:
            if language not in LOADED_TRANSLATIONS:
                LOADED_TRANSLATIONS[language] = dict()
            LOADED_TRANSLATIONS[language].update(lang_messages)


def load_language_texts(language: str = '', encoding: str = '', domain: str = '', reset: bool = False) -> str:
    """ load translation texts for the given language and optional domain.

    :param language:            language code of the translation texts to load. use the default language if not passed.
    :param encoding:            encoding to use to load message file.
    :param domain:              optional domain id, e.g. the id of an app, attached process or a user. if passed then it
                                will be used as prefix for the message file name to be loaded additionally and after the
                                default translation texts get loaded (overwriting the default translations).
    :param reset:               pass True to clear all previously added language/locale messages.
    :return:                    language code of the loaded/default language.
    """
    global LOADED_TRANSLATIONS

    if not language:
        language = default_language()
    if not encoding:
        encoding = default_locale[1]
    if reset:
        LOADED_TRANSLATIONS.clear()

    for root_path in TRANSLATIONS_PATHS:
        file_path = os.path.join(root_path, language, MSG_FILE_SUFFIX)
        if os.path.exists(file_path):
            load_language_file(file_path, encoding, language)
        file_path = os.path.join(root_path, language, domain + MSG_FILE_SUFFIX)
        if os.path.exists(file_path):
            load_language_file(file_path, encoding, language)

    return language


def plural_key(count: Optional[int]) -> str:
    """ convert number in :paramref:`~plural_key.count` into a dict key to access the correct plural form.

    :param count:               number of items used in the current context or None (resulting in empty string).
    :return:                    dict key (prefix) within the MsgType part of the translation data structure.
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


def register_package_translations():
    """ call from module scope of the package to register/add translations resources path.

    no parameters needed because we use here :func:`~ae.inspector.stack_var` helper function to determine the
    the module file path via the `__file__` module variable of the caller module in the call stack. in this call
    we have to overwrite the default value (:data:`~ae.inspector.SKIPPED_MODULES`) of the
    :paramref:`~ae.inspector.stack_var.skip_modules` parameter to not skip ae portions that are providing
    package resources and are listed in the :data:`~ae.inspector.SKIPPED_MODULES`, like e.g. :mod:`ae.gui_app` and
    :mod:`ae.gui_help` (passing empty string '' to overwrite default skip list).
    """
    package_path = os.path.abspath(os.path.dirname(stack_var('__file__', '')))
    register_translations_path(package_path)


def register_translations_path(translation_path: str = "") -> bool:
    """ add/register the passed root path as new resource of translation texts.

    :param translation_path:    root path of a translations folder structure to register, using cwd if not specified.
    :return:                    True if the translation folder structure exists and got properly added/registered,
                                else False.
    """
    global INSTALLED_LANGUAGES, TRANSLATIONS_PATHS

    translation_path = norm_path(os.path.join(translation_path, 'loc'))
    if not os.path.exists(translation_path):
        return False

    coll = Collector()
    coll.collect(translation_path, select="**/*" + MSG_FILE_SUFFIX, only_first_of='prefix')
    for file_path in coll.files:
        if file_path.endswith(MSG_FILE_SUFFIX):
            lang_path = os.path.basename(os.path.dirname(file_path))
            if lang_path not in INSTALLED_LANGUAGES:
                INSTALLED_LANGUAGES.append(lang_path)

    if translation_path not in TRANSLATIONS_PATHS:
        TRANSLATIONS_PATHS.append(translation_path)

    return True


def translation(text: str, language: str = '') -> Optional[Union[str, MsgType]]:
    """ determine translation for passed text string and language.

    :param text:                text message to be translated.
    :param language:            language code to load (def=current language code in 1st item of :data:`default_locale`).
    :return:                    None if not found else translation message or dict with plural forms.
    """
    if not language:
        language = default_locale[0]

    if language in LOADED_TRANSLATIONS:
        translations = LOADED_TRANSLATIONS[language]
        if text in translations:
            return translations[text]
    return None
