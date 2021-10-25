#!/usr/bin/env python3

from flask import Blueprint, Response, render_template, request, session
from ezprobs.hydraulics import (
    t_n_rect,
    t_crit_rect,
    l_transition_i_r_rect,
    depth_bernoulli_upstream,
    depth_bernoulli_downstream,
    froude,
)

from ezprobs.problems import Parameter, Plot
from ezprobs.units import M, S, M3PS, GRAVITY, PERMILLE
from io import BytesIO
from math import sqrt

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
    depth = np.empty(0)
    so = np.empty(0)

    # check flow regime
    isSubCritical = (t_n1 > t_crit, t_n2 > t_crit)
    if isSubCritical == (True, True):
        strFlow1 = "ö"
        strFlow2 = "ö"
        xlabels = ["$t_{N,1}$", "$t_{N,2}$"]
        xticks = [-l_transition_i_r_rect(q, ks_1, w, t_n1, t_n2, iso1), 0]

        # upstream channel
        xx1 = np.linspace(-600, 0, 101) * M
        # downstream channel
        xx2 = np.linspace(0, 600, 101) * M

        xx = np.concatenate((xx1, xx2), axis=None)
        so = np.concatenate((xx1 * -iso1, xx2 * -iso2), axis=None)
        depth = np.concatenate(
            (
                depth_bernoulli_upstream(xx1, t_n2, q, w, ks_1, iso1, t_n2),
                depth_bernoulli_downstream(xx2, t_n2, q, w, ks_2, iso2, t_n2),
            ),
            axis=None,
        )
    elif isSubCritical == (False, False):
        strFlow1 = "i"
        strFlow2 = "i"
        xlabels = ["$t_{N,1}$", "$t_{N,2}$"]
        xticks = [0, l_transition_i_r_rect(q, ks_2, w, t_n1, t_n2, iso1)]

        # upstream channel
        xx1 = np.linspace(-600, 0, 101) * M
        # downstream channel
        xx2 = np.linspace(0, 600, 101) * M

        xx = np.concatenate((xx1, xx2), axis=None)
        so = np.concatenate((xx1 * -iso1, xx2 * -iso2), axis=None)
        depth = np.concatenate(
            (
                depth_bernoulli_upstream(xx1, t_n1, q, w, ks_1, iso1, 1),
                depth_bernoulli_downstream(xx2, t_n1, q, w, ks_2, iso2, 1),
            ),
            axis=None,
        )
    elif isSubCritical == (True, False):
        strFlow1 = "ö"
        strFlow2 = "i"
        xlabels = ["$t_{N,1}$", "$t_{crit}$", "$t_{N,2}$"]
        xticks = [
            -l_transition_i_r_rect(q, ks_1, w, t_n1, t_crit, iso1),
            0,
            l_transition_i_r_rect(q, ks_2, w, t_crit, t_n2, iso1),
        ]

        # upstream channel
        xx1 = np.linspace(-600, 0, 101) * M
        # downstream channel
        xx2 = np.linspace(0, 600, 101) * M

        xx = np.concatenate((xx1, xx2), axis=None)
        so = np.concatenate((xx1 * -iso1, xx2 * -iso2), axis=None)
        depth = np.concatenate(
            (
                depth_bernoulli_upstream(xx1, t_crit, q, w, ks_1, iso1, t_crit),
                depth_bernoulli_downstream(xx2, t_crit, q, w, ks_2, iso2, 1),
            ),
            axis=None,
        )
    elif isSubCritical == (False, True):
        v_n1 = q / (w * t_n1)
        head_1 = v_n1 ** 2 / (2 * GRAVITY)
        v_n2 = q / (w * t_n2)
        head_2 = v_n2 ** 2 / (2 * GRAVITY)

        strFlow1 = "i"
        strFlow2 = "ö"

        if (t_n1 + head_1) > (t_n2 + head_2):
            t2 = t_n2
            v2 = v_n2
            t1 = 1 / 2 * t2 * (sqrt(1 + 8 * froude(v2, t2) ** 2) - 1)
            v1 = q / (w * t1)
            lw = 3 * t1 * (sqrt(1 + 8 * froude(v1, t1) ** 2) - 3)
            lv = l_transition_i_r_rect(q, ks_2, w, t_n1, t1, iso2)

            xlabels = ["$t_{N,1}$", "$t_1$", "$t_{N,2} = t_2$"]
            xticks = [0, lv, lv + lw]

            # upstream channel
            xx1 = np.linspace(-600, 0, 101) * M
            # downstream channel
            xx2 = np.linspace(0, lv + lw, 100) * M
            xx3 = np.linspace(lv + lw, 600, 100) * M

            xx = np.concatenate((xx1, xx2, xx3), axis=None)
            so = np.concatenate((xx1 * -iso1, xx2 * -iso2, xx3 * -iso2), axis=None)
            depth = np.concatenate(
                (
                    depth_bernoulli_upstream(xx1, t_n1, q, w, ks_1, iso1, t_n1),
                    depth_bernoulli_downstream(xx2, t_n1, q, w, ks_2, iso2, t_n1),
                    depth_bernoulli_downstream(xx3, t_n2, q, w, ks_2, iso2, t_n2),
                ),
                axis=None,
            )
        else:
            t1 = t_n1
            v1 = v_n1
            t2 = 1 / 2 * t1 * (sqrt(1 + 8 * froude(v1, t1) ** 2) - 1)
            v2 = q / (w * t2)
            lw = 3 * t1 * (sqrt(1 + 8 * froude(v1, t1) ** 2) - 3)
            lv = l_transition_i_r_rect(q, ks_1, w, t2, t_n2, iso1)

            xlabels = ["$t_{N,1} = t_1$", "$t_2$", "$t_{N,2}$"]
            xticks = [-(lw + lv), -lv, 0]

            # upstream channel
            xx1 = np.linspace(-600, -(lw + lv), 101) * M
            xx2 = np.linspace(-(lw + lv), -lv, 101) * M
            xx3 = np.linspace(-lv, 0, 101) * M
            # downstream channel
            xx4 = np.linspace(0, 600, 101) * M

            xx = np.concatenate((xx1, xx2, xx3, xx4), axis=None)
            so = np.concatenate(
                (xx1 * -iso1, xx2 * -iso1, xx3 * -iso1, xx4 * -iso2), axis=None
            )
            depth = np.concatenate(
                (
                    depth_bernoulli_upstream(xx1, t_n1, q, w, ks_1, iso1, t_n1),
                    depth_bernoulli_downstream(xx2, t_n1, q, w, ks_2, iso1, t_n1),
                    depth_bernoulli_upstream(xx3, t_n2, q, w, ks_1, iso1, t_n2),
                    depth_bernoulli_downstream(xx4, t_n2, q, w, ks_2, iso2, t_n2),
                ),
                axis=None,
            )

    if t_n1 == t_n2:
        xlabels = ["$t_{N,1} = t_{N,2}$"]
        xticks = [0]

    head = (q / (w * depth)) ** 2 / (2 * GRAVITY)

    ## begin plotting sequence ------------------------------------------------
    fig, ax = plt.subplots()
    ax.fill_between(xx, so, so + depth, color="b", alpha=0.1)
    ax.fill_between(xx, so, so - 0.5, color="k", alpha=0.1)

    # plot the sole
    ax.plot([x_min, 0], [x_min * -iso1, 0], "k", lw=1.5)
    ax.plot([0, x_max], [0, x_max * -iso2], "k", lw=3)

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
            -x_min * iso1 + depth[0],
            -x_min * iso1 + depth[0] + head[0],
        ]
    )
    ax.set_yticklabels(["$B.H.$", "$Sohle$", "$W.L.$", "$E.H.$"])
    # ax.set_ylabel("Height [m]")

    secax = ax.secondary_yaxis("right")
    secax.set_yticks(
        [
            -x_max * iso2,
            -x_max * iso2 + depth[-1],
            -x_max * iso2 + depth[-1] + head[-1],
            -x_min * iso1 + depth[0] + head[0],
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
