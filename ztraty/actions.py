"""Akce hráče a společné efekty (ztráta a návrat kousků sebe, práce s kapsami)."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .items import ITEMS
from .state import ACTION_MINUTES, MAX_PIECES, GameState
from .text import transparency

# Handler dostane stav a UI. Vrátí-li číslo, je to skutečně strávený čas v minutách;
# vrátí-li None, započítá se `cost` akce.
Handler = Callable[[GameState, Any], int | None]


@dataclass
class Action:
    key: str
    label: str
    handler: Handler
    cost: int = ACTION_MINUTES
    # Akce s klávesovou zkratkou se nečíslují a ukazují se v patičce.
    hotkey: str | None = None


def noop(state: GameState, ui) -> None:
    return None


def run_submenu(state: GameState, ui, options: list[Action], prompt: str) -> int:
    """Nabídne podvolbu a vrátí čas, který zabrala."""
    chosen = ui.choose(options + [Action("back", "Zpět", noop, cost=0)], prompt)
    spent = chosen.handler(state, ui)
    return chosen.cost if spent is None else spent


def lose_piece(state: GameState, ui, text: str) -> None:
    state.pieces -= 1
    ui.bad(text)
    ui.flicker("Ztrácíš kousek sebe.")
    if state.pieces > 0:
        ui.say(transparency(state))


def heal(state: GameState, ui, amount: int, text: str) -> bool:
    if state.pieces >= MAX_PIECES:
        ui.say(f"Teď jsi {state.g('celý', 'celá')}. Necháš si to na horší chvíli.")
        return False
    state.pieces = min(MAX_PIECES, state.pieces + amount)
    ui.good(text)
    return True


# --- Použití předmětů ---------------------------------------------------------


def _use_lost_hour(state: GameState, ui) -> None:
    state.remove_item("lost_hour")
    state.deadline += 60
    ui.good("Rozbalíš ztracenou hodinu. Všechny hodiny v úřadu couvnou o hodinu zpátky. Noc je delší.")


def _use_laugh_jar(state: GameState, ui) -> None:
    if heal(state, ui, 1, "Otevřeš sklenici a ven vyprskne smích. Hned je ti líp – kousek tebe se vrátil."):
        state.remove_item("laugh_jar")


def _use_own_photo(state: GameState, ui) -> None:
    if heal(state, ui, 2, "Zadíváš se na fotku. Vzpomeneš si, kdo jsi. Fotka u toho vybledne do bílého papíru."):
        state.remove_item("own_photo")
        state.flags.add("photo_used")


def wear_face(state: GameState, ui) -> None:
    state.face_worn = True
    state.face_turns = 0
    ui.say("Přiložíš si ředitelovu tvář. Přilne sama, chladně a hladce. Najednou máš chuť někoho napomenout.")
    ui.bad("Pozor: kdo nosí cizí tvář dlouho, ztratí tu svou.")


ITEM_USES: dict[str, Handler] = {
    "lost_hour": _use_lost_hour,
    "laugh_jar": _use_laugh_jar,
    "own_photo": _use_own_photo,
    "director_face": wear_face,
}


def remove_face(state: GameState, ui) -> None:
    state.face_worn = False
    state.face_turns = 0
    ui.say("Sloupneš ředitelovu tvář. Pod ní je tvůj vlastní obličej. Uf.")


# --- Kapsy --------------------------------------------------------------------

PICKUP_TEXTS = {
    "head": "Zvedneš hlavu z krabice. Okamžitě začne mluvit: „Konečně! Hlavně mě neupusťte!“",
}


def drop_item(state: GameState, ui, item_id: str) -> bool:
    item = ITEMS[item_id]
    if item_id == "director_face" and state.face_worn:
        ui.say("Tvář máš pořád na obličeji. Nejdřív ji sundej.")
        return False
    if item_id == "red_thread" and state.location == "hidden":
        ui.bad(f"Kdybys tu {state.g('pustil', 'pustila')} nit, už nenajdeš cestu zpátky.")
        return False
    state.remove_item(item_id)
    if item_id == "stolen_time":
        ui.say("Ukradený čas se ti rozsype a uteče zpátky do oddělení ztraceného času.")
        return True
    state.here().append(item_id)
    ui.say(f"Odložíš {item.accusative}.")
    if item_id == "head":
        ui.head("Cože? Na zem? Nenechávejte mě tu!")
    return True


def make_room(state: GameState, ui) -> bool:
    """Když jsou kapsy plné, zeptá se, co odložit. Vrátí True, pokud je místo."""
    if not state.pockets_full():
        return True
    options = [
        Action(f"drop:{held}", f"Odložit {ITEMS[held].accusative}", noop, cost=0)
        for held in dict.fromkeys(state.pockets)
    ]
    options.append(Action("keep", "Nic, nechám to být", noop, cost=0))
    chosen = ui.choose(options, "Kapsy máš plné. Co odložíš?")
    if chosen.key == "keep":
        return False
    return drop_item(state, ui, chosen.key.removeprefix("drop:"))


def take_item(state: GameState, ui, item_id: str) -> bool:
    if not make_room(state, ui):
        return False
    state.here().remove(item_id)
    state.add_item(item_id)
    ui.say(PICKUP_TEXTS.get(item_id, f"Vezmeš si {ITEMS[item_id].accusative}."))
    return True


def _take(item_id: str) -> Handler:
    def handler(state: GameState, ui) -> int | None:
        return None if take_item(state, ui, item_id) else 0

    return handler


def _drop(item_id: str) -> Handler:
    def handler(state: GameState, ui) -> int | None:
        return None if drop_item(state, ui, item_id) else 0

    return handler


def _open_pockets(state: GameState, ui) -> int:
    unique = list(dict.fromkeys(state.pockets))
    for item_id in unique:
        ui.say(f"• {ITEMS[item_id].name}: {ITEMS[item_id].description}")
    options: list[Action] = []
    for item_id in unique:
        item = ITEMS[item_id]
        if item.usable and not (item_id == "director_face" and state.face_worn):
            options.append(Action(f"use:{item_id}", f"{item.use_label} {item.accusative}", ITEM_USES[item_id]))
    for item_id in unique:
        options.append(Action(f"drop:{item_id}", f"Odložit {ITEMS[item_id].accusative}", _drop(item_id), cost=0))
    return run_submenu(state, ui, options, "Co s tím?")


# Předměty, které se na svém místě berou vlastní akcí (nasadit tvář, jít po niti).
SPECIAL_TAKES = {("faces", "director_face"), ("threads", "red_thread")}


def item_actions(state: GameState) -> list[Action]:
    """Braní předmětů ležících v místnosti a práce s kapsami."""
    actions = [
        Action(f"take:{item_id}", f"Vzít {ITEMS[item_id].accusative}", _take(item_id))
        for item_id in dict.fromkeys(state.here())
        if (state.location, item_id) not in SPECIAL_TAKES
    ]
    if state.face_worn:
        actions.append(Action("remove_face", "Sundat si ředitelovu tvář", remove_face))
    if state.pockets:
        actions.append(Action("pockets", "Sáhnout do kapes…", _open_pockets, cost=0))
    return actions
