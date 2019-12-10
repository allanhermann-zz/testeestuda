# coding=utf8

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json, requests
from sqlalchemy_utils import create_database

try:
    from app import db, engine, Escola

    create_database(engine)

    db.create_all()

    dados = requests.get(
        "http://educacao.dadosabertosbr.com/api/escolas/buscaavancada?estado=MT"
    )

    dadosjson = dados.json()[1]

    for jsoncode in range(len(dadosjson)):
        nome = dadosjson[jsoncode]["nome"]
        endereco = dadosjson[jsoncode]["cidade"] + ", " + dadosjson[jsoncode]["estado"]
        situacao = dadosjson[jsoncode]["situacaoFuncionamentoTxt"]
        data = dadosjson[jsoncode]["anoCenso"]
        var = Escola(nome=nome, endereco=endereco, situacao=situacao, data=data)
        db.session.add(var)
        db.session.commit()
except:
    pass


engine = "mysql://root:root@localhost/school"
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = engine
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


aulas = db.Table(
    "aulas",
    db.Column("aluno_id", db.Integer, db.ForeignKey("aluno.id")),
    db.Column("turma_id", db.Integer, db.ForeignKey("turma.id")),
)


class Escola(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200))
    endereco = db.Column(db.String(90))
    situacao = db.Column(db.String(45), nullable=True)
    data = db.Column(db.Integer, nullable=True)
    turmas = db.relationship("Turma", backref="escola", lazy="dynamic")

    def __init__(self, nome, endereco, situacao, data):
        self.nome = nome
        self.endereco = endereco
        self.situacao = situacao
        self.data = data


class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nivel = db.Column(db.String(45))
    ano = db.Column(db.Integer)
    serie = db.Column(db.Integer)
    turno = db.Column(db.String(45))
    escola_id = db.Column(db.Integer, db.ForeignKey("escola.id"))

    def __init__(self, nivel, ano, serie, turno, escola):
        self.nivel = nivel
        self.ano = ano
        self.serie = serie
        self.turno = turno
        self.escola = escola


class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(45), nullable=True)
    telefone = db.Column(db.String(45))
    email = db.Column(db.String(45), nullable=True)
    nascimento = db.Column(db.Date)
    genero = db.Column(db.String(1))
    aulas = db.relationship(
        "Turma", secondary=aulas, backref=db.backref("estudantes"), lazy="dynamic"
    )

    def __init__(self, nome, telefone, email, nascimento, genero):
        self.nome = nome
        self.telefone = telefone
        self.email = email
        self.nascimento = nascimento
        self.genero = genero


########################--ESCOLAS--####################
@app.route("/escolas.html", methods=["POST", "GET"])
def escolas():
    escoladados = request.form
    if request.method == "POST":
        if escoladados["action"] == "Enviar Dados":
            nome = escoladados["nome"]
            endereco = escoladados["endereco"]
            situacao = escoladados["situacao"]
            data = escoladados["data"]
            nova_escola = Escola(
                nome=nome, endereco=endereco, situacao=situacao, data=data
            )
            try:
                db.session.add(nova_escola)
                db.session.commit()
                return render_template("/escolas.html", verif=0)
            except:
                return "Erro durante a Inserção, cheque seus dados"

        elif escoladados["action"] == "Buscar Escola":
            escolas = Escola.query.filter(
                Escola.nome.like("%" + escoladados["nome"] + "%")
            ).all()
            if escolas:
                verif = 0
            else:
                verif = 1
            return render_template("escolas.html", escolas=escolas, verif=verif)

        elif escoladados["action"] == "Remover Escola":
            try:
                db.session.delete(Escola.query.get_or_404(escoladados["id"]))
                db.session.commit()
                return (
                    "<h1>Escola removida</h1> <br><a href='/'> Retornar à HomePage </a>"
                )
            except:
                return (
                    "<h1>Ocorreu um erro</h1> <br><a href='/'> Retornar à HomePage </a>"
                )
        elif escoladados["action"] == "Atualizar Escola":
            return render_template("escolas.html", verif=0)
    else:
        return render_template("escolas.html", verif=0)


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
            return redirect("../../escolas.html")
        except:
            return "Erro durante a Atualização, cheque seus dados"

    else:
        return render_template("updateescola.html", escola=escola)


