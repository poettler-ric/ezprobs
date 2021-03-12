#!/usr/bin/env python3

from flask import Blueprint, Response, render_template, request, session
from hydraulicstrainer.geometry import area_circle
from hydraulicstrainer.hydraulics import pipe_loss, local_loss
from hydraulicstrainer.problems import Parameter
from hydraulicstrainer.units import M, CM, MM, M3PS, KINEMATIC_VISCOSITY, GRAVITY
from io import BytesIO
from math import sqrt
from scipy.optimize import fsolve

import numpy as np
import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"


bp = Blueprint("pressure_pipe_01", __name__)


@bp.route("/", methods=["POST", "GET"])
def index():
    parameter_d1 = Parameter(
        "d1",
        "d1",
        5,
        6,
        val_initial=5.5,
        val_step=0.1,
        unit="cm",
        description="Diameter of the pipe between I and II",
    )
    parameter_d2 = Parameter(
        "d2",
        "d2",
        5,
        6,
        val_initial=5.5,
        val_step=0.1,
        unit="cm",
        description="Diameter of the pipe between II and III",
    )
    parameter_d3 = Parameter(
        "d3",
        "d3",
        5,
        6,
        val_initial=5.5,
        val_step=0.1,
        unit="cm",
        description="Diameter of the pipe between III and VI",
    )
    parameters = [parameter_d1, parameter_d2, parameter_d3]
    solution = None

    ha = 260.0 * M
    hb = 197.2 * M
    h2 = 211.6 * M
    h3 = 223.5 * M
    h4 = 197.45 * M
    l1 = 280 * M
    l2 = 250 * M
    l3 = 250 * M
    k = 0.4 * MM
    nu_entry = 0.5

    q_initial = 3 * 10 ** -3 * M3PS

    if request.method == "POST":
        d1 = float(request.form["d1"])
        d2 = float(request.form["d2"])
        d3 = float(request.form["d3"])
        parameter_d1.val_initial = d1
        parameter_d2.val_initial = d2
        parameter_d3.val_initial = d3

        d1 *= CM
        d2 *= CM
        d3 *= CM
        a1 = area_circle(d1 / 2)
        a2 = area_circle(d2 / 2)
        a3 = area_circle(d3 / 2)

        q = fsolve(
            lambda q: h4
            - ha
            + (q / a3) ** 2 / (2 / GRAVITY)
            + local_loss(nu_entry, a1, q)
            + pipe_loss(l1, a1, k, d1, q)
            + pipe_loss(l2, a2, k, d2, q)
            + pipe_loss(l3, a3, k, d3, q),
            1,
        )[0]

        v1 = q / a1
        v2 = q / a2
        v3 = q / a3

        x2 = sqrt(l1 ** 2 - (ha - h2) ** 2)
        x3 = sqrt(l2 ** 2 - (h2 - h3) ** 2)
        x4 = sqrt(l3 ** 2 - (h3 - h4) ** 2)
        distances = np.array([0, x2, 0, x3, 0, x4])

        x = np.cumsum(distances)
        pipe = np.array([ha, h2, h2, h3, h3, h4])
        energy_horizon = np.full((len(x)), ha)
        losses = np.array(
            [
                local_loss(nu_entry, a1, q),
                pipe_loss(l1, a1, k, d1, q),
                0,
                pipe_loss(l2, a2, k, d2, q),
                0,
                pipe_loss(l3, a3, k, d3, q),
            ]
        )
        cum_losses = np.cumsum(losses)
        energy_line = energy_horizon - cum_losses
        kinetic_energy = np.array([v1, v1, v2, v2, v3, v3]) ** 2 / (2 * GRAVITY)
        pressure_line = energy_line - kinetic_energy

        solution = {
            "discharge": q,
            "x": x.tolist(),
            "pipe": pipe.tolist(),
            "energy_horizon": energy_horizon.tolist(),
            "energy_line": energy_line.tolist(),
            "pressure_line": pressure_line.tolist(),
        }
        session["solution"] = solution

    return render_template(
        "problems/pressure_pipe_01.html", parameters=parameters, solution=solution
    )


@bp.route("/plot")
def plot_function():
    x = session["solution"]["x"]
    pipe = session["solution"]["pipe"]
    energy_horizon = session["solution"]["energy_horizon"]
    energy_line = session["solution"]["energy_line"]
    pressure_line = session["solution"]["pressure_line"]

    fig, ax = plt.subplots()
    ax.plot(x, energy_horizon, label="Energy Horizon")
    ax.plot(x, energy_line, label="Energy Line")
    ax.plot(x, pressure_line, label="Pressure Line")
    ax.plot(x, pipe, label="Pipe")
    ax.grid()
    ax.legend()
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Height [m]")
    ax.set_title("Pressure- and Energylines")

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    return Response(buffer.getvalue(), mimetype="image/png")
