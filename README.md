<!--
  THIS FILE IS EXCLUSIVELY MAINTAINED IN THE NAMESPACE ROOT PACKAGE. CHANGES HAVE TO BE DONE THERE.
-->
# i18n portion of ae namespace package

[![GitLabPipeline](https://img.shields.io/gitlab/pipeline/ae-group/ae_i18n/master?logo=python)](
    https://gitlab.com/ae-group/ae_i18n)
[![PyPIVersion](https://img.shields.io/pypi/v/ae_i18n)](
    https://pypi.org/project/ae-i18n/#history)

>The portions (modules and sub-packages) of the Application Environment for Python are within
the `ae` namespace and are providing helper methods and classes to develop
full-featured applications with Python.

[![Coverage](https://ae-group.gitlab.io/ae_i18n/coverage.svg)](
    https://ae-group.gitlab.io/ae_i18n/coverage/ae_i18n_py.html)
[![MyPyPrecision](https://ae-group.gitlab.io/ae_i18n/mypy.svg)](
    https://ae-group.gitlab.io/ae_i18n/lineprecision.txt)
[![PyLintScore](https://ae-group.gitlab.io/ae_i18n/pylint.svg)](
    https://ae-group.gitlab.io/ae_i18n/pylint.log)

[![PyPIImplementation](https://img.shields.io/pypi/implementation/ae_i18n)](
    https://pypi.org/project/ae-i18n/)
[![PyPIPyVersions](https://img.shields.io/pypi/pyversions/ae_i18n)](
    https://pypi.org/project/ae-i18n/)
[![PyPIWheel](https://img.shields.io/pypi/wheel/ae_i18n)](
    https://pypi.org/project/ae-i18n/)
[![PyPIFormat](https://img.shields.io/pypi/format/ae_i18n)](
    https://pypi.org/project/ae-i18n/)
[![PyPIStatus](https://img.shields.io/pypi/status/ae_i18n)](
    https://libraries.io/pypi/ae-i18n)
[![PyPIDownloads](https://img.shields.io/pypi/dm/ae_i18n)](
    https://pypi.org/project/ae-i18n/#files)


## installation


execute the following command to use the ae.i18n module in your
application. it will install ae.i18n into your python (virtual) environment:
 
```shell script
pip install ae-i18n
```

if you instead want to contribute to this portion then first fork
[the ae_i18n repository at GitLab](https://gitlab.com/ae-group/ae_i18n "ae.i18n code repository"),
then pull it to your machine and finally execute the following command in the root folder
of this repository (ae_i18n):

```shell script
pip install -e .[dev]
```

the last command will install this module portion into your virtual environment, along with
the tools you need to develop and run tests or to extend the portion documentation.
to contribute only to the unit tests or to the documentation of this portion replace
the setup extras key `dev` in the above command with `tests` or `docs` respectively.


## namespace portion documentation

more info on the features and usage of this portion are available at
[ReadTheDocs](https://ae.readthedocs.io/en/latest/_autosummary/ae.i18n.html#module-ae.i18n
"ae_i18n documentation").

<!-- common files version 0.2.77 deployed version 0.2.23 (with 0.2.77)
     to https://gitlab.com/ae-group as ae_i18n module as well as
     to https://ae-group.gitlab.io with CI check results as well as
     to https://pypi.org/project/ae-i18n as namespace portion ae-i18n.
-->
