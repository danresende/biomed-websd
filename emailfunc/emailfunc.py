from app import app, mail
from config import Config
from firebase import db
from flask import render_template
from flask_mail import Message
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(despesa, current_user, motivo=None):

    MAIL_DOMAIN = Config.MAIL_DOMAIN
    ADMIN = Config.ADMIN

    sender = current_user.email + '@' + MAIL_DOMAIN

    departamento = 'administrativo' if despesa['departamento'] == 'estoque' else despesa['departamento']

    recipients = dict(db.child('users').get(current_user.idToken).val())
    recipients = [v['email'] + '@' + MAIL_DOMAIN
                    for k, v in recipients.items()
                    if v['RD'] and v['departamento'] == departamento]

    if despesa['status'] == '1':
        subject = '[WebSD] Uma nova solicitação foi criada'
        template = 'status1'

    elif despesa['status'] == '2':
        subject = '[WebSD] Uma nova solicitação foi aprovada pelo Responsável do Departamento'
        recipients = [ADMIN, despesa['criado_por'] + '@' + MAIL_DOMAIN]
        template = 'status2'

    elif despesa['status'] == '3':
        subject = '[WebSD] Há uma nova solicitação para ser incluida no sistema'
        recipients = [ADMIN]
        template = 'status3'

    elif despesa['status'] == '4':
        sender = ADMIN
        recipients += [despesa['criado_por'] + '@' + MAIL_DOMAIN]
        template = 'status4'

    elif despesa['status'] == '5':
        subject = '[WebSD] Sua solicitação de despesa NÃO foi aprovada pelo Responsável do Departamento'
        recipients = [despesa['criado_por'] + '@' + MAIL_DOMAIN]
        template = 'status5'

    elif despesa['status'] == '6':
        sender = ADMIN
        recipients += [despesa['criado_por'] + '@' + MAIL_DOMAIN]
        subject = '[WebSD] Sua solicitação de despesa NÃO foi aprovada pelo Depto Financeiro'
        template = 'status6'

    elif despesa['status'] == '7':
        recipients += [ADMIN]
        subject = '[WebSD] A despesa ' + despesa['id'] + ' foi cancelada pelo usuário'
        template = 'status7'

    else:
        return None

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = render_template('mail/' + template + '.txt', despesa=despesa, motivo=motivo)
    msg.html = render_template('mail/' + template + '.html', despesa=despesa, motivo=motivo)
    Thread(target=send_async_email, args=(app, msg)).start()