#########################--TURMAS--####################
@app.route("/turmas.html", methods=["POST", "GET"])
def turmas():
    turmadados = request.form
    if request.method == "POST":
        if turmadados["action"] == "Buscar Escola":
            escolas = Escola.query.filter(
                Escola.nome.like("%" + turmadados["nome"] + "%")
            ).all()
            if escolas:
                verif = 0
            else:
                verif = 1
            return render_template("turmas.html", escolas=escolas, verif=verif)
        elif turmadados["action"] == "Selecionar Escola":
            escola = Escola.query.get_or_404(turmadados["id"])
            turmas = Turma.query.filter_by(escola=escola).all()
            if turmas:
                verifa = 0
            else:
                verifa = 1
            return render_template(
                "turmas.html", turmas=turmas, verifa=verifa, escola=escola
            )
        elif turmadados["action"] == "Remover Turma":
            try:
                db.session.delete(Turma.query.get_or_404(turmadados["id"]))
                db.session.commit()
                return (
                    "<h1>Turma removida</h1> <br><a href='/'> Retornar à HomePage </a>"
                )
            except:
                return (
                    "<h1>Ocorreu um erro</h1> <br><a href='/'> Retornar à HomePage </a>"
                )
        elif turmadados["action"] == "Atualizar turma":
            return render_template("turmas.html", verif=0)
        elif turmadados["action"] == "Cadastrar Turma":
            nivel = turmadados["nivel"]
            ano = turmadados["ano"]
            serie = turmadados["serie"]
            turno = turmadados["turno"]
            escola = Escola.query.filter_by(nome=turmadados["escola"]).first()
            nova_turma = Turma(
                nivel=nivel, ano=ano, serie=serie, turno=turno, escola=escola
            )
            turmas = Turma.query.filter_by(escola=escola).all()
            try:
                db.session.add(nova_turma)
                db.session.commit()
                return render_template(
                    "/turmas.html", turmas=turmas, escola=escola, verif=0, verifa=0
                )
            except:
                return "Erro durante a Inserção, cheque seus dados"
        elif turmadados["action"] == "Cadastrar Alunos":
            return render_template("/alunosturmas.html", turma=turmadados["id"])

    else:
        return render_template("turmas.html", verif=0, verifa=0)


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
            return redirect("../../turmas.html")
        except:
            return "Erro durante a Atualização, cheque seus dados"

    else:
        return render_template("updateturma.html", turma=turma)


#########################--ALUNOS--####################


@app.route("/alunos.html", methods=["POST", "GET"])
def alunos():
    alunodados = request.form
    if request.method == "POST":
        if alunodados["action"] == "Enviar Dados":
            nome = alunodados["nome"]
            tel = alunodados["tel"]
            email = alunodados["email"]
            nascimento = datetime.strptime(alunodados["nascimento"], "%d-%m-%Y")
            genero = alunodados["genero"]
            novo_aluno = Aluno(
                nome=nome,
                telefone=tel,
                email=email,
                nascimento=nascimento,
                genero=genero,
            )
            try:
                db.session.add(novo_aluno)
                db.session.commit()
                return render_template("/alunos.html", verif=0)
            except:
                return "Erro durante a Inserção, cheque seus dados"
        elif alunodados["action"] == "Buscar Aluno":
            alunos = Aluno.query.filter(
                Aluno.nome.like("%" + alunodados["nome"] + "%")
            ).all()
            if alunos:
                verif = 0
            else:
                verif = 1
            return render_template("alunos.html", alunos=alunos, verif=verif)

        elif alunodados["action"] == "Remover Aluno":
            try:
                db.session.delete(Aluno.query.get_or_404(alunodados["id"]))
                db.session.commit()
                return "<h1>Aluno(a) removido(a)</h1> <br><a href='/'> Retornar à HomePage </a>"
            except:
                return (
                    "<h1>Ocorreu um erro</h1> <br><a href='/'> Retornar à HomePage </a>"
                )
        elif alunodados["action"] == "Atualizar Aluno":
            return render_template("alunos.html", verif=0)
    else:
        return render_template("alunos.html", verif=0)


@app.route("/update/aluno/<int:id>", methods=["POST", "GET"])
def updatealuno(id):
    aluno = Aluno.query.get_or_404(id)
    if request.method == "POST":
        alunodados = request.form
        aluno.nome = alunodados["nome"]
        aluno.telefone = alunodados["tel"]
        aluno.email = alunodados["email"]
        aluno.nascimento = alunodados["born"]
        aluno.genero = alunodados["genre"]
        try:
            db.session.commit()
            return redirect("../../alunos.html")
        except:
            return "Erro durante a Atualização, cheque seus dados"

    else:
        return render_template("updatealuno.html", aluno=aluno)


##################--REL ALUNOS X TURMAS--##############
@app.route("/alunosturmas.html", methods=["GET", "POST"])
def matricula():
    alunoturma = request.form
    if request.method == "POST":
        turma = alunoturma["turmaid"]
        if alunoturma["action"] == "Buscar Aluno":
            alunos = Aluno.query.filter(
                Aluno.nome.like("%" + alunoturma["nome"] + "%")
            ).all()
            if alunos:
                verif = 0
            else:
                verif = 1
            return render_template(
                "alunosturmas.html", turma=turma, alunos=alunos, verif=verif
            )

        elif alunoturma["action"] == "Matricular Aluno":
            turmas = Turma.query.get_or_404(alunoturma["turmaid"])
            aluno = Aluno.query.get_or_404(alunoturma["alunoid"])
            try:
                turmas.estudantes.append(aluno)
                db.session.commit()
                return render_template("alunosturmas.html", turma=turma)
            except:
                return "Um erro ocorreu"
    else:
        return render_template("alunosturmas.html", turma=turma)


###########################################################
@app.route("/")
def basic():
    return render_template("/index.html")


if __name__ == "__main__":
    app.run(debug=True)
