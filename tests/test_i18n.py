""" ae.i18n unit tests. """
# noinspection PyProtectedMember
from ae.i18n import _, _ENCODING, _LANGUAGE, _LOADED_LANGUAGES


def test_default_locale():
    assert _ENCODING
    assert isinstance(_ENCODING, str)
    assert _LANGUAGE
    assert isinstance(_LANGUAGE, str)


def test_loaded_lang_type():
    assert isinstance(_LOADED_LANGUAGES, dict)


def test_func_def():
    assert callable(_)
