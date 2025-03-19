import os
from flask import Flask, request, jsonify, redirect, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import json
import httpx
import logging
import base64
from typing import Dict, List, Optional, Any
from app.cube_utils import get_algorithm, get_algorithm_image, get_f2l_groups, get_oll_groups
from asgiref.sync import async_to_sync

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da Evolution API
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

if not all([EVOLUTION_API_URL, INSTANCE_NAME]):
    raise ValueError("Variáveis de ambiente EVOLUTION_API_URL e INSTANCE_NAME são obrigatórias")

# Criar pasta de templates se não existir
os.makedirs('app/templates', exist_ok=True)

app = Flask(__name__, template_folder='templates')
CORS(app)  # Habilitar CORS para todas as origens

# Estado da conversação (para armazenar o contexto de cada usuário)
user_states = {}

# Estados possíveis
class UserState:
    INITIAL = "initial"
    MENU = "menu"
    F2L = "f2l"
    OLL = "oll"
    PLL = "pll"
    F2L_GROUP = "f2l_group"
    OLL_GROUP = "oll_group"

# Carregar os algoritmos
with open('algs.json', 'r') as f:
    ALGORITHMS = json.load(f)

# Função para enviar mensagem para o WhatsApp
async def send_whatsapp_message(to: str, text: str):
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
    payload = {
        "number": to,
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "textMessage": {
            "text": text
        }
    }
    
    headers = {}
    if EVOLUTION_API_KEY:
        headers["apikey"] = EVOLUTION_API_KEY
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            return response.json()
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return None

# Função para enviar imagem para o WhatsApp
async def send_whatsapp_image(to: str, image_path: str, caption: str = ""):
    url = f"{EVOLUTION_API_URL}/message/sendMedia/{INSTANCE_NAME}"
    
    # Preparar o payload com a imagem em base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    payload = {
        "number": to,
        "options": {
            "delay": 1200
        },
        "mediaMessage": {
            "mediatype": "image",
            "media": encoded_string,
            "caption": caption,
            "fileName": os.path.basename(image_path)
        }
    }
    
    headers = {}
    if EVOLUTION_API_KEY:
        headers["apikey"] = EVOLUTION_API_KEY
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            return response.json()
    except Exception as e:
        logger.error(f"Erro ao enviar imagem: {e}")
        return None

# Função para enviar o menu principal
async def send_main_menu(to: str):
    menu_text = """🧩 *MENU SPEEDCUBING ASSISTANT* 🧩

Escolha uma das opções abaixo:

1️⃣ - *F2L* (First 2 Layers)
2️⃣ - *OLL* (Orientation of Last Layer)
3️⃣ - *PLL* (Permutation of Last Layer)

Responda com o número ou nome da opção desejada."""
    
    await send_whatsapp_message(to, menu_text)
    user_states[to] = UserState.MENU

# Função para enviar o menu de F2L
async def send_f2l_menu(to: str):
    groups = get_f2l_groups()
    
    menu_text = """🧩 *F2L - GRUPOS* 🧩

Escolha um dos grupos de algoritmos F2L:

"""
    
    for i, (group_name, cases) in enumerate(groups.items(), 1):
        menu_text += f"{i}️⃣ - *{group_name}* ({len(cases)} casos)\n"
    
    menu_text += "\n0️⃣ - Voltar ao menu principal\n"
    menu_text += "\nOu digite o número do caso específico (1-41)"
    
    await send_whatsapp_message(to, menu_text)
    user_states[to] = UserState.F2L

# Função para enviar o menu de OLL
async def send_oll_menu(to: str):
    groups = get_oll_groups()
    
    menu_text = """🧩 *OLL - GRUPOS* 🧩

Escolha um dos grupos de algoritmos OLL:

"""
    
    for i, (group_name, cases) in enumerate(groups.items(), 1):
        menu_text += f"{i}️⃣ - *{group_name}* ({len(cases)} casos)\n"
    
    menu_text += "\n0️⃣ - Voltar ao menu principal\n"
    menu_text += "\nOu digite o número do caso específico (1-57)"
    
    await send_whatsapp_message(to, menu_text)
    user_states[to] = UserState.OLL

# Função para enviar o menu de PLL
async def send_pll_menu(to: str):
    menu_text = """🧩 *PLL - CASOS* 🧩

Escolha um dos casos de PLL:

"""
    
    for caso in ALGORITHMS["PLL"].keys():
        menu_text += f"- *{caso}*\n"
    
    menu_text += "\n0️⃣ - Voltar ao menu principal"
    
    await send_whatsapp_message(to, menu_text)
    user_states[to] = UserState.PLL

