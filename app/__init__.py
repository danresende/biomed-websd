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
import logging
from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_mail import Mail
from logging.handlers import SMTPHandler


# Setup app
################################################################################
app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager()
login.init_app(app)
mail = Mail(app)


# Setup views
################################################################################
from app import errors
from app.views.despesas import Despesas
from app.views.users import Users
from app.views.login import Login

app.register_blueprint(Despesas, url_prefix='/despesas')
app.register_blueprint(Users, url_prefix='/users')
app.register_blueprint(Login)

# Setup send error by email
################################################################################
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no_reply@' + app.config['MAIL_SERVER'],
            toaddrs = app.config['ADMIN'],
            subject = 'Erro em WebSD',
            credentials=auth,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

