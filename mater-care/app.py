from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Paciente, Medicamento, Prescricao, PlanoAlta
from datetime import datetime
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'intercare-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def verificar_alerta(paciente, medicamento):
    """
    Lógica central do MVP: verifica se o medicamento conflita com alergias do paciente.
    Retorna (status, mensagem).
    """

    if not paciente.alergias:
        return 'OK', 'Paciente sem alergias registradas. Medicamento liberado.'

    alergias = paciente.alergias.lower()
    nome_med = medicamento.nome.lower()
    substancia = (medicamento.substancia_ativa or '').lower()

    # Verifica se alguma palavra do medicamento ou substância está nas alergias
    for termo in [nome_med, substancia]:
        for palavra in termo.split():
            if len(palavra) > 3 and palavra in alergias:
                return 'ALERTA', f'⚠️ ATENÇÃO: Paciente tem alergia registrada a "{paciente.alergias}". Medicamento "{medicamento.nome}" pode causar reação adversa!'

    return 'OK', f'✓ Medicamento "{medicamento.nome}" liberado para prescrição.'

# -------------------- ROTAS --------------------

@app.route('/')
def index():
    """Dashboard principal com visão geral."""
    total_pacientes = Paciente.query.count()
    total_medicamentos = Medicamento.query.count()
    total_prescricoes = Prescricao.query.count()
    total_alertas = Prescricao.query.filter_by(status='ALERTA').count()
    total_planos = PlanoAlta.query.count()

    # Últimas prescrições
    ultimas_prescricoes = Prescricao.query.order_by(Prescricao.data.desc()).limit(5).all()

    return render_template(
        'index.html',
        total_pacientes=total_pacientes,
        total_medicamentos=total_medicamentos,
        total_prescricoes=total_prescricoes,
        total_alertas=total_alertas,
        total_planos=total_planos,
        ultimas_prescricoes=ultimas_prescricoes
    )


@app.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        alergias = request.form['alergias']

        data_nasc_obj = None
        if data_nascimento:
            try:
                data_nasc_obj = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
            except ValueError:
                data_nasc_obj = None

        novo_paciente = Paciente(nome=nome, data_nascimento=data_nasc_obj, alergias=alergias)
        db.session.add(novo_paciente)
        db.session.commit()

        try:
            with open('pacientes_cadastrados.csv', mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([nome, data_nascimento, alergias])
        except Exception as e:
            print(f"Erro ao salvar no CSV: {e}")

        flash('Paciente cadastrado com sucesso e salvo no sistema!', 'success')
        return redirect(url_for('pacientes'))

    pacientes_lista = Paciente.query.all()
    return render_template('pacientes.html', pacientes=pacientes_lista)

@app.route('/prescricao', methods=['GET', 'POST'])
def prescricao():
    """Tela de prescrição com verificação de alerta de alergias."""
    resultado = None

    if request.method == 'POST':
        paciente_id = request.form.get('paciente_id')
        medicamento_id = request.form.get('medicamento_id')

        if paciente_id and medicamento_id:
            paciente = Paciente.query.get(paciente_id)
            medicamento = Medicamento.query.get(medicamento_id)

            if paciente and medicamento:
                status, mensagem = verificar_alerta(paciente, medicamento)

                # Registra a prescrição
                prescricao_obj = Prescricao(
                    paciente_id=paciente.id,
                    medicamento_id=medicamento.id,
                    status=status,
                    observacao=mensagem
                )

                db.session.add(prescricao_obj)
                db.session.commit()

                resultado = {
                    'status': status,
                    'mensagem': mensagem,
                    'paciente': paciente,
                    'medicamento': medicamento
                }

    pacientes = Paciente.query.order_by(Paciente.nome).all()
    medicamentos = Medicamento.query.order_by(Medicamento.nome).all()

    return render_template(
        'prescricao.html',
        pacientes=pacientes,
        medicamentos=medicamentos,
        resultado=resultado
    )

@app.route('/alta', methods=['GET', 'POST'])
def alta():
    """Geração de plano de alta hospitalar."""
    if request.method == 'POST':
        paciente_id = request.form.get('paciente_id')
        orientacoes = request.form.get('orientacoes')
        medicamentos = request.form.get('medicamentos')
        data_retorno = request.form.get('data_retorno')

        if paciente_id and orientacoes:
            plano = PlanoAlta(
                paciente_id=paciente_id,
                orientacoes=orientacoes,
                medicamentos=medicamentos,
                data_retorno=datetime.strptime(data_retorno, '%Y-%m-%d') if data_retorno else None
            )
            db.session.add(plano)
            db.session.commit()
            flash('Plano de alta gerado com sucesso!', 'success')
            return redirect(url_for('ver_plano', plano_id=plano.id))
        else:
            flash('Paciente e orientações são obrigatórios.', 'danger')

    pacientes = Paciente.query.order_by(Paciente.nome).all()
    return render_template('alta.html', pacientes=pacientes, plano=None)

@app.route('/alta/<int:plano_id>')
def ver_plano(plano_id):
    """Visualização do plano de alta gerado."""
    plano = PlanoAlta.query.get_or_404(plano_id)
    return render_template('alta.html', plano=plano, pacientes=None)

@app.route('/planos')
def lista_planos():
    """Lista todos os planos de alta."""
    planos = PlanoAlta.query.order_by(PlanoAlta.criado_em.desc()).all()
    return render_template('planos.html', planos=planos)

@app.route('/editar_paciente/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id):
    paciente = Paciente.query.get_or_404(id)

    if request.method == 'POST':
        paciente.nome = request.form['nome']
        data_nasc = request.form['data_nascimento']
        if data_nasc:
            paciente.data_nascimento = datetime.strptime(data_nasc, '%Y-%m-%d').date()
        else:
            paciente.data_nascimento = None

        paciente.alergias = request.form['alergias']

        db.session.commit()
        flash('Paciente atualizado com sucesso!', 'success')
        return redirect(url_for('pacientes'))

    return render_template('editar_paciente.html', paciente=paciente)

# ------------------- INICIALIZAÇÃO ------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)