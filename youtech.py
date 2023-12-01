from flask import Flask, render_template, request, redirect, session
import os
import sqlite3 as sql
import uuid

app = Flask(__name__)
app.secret_key = "youtechlauraigor"

usuario = "lauraigor"
senha = "youtech@123"
login = False

if session:
    session.clear()

def conecta_database():
    conexao = sql.connect("db_youtech.bd")
    conexao.row_factory = sql.Row
    return conexao

def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()

def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False

@app.route('/')
def index():
    iniciar_db()
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas ORDER BY id DESC').fetchall()
    conexao.close()
    title = "Home"
    return render_template('home.html', vagas=vagas, title=title)

@app.route("/login")
def login():
    title = "Login"
    return render_template("login.html", title=title)

@app.route("/acesso", methods=['POST'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/adm')
    else:
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")

@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')
    
@app.route("/excluir/<id>")
def excluir(id):
    if verifica_sessao():
        id = int(id)
        conexao = conecta_database()
        vaga = conexao.execute('SELECT * FROM vagas WHERE id = ?',(id,)).fetchall()
        filename_old = vaga[0]['imagem']
        excluir_arquivo = "static/img/vagas/"+filename_old
        os.remove(excluir_arquivo)
        conexao.execute('DELETE FROM vagas WHERE id = ?',(id,))
        conexao.commit()
        conexao.close()
        return redirect('/adm')
    else:
        return redirect("/login")

@app.route("/editarvagas", methods=['POST'])
def editvagas():
    id = request.form['id']
    nome_imagem = request.form['nome_imagem']
    cargo = request.form['cargo']
    cargo = cargo.title()
    localizacao = request.form['localizacao']
    localizacao = localizacao.title()
    tipo_vaga = request.form['tipo_vaga']
    tipo_vaga = tipo_vaga.title()
    sobre = request.form ['sobre']
    sobre = sobre.capitalize()
    requisitos = request.form ['requisitos']
    requisitos = requisitos.capitalize()
    salario = request.form ['salario']
    email = request.form ['email']
    imagem=request.files['imagem']
    conexao = conecta_database()
    conexao.execute('UPDATE vagas SET cargo = ?, localizacao = ?, tipo_vaga = ?, sobre = ?, requisitos = ?, salario = ?, email = ?, imagem = ? WHERE id  = ?', (cargo,localizacao,tipo_vaga,sobre,requisitos,salario,email,nome_imagem,id))
    conexao.commit()
    conexao.close()

    if imagem:
        imagem.save("static/img/vagas/"+ nome_imagem)

    return redirect('/adm')
    
@app.route("/editar/<id>")
def editar(id):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        vagas = conexao.execute('SELECT * FROM vagas WHERE id = ?',(id,)).fetchall()
        conexao.close()
        title = "Edição de vagas"
        return render_template("editar.html", vagas=vagas, title=title)
    else:
        return redirect('/login')
    
@app.route("/cadastro", methods=["post"])
def cadastro():
    if verifica_sessao():
        cargo = request.form ['cargo']
        cargo = cargo.title()
        localizacao = request.form ['localizacao']
        localizacao = localizacao.title()
        tipo_vaga = request.form ['tipo_vaga']
        tipo_vaga = tipo_vaga.title()
        sobre = request.form ['sobre']
        sobre = sobre.capitalize()
        requisitos = request.form ['requisitos']
        requisitos = requisitos.capitalize()
        salario = request.form ['salario']
        email = request.form ['email']
        imagem=request.files['imagem']
        id_foto=str(uuid.uuid4().hex)
        filename=id_foto+cargo+'.png'
        imagem.save("static/img/vagas/"+filename)
        conexao = conecta_database()
        conexao.execute('INSERT INTO vagas (cargo, localizacao, tipo_vaga, sobre, requisitos, salario, email, imagem) VALUES (?,?,?,?,?,?,?,?)', (cargo, localizacao, tipo_vaga, sobre, requisitos, salario, email, filename))
        conexao.commit()
        conexao.close()
        return redirect('/adm')
    else:
        return redirect('/login')

@app.route("/cadvagas")
def cadvagas():
        if verifica_sessao():
            title = "Cadastro de Vagas"
            return render_template("cadvagas.html", title=title)
        else:
            return redirect("/login")
        
@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db() 
        conexao = conecta_database()
        vagas = conexao.execute('SELECT * FROM vagas ORDER BY id DESC').fetchall()
        conexao.close()
        title = "Administração"
        return render_template("adm.html", vagas=vagas, title=title)
    else:
        return redirect("/login")

@app.route('/vervaga/<id>')
def vervaga(id):
    iniciar_db()
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas WHERE id = ?',(id,)).fetchall()
    conexao.close()
    title = "Exibir vaga"
    return render_template("vervaga.html", vagas=vagas, title=title)

@app.route('/sobre')
def sobre():
    title = "Sobre"
    return render_template("sobre.html", title=title)

@app.route("/busca",methods=["post"])
def busca():
    busca = request.form['buscar']
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas WHERE cargo LIKE "%" || ? || "%"',(busca,)).fetchall()
    title = "Home"
    return render_template("home.html", vagas=vagas, title=title)

if __name__ == '__main__':
    app.run(debug=True)