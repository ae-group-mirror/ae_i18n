""" ae.i18n unit tests. """
import importlib
import os
import sys
import types
from unittest.mock import patch, MagicMock
import pytest

from ae.base import os_path_join
from ae.paths import I18N_FOLDER


import ae.i18n          # for TestDeclaration unit tests mocking module reimport via importlib.reload
from ae.i18n import (
    INSTALLED_LANGUAGES, LOADED_TRANSLATIONS, TRANSLATIONS_PATHS,
    default_encoding, default_language, default_locale, get_text, get_f_string, load_language_texts,
    register_package_translations, register_translations_path)


tst_message_texts = ("test message 1", "test message 2", "pluralize-able",)
tst_pluralize_keys = ('zero', 'one', 'many', 'negative', '',)
tst_umlaut = "àáäÄçÇëËìÌöÖßùüÜ"     # ẑ/Ẑ (U+1E91/U+1E90) are only included in UTF

TST_LOC_PATH = 'tst_loc_path'       # changes on each unit test via lang_file_es() fixture


@pytest.fixture
def lang_file_es(tmp_path):
    """ provide the test message file for the language es_ES. """
    global TST_LOC_PATH
    TST_LOC_PATH = str(tmp_path)
    lang = 'es'

    loc_path = os_path_join(TST_LOC_PATH, I18N_FOLDER)
    lang_path = os_path_join(loc_path, lang)
    os.makedirs(lang_path)
    with open(os_path_join(lang_path, 'Msg.txt'), 'w') as file_handle:
        file_handle.write('{\n')
        file_handle.write(',\n'.join(['"' + _t + '": "' + 'tst msg ' + _t[-1] + '"' for _t in tst_message_texts[:2]]))
        file_handle.write(',\n"' + tst_message_texts[2] + '": {')
        file_handle.write(', '.join(['"' + _t + '": "' + 2 * _t[:1].upper() + '"' for _t in tst_pluralize_keys]) + "\n")
        file_handle.write(' }\n')
        file_handle.write('}\n')
    with open(os_path_join(lang_path, 'tst_domain' + 'Msg.txt'), 'w', encoding='Latin-1') as file_handle:
        file_handle.write('{\n')
        file_handle.write('"' + tst_message_texts[1] + '": "' + 'OVERLOADED MESSAGE 2 TEXT' + '", ')
        file_handle.write('"' + 'test message 3' + '": "' + 'test message 3' * 3 + tst_umlaut + '",')
        file_handle.write('}\n')

    yield lang


tst_var = 'glo_var_val'


class TestDeclarationsNoModuleReload:   # see TestDefaultLocaleNoduleReloaded for more global var tests w/ module reload
    def test_default_locale(self):
        assert len(default_locale) >= 2
        assert default_locale[0]
        assert isinstance(default_locale[0], str)
        assert default_locale[1]
        assert isinstance(default_locale[1], str)

    def test_loaded_lang_type(self):
        assert isinstance(LOADED_TRANSLATIONS, dict)

    def test_func_aliases(self):
        assert callable(get_text)
        assert callable(get_f_string)

    def test_installed_languages(self):
        assert isinstance(INSTALLED_LANGUAGES, list)
        assert len(INSTALLED_LANGUAGES) == 3    # the 3 languages ES, DE, EN of this package (see ae/i18n/{loc}/**)


class TestMissingTranslation:
    def test_get_text(self):
        assert get_text('tst_no_translation') == 'tst_no_translation'

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'
        assert get_f_string("{loc_var}") == loc_var

    def test_f_string_globals(self):
        assert get_f_string("{tst_var}") == tst_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        assert get_f_string("{tst_var}{loc_var}") == tst_var + loc_var


