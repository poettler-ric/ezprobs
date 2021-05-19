#!/usr/bin/env python3

from flask import Blueprint, render_template

bp = Blueprint("test", __name__)

@bp.route("/", methods=["POST", "GET"])
def index():
    a = 5

    from flask import request
    if request.method == 'POST':
        a = int(request.form['a'])

    from ezprobs.problems import Parameter
    param_a = Parameter(
        "a",
        "a_display",
        0,
        10,
        1,
        a,
        unit="kN",
        description="some description",)

    result = a + 5

    s = {"a": a, "result": result}

    from flask import session
    session["solution"] = s

    from ezprobs.problems import Plot
    p = Plot("plot", "plot alt", "plot description")

    return render_template("problems/test.html",
                           parameters=[param_a],
                           solution=s,
                           plot=p)


@bp.route("/plot")
def plot_function():
    from flask import session
    a = session["solution"]["a"]

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    x = [0, 10]
    y = [i * a for i in x]
    ax.plot(x, y)

    from io import BytesIO
    buffer = BytesIO()
    fig.savefig(buffer, format="png")

    from flask import Response
    return Response(buffer.getvalue(), mimetype="image/png")

@bp.route("/svg")
def display_svg():
    from flask import session
    a = session["solution"]["a"]

    from svgwrite import Drawing
    dwg = Drawing()
    dwg.add(dwg.circle(center=(a, a), r=a))

    from flask import Response
    return Response(dwg.tostring(), mimetype="image/svg+xml")
