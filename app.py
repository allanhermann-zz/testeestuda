# -----------------------------------------------------------
# coding=utf8
# 
# Sistema de Controle Escolar
# Desenvolvido por: Allan Biagio Hermann
# email: allan.hermann@gmail.com
# 
# Utilizado Python Flask para o Backend 
# MySQL como Banco de Dados 
# Bootstrap 4 para o Frontend
#
# -----------------------------------------------------------

# Importação das dependências utilizadas
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from datetime import datetime
import json
import requests
from sqlalchemy_utils import create_database

# Selecione uma das Engines abaixo
engine = "mysql://bd784eaba7307d:4a6bd961@us-cdbr-iron-east-05.cleardb.net/heroku_56973eeaab8af2f" # Engine de conexão ao Heroku
#engine = "mysql://root:root@localhost/school" # Engine de conexão local

# Configuração do App
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = engine
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Definição das tabelas
# Tabela de Matrículas (Relacionamento Alunos x Turmas)
aulas = db.Table(
    "aulas",
    db.Column("aluno_id", db.Integer, db.ForeignKey("aluno.id")),
    db.Column("turma_id", db.Integer, db.ForeignKey("turma.id")),
    db.UniqueConstraint('aluno_id', 'turma_id', name='uniqueTurma'), # Definindo atributos unicos
)

# Tabela das Escolas
class Escola(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200))
    endereco = db.Column(db.String(150))
    situacao = db.Column(db.String(45), nullable=True)
    data = db.Column(db.Integer, nullable=True)
    turmas = db.relationship("Turma", backref="escola", lazy="dynamic") # Definindo o pai do relacionamento das Turmas
    __table_args__ = (db.UniqueConstraint('nome', 'endereco', name='duplaEscola'),) # Definindo atributos unicos
    def __init__(self, nome, endereco, situacao, data):
        self.nome = nome
        self.endereco = endereco
        self.situacao = situacao
        self.data = data

# Tabela das Turmas
class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nivel = db.Column(db.String(45))
    ano = db.Column(db.Integer)
    serie = db.Column(db.Integer)
    turno = db.Column(db.String(45))
    escola_id = db.Column(db.Integer, db.ForeignKey("escola.id")) # Chave secundária da escola
    aulas = db.relationship("Aluno", secondary=aulas, backref=db.backref("estudantes")) # Definindo o Pai no relacionamento das Matrículas

    def __init__(self, nivel, ano, serie, turno, escola):
        self.nivel = nivel
        self.ano = ano
        self.serie = serie
        self.turno = turno
        self.escola = escola

# Tabela dos Alunos
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(45), nullable=True)
    telefone = db.Column(db.String(45))
    email = db.Column(db.String(45), nullable=True)
    nascimento = db.Column(db.Date)
    genero = db.Column(db.String(1))
    __table_args__ = (db.UniqueConstraint('nome', 'nascimento', 'email', name='uniqueAluno'),) # Definindo atributos unicos

    def __init__(self, nome, telefone, email, nascimento, genero):
        self.nome = nome
        self.telefone = telefone
        self.email = email
        self.nascimento = nascimento
        self.genero = genero

# Inicialização do banco de dados
# O código abaixo apenas é executado caso o banco de dados ainda não tenha sido inicializado 
try:
    create_database(engine)
    db.create_all()

    # Conexão à API das escolas disponível em "http://educacao.dadosabertosbr.com/api/docs/%2Fapi%2Fescolas%2Fbuscaavancada"
    dados = requests.get("http://educacao.dadosabertosbr.com/api/escolas/buscaavancada?estado=MT")
    dadosjson = dados.json()[1]

    # Inserção dos dados da API no Banco de dados
    for jsoncode in range(len(dadosjson)):
        nome = dadosjson[jsoncode]["nome"]
        endereco = dadosjson[jsoncode]["cidade"] + "," + dadosjson[jsoncode]["estado"]
        situacao = dadosjson[jsoncode]["situacaoFuncionamentoTxt"]
        data = dadosjson[jsoncode]["anoCenso"]
        var = Escola(nome=nome, endereco=endereco, situacao=situacao, data=data)
        db.session.add(var)
        db.session.commit()
