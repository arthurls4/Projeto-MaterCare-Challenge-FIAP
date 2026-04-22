from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Paciente(db.Model):
    """Tabela de pacientes com informações de alergias."""
    __tablename__ = 'pacientes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    alergias = db.Column(db.Text, nullable=True, default="")  # Lista livre de alergias
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    prescricoes = db.relationship('Prescricao', backref='paciente', lazy=True)
    planos_alta = db.relationship('PlanoAlta', backref='paciente', lazy=True)

    def __repr__(self):
        return f'<Paciente {self.nome}>'


class Medicamento(db.Model):
    """Tabela de medicamentos disponíveis para prescrição."""
    __tablename__ = 'medicamentos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    substancia_ativa = db.Column(db.String(100), nullable=True)

    # Relacionamentos
    prescricoes = db.relationship('Prescricao', backref='medicamento', lazy=True)

    def __repr__(self):
        return f'<Medicamento {self.nome}>'


class Prescricao(db.Model):
    """Registro de prescrições médicas com status de alerta."""
    __tablename__ = 'prescricoes'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamentos.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)  # 'ALERTA' ou 'OK'
    observacao = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Prescricao {self.id} - {self.status}>'
 

class PlanoAlta(db.Model):
    """Plano de acompanhamento pós-alta hospitalar."""
    __tablename__ = 'planos_alta'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    orientacoes = db.Column(db.Text, nullable=False)
    medicamentos = db.Column(db.Text, nullable=True)  # Lista de medicamentos com horários
    data_retorno = db.Column(db.Date, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PlanoAlta {self.id} - Paciente {self.paciente_id}>'
 