class TestLangLoadingModuleVariables:  # unit test order is relevant!
    def test_default_language_change_after_register_translations_path(self, lang_file_es):
        assert len(TRANSLATIONS_PATHS) == 1     # module initialization from local i18n files
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 0

        register_translations_path()            # nothing more to register in cwd (apart from ae/i18n/loc)

        assert len(TRANSLATIONS_PATHS) == 1
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 0

        register_translations_path(TST_LOC_PATH)    # register/import lang_file_es tests

        assert len(TRANSLATIONS_PATHS) == 2
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 0
        assert default_locale[0] in INSTALLED_LANGUAGES  # default_locale[0] == 'en' on english OS

        register_translations_path()

        assert len(TRANSLATIONS_PATHS) == 2
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 0

        def_lang = default_language()

        assert def_lang == 'en'

        old_lang = default_language(lang_file_es)   # change and load test language

        assert old_lang != lang_file_es
        assert old_lang == 'en'

        assert len(TRANSLATIONS_PATHS) == 2
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 1

        assert default_language() == lang_file_es

        assert len(TRANSLATIONS_PATHS) == 2
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 1

    def test_ignore_missing_language_path(self):
        assert len(TRANSLATIONS_PATHS) == 2
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 1

        assert not register_translations_path('path_not_exists')

        assert len(TRANSLATIONS_PATHS) == 2
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 1

    def test_load_language_texts_lang_es(self, lang_file_es):
        register_translations_path(TST_LOC_PATH)
        load_language_texts(lang_file_es)

        assert lang_file_es in LOADED_TRANSLATIONS
        assert isinstance(LOADED_TRANSLATIONS[lang_file_es], dict)
        assert LOADED_TRANSLATIONS[lang_file_es][tst_message_texts[0]] == 'tst msg ' + '1'
        assert LOADED_TRANSLATIONS[lang_file_es][tst_message_texts[1]] == 'tst msg ' + '2'

    def test_load_language_texts_plural(self, lang_file_es):
        register_translations_path(TST_LOC_PATH)
        load_language_texts(lang_file_es)                           # test re-load because already loaded by prev test

        assert isinstance(LOADED_TRANSLATIONS[lang_file_es][tst_message_texts[2]], dict)
        for t in tst_pluralize_keys:
            assert LOADED_TRANSLATIONS[lang_file_es][tst_message_texts[2]][t] == 2 * t[:1].upper()

    def test_load_language_texts_returns_default_language(self, lang_file_es):
        assert load_language_texts() == default_language()

    def test_register_package_translations(self, lang_file_es):
        TRANSLATIONS_PATHS.clear()
        assert not TRANSLATIONS_PATHS

        with patch('ae.i18n.stack_var', return_value=os_path_join(TST_LOC_PATH, "any_package__init__" + '.py')):
            register_package_translations()

        assert TRANSLATIONS_PATHS == [os_path_join(TST_LOC_PATH, I18N_FOLDER)]

    def test_register_package_translations_missing(self):
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 1

        TRANSLATIONS_PATHS.clear()
        assert not TRANSLATIONS_PATHS

        register_package_translations()

        assert len(TRANSLATIONS_PATHS) == 0
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 1


class TestWithLoadedTranslations:
    def test_get_text(self, lang_file_es):
        assert register_translations_path(TST_LOC_PATH)
        assert load_language_texts(lang_file_es, reset=True) == lang_file_es

        assert get_text('tst_no_translation') == 'tst_no_translation'
        assert get_text(tst_message_texts[0], language=lang_file_es) == 'tst msg ' + tst_message_texts[0][-1]
        assert get_text(tst_message_texts[1], language=lang_file_es) == 'tst msg ' + tst_message_texts[1][-1]
        assert get_text('test message 3', language=lang_file_es) == 'test message 3'  # not found/translated w/o domain

    def test_get_text_with_additional_domain_specific_translation_file_and_encoding(self, lang_file_es):
        assert register_translations_path(TST_LOC_PATH)
        assert load_language_texts(lang_file_es, encoding='Latin-1', domain='tst_domain', reset=True) == lang_file_es

        assert get_text('tst_no_translation') == 'tst_no_translation'
        assert get_text(tst_message_texts[0], language=lang_file_es) == 'tst msg ' + tst_message_texts[0][-1]
        assert get_text(tst_message_texts[1], language=lang_file_es) == 'OVERLOADED MESSAGE 2 TEXT'
        assert get_text('test message 3', language=lang_file_es) == 'test message 3' * 3 + tst_umlaut

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'
        assert get_f_string("{loc_var}") == loc_var

    def test_f_string_globals(self):
        assert get_f_string("{tst_var}") == tst_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        assert get_f_string("{tst_var}{loc_var}") == tst_var + loc_var

    def test_get_text_pluralized(self, lang_file_es):
        assert get_text(tst_message_texts[2]) == ''
        assert get_text(tst_message_texts[2], language=lang_file_es) == ''    # any


