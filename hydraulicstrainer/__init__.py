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
    "Mathematics": {
        "XY Problem": "xy",
    },
}

import hydraulicstrainer.main
import hydraulicstrainer.demo
import hydraulicstrainer.problems.xy

app.register_blueprint(demo.bp, url_prefix="/demo")
app.register_blueprint(problems.xy.bp, url_prefix="/problems/xy")
