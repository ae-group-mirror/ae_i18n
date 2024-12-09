""" ae.i18n unit tests. """
import os
import pytest

from ae.base import TESTS_FOLDER

# noinspection PyProtectedMember
from ae.i18n import (
    INSTALLED_LANGUAGES, LOADED_TRANSLATIONS, MSG_FILE_SUFFIX, TRANSLATIONS_PATHS,
    default_encoding, default_language, default_locale, get_text, get_f_string, load_language_texts,
    register_package_translations, register_translations_path)


test_message_texts = ("test message 1", "test message 2", "pluralize-able", )
test_message_text2 = ("test message 3", "test message 2", )
pluralize_keys = ('zero', 'one', 'many', 'negative', '', )


@pytest.fixture
def lang_file_es():
    """ provide test message file for the language es_ES. """
    lang = 'es'

    fr = os.path.join(TESTS_FOLDER, 'loc')
    fp = os.path.join(fr, lang)
    os.makedirs(fp)
    fn = os.path.join(fp, MSG_FILE_SUFFIX)
    with open(fn, 'w') as file_handle:
        file_handle.write('{\n')
        file_handle.write(',\n'.join(['"' + t + '": "t m ' + t[-1] + '"' for t in test_message_texts[:2]]))
        file_handle.write(',\n"' + test_message_texts[2] + '": {')
        file_handle.write(', '.join(['"' + t + '": "' + t[:1] + '"' for t in pluralize_keys]) + '}\n')
        file_handle.write('}\n')
    fn2 = os.path.join(fp, 'additional' + MSG_FILE_SUFFIX)
    with open(fn2, 'w') as file_handle:
        file_handle.write('{\n')
        file_handle.write(f'"{test_message_text2[0]}": "' + 2 * test_message_text2[0] + '",')
        file_handle.write(f'"{test_message_text2[1]}": "OLD MESSAGE", ')
        file_handle.write('}\n')

    yield lang

    # check if file exists because some exception/error-check tests need to delete the file
    if os.path.exists(fn2):
        os.remove(fn2)
    if os.path.exists(fn):
        os.remove(fn)
    if os.path.exists(fp):
        os.rmdir(fp)
    if os.path.exists(fr):
        os.rmdir(fr)


glo_var = 'glo_var_val'


class TestDeclarations:
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
        assert len(INSTALLED_LANGUAGES) == 3    # the 3 languages ES, DE, EN of this package (see ae/loc/**)


class TestMissingTranslation:
    def test_get_text(self):
        assert get_text("tst_msg") == "tst_msg"

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'
        assert get_f_string("{loc_var}") == loc_var

    def test_f_string_globals(self):
        assert get_f_string("{glo_var}") == glo_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        assert get_f_string("{glo_var}{loc_var}") == glo_var + loc_var


class TestLangLoading:
    def test_ignore_missing_language_path(self):
        assert len(TRANSLATIONS_PATHS) == 1
        assert not register_translations_path('path_not_exists')
        assert len(TRANSLATIONS_PATHS) == 1

    def test_register_translations_path(self, lang_file_es):
        assert len(TRANSLATIONS_PATHS) == 1
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 0

        register_translations_path()            # nothing to register in cwd
        assert len(TRANSLATIONS_PATHS) == 1
        assert len(INSTALLED_LANGUAGES) == 3
        assert len(LOADED_TRANSLATIONS) == 0

        register_translations_path(TESTS_FOLDER)    # register/import lang_file_es tests
        assert len(TRANSLATIONS_PATHS) == 2
        assert len(INSTALLED_LANGUAGES) == 3
        # assert INSTALLED_LANGUAGES[0]=='en' == lang_file_es
        assert len(LOADED_TRANSLATIONS) == 0

        register_translations_path()
        assert len(LOADED_TRANSLATIONS) == 0
        assert default_language(lang_file_es) != lang_file_es       # change and load test language
        assert len(LOADED_TRANSLATIONS) == 1
        assert default_language() == lang_file_es

    def test_load_language_texts_str(self, lang_file_es):
        register_translations_path(TESTS_FOLDER)
        load_language_texts(lang_file_es)

        assert lang_file_es in LOADED_TRANSLATIONS
        assert isinstance(LOADED_TRANSLATIONS[lang_file_es], dict)
        assert LOADED_TRANSLATIONS[lang_file_es][test_message_texts[0]] == 't m 1'
        assert LOADED_TRANSLATIONS[lang_file_es][test_message_texts[1]] == 't m 2'

    def test_load_languages_texts_plural(self, lang_file_es):
        register_translations_path(TESTS_FOLDER)
        load_language_texts(lang_file_es)                           # test re-load because already loaded by prev test

        assert isinstance(LOADED_TRANSLATIONS[lang_file_es][test_message_texts[2]], dict)
        for t in pluralize_keys:
            assert LOADED_TRANSLATIONS[lang_file_es][test_message_texts[2]][t] == t[:1]

    def test_get_default_lang(self, lang_file_es):
        assert load_language_texts()

    def test_register_package_translations(self, lang_file_es):
        TRANSLATIONS_PATHS.clear()
        assert not TRANSLATIONS_PATHS
        register_package_translations()
        assert TRANSLATIONS_PATHS

    def test_register_package_translations_missing(self):
        TRANSLATIONS_PATHS.clear()
        assert not TRANSLATIONS_PATHS
        register_package_translations()
        assert not TRANSLATIONS_PATHS


