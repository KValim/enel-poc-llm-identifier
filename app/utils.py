"""
This module provides various utility functions for handling file validation, project data loading and saving,
distance calculation, latitude and longitude validation, and image processing with OpenAI integration.

Modules:
    base64: For encoding images to base64 strings.
    json: For handling JSON data.
    math: For performing mathematical operations.
    os: For interacting with the operating system.
    re: For regular expression operations.
    openai: For integrating OpenAI API.

Functions:
    allowed_file(filename): Checks if a file is allowed based on its extension.
    load_project_data(): Loads project data from the 'projetos.json' file.
    save_project_data(data): Saves project data to the 'projetos.json' file.
    load_validation_data(): Loads validation data from the 'validation.json' file.
    save_validation_data(data): Saves validation data to the 'validation.json' file.
    calculate_distance(lat1, lon1, lat2, lon2): Calculates the distance between two geographic coordinates.
    is_valid_latlong(lat, lon): Checks if the provided latitude and longitude are valid.
    generate_new_output_json(image_path): Generates a new output JSON based on the provided image.
    encode_image(image_path): Encodes an image to a base64 string.
"""

import base64
import json
import math
import os
import re

from openai import OpenAI

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if a file is allowed based on its extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file is allowed, False otherwise.
    """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_project_data():
    """Load project data from the 'projetos.json' file.

    Returns:
        dict: A dictionary containing the project data.
    """

    with open('instance/projetos.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def save_project_data(data):
    """Save project data to the 'projetos.json' file.

    Args:
        data (dict): The project data to save.
    """

    with open('instance/projetos.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_validation_data():
    """Load validation data from the 'validation.json' file.

    Returns:
        dict: A dictionary containing the validation data.
    """

    with open('instance/validation.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def save_validation_data(data):
    """Save validation data to the 'validation.json' file.

    Args:
        data (dict): The validation data to save.
    """

    with open('instance/validation.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two geographic coordinates.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.

    Returns:
        float: The distance between the two points in kilometers.
    """

    r = 6371.0  # Radius of the Earth in kilometers
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = r * c
    return distance

def is_valid_latlong(lat, lon):
    """Check if the provided latitude and longitude are valid.

    Args:
        lat (str): Latitude to check.
        lon (str): Longitude to check.

    Returns:
        bool: True if both latitude and longitude are valid, False otherwise.
    """

    lat_pattern = re.compile(r'^-?([1-8]?\d(\.\d+)?|90(\.0+)?)$')
    lon_pattern = re.compile(r'^-?((1[0-7]\d(\.\d+)?|180(\.0+)?)|(\d{1,2}(\.\d+)?))$')
    return lat_pattern.match(str(lat)) and lon_pattern.match(str(lon))

def generate_new_output_json(image_path):
    """Generate a new output JSON based on the provided image.

    Args:
        image_path (str): The path to the image file.

    Returns:
        None
    """

    base64_image = encode_image(image_path)
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """### MISSÃO
- Retornar um json com os objetos identificados.

### INSTRUÇÃO
- Você receberá uma imagem de um poste.
- A imagem pode conter dois ou três trasformadores, geralmente um trifásico e um monofásico, ou três monofásicos, preste atenção quando isso acontecer.

### IMPORTANTE
- Se a imagem não tiver nenhuma relação com os equipamentos descritos ou postes eletricos, retorne o json {"mensagem": "Imagem não relacionada."}
- Se a imagem não tiver qualidade o suficiente como foco, iluminação, etc, retorne o json {"mensagem": "Imagem sem qualidade."}
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

    if not response.choices:
        with open('instance/output.json', 'w', encoding='utf-8') as file:
            json.dump({"mensagem": "Erro na resposta da API. Por favor, tente novamente."}, file, ensure_ascii=False, indent=4)
        return

    output_data = response.choices[0].message.content.strip()

    with open('instance/output.txt', 'w', encoding='utf-8') as file:
        file.write(output_data)

    if not output_data:
        with open('instance/output.json', 'w', encoding='utf-8') as file:
            json.dump({"mensagem": "Erro na resposta da API. Por favor, tente novamente."}, file, ensure_ascii=False, indent=4)
        return

    json_match = re.search(r'```json\s*(\{.*\})\s*```', output_data, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = output_data

    try:
        json_str = json_str.strip()
        if json_str.startswith("```json"):
            json_str = json_str[6:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        json_str = json_str.strip()

        output_json = json.loads(json_str)
    except json.JSONDecodeError:
        with open('instance/json_error_log.txt', 'w', encoding='utf-8') as file:
            file.write(json_str)
        with open('instance/output.json', 'w', encoding='utf-8') as file:
            json.dump({"mensagem": "Erro ao processar a resposta da API. Por favor, tente novamente."}, file, ensure_ascii=False, indent=4)
        return

    with open('instance/output.json', 'w', encoding='utf-8') as file:
        json.dump(output_json, file, ensure_ascii=False, indent=4)


def encode_image(image_path):
    """Encode an image to a base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded string of the image.
    """

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
