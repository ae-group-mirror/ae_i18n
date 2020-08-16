""" ae.i18n unit tests. """
import os

import pytest

# noinspection PyProtectedMember
from ae.i18n import (
    MSG_FILE_SUFFIX, _, f_, COLL_FILES,
    default_encoding, default_language, default_locale,
    INSTALLED_LANGUAGES, LOADED_LANGUAGES, load_language_texts, init_installed_languages)


test_message_texts = ("test message 1", "test message 2", "pluralize-able", )
test_message_text2 = ("test message 3", "test message 2", )
pluralize_keys = ('zero', 'one', 'many', 'negative', '', )


@pytest.fixture
def lang_file_es():
    """ provide test message file for the language es_ES. """
    lang = 'es'
    fp = os.path.join('tests', lang)
    os.mkdir(fp)
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


glo_var = 'glo_var_val'


class TestDeclarations:
    def test_default_locale(self):
        assert len(default_locale) >= 2
        assert default_locale[0]
        assert isinstance(default_locale[0], str)
        assert default_locale[1]
        assert isinstance(default_locale[1], str)

    def test_loaded_lang_type(self):
        assert isinstance(LOADED_LANGUAGES, dict)

    def test_func_aliases(self):
        assert callable(_)
        assert callable(f_)

    def test_installed_languages(self):
        assert isinstance(INSTALLED_LANGUAGES, list)
        assert len(INSTALLED_LANGUAGES) == 0


class TestMissingTranslation:
    def test_get_text(self):
        assert _("tst_msg") == "tst_msg"

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'
        assert f_("{loc_var}") == loc_var

    def test_f_string_globals(self):
        assert f_("{glo_var}") == glo_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        assert f_("{glo_var}{loc_var}") == glo_var + loc_var


class TestLangLoading:
    def test_missing_languages(self):
        init_installed_languages('tst', reset=False)
        assert not COLL_FILES
        init_installed_languages('test1', 'test2', reset=False)
        assert not COLL_FILES
        init_installed_languages('test1', 'test2')
        assert not COLL_FILES

    def test_init_installed_languages(self, lang_file_es):
        assert not INSTALLED_LANGUAGES
        init_installed_languages()
        assert not INSTALLED_LANGUAGES

        init_installed_languages('tests', reset=False)
        assert INSTALLED_LANGUAGES
        assert INSTALLED_LANGUAGES[0] == lang_file_es

        init_installed_languages(reset=False)
        assert not LOADED_LANGUAGES
        assert default_language(lang_file_es) != lang_file_es       # change and load test language
        assert LOADED_LANGUAGES
        assert default_language() == lang_file_es

    def test_load_language_texts_str(self, lang_file_es):
        init_installed_languages('tests', reset=False)
        load_language_texts(lang_file_es)

        assert lang_file_es in LOADED_LANGUAGES
        assert isinstance(LOADED_LANGUAGES[lang_file_es], dict)
        assert LOADED_LANGUAGES[lang_file_es][test_message_texts[0]] == 't m 1'
        assert LOADED_LANGUAGES[lang_file_es][test_message_texts[1]] == 't m 2'

    def test_load_languages_texts_plural(self, lang_file_es):
        init_installed_languages('tests', reset=False)
        load_language_texts(lang_file_es)                           # test re-load because already loaded by prev test

        assert isinstance(LOADED_LANGUAGES[lang_file_es][test_message_texts[2]], dict)
        for t in pluralize_keys:
            assert LOADED_LANGUAGES[lang_file_es][test_message_texts[2]][t] == t[:1]


class TestWithLoadedTranslations:
    def test_get_text(self, lang_file_es):
        init_installed_languages('tests')
        load_language_texts(lang_file_es, reset=True)

        assert _("tst_msg") == "tst_msg"
        assert _(test_message_texts[0], language=lang_file_es) == "t m " + test_message_texts[0][-1]
        assert _(test_message_texts[1], language=lang_file_es) == "t m " + test_message_texts[1][-1]

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'
        assert f_("{loc_var}") == loc_var

    def test_f_string_globals(self):
        assert f_("{glo_var}") == glo_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        assert f_("{glo_var}{loc_var}") == glo_var + loc_var

    def test_get_text_pluralized(self, lang_file_es):
        assert _(test_message_texts[2]) == ''
        assert _(test_message_texts[2], language=lang_file_es) == ''    # any


