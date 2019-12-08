# coding=utf8

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    nome = db.Column(db.String(45))
    endereco = db.Column(db.String(90))
    situacao = db.Column(db.String(45), nullable=True)
    data = db.Column(db.Date, nullable=True)
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


@app.route("/escolas.html", methods=["POST", "GET"])
def escolas():
    if request.method == "POST":
        escoladados = request.form
        nome = escoladados["nome"]
        endereco = escoladados["endereco"]
        situacao = escoladados["situacao"]
        data = escoladados["data"]
        nova_escola = Escola(nome=nome, endereco=endereco, situacao=situacao, data=data)
        try:
            db.session.add(nova_escola)
            db.session.commit()
            return redirect("/escolas.html")
        except:
            return "Erro durante a Inserção, cheque seus dados"

    else:
        escolas = Escola.query.order_by(Escola.id).all()
        return render_template("escolas.html", escolas=escolas)


@app.route("/turmas.html", methods=["POST", "GET"])
def turmas():
    if request.method == "POST":
        turmadados = request.form
        nivel = turmadados["nivel"]
        ano = turmadados["ano"]
        serie = turmadados["serie"]
        turno = turmadados["turno"]
        var = turmadados["escola"]
        escola = Escola.query.filter_by(nome=var).first()
        nova_turma = Turma(
            nivel=nivel, ano=ano, serie=serie, turno=turno, escola=escola
        )
        try:
            db.session.add(nova_turma)
            db.session.commit()
            return redirect("/turmas.html")
        except:
            return "Erro durante a Inserção, cheque seus dados"

    else:
        turmas = Turma.query.order_by(Turma.id).all()
        return render_template("turmas.html", turmas=turmas)


@app.route("/alunos.html", methods=["POST", "GET"])
def alunos():
    if request.method == "POST":
        alunodados = request.form
        name = alunodados["nome"]
        tel = alunodados["tel"]
        mail = alunodados["email"]
        born = datetime.strptime(alunodados["born"],"%d-%m-%Y")
        genre = alunodados["genre"]
        novo_aluno = Aluno(
            nome=name, telefone=tel, email=mail, nascimento=born, genero=genre
        )
        try:
            db.session.add(novo_aluno)
            db.session.commit()
            return render_template("/aulas.html",aluno=novo_aluno)
        except:
            return "Erro durante a Inserção, cheque seus dados"

    else:
        alunos = Aluno.query.order_by(Aluno.id).all()
        return render_template("alunos.html", alunos=alunos)

@app.route("/aulas.html", methods=["GET","POST"])
def aulas():
    return render_template("/index.html")


@app.route("/")
def basic():
    return redirect("/index.html")


@app.route("/index.html")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
