#!/usr/bin/env python3

from flask import Blueprint, render_template, request
from hydraulicstrainer.problems import Parameter

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"


bp = Blueprint("pressure_pipe_01", __name__)


@bp.route("/", methods=["POST", "GET"])
def index():
    parameters = []
    solution = None

    if request.method == "POST":
        solution = {}

    return render_template(
        "problems/pressure_pipe_01.html", parameters=parameters, solution=solution
    )
