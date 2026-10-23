"""Místnost nehledaných věcí – sem padá všechno, co už nikdo nehledá."""

from ..actions import Action
from ..state import GameState

TITLE = "Místnost nehledaných věcí"


def _talk(state: GameState, ui) -> None:
    ui.say(
        "„Dobrý večer… nebo ráno? Já… byl jsem tu úředníkem? Nebo jsem byl něco, co někdo ztratil?“ "
        "Muž se na tebe dívá skrz vlastní průsvitné ruce. „Ztratil jsem něco hrozně důležitého. "
        "Myslím, že sebe. Kdybych aspoň věděl, jak se jmenuju…“"
    )


def _give_nametag(state: GameState, ui) -> None:
    state.remove_item("nametag")
    state.flags.add("hlavacek_found")
    ui.good(
        "Podáš mu jmenovku. Přečte si ji – jednou, dvakrát, potřetí nahlas: „Bohumil Hlaváček. Noční služba.“ "
        "A s každým slovem mu do tváře, do saka a do rukou stéká barva, jako když se do čaje nalije mléko."
    )
    ui.say(
        "„Hlaváček! No ovšem! Bohouš!“ Smeká neexistující klobouk. „Děkuju vám. Kdo ztratil sám sebe, "
        "potřebuje, aby mu někdo připomněl, kdo je.“ Pak se na tebe podívá zkoumavě. „A vy… vy jste tu taky "
        f"{state.g('nebyl', 'nebyla')} jen tak náhodou, viďte? Sem berou jen ty, kdo něco ztratili.“"
    )


def _leave_together(state: GameState, ui) -> None:
    state.ending = "found"


def _search_box(state: GameState, ui) -> None:
    if state.has("own_photo"):
        state.ending = "lost_and_found"
        return
    if "photo_used" in state.flags:
        ui.say(
            "Hledáš krabici se svým jménem, ale krabic se jmény jsou tu tisíce a všechna jména vybledla. "
            f"Kdyby sis jen {state.g('pamatoval', 'pamatovala')}, jak vypadáš – ale fotka, "
            f"kterou jsi {state.g('měl', 'měla')}, už je jen bílý papír."
        )
        return
    ui.say(
        "Hledáš krabici se svým jménem, ale krabic se jmény jsou tu tisíce a všechna jména vybledla. "
        f"{state.g('Potřeboval', 'Potřebovala')} bys něco, podle čeho se poznáš. Třeba tu fotku ze spisu."
    )


def _back(state: GameState, ui) -> None:
    state.location = "threads"
    ui.say("Navineš si nit kolem prstu a jdeš po ní zpátky. Za rohem, který tam předtím nebyl, je zase archiv.")


def describe(state: GameState) -> str:
    parts = [
        "Místnost nemá strop. Shora sem pomalu, jako sníh, padají věci: rukavice, dopisy, dětské kresby, "
        "sliby, staré přezdívky, jména kamarádů ze školy. Všechno, co už nikdo nehledá. Hromady sahají "
        "do nedohledna a všechno vybledlo do barvy starého papíru. Kdo tu zůstane, vybledne taky."
    ]
    if "hlavacek_found" in state.flags:
        parts.append("Pan Hlaváček stojí vedle tebe, zase barevný, a nervózně si leští jmenovku rukávem.")
    else:
        parts.append(
            "Mezi hromadami sedí muž v úředním saku. Je skoro průhledný; skrz jeho hruď vidíš padat sníh věcí. "
            "Šeptem si opakuje: „Jak se to… jak se to jmenuju…“ Pan Hlaváček."
        )
    if "read_own_file" in state.flags:
        parts.append("Někde tady, mezi tisíci krabicemi, je i krabice s tvým jménem.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    result = []
    if "hlavacek_found" not in state.flags:
        result.append(Action("talk_hlavacek", "Promluvit s blednoucím mužem", _talk))
        if state.has("nametag"):
            result.append(Action("give_nametag", "Dát mu Hlaváčkovu jmenovku", _give_nametag))
    else:
        if "read_own_file" in state.flags:
            result.append(Action("search_box", "Hledat krabici se svým jménem", _search_box))
        result.append(Action("leave_together", "Odejít s panem Hlaváčkem", _leave_together))
    result.append(Action("back", "Vrátit se po niti do archivu", _back))
    return result
