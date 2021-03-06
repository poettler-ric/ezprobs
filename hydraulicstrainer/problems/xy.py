#!/usr/bin/env python3

from flask import Blueprint, render_template
from hydraulicstrainer.problems import Parameter

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"


bp = Blueprint("xy", __name__)


@bp.route("/")
def index():
    parameters = [
        Parameter("a", "a", -5, 5, description="Inclination of the function"),
        Parameter(
            "b", "b", -5, 5, val_initial=-3, description="Offset of the function"
        ),
    ]
    return render_template("problems/xy.html", parameters=parameters)
