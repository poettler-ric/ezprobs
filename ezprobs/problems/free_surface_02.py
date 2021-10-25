#!/usr/bin/env python3

from flask import Blueprint, Response, render_template, request, session
from ezprobs.hydraulics import (
    t_n_rect,
    t_crit_rect,
    l_transition_i_r_rect,
    depth_bernoulli_upstream,
    depth_bernoulli_downstream,
)

from ezprobs.problems import Parameter, Plot
from ezprobs.units import M, S, M3PS, GRAVITY, PERMILLE
from io import BytesIO

import numpy as np
import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt

__author__ = "Manuel Pirker"
__copyright__ = "Copyright (c) 2021 Manuel Pirkerr"
__license__ = "MIT"
__email__ = "manuel.pirker@tugraz.at"


bp = Blueprint("free_surface_02", __name__)


@bp.route("/", methods=["POST", "GET"])
def index():
    w = 30 * M
    q = 150 * M3PS
    i1 = 5 * PERMILLE
    i2 = 5 * PERMILLE

    ks1 = 10 * M ** (1 / 3) / S
    ks2 = 70 * M ** (1 / 3) / S

    if request.method == "POST":
        ks1 = int(request.form["ks1"]) * M ** (1 / 3) / S
        ks2 = int(request.form["ks2"]) * M ** (1 / 3) / S

    t_crit = t_crit_rect(q, w)
    t_n1 = t_n_rect(q, ks1, i1, w)
    t_n2 = t_n_rect(q, ks2, i2, w)

    parameters = [
        Parameter(
            "ks1",
            "ks1",
            10,
            120,
            10,
            ks1,
            unit="m^{1/3}/s",
            description="Strickler value section 1",
        ),
        Parameter(
            "ks2",
            "ks2",
            10,
            120,
            10,
            ks2,
            unit="m^{1/3}/s",
            description="Strickler value section 2",
        ),
    ]

    solution = {
        "i1": i1,
        "i2": i2,
        "w": w,
        "q": q,
        "t_crit": t_crit,
        "t_n1": t_n1,
        "ks_1": ks1,
        "t_n2": t_n2,
        "ks_2": ks2,
    }
    session["solution"] = solution

    plot = Plot("plot", alt="surface", caption="Water Surface")

    return render_template(
        "problems/free_surface_02.html",
        plot=plot,
        parameters=parameters,
        solution=solution,
    )


