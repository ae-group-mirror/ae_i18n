# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.project_tpls v0.3.77
""" setup of ae namespace package portion i18n: internationalization / localization helpers. """
import sys
# noinspection PyUnresolvedReferences
import pathlib
# noinspection PyUnresolvedReferences
import setuptools


print("SetUp " + __name__ + ": " + sys.executable + str(sys.argv) + f" {sys.path=}")

setup_kwargs = {
    'author': 'AndiEcker',
    'author_email': 'aecker2@gmail.com',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed',
    ],
    'description': 'ae namespace package portion i18n: internationalization / localization helpers',
    'extras_require': {
        'dev': [
            'aedev_project_tpls',
            'ae_ae',
            'anybadge',
            'flake8',
            'mypy',
            'pylint',
            'pytest',
            'pytest-cov',
            'typing',
            'types-setuptools',
        ],
        'docs': [],
        'tests': [
            'anybadge',
            'flake8',
            'mypy',
            'pylint',
            'pytest',
            'pytest-cov',
            'typing',
            'types-setuptools',
        ],
    },
    'install_requires': [
        'ae_base',
        'ae_system',
        'ae_files',
        'ae_paths',
        'ae_dynamicod',
    ],
    'keywords': [
        'configuration',
        'development',
        'environment',
        'productivity',
    ],
    'license': 'GPL-3.0-or-later',
    'long_description': (pathlib.Path(__file__).parent / 'README.md').read_text(encoding='utf-8'),
    'long_description_content_type': 'text/markdown',
    'name': 'ae_i18n',
    'package_data': {
        '': [
            'loc/es/Msg.txt',
            'loc/de/Msg.txt',
            'loc/en/Msg.txt',
        ],
    },
    'packages': [
        'ae.i18n',
        'ae.i18n.loc',
        'ae.i18n.loc.es',
        'ae.i18n.loc.de',
        'ae.i18n.loc.en',
    ],
    'project_urls': {
        'Bug Tracker': 'https://gitlab.com/ae-group/ae_i18n/-/issues',
        'Documentation': 'https://ae.readthedocs.io/en/latest/_autosummary/ae.i18n.html',
        'Repository': 'https://gitlab.com/ae-group/ae_i18n',
        'Source': 'https://ae.readthedocs.io/en/latest/_modules/ae/i18n.html',
    },
    'python_requires': '>=3.12',
    'url': 'https://gitlab.com/ae-group/ae_i18n',
    'version': '0.3.35',
    'zip_safe': False,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    pass