except:
    pass


# Códigos da API
# Rota base das escolas
@app.route("/escolas.html", methods=["POST", "GET"])
def escolas():
    escoladados = request.form
    if request.method == "POST":
        
        # Cadastro de escolas
        if escoladados["action"] == "Enviar Dados":
            nome = escoladados["nome"]
            endereco = escoladados["endereco"]
            situacao = escoladados["situacao"]
            data = escoladados["data"]
            nova_escola = Escola(nome=nome, endereco=endereco, situacao=situacao, data=data)
            try:
                db.session.add(nova_escola)
                db.session.commit()
                escolas = Escola.query.filter(
                Escola.nome.like("%" + nova_escola.nome + "%")).all()
                return render_template("/escolas.html", escolas=escolas, alert=1)
            except:
                return render_template("/escolas.html", alert=2)

        # Busca de escolas
        elif escoladados["action"] == "Buscar Escola":
            escolas = Escola.query.filter(
                Escola.nome.like("%" + escoladados["nome"] + "%")
            ).all()
            if escolas:
                verif = 0
            else:
                verif = 1
            return render_template("escolas.html", escolas=escolas, verif=verif)

        # Remoção de escolas
        elif escoladados["action"] == "Remover":
            try:
                db.session.delete(Escola.query.get_or_404(escoladados["id"]))
                db.session.commit()
                return render_template("/escolas.html", alert=1)
            except:
                return render_template("/escolas.html", alert=2)

        # Encaminhamento para atualização dos dados das escolas
        elif escoladados["action"] == "Atualizar":
            return render_template("escolas.html", verif=0)
    else:
        return render_template("escolas.html", verif=0)

# Rota de atualização dos dados das escolas
@app.route("/update/escola/<int:id>", methods=["POST", "GET"])
def updateescola(id):
    escola = Escola.query.get_or_404(id)
    if request.method == "POST":
        escoladados = request.form
        escola.nome = escoladados["nome"]
        escola.endereco = escoladados["endereco"]
        escola.situacao = escoladados["situacao"]
        escola.data = escoladados["data"]
        try:
            db.session.commit()
            escolas=Escola.query.filter(Escola.nome.like("%" + escola.nome + "%")).all()
            return render_template("/escolas.html", escolas=escolas, alert=1)
        except:
            return render_template("/escolas.html", alert=2)

    else:
        return render_template("updateescola.html", escola=escola)


