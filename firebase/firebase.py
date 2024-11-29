import pyrebase

from config import Config

db_config = Config.DB_CONFIG

firebase = pyrebase.initialize_app(db_config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()
