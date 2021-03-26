#!/usr/bin/env python3

from flask import Blueprint, Response, render_template, request, session
from ezprobs.hydraulics import t_n_rect, t_crit_rect, ruehlmann_rect
from ezprobs.problems import Parameter
from ezprobs.units import M, S, M3PS, GRAVITY
from io import BytesIO

import numpy as np
import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"


bp = Blueprint("free_surface_01", __name__)


@bp.route("/", methods=["POST", "GET"])
def index():
    w = 2.5 * M
    q = 20 * M3PS
    i = 0.013

    ks1 = 25 * M ** (1 / 3) / S
    ks2 = 80 * M ** (1 / 3) / S
    ks3 = 32 * M ** (1 / 3) / S

    if request.method == "POST":
        ks1 = int(request.form["ks1"]) * M ** (1 / 3) / S
        ks2 = int(request.form["ks2"]) * M ** (1 / 3) / S
        ks3 = int(request.form["ks3"]) * M ** (1 / 3) / S

    t_crit = t_crit_rect(q, w)
    t_n1 = t_n_rect(q, ks1, i, w)
    t_n2 = t_n_rect(q, ks2, i, w)
    t_n3 = t_n_rect(q, ks3, i, w)

    parameters = [
        Parameter(
            "ks1",
            "ks1",
            20,
            30,
            1,
            ks1,
            unit="m^{1/3}/s",
            description="Strickler value section 1",
        ),
        Parameter(
            "ks2",
            "ks2",
            75,
            85,
            1,
            ks2,
            unit="m^{1/3}/s",
            description="Strickler value section 2",
        ),
        Parameter(
            "ks3",
            "ks3",
            25,
            35,
            1,
            ks3,
            unit="m^{1/3}/s",
            description="Strickler value section 3",
        ),
    ]

    l_au = ruehlmann_rect(0.99 * t_n1, t_n1, t_n2, t_crit, i)
    l_bu = ruehlmann_rect(1.01 * t_n2, t_n2, t_n3, t_crit, i)

    solution = {
        "i": i,
        "w": w,
        "q": q,
        "t_crit": t_crit,
        "t_n1": t_n1,
        "t_n2": t_n2,
        "t_n3": t_n3,
        "l_au": l_au,
        "l_bu": l_bu,
    }
    session["solution"] = solution

    return render_template(
        "problems/free_surface_01.html", parameters=parameters, solution=solution
    )


@bp.route("/plot")
def plot_function():
    i = session["solution"]["i"]
    w = session["solution"]["w"]
    q = session["solution"]["q"]
    t_crit = session["solution"]["t_crit"]
    t_n1 = session["solution"]["t_n1"]
    t_n2 = session["solution"]["t_n2"]
    t_n3 = session["solution"]["t_n3"]
    l_au = session["solution"]["l_au"]
    l_bu = session["solution"]["l_bu"]

    x_a = 400 * M
    x_b = 800 * M
    x_end = 900 * M
    h_start = x_end * i

    xsole = [0, x_end]
    ysole = [h_start, 0]

    # assemble crit line
    tcr = np.array([t_crit, t_crit])
    xcr = np.array([0, x_end])

    ycr = (h_start - (xcr * i)) + tcr

    # assemble normal line
    tn = [t_n1, t_n1, t_n2, t_n2, t_n3, t_n3]
    xn = [0, x_a, x_a, x_b, x_b, x_end]

    xn = np.array(xn)
    tn = np.array(tn)
    yn = (h_start - (xn * i)) + tn

    # assemble ruehlmann line
    xr = [0, x_a - l_au]
    tr = [t_n1, t_n1]

    ys = np.linspace(t_n1, t_n2, 22)
    for y in ys[1:-1]:
        xr.append(x_a - ruehlmann_rect(y, t_n1, t_n2, t_crit, i))
        tr.append(y)
    xr.append(x_a)
    tr.append(t_n2)
    xr.append(x_b - l_bu)
    tr.append(t_n2)

    ys = np.linspace(t_n2, t_n3, 22)
    for y in ys[1:-1]:
        xr.append(x_b - ruehlmann_rect(y, t_n2, t_n3, t_crit, i))
        tr.append(y)
    xr.append(x_b)
    tr.append(t_n3)
    xr.append(x_end)
    tr.append(t_n3)

    xr = np.array(xr)
    tr = np.array(tr)
    yr = (h_start - (xr * i)) + tr

    fig, ax = plt.subplots()
    ax.plot(xn, yn, label="Normal Depth", color="green")

    ax.plot(xr, yr, label="Ruehlmann", color="blue")

    ax.plot(xcr, ycr, label="Critical Depth", color="red")
    ax.plot(xsole, ysole, label="Ground", color="black")

    ax.grid()
    ax.legend()
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Height [m]")
    ax.set_title("Water Surfaces")

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    return Response(buffer.getvalue(), mimetype="image/png")
