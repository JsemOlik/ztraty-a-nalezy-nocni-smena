"""Hlavní smyčka hry: místnost, nabídka, akce, plynutí času."""

import argparse

from . import art, endings, head
from .actions import Action, item_actions, lose_piece, noop
from .goals import objective
from .items import ITEMS
from .rooms import ROOMS, room_actions
from .state import GameState
from .ui import ConsoleUI

FACE_DAMAGE_TURNS = (4, 7)
FACE_LIMIT = 10
TIME_WARNINGS = {
    60: "Odbila pátá. Do příchodu denní směny zbývá hodina.",
    30: "Obloha šedne. Zbývá půl hodiny.",
    15: "Venku zpívají ptáci. Zbývá čtvrthodina!",
}

HELP = """[bold]Jak se hraje[/bold]
• Napiš číslo volby a Enter. Každá akce zabere [bold]5 minut[/bold] (šedé volby nic nestojí).
• Nahoře je vždy [bold]Úkol[/bold] – co dělat dál.
• [bold]Kousky sebe[/bold] ●●●●●: chybami průhledníš. O všechny nepřijď.
• Do kapes se vejdou [bold]4 věci[/bold].
• Rčení tu platí doslova: kdo ztratil hlavu, musí ji dostat zpátky. Kdo ztratil nit, jde po niti."""


def intro(state: GameState) -> str:
    g = state.g
    return (
        f"Je půlnoc. Nastupuješ jako {g('noční úředník', 'noční úřednice')} do úřadu ztrát a nálezů "
        "pod starou poštou. Končí tu všechno, co lidé ztratí – deštníky, ale i čas, řeč nebo hlava.\n\n"
        "Tvůj předchůdce, pan Hlaváček, zmizel. Jeho poslední zápis v deníku: "
        "[italic]„Někdo tu zase ztratil hlavu. Jdu dolů to vyřešit.“[/italic]\n\n"
        "[bold yellow]Cíl: najdi pana Hlaváčka do šesti ráno.[/bold yellow]\n\n"
        + HELP
    )


def describe_room(state: GameState) -> str:
    room = ROOMS[state.location]
    text = room.describe(state)
    native = getattr(room, "NATIVE_ITEMS", ())
    loose = [ITEMS[item_id].name for item_id in dict.fromkeys(state.here()) if item_id not in native]
    if loose:
        text += "\nNa zemi leží: " + ", ".join(loose) + "."
    return text


def _help(state: GameState, ui) -> None:
    ui.say(HELP)


def _cycle_speed(state: GameState, ui) -> None:
    ui.say(f"Rychlost textu: {ui.cycle_speed()}.")


def _quit(state: GameState, ui) -> None:
    state.ending = "quit"


def meta_actions(ui) -> list[Action]:
    return [
        Action("help", "nápověda", _help, cost=0, hotkey="n"),
        Action("speed", f"rychlost textu ({ui.speed})", _cycle_speed, cost=0, hotkey="r"),
        Action("quit", "konec", _quit, cost=0, hotkey="k"),
    ]


def _face_tick(state: GameState, ui) -> None:
    state.face_turns += 1
    if state.face_turns >= FACE_LIMIT:
        state.ending = "director"
    elif state.face_turns in FACE_DAMAGE_TURNS:
        lose_piece(state, ui, "Ředitelova tvář ti přirůstá k lícím. Tvoje vlastní tvář pod ní bledne.")
    elif state.face_turns == FACE_DAMAGE_TURNS[-1] + 1:
        ui.bad("Okraje tváře už skoro nenahmatáš. Sundej ji, dokud to jde!")


def pass_time(state: GameState, ui, minutes: int) -> None:
    """Posune čas a vyhodnotí vše, co se děje mezi akcemi."""
    left_before = state.deadline - state.minutes
    state.minutes += minutes
    if state.face_worn:
        _face_tick(state, ui)
    if state.ending:
        return
    if state.pieces <= 0:
        state.ending = "nobody_searches"
        return
    left = state.deadline - state.minutes
    if left <= 0:
        if not state.has("lost_hour"):
            state.ending = "inventory"
            return
        state.remove_item("lost_hour")
        state.deadline += 60
        left = state.deadline - state.minutes
        left_before = left + minutes
        ui.good("Odbíjí šestá, když ti v kapse praskne ztracená hodina. Všechny hodiny couvnou o hodinu zpátky!")
    for threshold, warning in TIME_WARNINGS.items():
        if left_before > threshold >= left:
            ui.sfx("Bim… bam…")
            ui.bad(warning)
    if state.has("head"):
        ui.head(head.comment(state))


def new_game(ui) -> GameState:
    ui.title_screen()
    choice = ui.choose(
        [
            Action("male", "Nastupuji jako noční úředník", noop, cost=0),
            Action("female", "Nastupuji jako noční úřednice", noop, cost=0),
        ],
        "Kdo nastupuje na směnu?",
    )
    state = GameState(feminine=choice.key == "female")
    ui.page("Noční směna", intro(state))
    ui.pause()
    return state


def play(ui, state: GameState) -> GameState:
    while state.ending is None:
        room = ROOMS[state.location]
        ui.set_scene(state, room.TITLE, describe_room(state), art.ROOMS.get(state.location), objective(state))
        actions = room_actions(state) + item_actions(state) + meta_actions(ui)
        action = ui.choose(actions)
        spent = action.handler(state, ui)
        spent = action.cost if spent is None else spent
        if state.ending is not None:
            state.minutes += spent
        elif spent > 0:
            pass_time(state, ui, spent)
    endings.show(state, ui)
    return state


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Ztráty a nálezy: noční směna")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--rychle", action="store_true", help="rychlejší psaní textu")
    group.add_argument("--bez-animaci", action="store_true", help="vypne animace textu")
    args = parser.parse_args(argv)
    speed = "vypnutá" if args.bez_animaci else "rychlá" if args.rychle else "normální"
    ui = ConsoleUI(speed=speed)
    try:
        with ui:
            while True:
                state = play(ui, new_game(ui))
                if state.ending == "quit":
                    break
                again = ui.choose(
                    [Action("again", "Nastoupit na další směnu", noop, cost=0), Action("end", "Jít domů", noop, cost=0)],
                    "A teď?",
                )
                if again.key == "end":
                    break
    except (KeyboardInterrupt, EOFError):
        pass
    ui.farewell("Díky za noční směnu. Na shledanou!")
