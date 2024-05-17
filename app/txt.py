import os

def listar_arquivos(diretorio, ignorar):
    """Percorre todos os arquivos em um diretório, ignorando os especificados.
    
    Args:
        diretorio (str): Caminho do diretório para começar a busca.
        ignorar (list): Lista de nomes de arquivos ou pastas para ignorar.
        
    Returns:
        list: Lista de caminhos de arquivos que não estão ignorados.
    """
    arquivos_encontrados = []
    for raiz, pastas, arquivos in os.walk(diretorio):
        # Filtrar as pastas ignoradas diretamente na listagem de pastas
        pastas[:] = [p for p in pastas if p not in ignorar]
        for arquivo in arquivos:
            if arquivo not in ignorar:
                caminho_completo = os.path.join(raiz, arquivo)
                arquivos_encontrados.append(caminho_completo)
    return arquivos_encontrados

def escrever_conteudo_arquivos(arquivos, nome_arquivo_saida='saida.txt'):
    """Escreve o conteúdo de vários arquivos em um único arquivo de saída com um formato específico.
    
    Args:
        arquivos (list): Lista de caminhos de arquivos para ler.
        nome_arquivo_saida (str): Nome do arquivo de saída para escrever o conteúdo.
    """
    with open(nome_arquivo_saida, 'w', encoding='utf-8') as arquivo_saida:
        for arquivo in arquivos:
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    arquivo_saida.write(f"{os.path.basename(arquivo)}\n```\n{conteudo}\n```\n\n")
            except Exception as e:
                print(f"Erro ao ler o arquivo {arquivo}: {e}")

# Diretório root a partir do qual o script inicia a leitura
diretorio_root = os.path.dirname(os.path.realpath(__file__))

# Arquivos e pastas a serem ignorados
ignorar = [
    '__pycache__', 'txt.py',
    '.env', 'venv', '.venv', 'requirements.txt',
    'campeonato-lifeilin-414320-382bc3fe5429.json',
    '.git', '.gitattributes', '.gitignore', 'README.md', 'LICENSE',
    'static', 'db.sqlite3',  'txt.py' 'migrations',
    '.notes',
    '_.ipynb', 'modules', 'env.examples',
    'saida.txt'
    ]

# Listar arquivos
arquivos_para_leitura = listar_arquivos(diretorio_root, ignorar)

# Escrever conteúdo dos arquivos em um arquivo de saída com o formato especificado
escrever_conteudo_arquivos(arquivos_para_leitura)
