"""Oddělení ztraceného času – stovky hodin a každé jdou jinak."""

from ..actions import Action
from ..state import ACTION_MINUTES, GameState
from ..text import fmt_time

TITLE = "Oddělení ztraceného času"

CLOCKS = ["Kukačky", "Starý budík", "Věžní ciferník", "Náramkové hodinky", "Kyvadlové hodiny"]
WRONG_CLOCK_PENALTY = 15


def _clock_puzzle(state: GameState, ui) -> int | None:
    offsets = state.rng.sample([-60, -25, -10, 10, 20, 45, 60], 3)
    times = [state.minutes] + [state.minutes + offset for offset in offsets]
    faces = state.rng.sample(CLOCKS, 4)
    options = [
        Action("clock:right" if index == 0 else f"clock:wrong{index}", f"{face}: {fmt_time(time)}", lambda s, u: None)
        for index, (face, time) in enumerate(zip(faces, times))
    ]
    state.rng.shuffle(options)
    ui.sfx("Tik. Tak. Tik. Tak.")
    ui.say("Většina hodin lže. Jen jedny ukazují přesně tvůj čas – ten nahoře na obrazovce.")
    chosen = ui.choose(options, "Které hodiny jdou správně?")
    if chosen.key == "clock:right":
        state.flags.add("lost_hour_found")
        ui.good("Správně! Z dvířek hodin vypadne ztracená hodina. Použij ji, až bude čas docházet.")
        if not state.give_or_drop("lost_hour"):
            ui.say("Kapsy máš plné, tak hodina cinkne o podlahu vedle tebe.")
        return None
    ui.sfx("CRRRRR! Kuku! Kuku!")
    ui.bad("Špatné hodiny! Rozdrnčí se a ukousnou ti čtvrthodinu.")
    return ACTION_MINUTES + WRONG_CLOCK_PENALTY


def _steal_time(state: GameState, ui) -> None:
    while state.add_item("stolen_time"):
        pass
    ui.say("Cpeš si do kapes hrsti cizích minut. Kdesi ve městě někomu právě zmizelo odpoledne.")
    if state.has("head"):
        ui.head("To není naše! Tohle někomu chybí!")


def _return_time(state: GameState, ui) -> None:
    while state.has("stolen_time"):
        state.remove_item("stolen_time")
    ui.say("Vysypeš ukradený čas zpátky do misek. Někomu ve městě se vrátí kus dne.")


def describe(state: GameState) -> str:
    parts = ["Stovky hodin na stěnách i na zemi a každé jdou jinak. Na pultě se v miskách třpytí volné minuty. Nikdo je nehlídá."]
    if "lost_hour_found" not in state.flags:
        parts.append("Cedule: „Kdo najde hodiny, které jdou správně, tomu se odvděčí.“")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    result = []
    if "lost_hour_found" not in state.flags:
        result.append(Action("clock_puzzle", "Hledat hodiny, které jdou správně", _clock_puzzle))
    if not state.pockets_full():
        result.append(Action("steal_time", "Nacpat si kapsy ukradeným časem", _steal_time))
    if state.has("stolen_time"):
        result.append(Action("return_time", "Vrátit ukradený čas", _return_time))
    return result
