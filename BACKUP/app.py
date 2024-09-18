import os
import base64
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image as PILImage

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'  # Necessário para usar flash messages

# Verifica se a pasta 'uploads' existe, senão cria.
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Defina o caminho para o arquivo Excel fixo (modelo)
FIXED_EXCEL_FILE = os.path.join(UPLOAD_FOLDER, 'modelo.xlsx')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Recebe os dados do formulário
        nome = request.form['nome']
        nr_edp = request.form['nr_edp']
        ticket = request.form['ticket']
        removido = request.form['removido']
        instalado = request.form['instalado']
        beneficio = request.form['beneficio']  # Captura a resposta do Beneficio
        imagem1 = request.files['imagem1']
        imagem2 = request.files['imagem2']
        signature_data = request.form['signature_data']  # Assinatura capturada

        # Verifica se o arquivo Excel fixo existe
        if not os.path.exists(FIXED_EXCEL_FILE):
            flash('O arquivo Excel modelo não foi encontrado no servidor.', 'error')
            return redirect(url_for('index'))

        # Carrega o arquivo Excel fixo
        wb = load_workbook(FIXED_EXCEL_FILE)
        sheet = wb.active  # Usa a primeira aba do arquivo Excel fixo

        # Preenche as células com os dados do formulário
        sheet['D7'] = nome
        sheet['D8'] = nr_edp
        sheet['F7'] = ticket
        sheet['C10'] = removido
        sheet['F10'] = instalado
        sheet['D48'] = beneficio  # Preenche uma célula com o Beneficio

        # Se 1 imagem for enviada
        if imagem1:
            image_filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(imagem1.filename))
            imagem1.save(image_filename)

            # Carregar a imagem e inserir na célula C62
            img = Image(image_filename)
            img.width, img.height = 750, 750  # Ajusta o tamanho da imagem
            sheet.add_image(img, 'C62')  # Insere a imagem na célula C62

        # Se 2 imagens forem enviadas
        if imagem2:
            image_filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(imagem2.filename))
            imagem2.save(image_filename)

            # Carregar a imagem e inserir na célula G62
            img = Image(image_filename)
            img.width, img.height = 750, 750  # Ajusta o tamanho da imagem
            sheet.add_image(img, 'G62')  # Insere a imagem na célula G62

        # Se a assinatura foi capturada
        if signature_data:
            # Remove o cabeçalho da string base64
            signature_data = signature_data.replace('data:image/png;base64,', '')
            signature_data = base64.b64decode(signature_data)

            # Salva a assinatura temporariamente
            signature_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'signature.png')
            with open(signature_image_path, 'wb') as f:
                f.write(signature_data)

            # Carrega a assinatura e insere na célula F47
            signature_img = Image(signature_image_path)
            signature_img.width, signature_img.height = 200, 100  # Ajusta o tamanho da assinatura
            sheet.add_image(signature_img, 'F47')

        # Nome do arquivo Excel modificado (baseado no nome do usuário para ser único)
        modified_excel_filename = f"{ticket}.xlsx"
        modified_excel_filepath = os.path.join(app.config['UPLOAD_FOLDER'], modified_excel_filename)

        # Salva as alterações no novo arquivo Excel
        wb.save(modified_excel_filepath)

        # Redireciona para a rota de download do arquivo modificado
        return redirect(url_for('download_file', filename=modified_excel_filename))

    return render_template('index.html')

# Rota para baixar o arquivo Excel preenchido
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
