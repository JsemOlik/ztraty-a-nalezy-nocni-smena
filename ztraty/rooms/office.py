"""Ředitelna – kartotéka a v ní spis se jménem hráče."""

from ..actions import Action
from ..state import GameState

TITLE = "Ředitelna"


def enter(state: GameState, ui) -> int | None:
    if not state.face_worn:
        ui.say("Ředitelna je zamčená. Na dveřích je kukátko a cedule: „Jen pro pana ředitele. Poznám ho po tváři.“")
        return 0
    state.location = "office"
    ui.say("Kukátko si tě prohlédne a zámek cvakne: „Dobrý večer, pane řediteli.“")
    return None


def _search_files(state: GameState, ui) -> None:
    g = state.g
    ui.say(
        "[italic]Spis: Bohumil Hlaváček. Ztratil sám sebe. Uloženo: Místnost nehledaných věcí, "
        "přístup po červené niti.[/italic]"
    )
    ui.say(
        f"[italic]Spis s tvým jménem: {g('Přijat', 'Přijata')}, protože {g('sám', 'sama')} něco {g('ztratil', 'ztratila')}. "
        "Předmět ztráty: naděje. Uloženo: Místnost nehledaných věcí, krabice se jménem. Nikdo nehledá.[/italic]"
    )
    ui.say("Do úřadu berou jen lidi, kteří sami něco ztratili. Tahle práce nebyla náhoda.")
    state.flags.add("red_hint")
    if "read_own_file" not in state.flags:
        state.flags.add("read_own_file")
        if state.give_or_drop("own_photo"):
            ui.good("Ke spisu je připnutá tvoje fotka. Vezmeš si ji – podle ní poznáš svou krabici.")
        else:
            ui.say("Ke spisu je připnutá tvoje fotka. Kapsy máš plné, tak ji necháš na stole.")


def _chair(state: GameState, ui) -> None:
    if state.face_worn:
        state.ending = "director"
        return
    ui.say("Křeslo pod tebou nespokojeně zavrže, jako by čekalo někoho jiného.")


def describe(state: GameState) -> str:
    return "Mahagonový stůl, zelená lampa a křeslo s vysokým opěradlem, které na někoho čeká. V rohu stojí kartotéka."


def actions(state: GameState) -> list[Action]:
    return [
        Action("files", "Prohledat kartotéku", _search_files),
        Action("chair", "Sednout si do ředitelova křesla", _chair),
    ]
