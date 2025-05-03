import re
import unidecode
from openai import OpenAI
from config import OPENAI_API_KEY, CHAT_SETTINGS
from data_fetcher import (
    get_pro_team_roster_csgo_by_url,
    get_pro_team_upcoming_matches_csgo
)
from typing import Optional, List, Dict, Tuple

# ============================
# Cadastro de links dos times para reforço
# ============================
LINKS_TIMES: Dict[str, str] = {
    "furia": "https://draft5.gg/equipe/330-FURIA",
    "spirit": "https://draft5.gg/equipe/390-Spirit",
    "g2": "https://draft5.gg/equipe/35-G2",
    "natus vincere": "https://draft5.gg/equipe/22-Natus-Vincere",
    "the mongolz": "https://draft5.gg/equipe/2635-The-MongolZ",
    "big": "https://draft5.gg/equipe/190-BIG",
    "game hunters": "https://draft5.gg/equipe/3475-Game-Hunters",
    "gamehunters": "https://draft5.gg/equipe/3475-Game-Hunters",
    "mibr": "https://draft5.gg/equipe/639-MIBR",
    "astralis": "https://draft5.gg/equipe/8-Astralis",
    "pain": "https://draft5.gg/equipe/569-paiN",
    "virtus pro": "https://draft5.gg/equipe/5-Virtus.pro",
    "hotu": "https://draft5.gg/equipe/2498-HOTU",
    "nip": "https://draft5.gg/equipe/7-Ninjas-in-Pyjamas",
    "oddik": "https://draft5.gg/equipe/2246-ODDIK",
    "m80": "https://draft5.gg/equipe/2765-M80",
    "aurora": "https://draft5.gg/equipe/2292-Aurora",
    "faze": "https://draft5.gg/equipe/12-FaZe",
    "mouz": "https://draft5.gg/equipe/34-MOUZ",
    "falcons": "https://draft5.gg/equipe/2111-Falcons",
    "wildcard": "https://draft5.gg/equipe/2651-Wildcard",
    "flyquest": "https://draft5.gg/equipe/3233-FlyQuest",
    "liquid": "https://draft5.gg/equipe/20-Liquid",
    "3dmax": "https://draft5.gg/equipe/657-3DMAX",
    "heroic": "https://draft5.gg/equipe/21-HEROIC",
    "og": "https://draft5.gg/equipe/1189-OG",
    "nemiga gaming": "https://draft5.gg/equipe/628-Nemiga-Gaming",
    "lynn vision gaming": "https://draft5.gg/equipe/1300-Lynn-Vision-Gaming",
    "bbteam": "https://draft5.gg/equipe/2777-BB-Team",
    "fluxo": "https://draft5.gg/equipe/2283-Fluxo",
    "tyloo": "https://draft5.gg/equipe/25-TYLOO",
    "chinggis warriors": "https://draft5.gg/equipe/3111-Chinggis-Warriors",
    "bestia": "https://draft5.gg/equipe/2544-BESTIA",
    "nrg esports": "https://draft5.gg/equipe/17-NRG-Esports",
    "nrg": "https://draft5.gg/equipe/17-NRG-Esports",
}

# Palavras-chave para detectar intenções
PALAVRAS_ROSTER: List[str] = ["formacao", "lineup", "elenco", "roster", "players"]
PALAVRAS_PROXIMAS: List[str] = [
    "proximas partidas", "proxima partida", "proximos jogos", "proximo jogo",
    "agenda", "calendario", "upcoming", "jogos futuros"
]
PALAVRAS_RESULTADOS: List[str] = [
    "resultado", "resultados", "quem ganhou", "placar", "vencedor", "score"
]

client = OpenAI(api_key=OPENAI_API_KEY)
LIMITE_HISTORICO = 10

def formatar_mensagens(historico: List[Dict]) -> List[Dict]:
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in historico
        if msg.get("role") and msg.get("content")
    ]

def cortar_historico(historico: List[Dict]) -> List[Dict]:
    return historico[-LIMITE_HISTORICO:]

def detectar_time(texto: str) -> Optional[str]:
    texto_norm = unidecode.unidecode(texto.lower())
    for time in sorted(LINKS_TIMES.keys(), key=lambda t: -len(t)):
        pattern = r"\b" + re.escape(time) + r"\b"
        if re.search(pattern, texto_norm):
            print(f"DEBUG: detectar_time: '{time}' encontrado em '{texto_norm}'")
            return time
    print(f"DEBUG: detectar_time: nenhum time encontrado em '{texto_norm}'")
    return None

