"""Galerie ztracených tváří – masky lidí, kteří se kdysi ztrapnili."""

from ..actions import Action, make_room, wear_face
from ..state import GameState

TITLE = "Galerie ztracených tváří"
NATIVE_ITEMS = ("director_face",)


def _take_and_wear(state: GameState, ui) -> int | None:
    if not make_room(state, ui):
        return 0
    state.here().remove("director_face")
    state.add_item("director_face")
    wear_face(state, ui)
    return None


def describe(state: GameState) -> str:
    parts = ["Masky lidí, kteří se kdysi ztrapnili. Tiše rudnou a uhýbají pohledem."]
    if "director_face" in state.here():
        parts.append("V pozlaceném rámu visí tvář pana ředitele. Jako jediná se nestydí. Ředitelna by ji jistě poznala.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    if "director_face" in state.here():
        return [Action("wear_face", "Nasadit si ředitelovu tvář", _take_and_wear)]
    return []
