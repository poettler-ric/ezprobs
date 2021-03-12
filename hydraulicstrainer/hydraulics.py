#!/usr/bin/env python3

from hydraulicstrainer.units import GRAVITY, KINEMATIC_VISCOSITY
from math import log, sqrt
from scipy.optimize import fsolve

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"


def t_n_rect(discharge, strickler_roughness, inclination, width, start=1):
    """Calculates the normal depth of a rectangular channel."""

    A = lambda w, h: w * h
    U = lambda w, h: w + 2 * h
    R = lambda w, h: A(w, h) / U(w, h)

    return fsolve(
        lambda h: strickler_roughness
        * inclination ** (1 / 2)
        * R(width, h) ** (2 / 3)
        * A(width, h)
        - discharge,
        start,
    )[0]


def t_crit_rect(discharge, width):
    """Calculates the critical depth of a rectangular channel."""
    return (discharge / (width ** 2 * GRAVITY)) ** (1 / 3)


def lambda_turbulent_rough(k, d):
    """Calculates lambda for pipe loss for rough conditions"""
    return (1 / (2 * log(k / d / 3.71, 10))) ** 2


def lambda_turbulent_transition(k, d, re):
    """Calculates lambda for pipe loss for transition (rough->smoth) conditions"""
    return fsolve(
        lambda lam: (1 / (2 * log(2.51 / (re * sqrt(lam)) + k / d / 3.71, 10))) ** 2
        - lam,
        lambda_turbulent_rough(k, d),
    )[0]


def d_hyd(width, height):
    """Calculates hydraulic diameter for rectangular profiles"""
    return 4 * (width * height) / (2 * (width + height))


def reynolds_number(v, d):
    """Calculates the reynolds number"""
    return v * d / KINEMATIC_VISCOSITY


def pipe_loss(l, a, k, d, q):
    """Calculates the pipe loss for a given discharge"""
    v = q / a
    re = reynolds_number(v, d)
    lam = (
        lambda_turbulent_rough(k, d)
        if re * k / d > 1300
        else lambda_turbulent_transition(k, d, re)
    )
    return lam * l / d / (2 * GRAVITY * a ** 2) * q ** 2


def local_loss(nu, a, q):
    """Calculates a local loss for a given discharge"""
    return nu / (2 * GRAVITY * a ** 2) * q ** 2