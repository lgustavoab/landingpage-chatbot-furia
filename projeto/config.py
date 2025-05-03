# config.py

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Chave da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configurações para o ChatGPT (OpenAI)
CHAT_SETTINGS = {
    "model": "gpt-4",      # Utilize "gpt-4" para respostas mais precisas
    "temperature": 0.2,
    "max_tokens": 800,
    "top_p": 0.85,
    "frequency_penalty": 0.7,
    "presence_penalty": 0.7,
}
