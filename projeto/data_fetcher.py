# data_fetcher.py

import requests
from bs4 import BeautifulSoup
from functools import lru_cache
import logging
from datetime import datetime
from dateutil import parser as date_parser
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

# URLs para roster no Draft5.gg
DRAFT5_ROSTER_URLS = {
    "FURIA": "https://draft5.gg/equipe/330-FURIA",
    "SPIRIT": "https://draft5.gg/equipe/390-Spirit",
    "G2": "https://draft5.gg/equipe/35-G2",
    "NATUS VINCERE": "https://draft5.gg/equipe/22-Natus-Vincere",
    "THE MONGOLZ": "https://draft5.gg/equipe/2635-The-MongolZ",
    "BIG": "https://draft5.gg/equipe/190-BIG",
    "GAMER LEGION": "https://draft5.gg/equipe/953-GamerLegion",
    "MIBR": "https://draft5.gg/equipe/639-MIBR",
    "ASTRALIS": "https://draft5.gg/equipe/8-Astralis",
    "PAIN": "https://draft5.gg/equipe/569-paiN",
    "VIRTUS PRO": "https://draft5.gg/equipe/5-Virtus.pro",
    "HOTU": "https://draft5.gg/equipe/2498-HOTU",
    "NINJAS IN PYJAMAS": "https://draft5.gg/equipe/7-Ninjas-in-Pyjamas",
    "ODDIK": "https://draft5.gg/equipe/2246-ODDIK",
    "M80": "https://draft5.gg/equipe/2765-M80",
    "AURORA": "https://draft5.gg/equipe/2292-Aurora",
    "FAZE": "https://draft5.gg/equipe/12-FaZe",
    "MOUZ": "https://draft5.gg/equipe/34-MOUZ",
    "FALCONS": "https://draft5.gg/equipe/2111-Falcons",
    "WILDCARD": "https://draft5.gg/equipe/2651-Wildcard",
    "FLYQUEST": "https://draft5.gg/equipe/3233-FlyQuest",
    "LIQUID": "https://draft5.gg/equipe/20-Liquid",
    "3DMAX": "https://draft5.gg/equipe/657-3DMAX",
    "HEROIC": "https://draft5.gg/equipe/21-HEROIC",
    "OG": "https://draft5.gg/equipe/1189-OG",
    "NEMIGA GAMING": "https://draft5.gg/equipe/628-Nemiga-Gaming",
    "LYNN VISION GAMING": "https://draft5.gg/equipe/1300-Lynn-Vision-Gaming",
    "BB TEAM": "https://draft5.gg/equipe/2777-BB-Team",
    "FLUXO": "https://draft5.gg/equipe/2283-Fluxo",
    "TYLOO": "https://draft5.gg/equipe/25-TYLOO",
    "CHINGGIS WARRIORS": "https://draft5.gg/equipe/3111-Chinggis-Warriors",
    "BESTIA": "https://draft5.gg/equipe/2544-BESTIA",
    "GAME HUNTERS": "https://draft5.gg/equipe/3475-Game-Hunters",
    "NRG ESPORTS": "https://draft5.gg/equipe/17-NRG-Esports",
}

MAX_PAGES = 3


def _fetch_roster_from_url(url: str) -> list[dict]:
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"DRAFT5: falha ao buscar roster em '{url}': {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    header = soup.find(lambda tag:
        tag.name in ("h2", "span") and "Line-up Titular" in tag.get_text()
    )
    if not header:
        logger.warning(f"DRAFT5: 'Line-up Titular' não encontrado em '{url}'")
        return []

    roster = []
    for sib in header.find_all_next():
        text = sib.get_text(strip=True)
        if "Reservas" in text:
            break
        if sib.name == "img":
            nome = sib.next_sibling.strip() if sib.next_sibling else ""
            if nome and not nome.lower().startswith("image"):
                roster.append({"role": "", "nickname": nome, "realName": ""})
        elif sib.name == "div" and "team-lineup__name" in sib.get("class", []):
            roster.append({"role": "", "nickname": sib.get_text(strip=True), "realName": ""})
    return roster


@lru_cache(maxsize=32)
def get_pro_team_roster_csgo(slug: str) -> list[dict]:
    slug_norm = slug.strip().upper()
    url = DRAFT5_ROSTER_URLS.get(slug_norm)
    if not url:
        logger.error(f"DRAFT5: slug '{slug_norm}' não configurado")
        return []
    return _fetch_roster_from_url(url)


@lru_cache(maxsize=32)
def get_pro_team_roster_csgo_by_url(url: str) -> list[dict]:
    return _fetch_roster_from_url(url)


@lru_cache(maxsize=32)
def get_pro_team_upcoming_matches_csgo(team_name: str) -> list[dict]:
    url = "https://www.dust2.com.br/partidas?filter=todos"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"dust2.com.br: falha ao buscar partidas: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("div.match")

    matches = []
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    today = datetime.now().date()

    for row in rows:
        ts = row.get("data-item-entry-time")
        if ts:
            dt_full = datetime.fromtimestamp(int(ts) / 1000)
            date_txt = dt_full.strftime("%Y-%m-%d")
            time_txt = dt_full.strftime("%H:%M")
        else:
            date_el = row.select_one(".match-date")
            time_el = row.select_one(".match-hour")
            date_txt = date_el.get_text(strip=True) if date_el else ""
            time_txt = time_el.get_text(strip=True) if time_el else ""

        teams = row.select("a.match-teams-container")
        if len(teams) >= 2:
            team_a = teams[0].get_text(strip=True)
            team_b = teams[1].get_text(strip=True)
        else:
            href = next((a["href"] for a in row.find_all("a", href=True) if "-vs-" in a["href"]), None)
            if not href:
                continue
            slug_vs = href.split("/")[-1]
            m = re.match(r"(.+?)-vs-(.+?)(?:-|$)", slug_vs)
            if not m:
                continue
            team_a = m.group(1).replace("-", " ").title()
            team_b = m.group(2).replace("-", " ").title()

        ev = row.select_one("a.match-event")
        tournament = ev.get_text(strip=True) if ev else "Desconhecido"

        if norm(team_name) not in norm(team_a) and norm(team_name) not in norm(team_b):
            continue

        dt_str = f"{date_txt} {time_txt}"
        try:
            dt_parsed = date_parser.parse(dt_str)
        except Exception:
            continue

        if dt_parsed.date() < today:
            continue

        opponent = team_b if norm(team_name) in norm(team_a) else team_a
        matches.append({
            "date": dt_parsed.strftime("%Y-%m-%d %H:%M"),
            "opponent": opponent,
            "event": tournament
        })

    return matches
