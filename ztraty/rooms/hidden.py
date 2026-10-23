"""Místnost nehledaných věcí – sem padá všechno, co už nikdo nehledá."""

from ..actions import Action
from ..state import GameState

TITLE = "Místnost nehledaných věcí"


def no_travel(state: GameState) -> bool:
    return True


def _talk(state: GameState, ui) -> None:
    ui.say("„Byl jsem tu úředníkem? Nebo jsem něco, co někdo ztratil?“ Muž se dívá skrz vlastní ruce. „Kdybych aspoň věděl, jak se jmenuju…“")


def _give_nametag(state: GameState, ui) -> None:
    state.remove_item("nametag")
    state.flags.add("hlavacek_found")
    ui.good("Podáš mu jmenovku. „Bohumil Hlaváček!“ přečte nahlas a do tváře se mu vrací barva.")
    ui.say(
        f"„Děkuju. A vy… vy jste tu taky {state.g('nebyl', 'nebyla')} jen tak náhodou, viďte? "
        "Sem berou jen ty, kdo něco ztratili.“"
    )


def _leave_together(state: GameState, ui) -> None:
    state.ending = "found"


def _search_box(state: GameState, ui) -> None:
    if state.has("own_photo"):
        state.ending = "lost_and_found"
        return
    reason = "fotka už je jen bílý papír" if "photo_used" in state.flags else "nemáš u sebe svou fotku"
    ui.say(f"Krabic se jmény jsou tu tisíce a všechny vybledly. Tu svou bez fotky nepoznáš – a {reason}.")


def _back(state: GameState, ui) -> None:
    state.location = "threads"
    ui.say("Jdeš po niti zpátky do archivu.")


def describe(state: GameState) -> str:
    parts = ["Místnost bez stropu. Shora sem jako sníh padají věci, které už nikdo nehledá, a všechno tu bledne."]
    if "hlavacek_found" in state.flags:
        parts.append("Pan Hlaváček stojí vedle tebe, zase barevný, a leští si jmenovku.")
    else:
        parts.append("Mezi hromadami sedí skoro průhledný muž v úředním saku. Pan Hlaváček.")
    if "read_own_file" in state.flags:
        parts.append("Někde tady je i krabice s tvým jménem.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    result = []
    if "hlavacek_found" not in state.flags:
        if state.has("nametag"):
            result.append(Action("give_nametag", "Dát mu Hlaváčkovu jmenovku", _give_nametag))
        else:
            result.append(Action("talk_hlavacek", "Promluvit s ním", _talk))
    else:
        if "read_own_file" in state.flags:
            result.append(Action("search_box", "Hledat krabici se svým jménem", _search_box))
        result.append(Action("leave_together", "Odejít s panem Hlaváčkem", _leave_together))
    result.append(Action("back", "Vrátit se po niti do archivu", _back))
    return result