def extrair_time_bruto(texto: str) -> Optional[str]:
    texto_norm = unidecode.unidecode(texto.lower())
    m = re.search(r"partida(?:s)? (?:da|do|das|dos) ([a-z0-9\- ]+)", texto_norm)
    if m:
        team = m.group(1).strip()
        print(f"DEBUG: extrair_time_bruto: capturado '{team}'")
        return team
    return None

def chat_com_gpt(mensagem: str, historico: List[Dict]) -> Tuple[List[Dict], List[Dict], str]:
    print(f"\nDEBUG: Nova mensagem recebida: '{mensagem}'")
    texto_norm = unidecode.unidecode(mensagem.lower())
    historico = cortar_historico(historico)

    time_detectado = detectar_time(mensagem)
    print(f"DEBUG: time_detectado = {time_detectado}")

    # 1) ROSTER
    if time_detectado and any(k in texto_norm for k in PALAVRAS_ROSTER):
        print("DEBUG: Branch ROSTER ativado")
        url_time = LINKS_TIMES[time_detectado]
        roster = get_pro_team_roster_csgo_by_url(url_time)
        print(f"DEBUG: Roster obtido: {roster}")
        if roster:
            conteudo = f"Formação atual da {time_detectado.upper()} em CS:GO:"
            for p in roster:
                conteudo += f"\n- {p['nickname']}"
        else:
            conteudo = f"Não consegui obter o roster da {time_detectado.upper()}."
        conteudo += f"\n\nPara reforço, consulte: {url_time}"
        conteudo += "\n\nConfira todas as partidas no site: https://draft5.gg/proximas-partidas"
        novo_hist = historico + [{"role": "assistant", "content": conteudo}]
        return novo_hist, novo_hist, ""

    # 2) PRÓXIMAS PARTIDAS
    if any(k in texto_norm for k in PALAVRAS_PROXIMAS):
        print("DEBUG: Branch PRÓXIMAS PARTIDAS ativado")
        if not time_detectado:
            bruto = extrair_time_bruto(mensagem)
            if bruto:
                time_detectado = bruto
        slug = time_detectado.replace(" ", "_").upper() if time_detectado else ""
        print(f"DEBUG: slug para busca de partidas = {slug}")
        matches = get_pro_team_upcoming_matches_csgo(slug)
        print(f"DEBUG: matches retornadas = {matches}")
        if matches:
            conteudo = "Próximas Partidas CS:GO:"
            for m in matches:
                conteudo += f"\n- {m['date']}: vs {m['opponent']} ({m['event']})"
        else:
            nome = time_detectado.upper() if time_detectado else "essa equipe"
            conteudo = f"Não consegui obter as próximas partidas da {nome} no momento."
        if time_detectado in LINKS_TIMES:
            conteudo += f"\n\nPara reforço, consulte: {LINKS_TIMES[time_detectado]}"
        conteudo += "\n\nConfira todas as partidas no site: https://draft5.gg/proximas-partidas"
        novo_hist = historico + [{"role": "assistant", "content": conteudo}]
        return novo_hist, novo_hist, ""

    # 3) RESULTADOS DE PARTIDAS
    if any(k in texto_norm for k in PALAVRAS_RESULTADOS):
        print("DEBUG: Branch RESULTADOS ativado")
        nome = time_detectado.upper() if time_detectado else "o time desejado"
        conteudo = (
            f"Infelizmente, ainda não consigo buscar os resultados recentes de {nome} automaticamente. 😔\n\n"
            "Mas você pode conferir os resultados mais recentes e detalhados nos links abaixo:\n"
            "- [Draft5 Resultados](https://draft5.gg/resultados)\n"
            "- [Dust2 Resultados](https://www.dust2.com.br/resultados)"
        )
        novo_hist = historico + [{"role": "assistant", "content": conteudo}]
        return novo_hist, novo_hist, ""

    # 4) FALLBACK PARA GPT
    print("DEBUG: Branch GPT (fallback) ativado")
    mensagens = [
        {"role": "system", "content": (
            "Você é um assistente descolado, com linguagem descontraída e divertida. "
            "Responda com leveza e bom humor, mas sempre baseado em informações corretas."
        )}
    ] + formatar_mensagens(historico) + [{"role": "user", "content": mensagem}]

    resposta = client.chat.completions.create(**CHAT_SETTINGS, messages=mensagens)
    conteudo_gpt = resposta.choices[0].message.content.strip()
    print(f"DEBUG: resposta GPT bruta = '''{conteudo_gpt}'''")

    conteudo_final = conteudo_gpt  # <<< SEM links adicionais aqui

    novo_hist = historico + [
        {"role": "user", "content": mensagem},
        {"role": "assistant", "content": conteudo_final}
    ]
    return novo_hist, novo_hist, ""

def limpar_chat() -> Tuple[List[Dict], List[Dict], str]:
    return [], [], ""