# Função para enviar os casos de um grupo F2L
async def send_f2l_group(to: str, group_id: int):
    groups = get_f2l_groups()
    
    if group_id < 1 or group_id > len(groups):
        await send_whatsapp_message(to, "❌ Grupo inválido. Por favor, escolha uma opção válida.")
        await send_f2l_menu(to)
        return
    
    group_name = list(groups.keys())[group_id - 1]
    casos = groups[group_name]
    
    await send_whatsapp_message(to, f"🧩 *F2L - {group_name}* 🧩\n\nEscolha um dos casos abaixo ou digite 0 para voltar:")
    
    # Enviar lista de casos no grupo
    casos_text = ""
    for caso in casos:
        casos_text += f"- *{caso}*\n"
    
    await send_whatsapp_message(to, casos_text)
    
    user_states[to] = UserState.F2L_GROUP
    # Armazenar o grupo atual para referência
    user_states[f"{to}_group"] = group_name

# Função para enviar os casos de um grupo OLL
async def send_oll_group(to: str, group_id: int):
    groups = get_oll_groups()
    
    if group_id < 1 or group_id > len(groups):
        await send_whatsapp_message(to, "❌ Grupo inválido. Por favor, escolha uma opção válida.")
        await send_oll_menu(to)
        return
    
    group_name = list(groups.keys())[group_id - 1]
    casos = groups[group_name]
    
    await send_whatsapp_message(to, f"🧩 *OLL - {group_name}* 🧩\n\nEscolha um dos casos abaixo ou digite 0 para voltar:")
    
    # Enviar lista de casos no grupo
    casos_text = ""
    for caso in casos:
        casos_text += f"- *{caso}*\n"
    
    await send_whatsapp_message(to, casos_text)
    
    user_states[to] = UserState.OLL_GROUP
    # Armazenar o grupo atual para referência
    user_states[f"{to}_group"] = group_name

# Função para enviar informações de um caso específico
async def send_case_info(to: str, category: str, case: str):
    algorithm = get_algorithm(category, case)
    if not algorithm:
        await send_whatsapp_message(to, f"❌ Caso não encontrado: {case}")
        return False
    
    image_path = get_algorithm_image(category, case)
    if not image_path or not os.path.exists(image_path):
        await send_whatsapp_message(to, f"⚠️ Imagem não encontrada para o caso {case}, mas aqui está o algoritmo:\n\n*{case}*: `{algorithm}`")
        return True
    
    # Enviar a imagem com o algoritmo como legenda
    caption = f"*{case}*\n`{algorithm}`"
    await send_whatsapp_image(to, image_path, caption)
    return True

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        body = request.get_json()
        logger.info(f"Webhook recebido: {body}")
        
        # Verificar se é uma mensagem do tipo necessário
        if not body.get("event") == "messages.upsert":
            return jsonify({"status": "ignored", "reason": "not a message upsert event"})
        
        # Extrair a mensagem
        messages = body.get("data", {}).get("messages", [])
        if not messages:
            return jsonify({"status": "ignored", "reason": "no messages"})
        
        message = messages[0]
        # Ignorar mensagens enviadas pelo próprio bot
        if message.get("key", {}).get("fromMe", False):
            return jsonify({"status": "ignored", "reason": "message from me"})
        
        # Extrair informações da mensagem
        sender = message.get("key", {}).get("remoteJid", "").split("@")[0]
        push_name = message.get("pushName", "Usuário")
        
        # Extrair o texto da mensagem
        message_type = message.get("message", {})
        text = ""
        
        if "conversation" in message_type:
            text = message_type["conversation"]
        elif "extendedTextMessage" in message_type:
            text = message_type["extendedTextMessage"].get("text", "")
        
        if not text:
            return jsonify({"status": "ignored", "reason": "no text content"})
        
        # Processar a mensagem de acordo com o estado do usuário
        # Como estamos usando Flask (sync) e precisamos chamar funções async,
        # usamos async_to_sync para converter a chamada
        async_to_sync(process_message)(sender, text.strip())
        
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

