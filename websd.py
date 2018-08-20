from app import app 
from app.modules import User
from firebase import auth, db


@app.shell_context_processor
def make_shell_context():
    return {'auth': auth, 'db': db, 'User': User}
