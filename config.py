import os
import json
import urllib.request

with urllib.request.urlopen(os.environ['PATH_TO_JSON']) as url:
    serviceAccount = json.loads(url.read().decode())

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    DB_CONFIG = {
        'apiKey': os.environ.get('API_KEY'),
        'authDomain': os.environ.get('APP_DOMAIN') + '.firebaseio.com',
        'databaseURL': 'https://' + os.environ.get('APP_DOMAIN') + '.firebaseio.com',
        'storageBucket': os.environ.get('APP_DOMAIN') + '.appspot.com',
        'serviceAccount': serviceAccount
    }

    EMPRESA = [('biomed', 'Biomed'),
               ('eletromed', 'Eletromed')]

    DEPARTAMENTOS = [('administrativo', 'Administrativo'),
                     ('comercial', 'Comercial'),
                     ('diretoria', 'Diretoria'),
                     ('estoque', 'Estoque'),
                     ('financeiro', 'Financeiro'),
                     ('regulamentação', 'Regulamentação'),
                     ('técnico', 'Técnico')]

    FORMA_PGTO = [('BOL', 'Boleto'),
                  ('CHQ', 'Cheque'),
                  ('DEP', 'Depósito'),
                  ('DIN', 'Dinheiro')]

    TIPO_SOLICITACAO = [('34', 'Adiantamento'),
                        ('04', 'Eventual'),
                        ('50', 'Previsão'),
                        ('13', 'Reembolso')]


    MAIL_SERVER = os.environ.get('MAIL_SERVER')

    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)

    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None

    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')

    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    MAIL_DOMAIN = os.environ.get('MAIL_DOMAIN')

    ADMIN = 'financeiro@' + MAIL_DOMAIN
