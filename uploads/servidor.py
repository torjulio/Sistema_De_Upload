import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, send_file
from zipfile import ZipFile

# Diretório onde os arquivos serão salvos
UPLOAD_FOLDER = r'C:\Users\House\Desktop\uploads\uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'pptx', 'ppsx', 'odp', 'zip', 'rar', 'html', 'css', 'js'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cria o diretório de uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Função para verificar se o arquivo é permitido
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para salvar arquivos ou subpastas enviadas
def save_file(file, subfolder=""):
    filename = file.filename
    # Define o caminho de salvamento, incluindo a subpasta, caso exista
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder, filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Cria subpastas se necessário
    file.save(save_path)

# Função para listar arquivos e pastas do nível superior
def list_top_level_files(directory):
    items = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            items.append((item, True))  # True indica que é uma pasta
        elif os.path.isfile(item_path) and allowed_file(item):
            items.append((item, False))  # False indica que é um arquivo
    return items

# Página principal para upload de arquivos ou pastas
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Nenhum arquivo selecionado'
        
        files = request.files.getlist('file')
        for file in files:
            if file.filename:
                if allowed_file(file.filename):
                    # Se o arquivo tiver uma estrutura de pasta, extrai a subpasta do caminho
                    subfolder = os.path.dirname(file.filename)
                    save_file(file, subfolder=subfolder)

        return redirect(url_for('upload_success'))

    # Listar apenas arquivos e pastas do nível superior
    items = list_top_level_files(app.config['UPLOAD_FOLDER'])
    items_links = [
        f'<div class="file-item"><a href="/download/{item[0]}">{item[0]}{" (Pasta)" if item[1] else ""}</a></div>'
        for item in items
    ]
    items_list = ''.join(items_links)

    return render_template_string('''
    <!doctype html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" href="static/icon.png" type="image/x-icon">
        <title>Servidor M-Tech</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <div class="logo-container">
            <img src="static/lucas02.png" alt="Logo Esquerdo" class="logo">
            <h1>Faça upload de arquivos ou pastas</h1>
            <img src="static/MTECH.png" alt="Logo Direito" class="logo">
        </div>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" webkitdirectory multiple>
            <input type="submit" value="Upload">
        </form>
        <h2>Arquivos e Pastas disponíveis para download:</h2>
        <div id="file-grid">{{ items_list | safe }}</div>
    </body>
    </html>
    ''', items_list=items_list)

# Função para baixar arquivos ou pastas (pasta será baixada como .zip)
@app.route('/download/<path:filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Se for uma pasta, compacta para .zip
    if os.path.isdir(file_path):
        zip_path = file_path + '.zip'
        with ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(file_path):
                for file in files:
                    file_full_path = os.path.join(root, file)
                    zipf.write(file_full_path, os.path.relpath(file_full_path, file_path))
        return send_file(zip_path, as_attachment=True)
    
    # Se for um arquivo, envia diretamente
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Página de sucesso após upload
@app.route('/success')
def upload_success():
    return render_template_string('''
    <!doctype html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Carregar bem-sucedido</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <h1>Arquivos enviados com sucesso!</h1>
        <a href="/">Voltar para o upload</a>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
