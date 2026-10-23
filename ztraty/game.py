"""Hlavní smyčka hry: místnost, nabídka, akce, plynutí času."""

import argparse

from . import art, endings, head
from .actions import Action, item_actions, lose_piece, noop
from .items import ITEMS
from .rooms import ROOMS
from .state import GameState
from .ui import ConsoleUI

FACE_DAMAGE_TURNS = (4, 7)
FACE_LIMIT = 10
TIME_WARNINGS = {
    60: "Někde nahoře odbila pátá. Do příchodu denní směny zbývá hodina.",
    30: "Za okénkem u stropu šedne obloha. Zbývá půl hodiny.",
    15: "Ptáci. Venku zpívají ptáci. Zbývá čtvrthodina!",
}

HELP = """[bold]Jak se hraje[/bold]
• Vybíráš akce zadáním čísla. Každá akce zabere [bold]5 minut[/bold]; šedé akce jsou zadarmo.
• Směna začíná o půlnoci. V [bold]6:00[/bold] přijde denní směna – do té doby musíš zjistit, co se stalo s panem Hlaváčkem.
• Máš pět [bold]kousků sebe[/bold] (●). Chybami průhledníš. Když přijdeš o všechny, ztratíš se.
• Do kapes saka se vejdou jen [bold]čtyři[/bold] věci. Rozmýšlej, co si vezmeš.
• Hádanky se řeší tak, že česká rčení platí doslova. Kdo ztratil hlavu, potřebuje ji vrátit. Kdo ztratil nit, musí jít po niti.
• Když nevíš kudy kam, zvedni u přepážky telefon."""


def intro(state: GameState) -> str:
    g = state.g
    return (
        "Je pár minut před půlnocí, když sejdeš po schodech pod starou poštu. Nastupuješ "
        f"jako {g('nový noční úředník', 'nová noční úřednice')} do Centrálního úřadu ztrát a nálezů. "
        "Inzerát v novinách byl krátký: „Přijmeme na noční směnu. Podmínka: musíte něco postrádat.“ "
        "Tehdy ti to připadalo jako vtip.\n\n"
        "Tvůj předchůdce, pan Hlaváček, minulý týden beze stopy zmizel. Jeho poslední zápis v deníku zní: "
        "[italic]„Někdo tu zase ztratil hlavu. Jdu dolů to vyřešit.“[/italic] Od té doby ho nikdo neviděl.\n\n"
        "Úřad otevírá v šest ráno. Do té doby musíš zjistit, co se Hlaváčkovi stalo. A hlavně nedopadnout stejně.\n\n"
        + HELP
    )


def show_room(state: GameState, ui, animate: bool = False) -> None:
    room = ROOMS[state.location]
    text = room.describe(state)
    native = getattr(room, "NATIVE_ITEMS", ())
    loose = [ITEMS[item_id].name for item_id in dict.fromkeys(state.here()) if item_id not in native]
    if loose:
        text += "\nNa zemi leží: " + ", ".join(loose) + "."
    ui.room(room.TITLE, text, art.ROOMS.get(state.location), animate)


def _look(state: GameState, ui) -> None:
    show_room(state, ui)


def _help(state: GameState, ui) -> None:
    ui.say(HELP)


def _quit(state: GameState, ui) -> None:
    state.ending = "quit"


def _cycle_speed(state: GameState, ui) -> None:
    ui.say(f"Rychlost textu: {ui.cycle_speed()}.")


def meta_actions(ui) -> list[Action]:
    return [
        Action("look", "Rozhlédnout se", _look, cost=0),
        Action("help", "Nápověda", _help, cost=0),
        Action("speed", f"Rychlost textu: {ui.speed}", _cycle_speed, cost=0),
        Action("quit", "Ukončit hru", _quit, cost=0),
    ]


def _face_tick(state: GameState, ui) -> None:
    state.face_turns += 1
    if state.face_turns >= FACE_LIMIT:
        state.ending = "director"
    elif state.face_turns in FACE_DAMAGE_TURNS:
        lose_piece(
            state,
            ui,
            "Ředitelova tvář ti přirůstá k lícím. Když se chceš usmát, usměje se ona – po svém, chladně. "
            "Tvoje vlastní tvář pod ní bledne.",
        )
    elif state.face_turns == FACE_DAMAGE_TURNS[-1] + 1:
        ui.bad("Okraje tváře už nenahmatáš. Jestli ji chceš někdy sundat, teď je nejvyšší čas.")


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
        ui.good(
            "Ručičky se blíží k šesté, když ti v kapse něco praskne. Ztracená hodina se sama rozbalí "
            "a všechny hodiny v úřadu couvnou o hodinu zpátky. Ještě není konec!"
        )
    for threshold, warning in TIME_WARNINGS.items():
        if left_before > threshold >= left:
            ui.sfx("Bim… bam… bim…")
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
    ui.room("Noční směna", intro(state))
    ui.pause()
    return state


def play(ui, state: GameState) -> GameState:
    shown = None
    seen: set[str] = set()
    while state.ending is None:
        if shown != state.location:
            # Popis se píše animovaně jen při první návštěvě, pak už se jen ukáže.
            show_room(state, ui, animate=state.location not in seen)
            seen.add(state.location)
            shown = state.location
        ui.hud(state)
        actions = ROOMS[state.location].actions(state) + item_actions(state) + meta_actions(ui)
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
        ui.farewell("\nSměna přerušena. Na shledanou!")
