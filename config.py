import os 

class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']

    DB_CONFIG = {
        'apiKey': os.environ['API_KEY'],
        'authDomain': os.environ['APP_DOMAIN'] + '.firebaseio.com',
        'databaseURL': 'https://' + os.environ['APP_DOMAIN'] + '.firebaseio.com',
        'storageBucket': os.environ['APP_DOMAIN'] + '.appspot.com',
        'serviceAccount': os.environ['PATH_TO_JSON']
    }

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

    ADMIN = 'financeiro@biomedidas.com.br'
