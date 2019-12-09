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
                return "<h1>Escola removida</h1> <br><a href='index.html'> Retornar à HomePage </a>"
            except:
                return "<h1>Ocorreu um erro</h1> <br><a href='index.html'> Retornar à HomePage </a>"
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


@app.route("/turmas.html", methods=["POST", "GET"])
def turmas():
    turmadados = request.form
    if request.method == "POST":
        nivel = turmadados["nivel"]
        ano = turmadados["ano"]
        serie = turmadados["serie"]
        turno = turmadados["turno"]
        escola = Escola.query.filter_by(nome=turmadados["escola"]).first()
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


@app.route("/delete/turma/<int:id>")
def deleteturma(id):
    try:
        db.session.delete(Turma.query.get_or_404(id))
        db.session.commit()
        return redirect("/turmas.html")
    except:
        "Ocorreu um erro"


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


@app.route("/alunosbuscar.html", methods=["GET", "POST"])
def alunosbuscar():
    if request.method == "POST":
        alunodados = request.form
        nome = alunodados["nome"]
        aluno = Aluno.query.filter(Aluno.nome.like("%" + nome + "%")).all()
        return render_template("alunosbuscar.html", alunos=aluno)
    else:
        return render_template("alunosbuscar.html")


@app.route("/alunobuscar/<int:id>")
def alunobuscarid(id):
    aluno = Aluno.query.get_or_404(id)
    return render_template("escolabuscar.html", aluno=aluno)


@app.route("/escolabuscar.html", methods=["GET", "POST"])
def escolabuscar():
    if request.method == "POST":
        dados = request.form
        nome = dados["nome"]
        aluno = Aluno.query.get_or_404(dados["alid"])
        escola = Escola.query.filter(Escola.nome.like("%" + nome + "%")).all()
        return render_template("escolabuscar.html", escolas=escola, aluno=aluno)
    else:
        return render_template("escolabuscar.html", aluno=aluno)

#########################################################
@app.route("/escolabuscar/<int:ida>/<int:idb>")
def turmasexibir(ida, idb):
    aluno = Aluno.query.get_or_404(ida)
    escola = Escola.query.get_or_404(idb)
    turmas = Turma.query.filter_by(escola_id=idb).all()
    return render_template(
        "aulaselecionar.html", aluno=aluno, escola=escola, turmas=turmas
    )


@app.route("/aulaselecionar.html")
def aulaselecionar():
    return render_template(
        "aulaselecionar.html", aluno=aluno, escola=escola, turmas=turmas
    )


@app.route("/formselect/<int:id>", methods=["GET", "POST"])
def selectform(id):
    if request.method == "POST":
        aluno = Aluno.query.get_or_404(id)
        todasaulas = request.form.getlist("class")
        for aula in todasaulas:
            try:
                turmas = Turma.query.get_or_404(aula)
                turmas.estudantes.append(aluno)
                db.session.commit()
            except:
                "Um erro ocorreu"
        return redirect("/alunosbuscar.html")
    else:
        return redirect("/alunosbuscar.html")

###########################################################
@app.route("/")
def basic():
    return render_template("/index.html")


if __name__ == "__main__":
    app.run(debug=True)
