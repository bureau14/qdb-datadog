# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import re
from setuptools import setup

# Should equal quasardb api version
version = "3.4.2"

setup(
    name = "qdb-datadog",
    packages = ["qdb_datadog"],
    entry_points = {
        "console_scripts": ['qdb-datadog = qdb_datadog.check:main']
        },
    version = version,
    description = "QuasarDB utility to integrate into Datadog as a service check.",

    install_requires=[
        "datadog >= 0.28.0",
        "quasardb >= 3.4.1"],

    )
