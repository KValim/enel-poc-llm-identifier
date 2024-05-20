"""
Module for generating a structured report based on data analysis of electrical pole components.

This module handles the creation of a textual report that describes the status and 
specific characteristics of electrical pole components based on analyzed data. 
It includes handling for different component types and special characteristics like 
the location on the pole and oxidation levels.

Functions:
    generate_report(dict_desc, data) -> str: Generates a formatted report from dictionary descriptions and data.
"""

import os
import sys
from typing import Dict, List
from dotenv import load_dotenv

from modules.geoloc import IPInfo

load_dotenv()
IP_INFO_TOKEN = os.getenv('IP_INFO_TOKEN')

# Setting UTF-8 encoding for the environment
os.environ["PYTHONIOENCODING"] = "utf-8"

# Ensure stdout handles UTF-8 encoding
if sys.version_info[0] >= 3:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

# Dictionary describing each component and photo characteristics
dictionary = {
    "Foto": {
        "Qualidade": "Indica se a qualidade da foto é Ruim ou Boa",
        "Foco": "Determina se a foto está com foco adequado ou sem foco",
        "Visibilidade": "Descreve se a visibilidade dos objetos na foto é Parcial ou Completa",
        "Ângulos Necessários": "Avalia se são necessários mais ângulos para uma análise completa ou se os ângulos capturados são suficientes",
        "Iluminação": "Indica se a iluminação da foto é Adequada ou Inadequada para análise"
    },
    "Chave Seccionadora Telecomandada": "Presença de Chave Seccionadora Telecomandada",
    "Chave Seccionadora (Chave Faca)": "Presença de Chave Seccionadora do tipo faca",
    "Chave Seccionadora Por Mola": "Presença de Chave Seccionadora por mola",
    "Transformador Monofásico": "Presença de Transformador Monofásico",
    "Transformador Trifásico": "Presença de Transformador Trifásico",
    "Religador": "Presença de Religador",
    "Medidor de Energia": "Presença de Medidor de Energia",
    "Luminária": "Presença de Luminária",
    "Árvore": "Presença de Árvores nas proximidades",
    "Características da Chave": {
        "Localização no Poste": "Localização da Chave no Poste"
    },
    "Características do Transformador": {
        "Localização no Poste": "Localização do Transformador no Poste",
        "Nível de Oxidação": "Nível de Oxidação do Transformador"
    },
    "Características do Poste Elétrico": {
        "Material": "Material do Poste",
        "Estado de Conservação": "Estado de Conservação do Poste"
    },
    "Características da Luminária": {
        "Localização no Poste": "Localização da Luminária no Poste"
    },
    "Presença de Árvore": {
        "Proximidade com o Poste": "Proximidade da Árvore com o Poste",
        "Risco de Interferência": "Risco de Interferência da Árvore",
        "Intervenções": "Intervenções necessárias devido à Árvore",
        "Interferência Visual": "Interferência Visual causada pela Árvore"
    }
}

# Data returned from the LLM
llm_data = {
    "Foto": {
        "Qualidade": "Boa",
        "Foco": "Adequado",
        "Visibilidade": "Completa",
        "Ângulos Necessários": "Suficientes",
        "Iluminação": "Adequada"
    },
    "Transformador Monofásico": True,
    "Transformador Trifásico": True,
    "Religador": True,
    "Quantidades": {
        "Transformador Monofásico": 1,
        "Transformador Trifásico": 1
    },
    "Características do Transformador Monofásico": {
        "Localização no Poste": "Centro",
        "Nível de Oxidação": "Médio"
    },
    "Características do Transformador Trifásico": {
        "Localização no Poste": "Centro",
        "Nível de Oxidação": "Baixo"
    }
}


def generate_report(dict_desc: Dict[str, Dict[str, str]], data: Dict[str, Dict[str, str]]) -> str:
    """
    Generates a formatted report from given dictionary descriptions and data.

    Args:
        dict_desc (Dict[str, Dict[str, str]]): Dictionary containing descriptions and labels.
        data (Dict[str, Dict[str, str]]): Data dictionary containing the actual values for the components.

    Returns:
        str: A formatted string report with evaluated data.
    """
    report: List[str] = []

    # Analyzing the photo characteristics
    report.append("Análise da Foto:")
    for key, description in dict_desc["Foto"].items():
        value = data["Foto"].get(key, "Não disponível")
        report.append(f"  - {description.split(',')[0]}: {value}.")

    # Analyzing general components of the pole
    report.append("\nComponentes Identificados no Poste:")
    excluded_categories = [
        "Foto", "Características da Chave", "Características do Transformador",
        "Características do Poste Elétrico", "Características da Luminária", "Presença de Árvore"
    ]
    for component, present in data.items():
        if component in dict_desc and component not in excluded_categories:
            description = dict_desc[component]
            status = "Presente" if present else "Ausente"
            report.append(f"  - {description}: {status}.")

    # Detailing specific characteristics of components
    report.append("\nDetalhes Específicos dos Componentes:")
    for feature, details in data.items():
        if feature.startswith("Características") or feature == "Presença de Árvore":
            report.append(f"\n\tDetalhes de {feature.replace('Características de ', '')}:")
            for key, value in details.items():
                description = dict_desc.get(feature, {}).get(key, key)
                report.append(f"  - {description}: {value}.")

    return "\n".join(report)

def main():
    """Main function."""
    # Retrives the location information of the current device
    ip_info = IPInfo(access_token=IP_INFO_TOKEN)
    public_ip = ip_info.get_public_ip()
    location_info = ip_info.get_ip_location(public_ip)
    print(f"Localização: {location_info}")
    print()

    # Run report generator
    print(generate_report(dictionary, llm_data))

if __name__ == "__main__":
    main()
