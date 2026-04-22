"""
Script de seed - Popula o banco com dados a partir de arquivos CSV.
Certifique-se de que os arquivos 'pacientes_seed_50.csv' e 
'medicamentos_seed_50.csv' estão na mesma pasta que este script.
"""

import csv
from app import app, db
from models import Paciente, Medicamento
from datetime import datetime

def seed_database():
    with app.app_context():
        # 1. Cria as tabelas (se não existirem)
        db.create_all()

        # 2. Limpa dados existentes para evitar duplicatas
        print("Limpando banco de dados...")
        Medicamento.query.delete()
        Paciente.query.delete()
        db.session.commit()

        # 3. ========== IMPORTAR PACIENTES ==========
        print("Importando pacientes do CSV...")
        total_pacientes = 0
        with open('pacientes.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Converte a string 'YYYY-MM-DD' para um objeto date do Python
                data_nasc = datetime.strptime(row['data_nascimento'], '%Y-%m-%d').date()
                
                p = Paciente(
                    nome=row['nome'],
                    data_nascimento=data_nasc,
                    alergias=row['alergias']
                )
                db.session.add(p)
                total_pacientes += 1

        # 4. ========== IMPORTAR MEDICAMENTOS ==========
        print("Importando medicamentos do CSV...")
        total_meds = 0
        with open('medicamentos.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = Medicamento(
                    nome=row['nome'],
                    substancia_ativa=row['substancia_ativa']
                )
                db.session.add(m)
                total_meds += 1

        # 5. Salva tudo no banco de dados
        db.session.commit()

        print('\n' + '='*30)
        print('✔ Banco populado com sucesso!')
        print(f' - {total_pacientes} pacientes cadastrados')
        print(f' - {total_meds} medicamentos cadastrados')
        print('='*30)

if __name__ == '__main__':
    seed_database()