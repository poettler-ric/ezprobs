#!/usr/bin/env python3

from flask import Flask
from configparser import ConfigParser

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"


app = Flask(__name__)

config = ConfigParser()
config.read("config.ini")
app.secret_key = config["server"]["secret_key"]

app.config["problems"] = {
    "Hydraulics": {
        "Free Surface 01": "free_surface_01",
        "Pressure Pipe 01": "pressure_pipe_01",
    },
    "Mathematics": {
        "XY Problem": "xy",
    },
}
app.config["submit_on_change"] = config["application"].getboolean("submit_on_change")

import ezprobs.main
import ezprobs.demo
import ezprobs.problems.xy
import ezprobs.problems.free_surface_01
import ezprobs.problems.pressure_pipe_01

app.register_blueprint(demo.bp, url_prefix="/demo")
app.register_blueprint(problems.xy.bp, url_prefix="/problems/xy")
app.register_blueprint(
    problems.free_surface_01.bp, url_prefix="/problems/free_surface_01"
)
app.register_blueprint(
    problems.pressure_pipe_01.bp, url_prefix="/problems/pressure_pipe_01"
)