# Rota base das turmas
@app.route("/turmas.html", methods=["POST", "GET"])
def turmas():
    if request.method == "POST":
        turmadados = request.form
        # Busca de escolas para seleção de turmas
        if turmadados["action"] == "Buscar Escola":
            escolas = Escola.query.filter(Escola.nome.like("%" + turmadados["nome"] + "%")).all()
            if escolas:
                verif = 0
            else:
                verif = 1
            return render_template("turmas.html", escolas=escolas, verif=verif)

        # Seleção de escolas para seleção de turmas
        elif turmadados["action"] == "Selecionar Escola":
            escola = Escola.query.get_or_404(turmadados["id"])
            turmas = Turma.query.filter_by(escola=escola).all()
            if turmas:
                verifa = 0
            else:
                verifa = 1
            return render_template("turmas.html", turmas=turmas, verifa=verifa, escola=escola)

        # Visualização das turmas de uma escola
        elif turmadados["action"] == "Ver Turmas":
            escola = Escola.query.get_or_404(turmadados["id"])
            turmas = Turma.query.filter_by(escola=escola).all()
            if turmas:
                verifa = 0
            else:
                verifa = 1
            return render_template("turmas.html", turmas=turmas, verifa=verifa, escola=escola)

        # Remoção de uma turma
        elif turmadados["action"] == "Remover":
            try:
                turma = Turma.query.get_or_404(turmadados["id"])
                escola = turma.escola
                print(turma.escola)
                print(turma)
                db.session.delete(turma)
                db.session.commit()
                turmas = Turma.query.filter_by(escola=escola).all()
                print(turmas)
                if turmas:
                    verifa = 0
                else:
                    verifa = 1
                return render_template("/turmas.html", turmas=turmas, verifa=verifa, escola=escola,alert=1)
            except:
                return render_template("/turmas.html", alert=2)

        # Encaminhamento para atualização dos dados da turma
        elif turmadados["action"] == "Atualizar turma":
            return render_template("turmas.html", verif=0)

        # Cadastro de turma
        elif turmadados["action"] == "Cadastrar Turma":
            nivel = turmadados["nivel"]
            ano = turmadados["ano"]
            serie = turmadados["serie"]
            turno = turmadados["turno"]
            escola = Escola.query.filter_by(nome=turmadados["escola"]).first()
            nova_turma = Turma(nivel=nivel, ano=ano, serie=serie, turno=turno, escola=escola)
            turmas = Turma.query.filter_by(escola=escola).all()
            try:
                db.session.add(nova_turma)
                db.session.commit()
                return render_template("/turmas.html", turmas=turmas, escola=escola, verif=0, verifa=0, alert=1)
            except:
                return render_template("/turmas.html", alert=2)

        # O bloco abaixo não está em funcionamento

        #elif turmadados["action"] == "Ver Matriculas":
        #    aluno = Aluno.query.get_or_404(turmadados["id"])
        #    turmas = Turma.query.filter(
        #        Turma.estudantes.any(id=aluno.id)).all()
        #
        #    if turmas:
        #        verif = 0
        #    else:
        #        verif = 1
        #
        #   return render_template("turmas.html", turmas=turmas, escola=0, verif=verif, noc=1)

        # Encaminhamento para matrícula dos alunos em uma turma
        elif turmadados["action"] == "Matricular Alunos":
            return render_template("/alunosturmas.html", turma=turmadados["id"])

    else:
        return render_template("turmas.html", verif=0, verifa=0)

# Rota de atualização das turmas
@app.route("/update/turma/<int:id>", methods=["POST", "GET"])
def updateturma(id):
    turma = Turma.query.get_or_404(id)
    if request.method == "POST":
        turmadados = request.form
        turma.nivel = turmadados["nivel"]
        turma.ano = turmadados["ano"]
        turma.serie = turmadados["serie"]
        turma.turno = turmadados["turno"]
        turma.escola = Escola.query.filter_by(nome=turmadados["escola"]).first()
        try:
            db.session.commit()
            turmas = Turma.query.get_or_404(id)
            escola = turmas.escola
            turmas = Turma.query.filter_by(escola=escola).all()
            if turmas:
                verif = 0
            else:
                verif = 1
            return render_template("/turmas.html", escola=escola, turmas=turmas, alert=1)
        except:
            return render_template("/turmas.html", alert=2)

    else:
        return render_template("updateturma.html", turma=turma)