@bp.route("/plot")
def plot_function():
    ## load values  -----------------------------------------------------------
    iso1 = session["solution"]["i1"]
    iso2 = session["solution"]["i2"]
    w = session["solution"]["w"]
    q = session["solution"]["q"]
    t_crit = session["solution"]["t_crit"]
    t_n1 = session["solution"]["t_n1"]
    ks_1 = session["solution"]["ks_1"]
    t_n2 = session["solution"]["t_n2"]
    ks_2 = session["solution"]["ks_2"]

    ## begin calculation  -----------------------------------------------------
    # define plot size
    x_min = -400 * M
    x_max = 400 * M
    y_min = -2.5 * M
    y_max = 10 * M

    xlabels = []
    xticks = []

    # check flow regime
    isSubCritical = (t_n1 > t_crit, t_n2 > t_crit)
    if isSubCritical == (True, True):
        depthInKink = t_n2
        iterStartUp = t_n2
        iterStartDown = t_n2
        strFlow1 = "ö"
        strFlow2 = "ö"
        xlabels = ["$t_{N,1}$", "$t_{N,2}$"]
        xticks = [-l_transition_i_r_rect(q, ks_1, w, t_n1, depthInKink, iso1), 0]
    elif isSubCritical == (False, False):
        depthInKink = t_n1
        iterStartUp = 1
        iterStartDown = 1
        strFlow1 = "i"
        strFlow2 = "i"
        xlabels = ["$t_{N,1}$", "$t_{N,2}$"]
        xticks = [0, l_transition_i_r_rect(q, ks_2, w, depthInKink, t_n2, iso1)]
    elif isSubCritical == (True, False):
        depthInKink = t_crit
        iterStartUp = t_crit
        iterStartDown = 1
        strFlow1 = "ö"
        strFlow2 = "i"
        xlabels = ["$t_{N,1}$", "$t_{crit}$", "$t_{N,2}$"]
        xticks = [
            -l_transition_i_r_rect(q, ks_1, w, t_n1, depthInKink, iso1),
            0,
            l_transition_i_r_rect(q, ks_2, w, depthInKink, t_n2, iso1),
        ]
    elif isSubCritical == (False, True):
        # hydraulic jump (TO IMPLEMENT)
        depthInKink = t_crit
        headInKink = 0.5 * t_crit
        iterStartUp = 1
        iterStartDown = 1
        strFlow1 = "i"
        strFlow2 = "ö"

    if t_n1 == t_n2:
        xlabels = ["$t_{N,1} = t_{N,2}$"]
        xticks = [0]

    # upstream channel
    xx1 = np.linspace(-600, 0, 101) * M
    depth1 = depth_bernoulli_upstream(xx1, depthInKink, q, w, ks_1, iso1, iterStartUp)

    # downstream channel
    xx2 = np.linspace(0, 600, 101) * M
    depth2 = depth_bernoulli_downstream(
        xx2, depthInKink, q, w, ks_2, iso2, iterStartDown
    )

    xx = np.concatenate((xx1, xx2), axis=None)
    so = np.concatenate((xx1 * -iso1, xx2 * -iso2), axis=None)
    depth = np.concatenate((depth1, depth2), axis=None)
    head = (q / (w * depth)) ** 2 / (2 * GRAVITY)

    ## begin plotting sequence ------------------------------------------------
    fig, ax = plt.subplots()
    ax.fill_between(xx, so, so + depth, color="b", alpha=0.1)
    ax.fill_between(xx, so, so - 0.5, color="k", alpha=0.1)

    # TODO: find a better way to paint the sole before and after the switch with different strokes
    ax.plot(xx1, xx1 * -iso1, "k", lw=1.5)
    ax.plot(xx2, xx2 * -iso2, "k", lw=3)

    ax.plot(xx, so + t_crit, "k:", label="Krit. Wassertiefe", lw=1.5)
    ax.plot(xx, so + depth, "b", label="Wasserspiegel", lw=1.5)
    ax.plot(xx, so + depth + head, "r--", label="Energielinie", lw=1.5)

    plt.text(
        x_min / 2,
        y_max,
        strFlow1,
        ha="center",
        va="top",
        weight="bold",
        style="italic",
        size=14,
    )
    plt.text(
        x_max / 2,
        y_max,
        strFlow2,
        ha="center",
        va="top",
        weight="bold",
        style="italic",
        size=14,
    )

    ## figure style settings --------------------------------------------------
    # ax.grid()
    ax.set_frame_on(False)
    ax.xaxis.grid()
    ax.set_xlim(x_min, x_max)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)
    # ax.set_xlabel("Distance [m]")

    # ax.yaxis.grid()
    plt.axhline(y=-x_min * iso1 + depth[0] + head[0], color="k", lw=0.5, alpha=0.4)
    plt.axhline(y=-x_max * iso2, color="k", lw=0.5, alpha=0.4)
    ax.set_ylim(y_min, y_max)
    ax.set_yticks(
        [
            -x_max * iso2,
            -x_min * iso1,
            -x_min * iso1 + depth1[-1],
            -x_min * iso1 + depth1[-1] + head[0],
        ]
    )
    ax.set_yticklabels(["$B.H.$", "$Sohle$", "$W.L.$", "$E.H.$"])
    # ax.set_ylabel("Height [m]")

    secax = ax.secondary_yaxis("right")
    secax.set_yticks(
        [
            -x_max * iso2,
            -x_max * iso2 + depth2[-1],
            -x_max * iso2 + depth2[-1] + head[-1],
            -x_min * iso1 + depth1[-1] + head[0],
        ]
    )
    secax.set_yticklabels(["$B.H.$", "$W.L.$", "$E.L.$", "$E.H.$"])
    # secax.set_ylabel('Bernoulli [C]')

    secax.spines["right"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(loc="right")
    # ax.set_title("Water Surface")

    ## cashe figure -----------------------------------------------------------
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    return Response(buffer.getvalue(), mimetype="image/png")
