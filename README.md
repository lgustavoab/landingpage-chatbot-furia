FURIA CS:GO Landing Page com Chatbot

Este repositório contém uma landing page estática da FURIA Esports com um chatbot integrado desenvolvido em Python, usando FastAPI e Gradio para comunicação com a API OpenAI.

Features

Landing Page Responsiva: HTML5, CSS3 e JavaScript puro para carrossel de imagens, navegação e lightbox.

Chatbot Inteligente: integrado via Gradio, hospedado sob /chatbot, com lógica de consulta de rosters e partidas de CS:GO.

Scraping de Dados: data_fetcher.py extrai line-up titular de Draft5.gg e próximas partidas de Dust2.com.br.

Configuração Dinâmica: variáveis de ambiente via .env para proteger sua OPENAI_API_KEY.

Estrutura do Projeto

furia_landingpage_chatbot/ ├── projeto/ # Código da landing page e backend │ ├── index.html # Página principal │ ├── style.css # Estilos CSS │ ├── script.js # Comportamentos JS (carrossel, lightbox, loja) │ ├── produtos/ # Imagens de produtos │ ├── logos/ # Logos de parceiros │ ├── carrosel/ # Imagens do carrossel │ ├── furia-logo.png # Logo principal │ ├── chat_logic.py # Lógica de fluxo de chat e integração OpenAI │ ├── config.py # Carregamento de .env e configurações OpenAI │ ├── data_fetcher.py # Scraping de rosters e partidas │ ├── main.py # FastAPI + Gradio server (ponto de entrada) │ └── requirements.txt # Dependências Python └── venv/ # Ambiente virtual (não versionado)

Pré-requisitos

Python 3.10+ instalado

Conta e chave da OpenAI API (defina em .env)

Instalação e Execução Local

Clone o repositório:
git clone <URL_DO_REPO> cd furia_landingpage_chatbot

Crie e ative o ambiente virtual:
Windows:

python -m venv venv .\venv\Scripts\activate

macOS/Linux:

python3 -m venv venv source venv/bin/activate

Instale as dependências:
pip install -r projeto/requirements.txt

Configure variáveis de ambiente:
Crie um arquivo .env dentro da pasta projeto/ com:

OPENAI_API_KEY=(sua_chave_aqui)

OBS1: a OPENAI não permite publicar o .env e nem um "readme" com a chave exposta. Portanto, enviarei a chave junto com o video ou e-mail.

OBS2: essa chave está com crédito com fim de participar do processo seletivo - provavalmente da pra mandar +- umas 600 mensagens até acabarem os créditos.

Execute o servidor:
cd projeto uvicorn main:app --reload --port 5500

Acesse:
Landing page: http://localhost:5500/

Chatbot: no botão 💬 ou direto em http://localhost:5500/chatbot
