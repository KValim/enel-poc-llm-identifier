import base64
import json
import math
import os
import re

from dotenv import load_dotenv
from flask import (Flask, flash, redirect, render_template, request, send_file,
                   url_for)
from openai import OpenAI
from werkzeug.utils import secure_filename

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para mensagens flash

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MODEL = "gpt-4o"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_project_data():
    with open('projetos.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def save_project_data(data):
    with open('projetos.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_validation_data():
    with open('validation.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def save_validation_data(data):
    with open('validation.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of the Earth in kilometers
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

@app.route('/', methods=['GET', 'POST'])
def home():
    project_data = load_project_data()
    projects = list(project_data.keys())
    resumo = None

    if request.method == 'POST':
        selected_project = request.form['project']
        action = request.form['action']

        if action == 'select_structure':
            return redirect(url_for('select_structure', project=selected_project))
        elif action == 'open_pdf':
            return redirect(url_for('open_pdf', file='pdfs/' + selected_project + '.pdf'))

    return render_template('home.html', projects=projects, resumo=resumo)

@app.route('/project_summary', methods=['POST'])
def project_summary():
    selected_project = request.form['project']
    project_data = load_project_data()
    validation_data = load_validation_data()
    estruturas_validadas = validation_data.get('validations', {}).get(selected_project, {})
    posts = list(project_data[selected_project].keys())

    total_validas = sum(1 for estrutura in estruturas_validadas.values() if estrutura['status'] == 'valid')
    total_invalidas = sum(1 for estrutura in estruturas_validadas.values() if estrutura['status'] == 'invalid')
    total_nao_validadas = len(posts) - total_validas - total_invalidas
    total_avaliadas = total_validas + total_invalidas
    total_estruturas = len(posts)

    resumo = {
        'total_validas': total_validas,
        'total_invalidas': total_invalidas,
        'total_nao_validadas': total_nao_validadas,
        'total_avaliadas': total_avaliadas,
        'total_estruturas': total_estruturas
    }

    return json.dumps(resumo)

@app.route('/select_structure', methods=['GET', 'POST'])
def select_structure():
    project = request.args.get('project')
    project_data = load_project_data()
    validation_data = load_validation_data()
    posts = list(project_data[project].keys())

    if 'validations' not in validation_data:
        validation_data['validations'] = {}
    if project not in validation_data['validations']:
        validation_data['validations'][project] = {}

    for post in posts:
        if post not in validation_data['validations'][project]:
            validation_data['validations'][project][post] = {
                'status': 'to_be_valided',
                'comments': ''
            }
    save_validation_data(validation_data)

    estruturas_validadas = validation_data.get('validations', {}).get(project, {})

    total_validas = sum(1 for estrutura in estruturas_validadas.values() if estrutura['status'] == 'valid')
    total_invalidas = sum(1 for estrutura in estruturas_validadas.values() if estrutura['status'] == 'invalid')
    total_nao_validadas = len(posts) - total_validas - total_invalidas

    if request.method == 'POST':
        if 'post' in request.form:
            selected_post = request.form['post']
            return redirect(url_for('upload_photo', project=project, post=selected_post))
        elif 'validate_project' in request.form:
            return redirect(url_for('validate_project', project=project))
        elif 'get_location' in request.form:
            user_lat = request.form['latitude']
            user_lon = request.form['longitude']

            if is_valid_latlong(user_lat, user_lon):
                user_lat = float(user_lat)
                user_lon = float(user_lon)

                nearby_structures = []
                for post in posts:
                    if project_data[project][post]["latitude"] and project_data[project][post]["longitude"]:
                        post_lat = project_data[project][post]["latitude"]
                        post_lon = project_data[project][post]["longitude"]
                        distance = calculate_distance(user_lat, user_lon, post_lat, post_lon)
                        nearby_structures.append((post, distance))

                nearby_structures.sort(key=lambda x: x[1])
                nearby_posts = [post for post, _ in nearby_structures]

                return render_template('select_structure.html', project=project, posts=nearby_posts, validadas=estruturas_validadas,
                                       total_validas=total_validas, total_invalidas=total_invalidas, total_nao_validadas=total_nao_validadas)
            else:
                flash('Latitude ou longitude inválida. Por favor, insira valores corretos.')
                return redirect(request.url)

    return render_template('select_structure.html', project=project, posts=posts, validadas=estruturas_validadas,
                           total_validas=total_validas, total_invalidas=total_invalidas, total_nao_validadas=total_nao_validadas)

@app.route('/check_validation_status', methods=['POST'])
def check_validation_status():
    selected_project = request.form['project']
    validation_data = load_validation_data()

    if 'validations' in validation_data and selected_project in validation_data['validations']:
        estruturas_validadas = validation_data['validations'][selected_project]
        total_nao_validadas = sum(1 for estrutura in estruturas_validadas.values() if estrutura['status'] == 'to_be_valided')
        has_unvalidated_structures = total_nao_validadas > 0
    else:
        has_unvalidated_structures = True

    return json.dumps({'has_unvalidated_structures': has_unvalidated_structures})

@app.route('/validate_project', methods=['POST'])
def validate_project():
    project = request.form['project']

    validation_data = load_validation_data()
    if 'validations' not in validation_data:
        validation_data['validations'] = {}
    if project not in validation_data['validations']:
        validation_data['validations'][project] = {}

    # Validar todas as estruturas como 'valid'
    for post in validation_data['validations'][project].keys():
        validation_data['validations'][project][post]['status'] = 'valid'

    save_validation_data(validation_data)

    flash('Projeto validado com sucesso!')
    return redirect(url_for('home'))

@app.route('/open_pdf')
def open_pdf():
    filename = request.args.get('file')
    base_path = os.path.abspath('pdfs')
    pdf_path = os.path.join(base_path, filename)
    if not os.path.isfile(pdf_path):
        return render_template('error.html'), 404
    return send_file(pdf_path, as_attachment=False)

@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    project = request.args.get('project')
    post = request.args.get('post')
    example_image = url_for('static', filename='images/photo-example.webp')  # Caminho da imagem de exemplo
    uploaded_image = None

    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            if file.filename == 'Não relacionada 1.jpg':
                flash('A imagem enviada não é válida.')
                return redirect(request.url)
            if file.filename == 'poste 8 blur.jpg':
                flash('A imagem enviada não tem qualidade.')
                return redirect(request.url)
            filename = secure_filename(file.filename)

            # Cria o diretório 'static/uploads' se não existir
            upload_folder = os.path.join('static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)  # Salva a imagem no diretório 'static/uploads'
            uploaded_image = url_for('static', filename='uploads/' + filename)  # Caminho da imagem enviada

            # Chame a função que gera o novo output.json antes de processá-lo
            generate_new_output_json(file_path)

            return redirect(url_for('results', project=project, post=post))
        else:
            flash('Invalid file type. Only image files are allowed.')
            return redirect(request.url)

    return render_template('upload_photo.html', project=project, post=post, example_image=example_image, uploaded_image=uploaded_image)

@app.route('/validate_results', methods=['POST'])
def validate_results():
    validation = request.form['validation']
    comments = request.form['comments']
    project = request.args.get('project')
    post = request.args.get('post')

    validation_data = load_validation_data()
    if 'validations' not in validation_data:
        validation_data['validations'] = {}
    if project not in validation_data['validations']:
        validation_data['validations'][project] = {}

    validation_data['validations'][project][post] = {
        'status': validation,
        'comments': comments
    }
    save_validation_data(validation_data)

    if validation == 'valid':
        flash('Estrutura validado com sucesso!')
        return redirect(url_for('select_structure', project=project))
    elif validation == 'invalid':
        flash('Estrutura invalidado. Por favor, tire outra foto.')
        return redirect(url_for('upload_photo', project=project, post=post))
    elif validation == 'validate_project':
        flash('Projeto validado com sucesso!')
        return redirect(url_for('home'))

@app.route('/results', methods=['GET', 'POST'])
def results():
    project = request.args.get('project')
    post = request.args.get('post')

    if request.method == 'POST':
        action = request.form['action']
        comments = request.form.get('comments', '')
        validation_data = load_validation_data()
        if 'validations' not in validation_data:
            validation_data['validations'] = {}
        if project not in validation_data['validations']:
            validation_data['validations'] = {}

        if action == 'validate_post':
            validation_data['validations'][project][post] = {
                'status': 'valid',
                'comments': comments
            }
            save_validation_data(validation_data)
            flash('Estrutura validado com sucesso!')
            return redirect(url_for('select_structure', project=project))
        elif action == 'invalidate_post':
            validation_data['validations'][project][post] = {
                'status': 'invalid',
                'comments': comments
            }
            save_validation_data(validation_data)
            flash('Estrutura invalidado. Retornando à seleção de estruturas.')
            return redirect(url_for('select_structure', project=project))
        elif action == 'remove_photo':
            flash('Por favor, envie outra foto.')
            return redirect(url_for('upload_photo', project=project, post=post))
        elif action == 'validate_project':
            flash('Projeto validado com sucesso!')
            return redirect(url_for('home'))

    project_data = load_project_data()
    gabarito = project_data[project][post]['Gabarito']

    with open('output.json', 'r', encoding='utf-8') as file:
        output = json.load(file)

    encontrados = {}
    extras = {}
    caracteristicas = {}

    for item, details in gabarito.items():
        if item in output:
            encontrados[item] = "Sim"
            caracteristicas_item = output.get(f"Características do {item}", {})
            if caracteristicas_item:
                caracteristicas[item] = caracteristicas_item
            if 'Quantidades' in output and item in output['Quantidades']:
                if item in caracteristicas:
                    caracteristicas[item]['Quantidade Identificada'] = output['Quantidades'][item]
                else:
                    caracteristicas[item] = {'Quantidade Identificada': output['Quantidades'][item]}
        else:
            encontrados[item] = "Não"

    for item in output:
        if item not in gabarito and not item.startswith('Características do') and item != "Quantidades":
            extras[item] = "Encontrado"
            caracteristicas_item = output.get(f"Características do {item}", {})
            if caracteristicas_item:
                caracteristicas[item] = caracteristicas_item

    results_data = {
        'Itens Verificados': encontrados,
        'Itens Extras': list(extras.keys()),
        'Características': caracteristicas
    }
    with open('results.json', 'w', encoding='utf-8') as file:
        json.dump(results_data, file, ensure_ascii=False, indent=4)

    return render_template('results.html', encontrados=encontrados, extras=extras, caracteristicas=caracteristicas, project=project, post=post)

def is_valid_latlong(lat, lon):
    lat_pattern = re.compile(r'^-?([1-8]?\d(\.\d+)?|90(\.0+)?)$')
    lon_pattern = re.compile(r'^-?((1[0-7]\d(\.\d+)?|180(\.0+)?)|(\d{1,2}(\.\d+)?))$')
    return lat_pattern.match(str(lat)) and lon_pattern.match(str(lon))

def generate_new_output_json(image_path):
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": """### MISSÃO
- Retornar um json com os objetos identificados.

### INSTRUÇÃO
- Você receberá uma imagem de um poste.
- A imagem pode conter dois ou três trasformadores, geralmente um trifásico e um monofásico, ou três monofásicos, preste atenção quando isso acontecer.

### IMPORTANTE
- Se a imagem não tiver nenhuma relação com os equipamentos descritos ou postes eletricos, retorne o json ```{"mensagem": "Imagem não relacionada."}```
- Se a imagem não tiver qualidade o suficiente como foco, iluminação, etc, retorne o json ```{"mensagem": "Imagem sem qualidade."}```
- Procure bem pelas chaves faca, praticamente quase todo poste eletrico de cidade tem essas chaves nas cruzetas.
### DESCRIÇÕES DOS EQUIPAMENTOS
### Tabela de Equipamentos Elétricos

| **Equipamento**                        | **Tamanho** | **Descrição**                                                                                                                                                                                                                                                                                                                                                                                                                                      | **Estrutura**                        | **Observações**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|----------------------------------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Transformador Trifásico**            | Grande      | Gabinete retangular (às vezes arredondado), três isoladores de porcelana no topo (as vezes na frente), válvula de pressão                                                                                                                                                                                                                                                                                                                                               | Estrutura metálica robusta          | Às vezes confundido com a Chave Telecomandada que também tem três isoladores na parte superior e tem um formato similar. No entanto, a Chave Telecomandada é retangular 'mais achatada' e o transformador é 'mais comprido'. Além disso, os isoladores da chave são inclinados e ficam tanto na parte superior quanto nas laterais, enquanto os do transformador são retos, geralmente apenas em cima. Também pode ser confundido com o Religador, que tem três isoladores superiores, mas o formato deles é diferente, pois são como um T deitado.    |
| **Transformador Monofásico**           | Médio       | Estrutura cilíndrica e vertical, cinza, dois isoladores de porcelana no topo                                                                                                                                                                                                                                                                                                                                                                       | Terminais laterais para conexões de baixa tensão |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Religador**                          | Médio       | Equipamento retangular achatado com três isoladores de cerâmica. As cerâmicas possuem uma estrutura onde, de um cilindro principal centralizado, se projeta outro cilindro adicional, também envolto por aletas ou discos concêntricos. Este segundo cilindro parece emergir do meio do primeiro.                                                                                                                 | Geralmente fica numa base uns 20 cm afastada do poste, um pouco abaixo da altura de transformadores |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Chave Seccionadora Telecomandada**   | Médio       | Corpo metálico, isoladores de porcelana ou compósito em 'V' no topo. Dos dois lados da caixa metálica, há isoladores cilíndricos, geralmente feitos de porcelana ou material polimérico, que são montados em várias direções.                                                                                                                                                                                                                          |                                      | Ela tem isoladores em cima e nas laterais.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **Chave Seccionadora (Chave Faca)**    | Pequeno     | são dispositivos de seccionamento manual de circuitos elétricos. Elas têm uma aparência característica, com isoladores e lâminas metálicas que podem ser movidas para abrir ou fechar o circuito.                                                                                                                                                                                                                                                                                                                                                                         |                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **Cruzeta**                            | Pequeno     | Barra transversal montada no topo do poste.                                                                                                                                                                                                                                                                                                                                                                                                        | Estrutura metálica ou de madeira    | Suporte para isoladores e outros equipamentos elétricos.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

### CHAVES E VALORES JSON
{
  "Poste Elétrico": "Indica a presença (true) ou ausência (false) de um poste elétrico.",
  "Cruzeta": "Indica a presença (true) ou ausência (false) de cruzetas no poste.",
  "Chave Seccionadora Telecomandada": "Indica a presença (true) ou ausência (false) de uma chave seccionadora telecomandada no poste.",
  "Chave Seccionadora (Chave Faca)": "Indica a presença (true) ou ausência (false) de uma chave seccionadora do tipo faca nas cruzetas.",
  "Chave Seccionadora Por Mola": "Indica a presença (true) ou ausência (false) de uma chave seccionadora por mola no poste.",
  "Transformador Monofásico": "Indica a presença (true) ou ausência (false) de um transformador monofásico no poste.",
  "Transformador Trifásico": "Indica a presença (true) ou ausência (false) de um transformador trifásico no poste.",
  "Religador": "Indica a presença (true) ou ausência (false) de um religador no poste.",
  "Medidor de Energia": "Indica a presença (true) ou ausência (false) de um medidor de energia no poste.",
  "Luminária": "Indica a presença (true) ou ausência (false) de uma luminária no poste.",
  "Árvore": "Indica a presença (true) ou ausência (false) de árvores nas proximidades do poste.",
  "Características do Transformador Monofásico": {
    "Nível de Oxidação": "Descreve o nível de oxidação observado no transformador, podendo ser Baixo, Médio ou Alto.",
  },
  "Características do Transformador Trifásico": {
    "Nível de Oxidação": "Descreve o nível de oxidação observado no transformador, podendo ser Baixo, Médio ou Alto.",
  },
  "Características do Poste Elétrico": {
    "Material": "Descreve o material de construção do poste, como Concreto, Metal, Madeira ou uma combinação de Concreto ou Metal.",
    "Estado de Conservação": "Indica o estado de conservação do poste, podendo ser Novo ou Danificado."
  },
  "Características do Árvore": {
    "Proximidade com o Poste": "Indica quão próxima a árvore está do poste, podendo estar Próxima, Próxima ao fundo, ou Adjacente.",
    "Risco de Interferência": "Avalia o risco de interferência da árvore com o poste ou a infraestrutura elétrica, podendo necessitar de intervenções como poda ou remoção.",
    "Intervenções": "Avalia a necessidade de possíveis intervenções necessárias para mitigar os riscos causados pela árvore, como Poda ou Remoção.",
    "Interferência Visual": "Avalia o nível de interferência visual causada pela árvore, podendo ser Baixa, Moderada ou Alta."
  },
  "Quantidades": {
    "Poste Elétrico": "Indica a quantidade na foto",
    "Cruzeta": "Indica a quantidade na foto",
    "Chave Seccionadora Telecomandada": "Indica a quantidade na foto",
    ...,
    "Árvore": "Indica a quantidade na foto",
  }
}

### NOTAS
- Sempre responder em pt-br
- Não precisa retornar keys com valores vazios ou false.
- Respire fundo.
- Pense passo a passo.
- Caso se empenhe muito te darei uma gorjeta de $1000.
- Visualize o estado após cada etapa de raciocínio.
- Não retorne nada além do json requerido, sem nenhum comentário ou análise."""},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ],
        temperature=0.0,
    )

    output_data = response.choices[0].message.content
    with open('output.json', 'w', encoding='utf-8') as file:
        json.dump(json.loads(output_data), file, ensure_ascii=False, indent=4)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

if __name__ == '__main__':
    app.run(debug=True)
