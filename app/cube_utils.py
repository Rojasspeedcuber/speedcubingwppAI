import os
import json
import re

# Diretório base para imagens
IMAGES_DIR = 'imagens_algoritmos'

# Carregar os algoritmos
with open('algs.json', 'r') as f:
    ALGORITHMS = json.load(f)

def get_algorithm(category: str, case: str) -> str:
    """
    Obter o algoritmo para um caso específico
    
    Args:
        category: F2L, OLL ou PLL
        case: O caso específico (ex: "Caso 01", "Caso U1", etc)
    
    Returns:
        O algoritmo correspondente ou None se não encontrado
    """
    if category not in ALGORITHMS:
        return None
    
    if case in ALGORITHMS[category]:
        return ALGORITHMS[category][case]
    
    # Tentativa alternativa para lidar com formatação diferente
    if case.startswith("Caso "):
        case_num = case[5:]
        if len(case_num) == 1:
            # Tentar com formato "Caso 01"
            padded_case = f"Caso 0{case_num}"
            if padded_case in ALGORITHMS[category]:
                return ALGORITHMS[category][padded_case]
        else:
            # Tentar com formato "Caso 1"
            if case_num.startswith("0"):
                unpadded_case = f"Caso {case_num[1:]}"
                if unpadded_case in ALGORITHMS[category]:
                    return ALGORITHMS[category][unpadded_case]
    
    return None

def get_algorithm_image(category: str, case: str) -> str:
    """
    Obter o caminho da imagem para um caso específico
    
    Args:
        category: F2L, OLL ou PLL
        case: O caso específico (ex: "Caso 01", "Caso U1", etc)
    
    Returns:
        O caminho da imagem ou None se não encontrado
    """
    category_dir = os.path.join(IMAGES_DIR, category)
    if not os.path.exists(category_dir):
        return None
    
    # Formatar o nome do arquivo
    if case.startswith("Caso "):
        filename = f"{category}_{case}.png"
    else:
        filename = f"{category}_Caso_{case}.png"
    
    file_path = os.path.join(category_dir, filename)
    
    # Verificar se o arquivo existe
    if os.path.exists(file_path):
        return file_path
    
    # Tentativas alternativas para diferentes formatações
    if case.startswith("Caso "):
        case_num = case[5:]
        # Tentar com formato diferente do número do caso
        if len(case_num) == 1:
            # Tentar com número preenchido com zero
            padded_filename = f"{category}_Caso_0{case_num}.png"
            padded_path = os.path.join(category_dir, padded_filename)
            if os.path.exists(padded_path):
                return padded_path
        else:
            # Tentar sem zero à esquerda
            if case_num.startswith("0"):
                unpadded_filename = f"{category}_Caso_{case_num[1:]}.png"
                unpadded_path = os.path.join(category_dir, unpadded_filename)
                if os.path.exists(unpadded_path):
                    return unpadded_path
    
    # Para PLL, tentar com formatação especial
    if category == "PLL" and not case.startswith("Caso "):
        pll_filename = f"{category}_Caso_{case}.png"
        pll_path = os.path.join(category_dir, pll_filename)
        if os.path.exists(pll_path):
            return pll_path
    
    return None

def get_f2l_groups() -> dict:
    """
    Agrupar casos de F2L em categorias lógicas
    
    Returns:
        Dicionário com grupos de casos F2L
    """
    # Podemos agrupar os casos F2L de acordo com características comuns
    # Por exemplo, baseado na posição inicial das peças
    groups = {
        "Canto e Aresta Corretamente Orientados": [
            "Caso 1", "Caso 2", "Caso 3", "Caso 4"
        ],
        "Canto Orientado, Aresta Mal Orientada": [
            "Caso 5", "Caso 6", "Caso 7", "Caso 8", "Caso 9", "Caso 10", "Caso 11", "Caso 12"
        ],
        "Canto Mal Orientado, Aresta Orientada": [
            "Caso 13", "Caso 14", "Caso 15", "Caso 16", "Caso 17", "Caso 18", "Caso 19", "Caso 20"
        ],
        "Canto e Aresta Mal Orientados": [
            "Caso 21", "Caso 22", "Caso 23", "Caso 24", "Caso 25", "Caso 26", "Caso 27", "Caso 28"
        ],
        "Casos com Slot Preenchido": [
            "Caso 29", "Caso 30", "Caso 31", "Caso 32", "Caso 33", "Caso 34", "Caso 35", "Caso 36"
        ],
        "Casos Avançados": [
            "Caso 37", "Caso 38", "Caso 39", "Caso 40", "Caso 41"
        ]
    }
    
    return groups

def get_oll_groups() -> dict:
    """
    Agrupar casos de OLL em categorias lógicas
    
    Returns:
        Dicionário com grupos de casos OLL
    """
    # Podemos agrupar os casos OLL baseado nos padrões de orientação das peças
    groups = {
        "Todos os Cantos Orientados": [
            "Caso 1", "Caso 2", "Caso 3", "Caso 4", "Caso 5", "Caso 6", "Caso 7", "Caso 8"
        ],
        "Linha na Face Superior": [
            "Caso 9", "Caso 10", "Caso 11", "Caso 12", "Caso 13", "Caso 14"
        ],
        "Dot na Face Superior": [
            "Caso 15", "Caso 16", "Caso 17", "Caso 18", "Caso 19", "Caso 20", "Caso 21"
        ],
        "Cantos em L": [
            "Caso 22", "Caso 23", "Caso 24", "Caso 25", "Caso 26", "Caso 27"
        ],
        "Padrões de Cruz": [
            "Caso 28", "Caso 29", "Caso 30", "Caso 31", "Caso 32", "Caso 33"
        ],
        "Padrões em T": [
            "Caso 34", "Caso 35", "Caso 36", "Caso 37", "Caso 38", "Caso 39"
        ],
        "Padrões em W": [
            "Caso 40", "Caso 41", "Caso 42", "Caso 43", "Caso 44", "Caso 45"
        ],
        "Padrões em P": [
            "Caso 46", "Caso 47", "Caso 48", "Caso 49", "Caso 50", "Caso 51"
        ],
        "Padrões Avançados": [
            "Caso 52", "Caso 53", "Caso 54", "Caso 55", "Caso 56", "Caso 57"
        ]
    }
    
    return groups 