class TestCount:
    def test_get_text(self):
        assert _("tst_msg", count=3) == "tst_msg"

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'
        assert f_("{loc_var}", count=4) == loc_var
        assert f_("{loc_var}", count=4, loc_vars=dict(loc_var=loc_var)) == loc_var

    def test_f_string_globals(self):
        assert f_("{glo_var}", count=5) == glo_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        count = 6
        assert f_("{glo_var}{loc_var}{count}", count=count) == glo_var + loc_var + str(count)

    def test_get_text_pluralized(self, lang_file_es):
        assert _(test_message_texts[2], count=-1, language=lang_file_es) == 'n'     # negative
        assert _(test_message_texts[2], count=0, language=lang_file_es) == "z"      # zero
        assert _(test_message_texts[2], count=1, language=lang_file_es) == "o"      # one
        assert _(test_message_texts[2], count=2, language=lang_file_es) == "m"      # many
        assert _(test_message_texts[2], count=3, language=lang_file_es) == "m"
        assert _(test_message_texts[2], count=999, language=lang_file_es) == "m"

    def test_get_text_pluralized_without_count(self, lang_file_es):
        assert _(test_message_texts[2], language=lang_file_es) == ""       # any

    def test_f_string_pluralized_without_count(self, lang_file_es):
        assert f_(test_message_texts[2], language=lang_file_es) == ""      # any


class TestLocaleSwitch:
    def test_get_text(self, lang_file_es):
        # already added: add_paths('tests')
        assert _("tst_msg") == "tst_msg"
        assert _("tst_msg", language=lang_file_es) == "tst_msg"
        assert _("tst_msg", language='not_loaded_lang_code') == "tst_msg"

        assert _(test_message_texts[0], language=lang_file_es) == "t m " + test_message_texts[0][-1]
        assert _(test_message_texts[0], language='not_loaded_lang_code') == test_message_texts[0]

        assert _("tst_msg") == "tst_msg"
        assert _("tst_msg", language=lang_file_es) == "tst_msg"
        assert _("tst_msg", language='not_loaded_lang_code') == "tst_msg"

        assert _(test_message_texts[0]) == "t m " + test_message_texts[0][-1]
        assert _(test_message_texts[0], language=lang_file_es) == "t m " + test_message_texts[0][-1]
        assert _(test_message_texts[0], language='not_loaded_lang_code') == test_message_texts[0]

    def test_f_string_locals(self, lang_file_es):
        loc_var = 'loc_var_val'
        assert f_("{loc_var}", language=lang_file_es) == loc_var

        init_installed_languages('tests', reset=False)
        load_language_texts(lang_file_es)
        default_language(lang_file_es)
        loc_var = 'loc_var_val'
        assert f_("{loc_var}", language=lang_file_es) == loc_var

    def test_f_string_globals(self):
        assert f_("{glo_var}") == glo_var
        assert f_("{glo_var}", language=lang_file_es) == glo_var

        default_language(lang_file_es)
        assert f_("{glo_var}") == glo_var

    def test_f_string(self, lang_file_es):
        loc_var = 'loc_var_val'
        count = 6

        assert f_("{glo_var}{loc_var}{count}", count=count) == glo_var + loc_var + str(count)
        assert f_("{glo_var}{loc_var}{count}", count=count, language=lang_file_es) == glo_var + loc_var + str(count)

        default_language(lang_file_es)
        assert f_("{glo_var}{loc_var}{count}", count=count, language=lang_file_es) == glo_var + loc_var + str(count)

    def test_get_text_pluralized(self, lang_file_es):
        default_language(lang_file_es)
        assert _(test_message_texts[2]) == ""               # any
        assert _(test_message_texts[2], count=-1) == "n"    # negative
        assert _(test_message_texts[2], count=0) == "z"     # zero
        assert _(test_message_texts[2], count=1) == "o"     # one
        assert _(test_message_texts[2], count=2) == "m"     # many
        assert _(test_message_texts[2], count=3) == "m"
        assert _(test_message_texts[2], count=999) == "m"

    def test_default_encoding(self):
        old_enc = default_encoding()
        try:
            assert default_encoding('xx_XX')
            assert default_encoding('yy_YY') == 'xx_XX'
        finally:
            default_encoding(old_enc)
