"""
This module provides the Flask application routes and logic for managing project validations,
including selecting structures, uploading and validating photos, and generating project summaries.
It integrates OpenAI for generating new output JSON files based on uploaded photos, and uses
utility functions for various validation and data handling tasks.

Modules:
    json: For handling JSON data.
    os: For interacting with the operating system.
    dotenv: For loading environment variables from a .env file.
    flask: For creating the web application and handling routes.
    openai: For integrating OpenAI API.
    werkzeug.utils: For handling secure filenames.

Functions:
    home(): Displays the list of projects and handles project selection and PDF opening actions.
    project_summary(): Returns a summary of the project validation status.
    select_structure(): Allows the selection of a structure within a project for validation.
    validate_project(): Validates all structures within a selected project.
    open_pdf(): Opens and displays a PDF file related to a project.
    upload_photo(): Handles the upload and validation of a photo for a specific structure in a project.
    results(): Displays the validation results of a structure and handles validation actions.
    check_validation_status(): Checks if there are any unvalidated structures in a project.
"""

import json
import os

from dotenv import load_dotenv
from flask import (
    Blueprint, flash, redirect,
    render_template, request, send_file, url_for
    )
from openai import OpenAI
from werkzeug.utils import secure_filename

from .utils import (
    allowed_file, calculate_distance,
    generate_new_output_json, is_valid_latlong,
    load_project_data, load_validation_data,
    save_validation_data, save_project_data,
    order_structures_by_latlong, get_next_post
    )

load_dotenv()

main_bp = Blueprint('main', __name__, template_folder='templates')
validation_bp = Blueprint('validation', __name__, template_folder='templates')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@main_bp.route('/', methods=['GET', 'POST'])
def home():
    """
    Home route that displays the list of projects and handles project selection and PDF opening actions.
    Methods: GET, POST
    """

    project_data = load_project_data()
    projects = list(project_data.keys())
    resumo = None

    if request.method == 'POST':
        selected_project = request.form['project']
        action = request.form['action']

        if action == 'select_structure':
            return redirect(url_for('validation.select_structure', project=selected_project))
        elif action == 'open_pdf':
            return redirect(url_for('validation.open_pdf', file='instance/pdfs/' + selected_project + '.pdf'))

    return render_template('home.html', projects=projects, resumo=resumo)

@validation_bp.route('/project_summary', methods=['GET'])
def project_summary():
    """
    Route to display the project summary page.
    Methods: GET
    """
    project = request.args.get('project')
    project_data = load_project_data()
    validation_data = load_validation_data()
    
    if project in project_data:
        estruturas_validadas = validation_data.get('validations', {}).get(project, {})
        posts = list(project_data[project].keys())

        total_extras = sum(1 for estrutura in estruturas_validadas.values() if estrutura['status'] == 'extra')
        total_validas = sum(1 for estrutura in estruturas_validadas.values() if estrutura['status'] == 'valid')
        total_invalidas = sum(1 for estrutura in estruturas_validadas.values() if estrutura['status'] == 'invalid')
        total_nao_validadas = len(posts) - total_validas - total_invalidas - total_extras
        total_avaliadas = total_validas + total_invalidas
        total_estruturas = len(posts) - total_extras

        resumo = {
            'total_validas': total_validas,
            'total_invalidas': total_invalidas,
            'total_nao_validadas': total_nao_validadas,
            'total_avaliadas': total_avaliadas,
            'total_estruturas': total_estruturas,
            'total_extras': total_extras
        }

        return render_template('project_summary.html', project=project, resumo=resumo)
    else:
        flash('Projeto não encontrado.')
        return redirect(url_for('main.home'))