class TestCount:
    def test_get_text(self):
        assert get_text('tst_no_translation', count=3) == 'tst_no_translation'

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'

        assert get_f_string("{loc_var}") == loc_var
        assert get_f_string("{loc_var}", loc_vars=dict(count=4)) == loc_var
        assert get_f_string("{loc_var}", loc_vars=dict(loc_var=loc_var, count=4)) == loc_var

    def test_f_string_globals(self):
        assert get_f_string("{tst_var}") == tst_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        loc_count = 6

        assert get_f_string("{loc_count}", loc_vars=locals()) == str(loc_count)

        assert get_f_string("{loc_count}{tst_var}{loc_var}") == str(loc_count) + tst_var + loc_var

        loc_count = 9
        assert get_f_string("{tst_var}{loc_var}{loc_count}", glo_vars=globals(), loc_vars=locals()) \
               == tst_var + loc_var + str(loc_count)

    def test_get_text_pluralized(self, lang_file_es):
        assert get_text(tst_message_texts[2], count=-1, language=lang_file_es) == "NN"  # negative
        assert get_text(tst_message_texts[2], count=0, language=lang_file_es) == "ZZ"   # zero
        assert get_text(tst_message_texts[2], count=1, language=lang_file_es) == "OO"   # one
        assert get_text(tst_message_texts[2], count=2, language=lang_file_es) == "MM"   # many
        assert get_text(tst_message_texts[2], count=3, language=lang_file_es) == "MM"
        assert get_text(tst_message_texts[2], count=999, language=lang_file_es) == "MM"

    def test_get_text_pluralized_without_count(self, lang_file_es):
        assert get_text(tst_message_texts[2], language=lang_file_es) == ""       # any

    def test_f_string_pluralized_without_count(self, lang_file_es):
        assert get_f_string(tst_message_texts[2], language=lang_file_es) == ""      # any


class TestLocaleSwitch:
    def test_get_text(self, lang_file_es):
        # already added: add_paths(TST_LOC_PATH)
        assert get_text('tst_no_translation') == 'tst_no_translation'
        assert get_text('tst_no_translation', language=lang_file_es) == 'tst_no_translation'
        assert get_text('tst_no_translation', language='not_loaded_lang_code') == 'tst_no_translation'

        assert get_text(tst_message_texts[0], language=lang_file_es) == 'tst msg ' + tst_message_texts[0][-1]
        assert get_text(tst_message_texts[0], language='not_loaded_lang_code') == tst_message_texts[0]

        assert get_text('tst_no_translation') == 'tst_no_translation'
        assert get_text('tst_no_translation', language=lang_file_es) == 'tst_no_translation'
        assert get_text('tst_no_translation', language='not_loaded_lang_code') == 'tst_no_translation'

        assert get_text(tst_message_texts[0]) == 'tst msg ' + tst_message_texts[0][-1]
        assert get_text(tst_message_texts[0], language=lang_file_es) == 'tst msg ' + tst_message_texts[0][-1]
        assert get_text(tst_message_texts[0], language='not_loaded_lang_code') == tst_message_texts[0]

    def test_f_string_locals(self, lang_file_es):
        loc_var = 'loc_var_val'
        assert get_f_string("{loc_var}", language=lang_file_es) == loc_var

        register_translations_path(TST_LOC_PATH)
        load_language_texts(lang_file_es)
        default_language(lang_file_es)
        loc_var = 'loc_var_val'
        assert get_f_string("{loc_var}", language=lang_file_es) == loc_var

    def test_f_string_globals(self, lang_file_es):
        assert get_f_string("{tst_var}") == tst_var
        assert get_f_string("{tst_var}", language=lang_file_es) == tst_var

        default_language(lang_file_es)
        assert get_f_string("{tst_var}") == tst_var

    def test_f_string(self, lang_file_es):
        loc_var = 'loc_var_val'
        assert get_f_string("{tst_var}{loc_var}") == tst_var + loc_var
        assert get_f_string("{tst_var}{loc_var}", language=lang_file_es) == tst_var + loc_var

        count = 6
        assert get_f_string("{tst_var}{loc_var}{count}", glo_vars=globals(), loc_vars=locals()) \
               == tst_var + loc_var + str(count)
        assert get_f_string("{tst_var}{loc_var}{count}", language=lang_file_es, glo_vars=globals(), loc_vars=locals()) \
               == tst_var + loc_var + str(count)

        default_language(lang_file_es)
        assert get_f_string("{tst_var}{loc_var}{count}", language=lang_file_es, glo_vars=globals(), loc_vars=locals()) \
               == tst_var + loc_var + str(count)

    def test_get_text_pluralized(self, lang_file_es):
        default_language(lang_file_es)
        assert get_text(tst_message_texts[2]) == ""                 # any
        assert get_text(tst_message_texts[2], count=-1) == "NN"     # negative
        assert get_text(tst_message_texts[2], count=0) == "ZZ"      # zero
        assert get_text(tst_message_texts[2], count=1) == "OO"      # one
        assert get_text(tst_message_texts[2], count=2) == "MM"      # many
        assert get_text(tst_message_texts[2], count=3) == "MM"
        assert get_text(tst_message_texts[2], count=999) == "MM"

    def test_default_encoding(self):
        old_enc = default_encoding()
        try:
            assert default_encoding('xx_XX')
            assert default_encoding('yy_YY') == 'xx_XX'
        finally:
            default_encoding(old_enc)


