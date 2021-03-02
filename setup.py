#!/usr/bin/env python3

from distutils.core import setup
from glob import glob
import py2exe

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"

setup(
    console=["hydraulicstrainer.py"],
    data_files=[
        ("templates", glob("templates/*")),
        ("static/css", glob("static/css/*")),
        ("static/js", glob("static/js/*")),
    ],
    options={"py2exe": {"includes": ["jinja2.ext"]}},
)
