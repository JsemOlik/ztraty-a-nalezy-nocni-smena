"""Stav hry a předměty.

Celý stav hry je jeden obyčejný slovník (dictionary). Funkce v tomhle souboru
s ním jen pracují: zjišťují, co má hráč v kapsách, přidávají příznaky a podobně.
"""

MAX_POCKETS = 4
MAX_PIECES = 5
SHIFT_END = 6 * 60  # šest ráno, v minutách od půlnoci
ACTION_MINUTES = 5

# Každý předmět: jméno (1. pád), jméno ve 4. pádě, popis a jak se používá.
# "use" je None, když se předmět použít nedá.
ITEMS = {
    "umbrella": {
        "name": "suchý deštník",
        "accusative": "suchý deštník",
        "description": "Jediný suchý deštník v celém úřadu. Chrání před deštěm ve skladu.",
        "use": None,
    },
    "head": {
        "name": "mluvící hlava",
        "accusative": "mluvící hlavu",
        "description": "Hlava pána s knírem. Pořád mluví a bojí se. Patří někomu ve sklepě.",
        "use": None,
    },
    "lost_hour": {
        "name": "ztracená hodina",
        "accusative": "ztracenou hodinu",
        "description": "Hodina, kterou kdosi prostál ve frontě. Prodlouží noc o hodinu.",
        "use": "Použít",
    },
    "laugh_jar": {
        "name": "sklenice se smíchem",
        "accusative": "sklenici se smíchem",
        "description": "Něčí ztracený smích. Když ji otevřeš, vrátí ti kousek sebe.",
        "use": "Otevřít",
    },
    "stolen_time": {
        "name": "hrst ukradeného času",
        "accusative": "hrst ukradeného času",
        "description": "Cizí minuty. Lepí se na prsty a tikají.",
        "use": None,
    },
    "red_thread": {
        "name": "červená nit",
        "accusative": "červenou nit",
        "description": "Konec červené niti. Dokud ji držíš, neztratíš se.",
        "use": None,
    },
    "director_face": {
        "name": "ředitelova tvář",
        "accusative": "ředitelovu tvář",
        "description": "Tvář pana ředitele. Otevře ředitelnu. Nenos ji dlouho.",
        "use": "Nasadit si",
    },
    "nametag": {
        "name": "Hlaváčkova jmenovka",
        "accusative": "Hlaváčkovu jmenovku",
        "description": "„Bohumil Hlaváček – noční služba.“ Připomene mu, kdo je.",
        "use": None,
    },
    "own_photo": {
        "name": "vlastní fotka",
        "accusative": "vlastní fotku",
        "description": "Tvoje stará fotka. Připomene ti, kdo jsi (vrátí 2 kousky sebe, ale vybledne).",
        "use": "Zadívat se na",
    },
}


def new_state(feminine):
    """Vytvoří stav nové hry."""
    return {
        "feminine": feminine,
        "location": "counter",
        "minutes": 0,
        "deadline": SHIFT_END,
        "pieces": MAX_PIECES,
        "pockets": [],
        # Co kde leží na zemi.
        "room_items": {
            "counter": ["umbrella"],
            "umbrellas": ["head"],
            "time_dept": [],
            "speech": [],
            "threads": ["red_thread"],
            "faces": ["director_face"],
            "cellar": [],
            "office": [],
            "hidden": [],
        },
        # Příznaky, co se už stalo (např. "tea_drunk").
        "flags": [],
        "face_worn": False,
        "face_turns": 0,
        "ending": None,
    }


def g(state, masculine, feminine):
    """Vrátí tvar slova podle toho, jestli hraje úředník, nebo úřednice."""
    if state["feminine"]:
        return feminine
    return masculine


def has_flag(state, flag):
    return flag in state["flags"]


def add_flag(state, flag):
    if flag not in state["flags"]:
        state["flags"].append(flag)


def has_item(state, item):
    return item in state["pockets"]


def count_item(state, item):
    return state["pockets"].count(item)


def pockets_full(state):
    return len(state["pockets"]) >= MAX_POCKETS


def add_item(state, item):
    """Dá předmět do kapsy. Vrátí False, když se už nevejde."""
    if pockets_full(state):
        return False
    state["pockets"].append(item)
    return True


def remove_item(state, item):
    state["pockets"].remove(item)


def items_here(state):
    """Seznam věcí, které leží v místnosti, kde hráč právě je."""
    return state["room_items"][state["location"]]


def give_or_drop(state, item):
    """Dá předmět do kapsy, a když se nevejde, položí ho na zem v místnosti."""
    if add_item(state, item):
        return True
    items_here(state).append(item)
    return False


def unique(items):
    """Vrátí seznam bez opakování (pořadí zůstane stejné)."""
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def fmt_time(minutes):
    """Z minut od půlnoci udělá text jako 05:35."""
    minutes = minutes % (24 * 60)
    hours = minutes // 60
    rest = minutes % 60
    return f"{hours:02d}:{rest:02d}"


def pieces_bar(state):
    return "●" * state["pieces"] + "○" * (MAX_PIECES - state["pieces"])


def transparency(state):
    """Krátká věta o tom, jak moc je hráč průhledný."""
    pieces = state["pieces"]
    if pieces == 5:
        return f"Jsi {g(state, 'celý', 'celá')} a pevně stojíš na zemi."
    if pieces == 4:
        return f"Konečky prstů ti lehce průsvitní, jako bys je {g(state, 'držel', 'držela')} proti lampě."
    if pieces == 3:
        return "Přes ruce ti prosvítá podlaha."
    if pieces == 2:
        return "Tvůj stín je výraznější než ty. Lidé by tě přehlédli i ve frontě."
    if pieces == 1:
        return "Zrcadlo tě skoro neukazuje. Zbývá z tebe jen obrys a ozvěna."
    return "Nejsi tu."
