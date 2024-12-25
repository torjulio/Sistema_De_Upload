import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

UPLOAD_FOLDER = r'C:\Users\House\Desktop\uploads\uploads'
arquivo_pontos = 'pontos.txt'
arquivo_nomes = 'nomes.txt'
senha_administrador = 'admin123'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Função para salvar o nome e a senha no arquivo
def salvar_nome(nome_completo, senha):
    codigo = str(random.randint(100000, 999999))
    with open(arquivo_nomes, 'a') as f:
        f.write(f'{nome_completo},{senha},{codigo}\n')
    
    # Cria uma pasta exclusiva para o usuário
    user_folder = os.path.join(UPLOAD_FOLDER, nome_completo)
    os.makedirs(user_folder, exist_ok=True)
    
    return codigo

def verificar_nome(nome_completo):
    with open(arquivo_nomes, 'r') as f:
        nomes = f.readlines()
    for nome in nomes:
        if nome_completo in nome:
            return True
    return False

# Função para verificar a autenticação do usuário
def autenticar_usuario(codigo, senha):
    with open(arquivo_nomes, 'r') as f:
        linhas = f.readlines()
    for linha in linhas:
        nome_arquivo, senha_arquivo, codigo_arquivo = linha.strip().split(',')
        if codigo_arquivo == codigo and senha_arquivo == senha:
            return nome_arquivo
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    mensagem = None
    if request.method == 'POST':
        if 'cadastrar' in request.form:
            nome = request.form['nome']
            senha = request.form['senha']
            if not verificar_nome(nome):
                codigo = salvar_nome(nome, senha)
                mensagem = f'Seu código de acesso é: {codigo}'
            else:
                mensagem = 'Nome já cadastrado!'
        elif 'bater_ponto' in request.form:
            codigo = request.form['codigo']
            senha = request.form['senha_bater']
            nome_usuario = autenticar_usuario(codigo, senha)
            if nome_usuario:
                session['username'] = nome_usuario
                return redirect(url_for('user_files'))
            else:
                mensagem = 'Erro: Código ou senha incorretos.'

    return render_template('index.html', mensagem=mensagem)

@app.route('/user_files', methods=['GET', 'POST'])
def user_files():
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']
    user_folder = os.path.join(UPLOAD_FOLDER, username)
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Nenhum arquivo selecionado'
        
        file = request.files['file']
        if file and '.' in file.filename:
            filename = file.filename
            file.save(os.path.join(user_folder, filename))

    # Listar arquivos do usuário
    arquivos = os.listdir(user_folder)
    return render_template('user_files.html', arquivos=arquivos, username=username)

@app.route('/download/<filename>')
def download_file(filename):
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']
    user_folder = os.path.join(UPLOAD_FOLDER, username)
    return send_from_directory(user_folder, filename, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
