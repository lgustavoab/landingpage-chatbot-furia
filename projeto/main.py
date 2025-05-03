# projeto/main.py

import os
import gradio as gr
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from gradio.routes import mount_gradio_app
from chat_logic import chat_com_gpt, limpar_chat

app = FastAPI()

# 1) Define o Gradio Blocks para o chatbot
with gr.Blocks(title="Chatbot de Precisão", theme=gr.themes.Soft()) as chatbot_app:
    gr.Markdown("## O que você gostaria de aprender hoje?")
    gr.Markdown(
        "Envie suas perguntas sobre o que quiser: formação, próximas partidas, "
        "resultados, jogador, títulos, o que quiser saber! Iremos tentar responder da "
        "melhor e mais confiável maneira!"
    )

    chatbot = gr.Chatbot(height=500, type="messages")
    mensagem = gr.Textbox(label="Sua pergunta", placeholder="Faça uma pergunta objetiva...")
    state = gr.State([])

    with gr.Row():
        enviar = gr.Button("📩 Enviar", variant="primary")
        limpar = gr.Button("🧹 Limpar")

    enviar.click(
        fn=chat_com_gpt,
        inputs=[mensagem, state],
        outputs=[chatbot, state, mensagem],
        show_progress=True
    )
    mensagem.submit(
        fn=chat_com_gpt,
        inputs=[mensagem, state],
        outputs=[chatbot, state, mensagem],
        show_progress=True
    )
    limpar.click(
        fn=limpar_chat,
        inputs=None,
        outputs=[chatbot, state, mensagem],
        queue=False
    )

# 2) Monta o Gradio como sub-app em /chatbot
mount_gradio_app(app, chatbot_app, path="/chatbot")

# 3) Serve a landing page em / para GET e HEAD
@app.api_route("/", methods=["GET", "HEAD"])
async def serve_index(request: Request):
    return FileResponse("index.html")

# 4) Serve arquivos estáticos em /static
app.mount("/static", StaticFiles(directory=".", html=False), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5500))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
