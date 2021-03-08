#!/usr/bin/env python3

from flask import Blueprint, Response, render_template, request, session
from hydraulicstrainer.problems import Parameter
from io import BytesIO

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"


bp = Blueprint("xy", __name__)


@bp.route("/", methods=["POST", "GET"])
def index():
    parameter_a = Parameter(
        "a",
        "a",
        -5,
        5,
        val_initial=0,
        description="Inclination of the function",
    )
    parameter_b = Parameter(
        "b", "b", -5, 5, val_initial=0, description="Offset of the function"
    )
    parameters = [parameter_a, parameter_b]
    solution = None

    if request.method == "POST":
        a = int(request.form["a"])
        b = int(request.form["b"])
        parameter_a.val_initial = a
        parameter_b.val_initial = b
        solution = {"a": a, "b": b}
        session["solution"] = solution

    return render_template("problems/xy.html", parameters=parameters, solution=solution)


@bp.route("/plot")
def plot_function():
    a = session["solution"]["a"]
    b = session["solution"]["b"]

    fig, ax = plt.subplots()
    x = [0, 10]
    y = [i * a + b for i in x]
    ax.plot(x, y)

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    return Response(buffer.getvalue(), mimetype="image/png")
