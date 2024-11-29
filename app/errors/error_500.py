from flask import render_template

from app import app


@app.errorhandler(500)
def internal_error(error):
    return render_template("errors/500.html"), 500
