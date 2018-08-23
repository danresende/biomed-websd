import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, login_required, current_user
from werkzeug import secure_filename
from firebase import db, storage
from app.forms import DespesaForm

Despesas = Blueprint('despesas', __name__)


# Despesas
################################################################################

# Listar
@Despesas.route('/')
@login_required
def listar():
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    usuario = db.child('users').child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())

    data = {}
    try:
        data = db.child('despesas').get(current_user.idToken)
        data = dict(data.val())

    except Exception as e:
        data = {}

    despesas = []
    for k, v in data.items():
        despesa = v
        despesa['id'] = k
        despesa['data_criacao'] = datetime.strptime(despesa['data_criacao'], '%d/%m/%Y')
        despesa['data_pagamento'] = datetime.strptime(despesa['data_pagamento'], '%d/%m/%Y')
        despesa['data_ult_alt'] = datetime.strptime(despesa['data_ult_alt'], '%d/%m/%Y')
        despesas.append(despesa)

    despesas = sorted(despesas, key=lambda k: k['data_criacao'], reverse=True)

    depto_usuario = current_user.departamento

    if depto_usuario == 'financeiro':
        return render_template('despesas/listar.html', despesas=despesas, is_dba=usuario['DBA'])

    elif current_user.departamento == 'administrativo':
        despesas = [despesa for despesa in despesas
                        if (despesa['departamento'] == depto_usuario
                                or despesa['departamento'] == 'estoque'
                                    or despesa['criado_por'] == current_user.email)]
        return render_template('despesas/listar.html', despesas=despesas, is_dba=usuario['DBA'])

    else:
        despesas = [despesa for despesa in despesas
                        if (despesa['departamento'] == depto_usuario
                                or despesa['criado_por'] == current_user.email)]
        return render_template('despesas/listar.html', despesas=despesas, is_dba=usuario['DBA'])


# Criar
@Despesas.route('/criar', methods=['GET', 'POST'])
@login_required
def criar():
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    form = DespesaForm()
    if form.validate_on_submit():
        despesa = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'centro_custo': form.centro_custo.data,
            'criado_por': current_user.email,
            'modificado_por': current_user.email,
            'data_criacao': datetime.now().strftime('%d/%m/%Y'),
            'data_pagamento': form.data_pagamento.data.strftime('%d/%m/%Y'),
            'data_ult_alt': datetime.now().strftime('%d/%m/%Y'),
            'departamento': form.departamento.data,
            'descricao': form.descricao.data,
            'forma_pagamento': form.forma_pagamento.data,
            'observacao': form.observacao.data,
            'tipo_solicitacao': form.tipo_solicitacao.data,
            'valor_total': '{:.2f}'.format(form.valor_total.data),
            'status': '1',
            'tem_arquivo': False
        }

        if form.boleto.data is not None:
            despesa['tem_arquivo'] = True
            boleto = os.path.join('/tmp', secure_filename(form.boleto.data.filename))
            form.boleto.data.save(boleto)

        if despesa['departamento'] == 'diretoria':
            despesa['status'] = '2'

        try:
            if form.boleto.data is not None:
                response = storage.child('boletos/' + despesa['id']).put(boleto, current_user.idToken)
                despesa['download_token'] = response['downloadTokens']
            db.child('despesas').child(despesa['id']).update(despesa, current_user.idToken)
            return redirect(url_for('despesas.listar'))

        except Exception as e:
            mensagem = 'Não foi possível incluir essa despesa.'
            print(e)
            flash(mensagem)
            return redirect(url_for('despesas.criar'))

    return render_template('despesas/criar.html', form=form)

# Detalhar
@Despesas.route('/detalhar/<id>')
@login_required
def detalhar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    usuario = db.child('users').child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())

    despesa = db.child('despesas').child(id).get(current_user.idToken)
    despesa = dict(despesa.val())
    despesa['id'] = id

    if despesa['tem_arquivo']:
        try:
            arquivo_url = storage.child('boletos/' + id).get_url(despesa['download_token'])
        except Exception as e:
            print(e)
    else:
        arquivo_url = '#'

    return render_template('despesas/detalhar.html', despesa=despesa, usuario=usuario, download=arquivo_url)

