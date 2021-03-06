#!/usr/bin/env python3

from flask import Flask

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"


app = Flask(__name__)

app.config["problems"] = {
    "Mathematics": {
        "XY Problem": "xy",
        "XZ Problem": "xz",
    },
    "Hydraulics": {
        "Pipes": "pipes",
        "Free Surface": "freesurface",
    },
}

# from hydraulicstrainer import main
# from hydraulicstrainer import demo

import hydraulicstrainer.main
import hydraulicstrainer.demo
import hydraulicstrainer.problems.xy

app.register_blueprint(demo.bp, url_prefix="/demo")
app.register_blueprint(problems.xy.bp, url_prefix="/problems/xy")
