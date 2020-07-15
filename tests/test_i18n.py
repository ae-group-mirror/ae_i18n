""" ae.i18n unit tests. """
import os

import pytest

# noinspection PyProtectedMember
from ae.i18n import (
    DOMAIN_LANGUAGES, ENCODING, LANGUAGE, LOADED_LANGUAGES, MSG_FILE_SUFFIX,
    _, f_, add_domain, load_language_texts
)


test_message_texts = ("test message 1", "test message 2", "pluralize-able")
pluralize_keys = ('zero', 'one', 'many', 'negative', 'any')


@pytest.fixture
def lang_file_es():
    """ provide test message file for the language es_ES. """
    lang = 'es_ES'
    fp = os.path.join('tests', lang)
    os.mkdir(fp)
    fn = os.path.join(fp, MSG_FILE_SUFFIX)
    with open(fn, 'w') as file_handle:
        file_handle.write('{\n')
        file_handle.write(',\n'.join(['"' + t + '": "t m ' + t[-1] + '"' for t in test_message_texts[:2]]))
        file_handle.write(',\n"' + test_message_texts[2] + '": {')
        file_handle.write(', '.join(['"' + t + '": "' + t[0] + '"' for t in pluralize_keys]) + '}\n')
        file_handle.write('}\n')
    yield lang
    if os.path.exists(fn):      # check if file exists because some exception/error-check tests need to delete the file
        os.remove(fn)
    if os.path.exists(fp):
        os.rmdir(fp)


glo_var = 'glo_var_val'


class TestDeclarations:
    def test_default_locale(self):
        assert ENCODING
        assert isinstance(ENCODING, str)
        assert LANGUAGE
        assert isinstance(LANGUAGE, str)

    def test_loaded_lang_type(self):
        assert isinstance(LOADED_LANGUAGES, dict)

    def test_func_aliases(self):
        assert callable(_)
        assert callable(f_)


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
    def test_load_language_texts_str(self, lang_file_es):
        assert not DOMAIN_LANGUAGES
        load_language_texts(lang_file_es, file_paths=('tests',))

        assert lang_file_es in LOADED_LANGUAGES
        assert isinstance(LOADED_LANGUAGES[lang_file_es], dict)
        assert LOADED_LANGUAGES[lang_file_es][test_message_texts[0]] == 't m 1'
        assert LOADED_LANGUAGES[lang_file_es][test_message_texts[1]] == 't m 2'

    def test_load_languages_texts_plural(self, lang_file_es):
        load_language_texts(lang_file_es, file_paths=('tests',))    # test re-load because already loaded by prev tests

        assert isinstance(LOADED_LANGUAGES[lang_file_es][test_message_texts[2]], dict)
        for t in pluralize_keys:
            assert LOADED_LANGUAGES[lang_file_es][test_message_texts[2]][t] == t[0]


class TestWithLoadedTranslations:
    def test_get_text(self, lang_file_es):
        load_language_texts(lang_file_es, file_paths=('tests',))    # load for all other test methods of this class

        assert _("tst_msg") == "tst_msg"
        assert _(test_message_texts[0]) == "t m " + test_message_texts[0][-1]
        assert _(test_message_texts[1]) == "t m " + test_message_texts[1][-1]

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'
        assert f_("{loc_var}") == loc_var

    def test_f_string_globals(self):
        assert f_("{glo_var}") == glo_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        assert f_("{glo_var}{loc_var}") == glo_var + loc_var

    def test_get_text_pluralized(self):
        assert _(test_message_texts[2]) == 'a'    # any


class TestCount:
    def test_get_text(self):
        assert _("tst_msg", count=3) == "tst_msg"

    def test_f_string_locals(self):
        loc_var = 'loc_var_val'
        assert f_("{loc_var}", count=4) == loc_var

    def test_f_string_globals(self):
        assert f_("{glo_var}", count=5) == glo_var

    def test_f_string(self):
        loc_var = 'loc_var_val'
        count = 6
        assert f_("{glo_var}{loc_var}{count}", count=count) == glo_var + loc_var + str(count)

    def test_get_text_pluralized(self, lang_file_es):
        assert _(test_message_texts[2], count=-1) == 'n'    # negative
        assert _(test_message_texts[2], count=0) == "z"     # zero
        assert _(test_message_texts[2], count=1) == "o"     # one
        assert _(test_message_texts[2], count=2) == "m"     # many
        assert _(test_message_texts[2], count=3) == "m"
        assert _(test_message_texts[2], count=999) == "m"

    def test_get_text_pluralized_without_count(self, lang_file_es):
        assert _(test_message_texts[2]) == "a"      # any

    def test_f_string_pluralized_without_count(self, lang_file_es):
        assert f_(test_message_texts[2]) == "a"     # any


class TestDomain:
    def test_add_domain(self):
        try:
            add_domain('tst', 'de_DE')
            assert DOMAIN_LANGUAGES['tst'] == 'de_DE'

            domain_count = len(DOMAIN_LANGUAGES)
            add_domain('tst', 'es_ES')
            assert DOMAIN_LANGUAGES['tst'] == 'es_ES'
            assert len(DOMAIN_LANGUAGES) == domain_count
        finally:
            DOMAIN_LANGUAGES.pop('tst')

    def test_get_text(self, lang_file_es):
        domain = 'tst_es_domain'
        add_domain(domain, lang_file_es)
        try:
            load_language_texts(lang_file_es, domain=domain, file_paths=('tests',))
            assert _("tst_msg", domain=domain) == "tst_msg"
            assert _(test_message_texts[0], domain=domain) == "t m " + test_message_texts[0][-1]
        finally:
            DOMAIN_LANGUAGES.pop(domain)

    def test_f_string_locals(self, lang_file_es):
        domain = 'tst_es_domain'
        add_domain(domain, lang_file_es)
        try:
            loc_var = 'loc_var_val'
            assert f_("{loc_var}", domain=domain) == loc_var
        finally:
            DOMAIN_LANGUAGES.pop(domain)

    def test_f_string_globals(self):
        domain = 'tst_es_domain'
        add_domain(domain, lang_file_es)
        try:
            assert f_("{glo_var}", domain=domain) == glo_var
        finally:
            DOMAIN_LANGUAGES.pop(domain)

    def test_f_string(self, lang_file_es):
        domain = 'tst_es_domain'
        add_domain(domain, lang_file_es)
        try:
            loc_var = 'loc_var_val'
            count = 6
            assert f_("{glo_var}{loc_var}{count}", count=count, domain=domain) == glo_var + loc_var + str(count)
        finally:
            DOMAIN_LANGUAGES.pop(domain)

    def test_get_text_pluralized(self, lang_file_es):
        domain = 'tst_es_domain'
        try:
            load_language_texts(lang_file_es, domain=domain, file_paths=('tests',))  # reload with domain
            assert _(test_message_texts[2], domain=domain) == "a"  # any
            assert _(test_message_texts[2], count=-1, domain=domain) == "n"  # negative
            assert _(test_message_texts[2], count=0, domain=domain) == "z"  # zero
            assert _(test_message_texts[2], count=1, domain=domain) == "o"  # one
            assert _(test_message_texts[2], count=2, domain=domain) == "m"  # many
            assert _(test_message_texts[2], count=3, domain=domain) == "m"
            assert _(test_message_texts[2], count=999, domain=domain) == "m"
        finally:
            DOMAIN_LANGUAGES.pop(domain)
