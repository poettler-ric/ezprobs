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
    # define initial state of the parameters
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
    # save them into the list passed later to the template
    parameters = [parameter_a, parameter_b]
    # currently we don't have no calcluated solution, since we haven't been
    # passed any parameters
    solution = None

    # a POST request is used to pass parameters to the calculation
    if request.method == "POST":
        # extract and cast the parameters
        a = int(request.form["a"])
        b = int(request.form["b"])
        # set the initial values for the sliders
        parameter_a.val_initial = a
        parameter_b.val_initial = b
        # pack the values needed when generating the solution section
        solution = {"a": a, "b": b}
        # add the solution values to the session since the generation of the
        # graph is a separate request
        session["solution"] = solution

    return render_template("problems/xy.html", parameters=parameters, solution=solution)


@bp.route("/plot")
def plot_function():
    # extract the needd values from the session
    a = session["solution"]["a"]
    b = session["solution"]["b"]

    # generate the plot
    fig, ax = plt.subplots()
    x = [0, 10]
    y = [i * a + b for i in x]
    ax.plot(x, y)

    # save the plot to a buffer
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    # stream the buffer to the client
    return Response(buffer.getvalue(), mimetype="image/png")
