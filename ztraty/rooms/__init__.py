"""Místnosti úřadu. Každý modul má TITLE, describe(state) a actions(state);
volitelně enter(state, ui) při vstupu a no_travel(state), když se odtud nedá jen tak odejít."""

from ..actions import Action, run_submenu
from . import cellar, counter, faces, hidden, office, speech, threads, time_dept, umbrellas

ROOMS = {
    "counter": counter,
    "umbrellas": umbrellas,
    "time_dept": time_dept,
    "speech": speech,
    "threads": threads,
    "faces": faces,
    "cellar": cellar,
    "office": office,
    "hidden": hidden,
}

# Do skryté místnosti se dá dojít jen po niti.
UNLISTED = {"hidden"}


def _enter(key: str):
    def handler(state, ui) -> int | None:
        enter = getattr(ROOMS[key], "enter", None)
        if enter:
            return enter(state, ui)
        state.location = key
        return None

    return handler


def _travel(state, ui) -> int:
    options = [
        Action(f"go:{key}", room.TITLE, _enter(key))
        for key, room in ROOMS.items()
        if key != state.location and key not in UNLISTED
    ]
    options.append(Action("go:out", "Odejít z úřadu domů", counter.leave_building))
    return run_submenu(state, ui, options, "Kam půjdeš?")


def room_actions(state) -> list[Action]:
    room = ROOMS[state.location]
    result = room.actions(state)
    no_travel = getattr(room, "no_travel", None)
    if not (no_travel and no_travel(state)):
        result.append(Action("travel", "Jít jinam…", _travel, cost=0))
    return result
