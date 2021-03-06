#!/usr/bin/env python3

from flask import Blueprint, render_template

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"


bp = Blueprint("xy", __name__)


@bp.route("/")
def index():
    return render_template("problems/xy.html")