class TestDefaultLocaleModuleReloaded:
    """ this test class has to be at the end because of importlib.reload() resetting other module vars """
    @pytest.fixture(autouse=True)
    def reset_module(self):
        yield
        importlib.reload(ae.i18n)

    def test_default_locale(self):
        with (patch('locale.getlocale', return_value=[None, None]),
              patch('locale.getencoding', return_value="")):
            importlib.reload(ae.i18n)
        assert len(ae.i18n.default_locale) >= 2
        assert isinstance(ae.i18n.default_locale[0], str)
        assert ae.i18n.default_locale[0] == 'en'
        assert isinstance(ae.i18n.default_locale[1], str)
        assert ae.i18n.default_locale[1] == 'utf-8'

    def test_android_locale(self):
        activity = MagicMock()
        activity.getResources().getConfiguration().locale.toString.return_value = 'xx_ZZ'
        jnius = types.ModuleType('jnius')
        autoclass = MagicMock()
        autoclass.return_value.mActivity = activity
        jnius.autoclass = autoclass

        with (patch('ae.system.os_platform', 'android'),
              patch.dict(sys.modules, {'jnius': jnius})):
            importlib.reload(ae.i18n)

        assert ae.i18n.default_locale == ['xx', 'utf-8']
        autoclass.assert_called_once_with('org.kivy.android.PythonActivity')

    def test_android_locale_fallback_to_get_locales(self):
        activity = MagicMock()
        configuration = activity.getResources().getConfiguration()
        configuration.locale.toString.side_effect = ValueError
        configuration.getLocales().get.return_value.toString.return_value = 'xx-YY'
        jnius = types.ModuleType('jnius')
        autoclass = MagicMock()
        autoclass.return_value.mActivity = activity
        jnius.autoclass = autoclass

        with (patch('ae.system.os_platform', 'android'),
              patch.dict(sys.modules, {'jnius': jnius})):
            importlib.reload(ae.i18n)

        assert ae.i18n.default_locale == ['xx-YY', 'utf-8']

    def test_android_locale_fallback_without_locale(self):
        activity = MagicMock()
        configuration = activity.getResources().getConfiguration()
        configuration.locale.toString.side_effect = ValueError
        configuration.getLocales().get.side_effect = ValueError
        jnius = types.ModuleType('jnius')
        autoclass = MagicMock()
        autoclass.return_value.mActivity = activity
        jnius.autoclass = autoclass

        with (patch('ae.system.os_platform', 'android'),
              patch.dict(sys.modules, {'jnius': jnius})):
            importlib.reload(ae.i18n)

        assert ae.i18n.default_locale == ['en', 'utf-8']