# Rota base dos Alunos
@app.route("/alunos.html", methods=["POST", "GET"])
def alunos():
    alunodados = request.form
    if request.method == "POST":

        # Cadastro de alunos
        if alunodados["action"] == "Enviar Dados":
            nome = alunodados["nome"]
            tel = alunodados["tel"]
            email = alunodados["email"]
            nascimento = datetime.strptime(
                alunodados["nascimento"], "%Y-%m-%d")
            genero = alunodados["genero"]
            novo_aluno = Aluno(
                nome=nome,
                telefone=tel,
                email=email,
                nascimento=nascimento,
                genero=genero)
            try:
                db.session.add(novo_aluno)
                db.session.commit()
                alunos = Aluno.query.filter(
                Aluno.nome.like("%" + alunodados["nome"] + "%")).all()
                return render_template("/alunos.html", alert=1, alunos=alunos)
            except:
                return render_template("/alunos.html", alert=2)

        # Busca de alunos
        elif alunodados["action"] == "Buscar Aluno":
            alunos = Aluno.query.filter(
                Aluno.nome.like("%" + alunodados["nome"] + "%")
            ).all()
            if alunos:
                verif = 0
            else:
                verif = 1
            return render_template("alunos.html", alunos=alunos, verif=verif, nod = 0)
        
        # Visualização dos Alunos de uma Turma
        elif alunodados["action"] == "Ver Alunos":
            turma = Turma.query.get_or_404(alunodados["id"])
            alunos = Aluno.query.filter(
                Aluno.estudantes.any(id=turma.id)).all()
            if alunos:
                verif = 0
            else:
                verif = 1
            return render_template("alunos.html", alunos=alunos, verif=verif, noc=1, nod=1, noe=1)

        # Remoção de alunos
        elif alunodados["action"] == "Remover":
            try:
                db.session.delete(Aluno.query.get_or_404(alunodados["id"]))
                db.session.commit()
                return render_template("/alunos.html", alert=1)
            except:
                return render_template("/alunos.html", alert=2)
        
        # Encaminhamento para Atualização dos Alunos
        elif alunodados["action"] == "Atualizar Aluno":
            return render_template("alunos.html", verif=0)

    else:
        return render_template("alunos.html", verif=0)

# Rota de atualização dos Alunos
@app.route("/update/aluno/<int:id>", methods=["POST", "GET"])
def updatealuno(id):
    aluno = Aluno.query.get_or_404(id)
    if request.method == "POST":
        alunodados = request.form
        aluno.nome = alunodados["nome"]
        aluno.telefone = alunodados["tel"]
        aluno.email = alunodados["email"]
        aluno.nascimento = alunodados["nascimento"]
        aluno.genero = alunodados["genero"]
        try:
            db.session.commit()
            alunos = Aluno.query.filter(Aluno.nome.like("%" + alunodados["nome"] + "%")).all()
            return render_template("/alunos.html", alert=1, alunos=alunos)
        except:
            return render_template("/alunos.html", alert=2, alunos=alunos)
    else:
        return render_template("updatealuno.html", aluno=aluno)


# Rota das Matrículas
@app.route("/alunosturmas.html", methods=["GET", "POST"])
def matricula():
    alunoturma = request.form
    if request.method == "POST":
        turma = alunoturma["turmaid"]

        # Busca de alunos
        if alunoturma["action"] == "Buscar Aluno(a)":
            alunos = Aluno.query.filter(
                Aluno.nome.like("%" + alunoturma["nome"] + "%")).all()
            if alunos:
                verif = 0
            else:
                verif = 1
            return render_template("alunosturmas.html", turma=turma, alunos=alunos, verif=verif)

        # Matrícula de Alunos
        elif alunoturma["action"] == "Matricular Aluno(a)":
            turmas = Turma.query.get_or_404(turma)
            aluno = Aluno.query.get_or_404(alunoturma["alunoid"])
            try:
                aluno.estudantes.append(turmas)
                db.session.commit()
                return render_template("alunosturmas.html", turma=turma, alert=1)
            except:
                return render_template("alunosturmas.html", turma=turma, alert=2)
        
        # Busca de novos alunos
        elif alunoturma["action"] == "Buscar novo aluno(a)":
            return render_template("alunosturmas.html", turma=turma)
    else:
        return render_template("alunosturmas.html")

# Rota principal
@app.route("/")
@app.route("/index.html")
def basic():
    return render_template("/index.html")

# Inicialização do app e debug
if __name__ == "__main__":
    app.run(debug=True)
