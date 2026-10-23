"""Sklep – ve tmě tu pobíhá Bezhlavý."""

from ..actions import Action, lose_piece
from ..state import GameState

TITLE = "Sklep"


def enter(state: GameState, ui) -> None:
    state.location = "cellar"
    if "headless_calm" not in state.flags:
        ui.sfx("cup cup cup… cupcupcup…")


def no_travel(state: GameState) -> bool:
    """Před Bezhlavým se nedá jen tak odkráčet."""
    return "headless_calm" not in state.flags


def _head_available(state: GameState) -> bool:
    return state.has("head") or "head" in state.here()


def _return_head(state: GameState, ui) -> None:
    if state.has("head"):
        state.remove_item("head")
    else:
        state.here().remove("head")
    state.flags.update({"headless_calm", "red_hint"})
    ui.say("Kdo ztratil hlavu, potřebuje ji vrátit. Podáš ji Bezhlavému a hlava mu zaklapne na krk jako víčko.")
    ui.say(
        "„Děkuju,“ vydechne. „Minulý týden sem slezl pan Hlaváček. V panice jsem do něj vrazil a on… ztratil sám sebe. "
        "Spadl tam, kam padá všechno, co nikdo nehledá – po červené niti z archivu. Zůstala tu po něm jmenovka.“"
    )
    if state.give_or_drop("nametag"):
        ui.good("Dostáváš Hlaváčkovu jmenovku.")
    else:
        ui.say("Kapsy máš plné, tak jmenovka cinkne o zem vedle tebe.")


def _flee(state: GameState, ui) -> None:
    state.location = "counter"
    if _head_available(state):
        ui.say("Vyběhneš zpátky nahoru k přepážce.")
        return
    lose_piece(state, ui, "Utíkáš. Bezhlavý tě chytí za šos a utrhne z tebe kus – ne látky, tebe.")


def _stay(state: GameState, ui) -> None:
    state.ending = "lost_head"


def describe(state: GameState) -> str:
    if "headless_calm" in state.flags:
        return "Obyčejný sklep: brambory, uhlí, rozbité kolo. Na schodu sedí Bezhlavý s hlavou na krku a poprvé po letech v klidu dýchá."
    parts = ["Ve tmě cupitají zmatené kroky. Vynoří se Bezhlavý: muž v kabátě, místo hlavy jen límec, v nekonečné panice."]
    if state.has("head"):
        parts.append("Hlava v kapse zapiští: „To je moje tělo!“")
    elif not _head_available(state):
        parts.append(f"Nemáš nic, čím bys ho {state.g('uklidnil', 'uklidnila')}.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    if "headless_calm" in state.flags:
        return []
    if _head_available(state):
        return [
            Action("return_head", "Vrátit Bezhlavému jeho hlavu", _return_head),
            Action("flee", "Vyběhnout nahoru", _flee),
        ]
    return [
        Action("flee", "Utéct nahoru", _flee),
        Action("stay", "Zůstat a zkusit ho uklidnit", _stay),
    ]
