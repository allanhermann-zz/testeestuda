# Sistema CRUD de Gerenciamento Escolar

  Nesse repositório foi desenvolvido um sistema CRUD com backend implementado em Python, banco de dados MySQL e frontend utilizando o framework Bootstrap 4.
O sistema foi desenvolvido como parte do Processo Seletivo para vaga no [Grupo Estuda](https://www.grupoestuda.com.br/).

## Iniciando

  Essas instruções vão te ensinar como realizar a instalação do App em um servidor local, com banco de dados local ou utilizando o banco de dados gratuito do ClearDB MySQL.

### Pré-Requisitos

  Você precisa ter previamente instalado os seguintes componentes:

```
* Python 3, com PIP
* Servidor MySQL (se deseja implementar um servidor local)
* GIT(acho que você não estaria aqui se não tivesse isso instalado :) )
```

### Instalando

* Passo 1: Clone o Repositório (ou realize seu download)

```
git clone "https://github.com/allanhermann/testeestuda" 
```

* Passo 2: Instale os pacotes necessários

```
pip install -r requirements.txt
```

* Passo 3: Selecione qual banco de dados deseja utilizar.
Ou pule para o próximo passo se deseja utilizar o já configurado ClearDB MySQL.

```
* Acesse o arquivo "python.app" com algum editor de texto.
* Procure por "engine". Você verá duas linhas de código.
* Comente a linha da Engine de conexão ao Heroku
* Descomente a linha da Engine local
* Altere os dados seguindo o seguinte modelo:
    engine = "mysql://<usuario>:<senha>@<servidor_local>/<banco_de_dados_local>"
```

* Passo 4: Execute o comando 
```
python app.py
```

## Versão online

  Uma versão online está disponível no Heroku, e pode ser acessada através do seguinte link:
* [Versão Online no Heroku](https://teste-estuda.herokuapp.com)

## Built With

* [Flask](https://www.palletsprojects.com/p/flask/)
* [Python](https://www.python.org/)
* [Bootstrap 4](https://getbootstrap.com.br/)

## Authors

* **Allan Biagio Hermann** - *Projeto* - [allanherm](https://github.com/allanhermann)
