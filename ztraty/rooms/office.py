"""Ředitelna – kartotéka a v ní spis se jménem hráče."""

from ..actions import Action, go
from ..state import GameState

TITLE = "Ředitelna"


def _own_file(state: GameState, ui) -> None:
    g = state.g
    ui.say(
        "V šuplíku na písmeno, které je tvoje, najdeš tenké desky se svým jménem. Papír je ještě teplý, "
        "jako by ho někdo psal teprve dnes v noci."
    )
    ui.say(
        f"[italic]„{g('Uchazeč', 'Uchazečka')} o místo nočního {g('úředníka', 'úřednice')}. "
        f"Důvod přijetí: {g('dotyčný', 'dotyčná')} {g('sám', 'sama')} něco {g('ztratil', 'ztratila')}. "
        "Předmět ztráty: naděje. Ztraceno: postupně, za poslední roky, nikdo si nevšiml kdy. "
        "Uloženo: Místnost nehledaných věcí, krabice se jménem. Stav: nikdo nehledá.“[/italic]"
    )
    ui.say(
        "Teprve teď ti to dojde. Do úřadu berou jen lidi, kteří sami něco ztratili. Tvůj inzerát nebyl "
        "náhoda a tahle práce taky ne."
    )
    if "read_own_file" not in state.flags:
        state.flags.add("read_own_file")
        if state.give_or_drop("own_photo"):
            ui.good("Ke spisu je sponkou připnutá tvoje fotka. Vezmeš si ji.")
        else:
            ui.say("Ke spisu je připnutá tvoje fotka. Kapsy máš plné, tak ji necháš ležet na stole.")


def _hlavacek_file(state: GameState, ui) -> None:
    state.flags.add("red_hint")
    ui.say(
        "[italic]„Bohumil Hlaváček. Noční služba od roku 1979. Důvod přijetí: ztratil domov. "
        "Poslední záznam: ztratil sám sebe. Uloženo: Místnost nehledaných věcí. Přístup: po červené niti z archivu. "
        "Doporučení: připomenout mu, kdo je.“[/italic]"
    )


def _chair(state: GameState, ui) -> None:
    if state.face_worn:
        state.ending = "director"
        return
    ui.say("Křeslo pod tebou nespokojeně zavrže, jako by čekalo někoho jiného. Radši zase vstaneš.")


def describe(state: GameState) -> str:
    parts = [
        "Ředitelna. Mahagonový stůl, zelená lampa, těžký koberec, který spolkne každý krok. Za stolem křeslo "
        "s vysokým opěradlem, které vypadá, jako by na někoho čekalo. Na stěně visí portrét bez tváře. "
        "V rohu stojí kartotéka se šuplíky podle abecedy.",
    ]
    if state.face_worn:
        parts.append("S ředitelovou tváří na obličeji tu cítíš zvláštní pocit, že ti to tu všechno patří.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    return [
        Action("own_file", "Prohledat kartotéku: spis se svým jménem", _own_file),
        Action("hlavacek_file", "Prohledat kartotéku: spis pana Hlaváčka", _hlavacek_file),
        Action("chair", "Sednout si do ředitelova křesla", _chair),
        Action("back", "Vrátit se k přepážce", go("counter")),
    ]