class TestWithLoadedTranslations:
    def test_get_text(self, lang_file_es):
        assert register_translations_path(TESTS_FOLDER)
        load_language_texts(lang_file_es, reset=True)

        assert get_text("tst_msg") == "tst_msg"
        assert get_text(test_message_texts[0], language=lang_file_es) == "t m " + test_message_texts[0][-1]
        assert get_text(test_message_texts[1], language=lang_file_es) == "t m " + test_message_texts[1][-1]

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'
        assert get_f_string("{loc_var}") == loc_var

    def test_f_string_globals(self):
        assert get_f_string("{glo_var}") == glo_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        assert get_f_string("{glo_var}{loc_var}") == glo_var + loc_var

    def test_get_text_pluralized(self, lang_file_es):
        assert get_text(test_message_texts[2]) == ''
        assert get_text(test_message_texts[2], language=lang_file_es) == ''    # any


class TestCount:
    def test_get_text(self):
        assert get_text("tst_msg", count=3) == "tst_msg"

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'

        assert get_f_string("{loc_var}") == loc_var
        assert get_f_string("{loc_var}", loc_vars=dict(count=4)) == loc_var
        assert get_f_string("{loc_var}", loc_vars=dict(loc_var=loc_var, count=4)) == loc_var

    def test_f_string_globals(self):
        assert get_f_string("{glo_var}") == glo_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        assert get_f_string("{glo_var}{loc_var}") == glo_var + loc_var

        count = 6
        assert get_f_string("{glo_var}{loc_var}{count}", glo_vars=globals(), loc_vars=locals()) \
               == glo_var + loc_var + str(count)

    def test_get_text_pluralized(self, lang_file_es):
        assert get_text(test_message_texts[2], count=-1, language=lang_file_es) == 'n'     # negative
        assert get_text(test_message_texts[2], count=0, language=lang_file_es) == "z"      # zero
        assert get_text(test_message_texts[2], count=1, language=lang_file_es) == "o"      # one
        assert get_text(test_message_texts[2], count=2, language=lang_file_es) == "m"      # many
        assert get_text(test_message_texts[2], count=3, language=lang_file_es) == "m"
        assert get_text(test_message_texts[2], count=999, language=lang_file_es) == "m"

    def test_get_text_pluralized_without_count(self, lang_file_es):
        assert get_text(test_message_texts[2], language=lang_file_es) == ""       # any

    def test_f_string_pluralized_without_count(self, lang_file_es):
        assert get_f_string(test_message_texts[2], language=lang_file_es) == ""      # any


class TestLocaleSwitch:
    def test_get_text(self, lang_file_es):
        # already added: add_paths(TESTS_FOLDER)
        assert get_text("tst_msg") == "tst_msg"
        assert get_text("tst_msg", language=lang_file_es) == "tst_msg"
        assert get_text("tst_msg", language='not_loaded_lang_code') == "tst_msg"

        assert get_text(test_message_texts[0], language=lang_file_es) == "t m " + test_message_texts[0][-1]
        assert get_text(test_message_texts[0], language='not_loaded_lang_code') == test_message_texts[0]

        assert get_text("tst_msg") == "tst_msg"
        assert get_text("tst_msg", language=lang_file_es) == "tst_msg"
        assert get_text("tst_msg", language='not_loaded_lang_code') == "tst_msg"

        assert get_text(test_message_texts[0]) == "t m " + test_message_texts[0][-1]
        assert get_text(test_message_texts[0], language=lang_file_es) == "t m " + test_message_texts[0][-1]
        assert get_text(test_message_texts[0], language='not_loaded_lang_code') == test_message_texts[0]

    def test_f_string_locals(self, lang_file_es):
        loc_var = 'loc_var_val'
        assert get_f_string("{loc_var}", language=lang_file_es) == loc_var

        register_translations_path(TESTS_FOLDER)
        load_language_texts(lang_file_es)
        default_language(lang_file_es)
        loc_var = 'loc_var_val'
        assert get_f_string("{loc_var}", language=lang_file_es) == loc_var

    def test_f_string_globals(self, lang_file_es):
        assert get_f_string("{glo_var}") == glo_var
        assert get_f_string("{glo_var}", language=lang_file_es) == glo_var

        default_language(lang_file_es)
        assert get_f_string("{glo_var}") == glo_var

    def test_f_string(self, lang_file_es):
        loc_var = 'loc_var_val'
        assert get_f_string("{glo_var}{loc_var}") == glo_var + loc_var
        assert get_f_string("{glo_var}{loc_var}", language=lang_file_es) == glo_var + loc_var

        count = 6
        assert get_f_string("{glo_var}{loc_var}{count}", glo_vars=globals(), loc_vars=locals()) \
               == glo_var + loc_var + str(count)
        assert get_f_string("{glo_var}{loc_var}{count}", language=lang_file_es, glo_vars=globals(), loc_vars=locals()) \
               == glo_var + loc_var + str(count)

        default_language(lang_file_es)
        assert get_f_string("{glo_var}{loc_var}{count}", language=lang_file_es, glo_vars=globals(), loc_vars=locals()) \
               == glo_var + loc_var + str(count)

    def test_get_text_pluralized(self, lang_file_es):
        default_language(lang_file_es)
        assert get_text(test_message_texts[2]) == ""               # any
        assert get_text(test_message_texts[2], count=-1) == "n"    # negative
        assert get_text(test_message_texts[2], count=0) == "z"     # zero
        assert get_text(test_message_texts[2], count=1) == "o"     # one
        assert get_text(test_message_texts[2], count=2) == "m"     # many
        assert get_text(test_message_texts[2], count=3) == "m"
        assert get_text(test_message_texts[2], count=999) == "m"

    def test_default_encoding(self):
        old_enc = default_encoding()
        try:
            assert default_encoding('xx_XX')
            assert default_encoding('yy_YY') == 'xx_XX'
        finally:
            default_encoding(old_enc)