async def process_message(sender: str, text: str):
    # Se for um novo usuário, inicializar o estado
    if sender not in user_states:
        user_states[sender] = UserState.INITIAL
    
    # Estado inicial - enviar menu principal
    if user_states[sender] == UserState.INITIAL:
        await send_whatsapp_message(sender, f"Olá! Bem-vindo ao Speedcubing Assistant Bot!")
        await send_main_menu(sender)
        return
    
    # Processamento do menu principal
    if user_states[sender] == UserState.MENU:
        text_lower = text.lower()
        
        if text == "1" or "f2l" in text_lower:
            await send_f2l_menu(sender)
        elif text == "2" or "oll" in text_lower:
            await send_oll_menu(sender)
        elif text == "3" or "pll" in text_lower:
            await send_pll_menu(sender)
        else:
            await send_whatsapp_message(sender, "❌ Opção inválida. Por favor, escolha uma opção válida.")
            await send_main_menu(sender)
        return
    
    # Processamento do menu F2L
    if user_states[sender] == UserState.F2L:
        if text == "0":
            await send_main_menu(sender)
            return
        
        # Verificar se é um número de grupo
        try:
            group_id = int(text)
            # Se for um número entre 1 e 41, é um caso específico
            if 1 <= group_id <= 41:
                case = f"Caso {group_id:02d}"
                if group_id < 10:
                    case = f"Caso {group_id}"
                await send_case_info(sender, "F2L", case)
                return
            else:
                # Caso contrário, é um grupo
                await send_f2l_group(sender, group_id)
                return
        except ValueError:
            # Não é um número, verificar se é um nome de caso
            if text.startswith("Caso "):
                await send_case_info(sender, "F2L", text)
                return
            else:
                await send_whatsapp_message(sender, "❌ Opção inválida. Por favor, escolha uma opção válida.")
                await send_f2l_menu(sender)
                return
    
    # Processamento do menu OLL
    if user_states[sender] == UserState.OLL:
        if text == "0":
            await send_main_menu(sender)
            return
        
        # Verificar se é um número de grupo
        try:
            group_id = int(text)
            # Se for um número entre 1 e 57, é um caso específico
            if 1 <= group_id <= 57:
                case = f"Caso {group_id:02d}"
                if group_id < 10:
                    case = f"Caso {group_id}"
                await send_case_info(sender, "OLL", case)
                return
            else:
                # Caso contrário, é um grupo
                await send_oll_group(sender, group_id)
                return
        except ValueError:
            # Não é um número, verificar se é um nome de caso
            if text.startswith("Caso "):
                await send_case_info(sender, "OLL", text)
                return
            else:
                await send_whatsapp_message(sender, "❌ Opção inválida. Por favor, escolha uma opção válida.")
                await send_oll_menu(sender)
                return
    
    # Processamento do menu PLL
    if user_states[sender] == UserState.PLL:
        if text == "0":
            await send_main_menu(sender)
            return
        
        # Verificar se é um caso de PLL válido
        if text in ALGORITHMS["PLL"]:
            await send_case_info(sender, "PLL", text)
            return
        elif text.upper() in ALGORITHMS["PLL"]:
            await send_case_info(sender, "PLL", text.upper())
            return
        elif f"Caso {text}" in ALGORITHMS["PLL"]:
            await send_case_info(sender, "PLL", f"Caso {text}")
            return
        else:
            await send_whatsapp_message(sender, "❌ Caso inválido. Por favor, escolha um caso válido.")
            await send_pll_menu(sender)
            return
    
    # Processamento de um grupo específico de F2L
    if user_states[sender] == UserState.F2L_GROUP:
        if text == "0":
            await send_f2l_menu(sender)
            return
        
        # Verificar se o caso existe no grupo atual
        group_name = user_states.get(f"{sender}_group")
        if not group_name:
            await send_f2l_menu(sender)
            return
        
        groups = get_f2l_groups()
        if group_name not in groups:
            await send_f2l_menu(sender)
            return
        
        # Verificar se o texto corresponde a um caso no grupo
        if text in groups[group_name]:
            await send_case_info(sender, "F2L", text)
            return
        else:
            try:
                case_num = int(text)
                case = f"Caso {case_num:02d}"
                if case_num < 10:
                    case = f"Caso {case_num}"
                
                if case in groups[group_name]:
                    await send_case_info(sender, "F2L", case)
                    return
            except ValueError:
                pass
            
            await send_whatsapp_message(sender, "❌ Caso inválido. Por favor, escolha um caso válido.")
            return
    
    # Processamento de um grupo específico de OLL
    if user_states[sender] == UserState.OLL_GROUP:
        if text == "0":
            await send_oll_menu(sender)
            return
        
        # Verificar se o caso existe no grupo atual
        group_name = user_states.get(f"{sender}_group")
        if not group_name:
            await send_oll_menu(sender)
            return
        
        groups = get_oll_groups()
        if group_name not in groups:
            await send_oll_menu(sender)
            return
        
        # Verificar se o texto corresponde a um caso no grupo
        if text in groups[group_name]:
            await send_case_info(sender, "OLL", text)
            return
        else:
            try:
                case_num = int(text)
                case = f"Caso {case_num:02d}"
                if case_num < 10:
                    case = f"Caso {case_num}"
                
                if case in groups[group_name]:
                    await send_case_info(sender, "OLL", case)
                    return
            except ValueError:
                pass
            
            await send_whatsapp_message(sender, "❌ Caso inválido. Por favor, escolha um caso válido.")
            return

@app.route('/')
def read_root():
    return jsonify({"status": "online", "message": "Speedcubing Assistant Bot está funcionando!"})

# Rota para o dashboard - suporta tanto /manager quanto /manager/
@app.route('/manager')
@app.route('/manager/')
def manager():
    # Log da URL para facilitar o diagnóstico
    logger.info(f"Redirecionando para Evolution API URL: {EVOLUTION_API_URL}")
    
    # Verificar se a URL tem o protocolo HTTP, caso contrário adicionar
    redirect_url = EVOLUTION_API_URL
    if not redirect_url.startswith(('http://', 'https://')):
        redirect_url = 'https://' + redirect_url
    
    # Redirecionamento direto para a Evolution API
    return redirect(redirect_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False) 