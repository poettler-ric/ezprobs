#!/usr/bin/env python3

from flask import Flask, render_template, url_for

__author__ = "Richard Pöttler"
__copyright__ = "Copyright (c) 2021 Richard Pöttler"
__license__ = "MIT"
__email__ = "richard.poettler@gmail.com"


app = Flask(__name__)
# url_for("static", file_name="js/bootstrap.bundle.min.js")


@app.route("/")
def index():
    return render_template("index.html")


def main():
    # not needed if deployed properly https://flask.palletsprojects.com/en/1.1.x/deploying/
    app.run()


if __name__ == "__main__":
    main()