@validation_bp.route('/select_structure', methods=['GET', 'POST'])
def select_structure():
    project = request.args.get('project')
    project_data = load_project_data()
    validation_data = load_validation_data()
    posts = list(project_data[project].keys())

    # Excluir estruturas com status 'extra'
    posts = [post for post in posts if validation_data['validations'][project].get(post, {}).get('status') != 'extra']

    if 'validations' not in validation_data:
        validation_data['validations'] = {}
    if project not in validation_data['validations']:
        validation_data['validations'][project] = {}

    for post in posts:
        if post not in validation_data['validations'][project]:
            validation_data['validations'][project][post] = {
                'status': 'to_be_validated',
                'comments': ''
            }
    save_validation_data(validation_data)

    # Ordenar estruturas por lat long
    ordered_posts = order_structures_by_latlong({post: project_data[project][post] for post in posts})

    total_validas = sum(1 for estrutura in validation_data['validations'][project].values() if estrutura['status'] == 'valid')
    total_invalidas = sum(1 for estrutura in validation_data['validations'][project].values() if estrutura['status'] == 'invalid')
    total_nao_validadas = len(posts) - total_validas - total_invalidas

    if request.method == 'POST':
        if 'start_validation' in request.form:
            side = request.form['side']
            if side == 'B':
                ordered_posts = ordered_posts[::-1]  # Reverter a ordem dos posts para o lado B
            first_post = ordered_posts[0]
            direction = 'forward' if side == 'A' else 'backward'
            return redirect(url_for('validation.upload_photo', project=project, post=first_post, direction=direction))
        elif 'post' in request.form:
            selected_post = request.form['post']
            return redirect(url_for('validation.upload_photo', project=project, post=selected_post))

    return render_template('select_structure.html', project=project, posts=ordered_posts, validadas=validation_data['validations'][project],
                           total_validas=total_validas, total_invalidas=total_invalidas, total_nao_validadas=total_nao_validadas)

@validation_bp.route('/validate_project', methods=['POST'])
def validate_project():
    """
    Route to validate all structures within a selected project.
    Methods: POST
    """
    project = request.form['project']

    validation_data = load_validation_data()
    if 'validations' not in validation_data:
        validation_data['validations'] = {}
    if project not in validation_data['validations']:
        validation_data['validations'][project] = {}

    unvalidated_structures = {post: data for post, data in validation_data['validations'][project].items() if data['status'] == 'to_be_validated'}

    if not unvalidated_structures:
        flash(f'Projeto {project} Validado com sucesso!')
        return redirect(url_for('main.home'))
    else:
        flash('Ainda existem estruturas não validadas. Confirme a validação manualmente.')
        return redirect(url_for('validation.project_summary', project=project))


@validation_bp.route('/open_pdf')
def open_pdf():
    """
    Route to open and display a PDF file related to a project.
    Methods: GET
    """

    filename = request.args.get('file')
    base_path = os.path.abspath('instance/pdfs')
    pdf_path = os.path.join(base_path, filename)
    if not os.path.isfile(pdf_path):
        return render_template('error.html'), 404
    return send_file(pdf_path, as_attachment=False)

