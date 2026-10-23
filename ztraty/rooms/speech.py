"""Kabinet ztracených řečí – v každé sklenici je hlas, který někomu došel uprostřed věty."""

from ..actions import Action, heal, lose_piece
from ..state import MAX_PIECES, GameState

TITLE = "Kabinet ztracených řečí"

JARS = {
    "laugh": "malou sklenici",
    "whisper": "sklenici s cedulkou „B. H.“",
    "curses": "baňatou sklenici od zelí",
}


def _listen(state: GameState, ui) -> None:
    ui.say("Přikládáš ucho ke sklenicím:")
    if "jar_laugh_gone" not in state.flags:
        ui.say("• Malá sklenice: tiché chichotání. Něčí ztracený smích.")
    if "jar_whisper_gone" not in state.flags:
        ui.say("• Sklenice „B. H.“: unavený hlas šeptá „…jdi po červené niti…“")
    ui.say("• Baňatá sklenice od zelí: syčení a sprostá slova. Tu radši neotvírat.")


def _open(jar: str):
    def handler(state: GameState, ui) -> None:
        ui.sfx("Pšššš!")
        if jar == "curses":
            lose_piece(state, ui, "Ven vyletí hejno nadávek a zalezou ti do uší. Kus tebe se studem schová a už ho nenajdeš.")
        elif jar == "whisper":
            state.flags.update({"jar_whisper_gone", "red_hint"})
            ui.say("Vyletí hlas pana Hlaváčka: „Kdyby se mi něco stalo, jdi po červené niti. A přines mi něco, podle čeho se poznám.“")
        elif state.pieces >= MAX_PIECES:
            state.flags.add("jar_laugh_gone")
            state.give_or_drop("laugh_jar")
            ui.say("Uvnitř se něco chichotá. Teď ti nic nechybí, tak si sklenici se smíchem schováš na později.")
        else:
            state.flags.add("jar_laugh_gone")
            heal(state, ui, 1, "Ven vyprskne smích a rozběhne se po kabinetu. Kousek tebe se vrátil.")

    return handler


def describe(state: GameState) -> str:
    return (
        "Na policích stojí zavařovací sklenice a v každé je hlas, který někomu došel uprostřed věty. "
        "Stranou stojí tři sklenice, jako by na tebe čekaly."
    )


def actions(state: GameState) -> list[Action]:
    result = [Action("listen", "Poslouchat u sklenic", _listen)]
    for jar, name in JARS.items():
        if f"jar_{jar}_gone" not in state.flags:
            result.append(Action(f"open:{jar}", f"Otevřít {name}", _open(jar)))
    return result
