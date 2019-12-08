# coding=utf8

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@localhost/school"
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
    data = db.Column(db.DateTime, nullable=True)
    turmas = db.relationship("Turma", backref="escola", lazy="dynamic")

    def __init__(self, nome, endereco, situacao, data):
        self.nivel = nivel
        self.ano = ano
        self.serie = serie
        self.turno = turno


class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nivel = db.Column(db.String(45))
    ano = db.Column(db.DateTime)
    serie = db.Column(db.Integer)
    turno = db.Column(db.String(45))
    escola_id = db.Column(db.Integer, db.ForeignKey("escola.id"))

    def __init__(self, nivel, ano, serie, turno):
        self.nivel = nivel
        self.ano = ano
        self.serie = serie
        self.turno = turno


class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(45), nullable=True)
    telefone = db.Column(db.String(45))
    email = db.Column(db.String(45), nullable=True)
    nascimento = db.Column(db.DateTime)
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


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        alunodados = request.form
        name = alunodados["nome"]
        tel = alunodados["tel"]
        mail = alunodados["email"]
        born = alunodados["born"]
        genre = alunodados["genre"]
        novo_aluno = Aluno(
            nome=name, telefone=tel, email=mail, nascimento=born, genero=genre
        )
        try:
            db.session.add(novo_aluno)
            db.session.commit()
            return redirect("/")
        except:
            return "Erro ocorre nada acontece feijoada"

    else:
        alunos = Aluno.query.order_by(Aluno.id).all()
        return render_template("index.html", alunos=alunos)


if __name__ == "__main__":
    app.run(debug=True)