@validation_bp.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    project = request.args.get('project')
    post = request.args.get('post')
    direction = request.args.get('direction')
    new_structure = request.args.get('new_structure', 'False').lower() == 'true'
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    example_image = url_for('static', filename='images/photo-example.webp')
    uploaded_image = None

    if request.method == 'POST':
        # Check if a file is uploaded
        if 'photo' not in request.files:
            flash('Nenhuma foto selecionada.')
            return redirect(request.url)

        file = request.files['photo']

        if file.filename == '':
            flash('Nenhuma foto selecionada.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Cria o diretório 'static/uploads' se não existir
            upload_folder = os.path.join('app', 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            uploaded_image = url_for('static', filename=f'uploads/{filename}')

            # Process the image using OpenAI API
            generate_new_output_json(file_path)
            
            # Verifique o conteúdo do JSON de saída
            with open('instance/output.json', 'r', encoding='utf-8') as file:
                output_data = file.read()  # Leia o conteúdo como string

            # Verificar se as frases específicas existem no conteúdo do JSON
            if "Imagem não relacionada." in output_data:
                flash('A imagem enviada não é válida.')
                return redirect(request.url)
            elif "Imagem sem qualidade." in output_data:
                flash('A imagem enviada não tem qualidade.')
                return redirect(request.url)

            # Redirect to results page after processing the image
            return redirect(url_for('validation.results', project=project, post=post, new_structure=new_structure, latitude=latitude, longitude=longitude, direction=direction))

        else:
            flash('Formato de arquivo inválido. Apenas imagens são permitidas.')
            return redirect(request.url)
    return render_template('upload_photo.html', project=project, post=post, example_image=example_image, uploaded_image=uploaded_image, new_structure=new_structure)


@validation_bp.route('/add_structure_to_project', methods=['POST'])
def add_structure_to_project():
    """
    Route to add the new structure to the project.
    Methods: POST
    """
    project = request.form.get('project')
    post = request.form.get('post')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    # Debugging statements
    print(f"Received latitude: {latitude}")
    print(f"Received longitude: {longitude}")

    if not latitude or not longitude:
        flash('Latitude e Longitude são obrigatórias.')
        return redirect(url_for('validation.select_structure', project=project))

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        flash('Latitude e Longitude devem ser números válidos.')
        return redirect(url_for('validation.select_structure', project=project))

    # Add the new structure to the project data
    project_data = load_project_data()
    if project not in project_data:
        project_data[project] = {}
    if post not in project_data[project]:
        project_data[project][post] = {
            "latitude": latitude,
            "longitude": longitude,
            "Gabarito": {}
        }
        save_project_data(project_data)

        # Add the new structure to the validation data
        validation_data = load_validation_data()
        if 'validations' not in validation_data:
            validation_data['validations'] = {}
        if project not in validation_data['validations']:
            validation_data['validations'][project] = {}
        validation_data['validations'][project][post] = {
            'status': 'extra',
            'comments': ''
        }
        save_validation_data(validation_data)

        flash(f'Nova estrutura "{post}" adicionada com sucesso ao projeto "{project}"!')

    return redirect(url_for('validation.project_summary', project=project))


@validation_bp.route('/results', methods=['GET', 'POST'])
def results():
    project = request.args.get('project')
    post = request.args.get('post')
    new_structure = request.args.get('new_structure', 'False').lower() == 'true'
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    direction = request.args.get('direction', 'forward')

    if request.method == 'POST':
        action = request.form['action']
        comments = request.form.get('comments', '')
        validation_data = load_validation_data()
        project_data = load_project_data()

        if 'validations' not in validation_data:
            validation_data['validations'] = {}
        if project not in validation_data['validations']:
            validation_data['validations'][project] = {}

        if action == 'validate_post':
            validation_data['validations'][project][post] = {
                'status': 'valid',
                'comments': comments
            }
            save_validation_data(validation_data)
            if new_structure:
                if project not in project_data:
                    project_data[project] = {}
                project_data[project][post] = {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                    "Gabarito": {}
                }
                save_project_data(project_data)
                flash('Nova estrutura validada e adicionada ao projeto com sucesso!')
            else:
                flash('Estrutura validada com sucesso!')
            next_post = get_next_post(project, post, direction)
            if next_post:
                return redirect(url_for('validation.upload_photo', project=project, post=next_post, direction=direction))
            else:
                flash('Todas as estruturas foram avaliadas.')
                return redirect(url_for('validation.project_summary', project=project))

        elif action == 'invalidate_post':
            validation_data['validations'][project][post] = {
                'status': 'invalid',
                'comments': comments
            }
            save_validation_data(validation_data)
            flash('Estrutura invalidada. Retornando à seleção de estruturas.')
            next_post = get_next_post(project, post, direction)
            if next_post:
                return redirect(url_for('validation.upload_photo', project=project, post=next_post, direction=direction))
            else:
                flash('Todas as estruturas foram avaliadas.')
                return redirect(url_for('validation.project_summary', project=project))

        elif action == 'remove_photo':
            flash('Por favor, envie outra foto.')
            return redirect(url_for('validation.upload_photo', project=project, post=post, new_structure=new_structure, latitude=latitude, longitude=longitude, direction=direction))

    validation_data = load_validation_data()
    project_data = load_project_data()

    with open('instance/output.json', 'r', encoding='utf-8') as file:
        output = json.load(file)

    encontrados = {}
    caracteristicas = {}
    extras = {}
    
    if new_structure:
        for item in output:
            if not item.startswith('Características do') and item != "Quantidades":
                encontrados[item] = "Encontrado"
                caracteristicas_item = output.get(f"Características do {item}", {})
                if caracteristicas_item:
                    caracteristicas[item] = caracteristicas_item
    else:
        gabarito = project_data[project][post]['Gabarito']

        for item, _ in gabarito.items():
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

    with open('instance/results.json', 'w', encoding='utf-8') as file:
        json.dump(results_data, file, ensure_ascii=False, indent=4)

    return render_template('results.html', encontrados=encontrados, extras=extras, caracteristicas=caracteristicas, project=project, post=post, new_structure=new_structure)


@validation_bp.route('/check_validation_status', methods=['POST'])
def check_validation_status():
    """
    Endpoint to check if there are any unvalidated structures in a project.
    Methods: POST
    """

    project = request.form['project']
    validation_data = load_validation_data()
    estruturas_validadas = validation_data.get('validations', {}).get(project, {})

    has_unvalidated_structures = any(estrutura['status'] == 'to_be_validated' for estrutura in estruturas_validadas.values())

    return json.dumps({'has_unvalidated_structures': has_unvalidated_structures})

@validation_bp.route('/add_new_structure', methods=['GET', 'POST'])
def add_new_structure():
    """
    Route to add a new structure to the project.
    Methods: GET, POST
    """
    project = request.args.get('project')

    if request.method == 'POST':
        new_structure = request.form.get('new_structure')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if not new_structure or not latitude or not longitude:
            flash('Todos os campos são obrigatórios.')
            return redirect(url_for('validation.add_new_structure', project=project))

        # Carregar os dados de validação
        validation_data = load_validation_data()

        # Contar o número de novas estruturas já existentes no projeto
        existing_new_structures = [key for key in validation_data['validations'].get(project, {}) if key.startswith('Nova Estrutura')]
        new_structure_number = len(existing_new_structures) + 1
        new_structure_name = f"Nova Estrutura {new_structure_number}"

        flash(f'Nova estrutura "{new_structure_name}" iniciando validação!')
        return redirect(url_for('validation.upload_photo', project=project, post=new_structure_name, new_structure=True, latitude=latitude, longitude=longitude))

    return render_template('add_new_structure.html', project=project)

@validation_bp.route('/add_and_upload', methods=['POST'])
def add_and_upload():
    """
    Route to generate a new structure name and latitude/longitude,
    then redirect to the upload photo page without saving to the database.
    Methods: POST
    """
    project = request.form['project']

    # Carregar os dados de validação
    validation_data = load_validation_data()
    
    # Contar o número de novas estruturas já existentes no projeto
    existing_new_structures = [key for key in validation_data['validations'].get(project, {}) if key.startswith('Nova Estrutura')]
    new_structure_number = len(existing_new_structures) + 1
    new_structure_name = f"Nova Estrutura {new_structure_number}"

    # Obter latitude e longitude automaticamente (simulando com valores fixos ou usando lógica real)
    latitude = request.form.get('latitude', '-23.550520')
    longitude = request.form.get('longitude', '-46.633308')

    # Redirecionar para upload de foto com parâmetros necessários
    return redirect(url_for('validation.upload_photo', project=project, post=new_structure_name, new_structure=True, latitude=latitude, longitude=longitude))
