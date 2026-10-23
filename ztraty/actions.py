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


def noop(state: GameState, ui) -> None:
    return None


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
    ui.say(transparency(state))
    return True


# --- Použití předmětů ---------------------------------------------------------


def _use_lost_hour(state: GameState, ui) -> None:
    state.remove_item("lost_hour")
    state.deadline += 60
    ui.good(
        "Rozbalíš ztracenou hodinu jako bonbon. Chvíli tiká na dlani, pak se rozplyne do vzduchu "
        "a všechny hodiny v úřadu se najednou zarazí a couvnou o hodinu zpátky. Noc je delší."
    )


def _use_laugh_jar(state: GameState, ui) -> None:
    if heal(
        state,
        ui,
        1,
        "Odšroubuješ víčko. Ven vyprskne smích – zvonivý, trochu přiblblý a úplně nakažlivý. "
        "Smíchem se ti zahřeje hrudník a kus tebe se vrátí na své místo.",
    ):
        state.remove_item("laugh_jar")


def _use_own_photo(state: GameState, ui) -> None:
    if heal(
        state,
        ui,
        2,
        "Zadíváš se na fotku. Ten člověk na ní se směje a je to opravdu ty. Vzpomeneš si, jaké to je, "
        "být někým. Kousky tebe se vracejí – a fotka u toho vybledne do čistého bílého papíru.",
    ):
        state.remove_item("own_photo")
        state.flags.add("photo_used")


def _wear_face(state: GameState, ui) -> None:
    state.face_worn = True
    state.face_turns = 0
    ui.say(
        "Přiložíš si ředitelovu tvář k obličeji. Přilne sama, chladně a hladce, jako by tam vždycky patřila. "
        "Narovnáš se. Najednou máš chuť někoho napomenout."
    )
    ui.bad("Cizí tvář se nemá nosit dlouho. Kdo si nasadí cizí tvář, riskuje, že ztratí tu svou.")


ITEM_USES: dict[str, Handler] = {
    "lost_hour": _use_lost_hour,
    "laugh_jar": _use_laugh_jar,
    "own_photo": _use_own_photo,
    "director_face": _wear_face,
}


def remove_face(state: GameState, ui) -> None:
    state.face_worn = False
    state.face_turns = 0
    ui.say(
        "Zaryješ nehty pod okraj ředitelovy tváře a pomalu ji sloupneš. Pod ní je tvůj vlastní obličej, "
        "trochu pomačkaný, ale tvůj. Vydechneš."
    )


# --- Braní a odkládání --------------------------------------------------------

PICKUP_TEXTS = {
    "head": (
        "Opatrně zvedneš hlavu z krabice na klobouk. Je těžší, než vypadá, a okamžitě začne mluvit: "
        "„Konečně! Kde to jsem? Kdo jste? Neupusťte mě! Hlavně mě neupusťte!“"
    ),
    "red_thread": "Sevřeš konec červené niti. Ucítíš jemný tah, jako když tě někdo vede za ruku.",
    "director_face": (
        "Sundáš tvář ze zdi. Je teplá a lehce se zavlní, jako by se usmála. To se řediteli za života prý nikdy nestalo."
    ),
}


def _take(item_id: str) -> Handler:
    def handler(state: GameState, ui) -> int | None:
        item = ITEMS[item_id]
        if state.pockets_full():
            ui.say(f"Kapsy saka máš plné. Než si vezmeš {item.accusative}, musíš něco odložit.")
            return 0
        state.here().remove(item_id)
        state.add_item(item_id)
        ui.say(PICKUP_TEXTS.get(item_id, f"Strčíš si do kapsy {item.accusative}."))
        return None

    return handler


def _drop(item_id: str) -> Handler:
    def handler(state: GameState, ui) -> int | None:
        item = ITEMS[item_id]
        if item_id == "director_face" and state.face_worn:
            ui.say("Tvář máš pořád na obličeji. Nejdřív ji musíš sundat.")
            return 0
        if item_id == "red_thread" and state.location == "hidden":
            ui.bad(f"Kdybys tu {state.g('pustil', 'pustila')} nit, už nikdy nenajdeš cestu zpátky.")
            return 0
        state.remove_item(item_id)
        if item_id == "stolen_time":
            ui.say("Vysypeš hrst ukradeného času. Minuty se rozcupitají po podlaze a utečou zpátky do oddělení ztraceného času.")
            return None
        state.here().append(item_id)
        ui.say(f"Odložíš {item.accusative}.")
        if item_id == "head":
            ui.head("Cože? Tady? Na zemi? Nenechávejte mě tu, prosím, já se bojím tmy, světla i podlahy!")
        return None

    return handler


def _open_pockets(state: GameState, ui) -> int | None:
    unique = list(dict.fromkeys(state.pockets))
    for item_id in unique:
        item = ITEMS[item_id]
        ui.say(f"• {item.name}: {item.description}")
    sub: list[Action] = []
    for item_id in unique:
        item = ITEMS[item_id]
        if item.usable and not (item_id == "director_face" and state.face_worn):
            sub.append(Action(f"use:{item_id}", f"{item.use_label} {item.accusative}", ITEM_USES[item_id]))
    for item_id in unique:
        sub.append(Action(f"drop:{item_id}", f"Odložit {ITEMS[item_id].accusative}", _drop(item_id), cost=0))
    sub.append(Action("back", "Zpět", noop, cost=0))
    chosen = ui.choose(sub, "Co s tím?")
    spent = chosen.handler(state, ui)
    return chosen.cost if spent is None else spent


def item_actions(state: GameState) -> list[Action]:
    """Braní předmětů ležících v místnosti a práce s kapsami."""
    actions = [
        Action(f"take:{item_id}", f"Vzít {ITEMS[item_id].accusative}", _take(item_id))
        for item_id in dict.fromkeys(state.here())
    ]
    if state.face_worn:
        actions.append(Action("remove_face", "Sundat si ředitelovu tvář", remove_face))
    if state.pockets:
        actions.append(Action("pockets", "Kapsy (prohlédnout, použít, odložit)", _open_pockets, cost=0))
    return actions


def go(target: str) -> Handler:
    def handler(state: GameState, ui) -> None:
        state.location = target

    return handler
