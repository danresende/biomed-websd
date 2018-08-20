################################################################################
#                                                                              #
#                                  Web SD                                      #
#                                                                              #
################################################################################


#! /usr/bin/env python3
#-*- coding: latin-1 -*-

# Autor do app
__autor__ = 'Daniel Resende'


# Bibliotecas
################################################################################
import os
from flask import Flask
from config import Config
from flask_login import LoginManager


# Setup app
################################################################################
app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager()
login.init_app(app)


# Setup views
################################################################################
from app import errors
from app.views.despesas import Despesas
from app.views.users import Users
from app.views.login import Login

app.register_blueprint(Despesas, url_prefix='/despesas')
app.register_blueprint(Users, url_prefix='/users')
app.register_blueprint(Login)