# Editar
@Despesas.route('/editar/<id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    despesa = db.child('despesas').child(id).get(current_user.idToken)
    despesa = dict(despesa.val())
    despesa['id'] = id

    form = DespesaForm()
    if form.validate_on_submit():
        despesa = {
            'centro_custo': form.centro_custo.data,
            'modificado_por': current_user.email,
            'data_pagamento': form.data_pagamento.data.strftime('%d/%m/%Y'),
            'data_ult_alt': datetime.now().strftime('%d/%m/%Y'),
            'departamento': form.departamento.data,
            'descricao': form.descricao.data,
            'forma_pagamento': form.forma_pagamento.data,
            'observacao': form.observacao.data,
            'tipo_solicitacao': form.tipo_solicitacao.data,
            'valor_total': '{:.2f}'.format(form.valor_total.data),
            'status': '1'
        }

        if form.boleto.data is not None:
            despesa['tem_arquivo'] = True
            boleto = os.path.join('/tmp', secure_filename(form.boleto.data.filename))
            form.boleto.data.save(boleto)

        try:
            if form.boleto.data is not None:
                response = storage.child('boletos/' + id).put(boleto, current_user.idToken)
                despesa['download_token'] = response['downloadTokens']
            db.child('despesas').child(id).update(despesa, current_user.idToken)
            return redirect(url_for('despesas.listar'))

        except Exception as e:
            mensagem = 'Não foi possível atualizar essa despesa.'
            print(e)
            flash(mensagem)

        return redirect(url_for('despesas.detalhar', id=id))

    elif request.method == 'GET':
        form.centro_custo.data = despesa['centro_custo']
        form.data_pagamento.data = datetime.strptime(despesa['data_pagamento'], "%d/%m/%Y")
        form.departamento.data = despesa['departamento']
        form.descricao.data = despesa['descricao']
        form.forma_pagamento.data = despesa['forma_pagamento']
        form.observacao.data = despesa['observacao']
        form.tipo_solicitacao.data = despesa['tipo_solicitacao']
        form.valor_total.data = float(despesa['valor_total'])

    return render_template('despesas/editar.html', form=form, despesa=despesa)

# Deletar
@Despesas.route('/deletar/<id>')
@login_required
def deletar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token

    despesa = db.child('despesas').child(id).get(current_user.idToken)
    despesa = dict(despesa.val())

    try:
        if despesa['tem_arquivo']:
            storage.child('gs://').delete('boletos/' + id)
        db.child('despesas').child(id).remove(current_user.idToken)

    except Exception as e:
        mensagem = 'Não foi possível deletar a despesa'
        print(e)
        flash(mensagem)

    return redirect(url_for('despesas.listar'))

#Aprovação
@Despesas.route('/aprovar/<id>')
@login_required
def aprovacao(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token

    usuario = db.child('users').child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())

    despesa = db.child('despesas').child(id).get(current_user.idToken)
    despesa = dict(despesa.val())

    fin = (usuario['departamento'] == 'financeiro')

    resp_depto = (usuario['RD'] and usuario['departamento'] == despesa['departamento'])

    resp_fin = (usuario['RD'] and fin)

    if despesa['status'] == '1' and resp_depto:
        print(despesa['status'])
        despesa['status'] = '2'
        despesa['modificado_por'] = usuario['email']

    elif despesa['status'] == '2' and resp_fin:
        despesa['status'] = '3'
        despesa['modificado_por'] = usuario['email']

    elif despesa['status'] == '3' and fin:
        despesa['status'] = '4'
        despesa['modificado_por'] = usuario['email']

    try:
        db.child('despesas').child(id).update(despesa, current_user.idToken)

    except Exception as e:
        mensagem = 'Não foi possível atualizar essa despesa.'
        print(e)
        flash(mensagem)

    return redirect(url_for('despesas.listar'))

#Desaprovação
@Despesas.route('/deaprovar/<id>')
@login_required
def desaprovacao(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token

    usuario = db.child('users').child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())

    despesa = db.child('despesas').child(id).get(current_user.idToken)
    despesa = dict(despesa.val())

    fin = (usuario['departamento'] == 'financeiro')

    resp_depto = (usuario['RD'] and usuario['departamento'] == despesa['departamento'])

    resp_fin = (usuario['RD'] and fin)

    if despesa['status'] == '1' and resp_depto:
        print(despesa['status'])
        despesa['status'] = '5'
        despesa['modificado_por'] = usuario['email']

    elif despesa['status'] == '2' and resp_fin:
        despesa['status'] = '6'
        despesa['modificado_por'] = usuario['email']

    try:
        db.child('despesas').child(id).update(despesa, current_user.idToken)

    except Exception as e:
        mensagem = 'Não foi possível atualizar essa despesa.'
        print(e)
        flash(mensagem)

    return redirect(url_for('despesas.listar'))

#Cancelar
@Despesas.route('/cancelar/<id>')
@login_required
def cancelar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token

    usuario = db.child('users').child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())

    despesa = db.child('despesas').child(id).get(current_user.idToken)
    despesa = dict(despesa.val())

    pode_cancelar = (usuario['departamento'] == despesa['departamento']
                     or usuario['email'] == despesa['criado_por'])

    if pode_cancelar and despesa['status'] != '7':
        despesa['status'] = '7'
        despesa['modificado_por'] = usuario['email']

    try:
        db.child('despesas').child(id).update(despesa, current_user.idToken)

    except Exception as e:
        mensagem = 'Não foi possível atualizar essa despesa.'
        print(e)
        flash(mensagem)

    return redirect(url_for('despesas.listar'))

