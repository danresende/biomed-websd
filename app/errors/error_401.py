from flask import redirect, url_for
from app import app

@app.errorhandler(401)
def unauthorized_error(error):
    return redirect(url_for('login.login'))
