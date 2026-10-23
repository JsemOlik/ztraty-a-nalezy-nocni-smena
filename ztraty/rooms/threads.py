"""Archiv ztracených nití – klubka lidí, kteří ztratili nit."""

from ..actions import Action, lose_piece, make_room
from ..state import ACTION_MINUTES, GameState

TITLE = "Archiv ztracených nití"
NATIVE_ITEMS = ("red_thread",)

LOST_PENALTY = 30

WRONG_THREADS = {
    "blue": ("modré", "Modrá nit vede do cizí nedokončené přednášky o termodynamice. Bloudíš v ní celou věčnost."),
    "gold": ("zlaté", "Zlatá nit vede do něčího snu o bohatství. Cesta zpátky se pořád stáčí do kruhu."),
}


def _follow_red(state: GameState, ui) -> int | None:
    if not state.has("red_thread"):
        if not make_room(state, ui):
            ui.say("Kdo jde po niti, musí ji držet. Bez volné kapsy to nepůjde.")
            return 0
        state.here().remove("red_thread")
        state.add_item("red_thread")
    state.location = "hidden"
    ui.say("Sevřeš červenou nit a jdeš. Zeď se rozestoupí a nit tě vede chodbou, která není na žádném plánku.")
    return None


def _follow_wrong(color: str):
    genitive, text = WRONG_THREADS[color]

    def handler(state: GameState, ui) -> int:
        ui.say(f"Chytíš se {genitive} niti a jdeš za ní.")
        lose_piece(state, ui, text)
        ui.say("Než se vymotáš zpátky do archivu, uběhne půl hodiny.")
        return ACTION_MINUTES + LOST_PENALTY

    return handler


def describe(state: GameState) -> str:
    return (
        "Regály plné klubek od lidí, kteří „ztratili nit“. Tři nitě se táhnou přes podlahu a mizí ve zdi: "
        "červená, modrá a zlatá."
    )


def actions(state: GameState) -> list[Action]:
    return [
        Action("follow:red", "Jít po červené niti", _follow_red),
        Action("follow:blue", "Jít po modré niti", _follow_wrong("blue")),
        Action("follow:gold", "Jít po zlaté niti", _follow_wrong("gold")),
    ]
