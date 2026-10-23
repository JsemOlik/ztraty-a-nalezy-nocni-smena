"""Osm konců noční směny."""

from collections.abc import Callable
from dataclasses import dataclass

from . import art
from .state import GameState
from .text import fmt_time


@dataclass(frozen=True)
class Ending:
    number: int
    title: Callable[[GameState], str]
    text: Callable[[GameState], str]


def _resignation(s: GameState) -> str:
    return (
        "Pověsíš sako na věšák a necháš na přepážce lísteček: „Dávám výpověď. Hezkou noc.“\n\n"
        f"Do historie úřadu ses {s.g('zapsal', 'zapsala')} jako {s.g('zaměstnanec', 'zaměstnankyně')} "
        "s nejkratší pracovní smlouvou všech dob: pět minut."
    )


def _lost_head(s: GameState) -> str:
    return (
        "Jak chceš uklidnit někoho, kdo ztratil hlavu? Bezhlavý do tebe vrazí a jeho panika přeskočí na tebe. "
        "Nevíš, kde je nahoře ani dole. Nevíš, kde máš hlavu. A pak zjistíš, že ji opravdu nemáš.\n\n"
        "Ráno ve sklepě pobíhají dva."
    )


def _inventory(s: GameState) -> str:
    return (
        f"Odbije šestá a po schodech sestupuje denní směna. {s.g('Nestihl', 'Nestihla')} jsi to. "
        "Úřednice o tebe zakopne, zvedne obočí a sáhne po razítku.\n\n"
        "V deníku služeb přibude nový zápis:\n"
        f"[italic]„Nalezeno: {s.g('noční úředník', 'noční úřednice')}, 1 kus. Nikdo se nehlásí.“[/italic]"
    )


def _nobody_searches(s: GameState) -> str:
    if "hlavacek_found" in s.flags:
        place = f"do místnosti, ze které jsi pana Hlaváčka {s.g('vyvedl', 'vyvedla')}. Teď tu blednou jiní – a ty s nimi."
    else:
        place = "vedle pana Hlaváčka. Smutně se na tebe usměje a posune se."
    return (
        f"Poslední kousek tebe se odloupne. Už nevrháš stín a nejsi si {s.g('jistý', 'jistá')}, jak se jmenuješ.\n\n"
        f"Padáš jako sníh do místnosti, kam padá všechno, co nikdo nehledá. Dopadneš {place}\n\n"
        "Blednete spolu. Nikdo nehledá."
    )


def _director(s: GameState) -> str:
    return (
        "Ředitelova tvář ti přirostla. Když ji chceš sundat, nahmatáš jen kůži – a ta už není tvoje.\n\n"
        "Usedneš do křesla s vysokým opěradlem. Najednou víš, kdo co ztratil a kolik by za to dal. "
        "Všechny ztracené věci se ti pokloní.\n\n"
        "Navždy vládneš všemu ztracenému. Jen sebe už nenajdeš."
    )


def _time_thief(s: GameState) -> str:
    return (
        "Dveře se před tebou otevřou – v kapsách máš totiž už ráno. Jdeš domů a ukradený čas ti vydrží "
        "na dlouhý, předlouhý život.\n\n"
        "Až ve sto čtyřech letech ti sestřička v nemocnici vypráví o mamince, která se nestihla rozloučit s tátou. "
        "Chybělo jí pár minut. Ten den jí prostě zmizelo odpoledne.\n\n"
        "Ty víš, komu ty hodiny chybí."
    )


def _found(s: GameState) -> str:
    return (
        "Pan Hlaváček si připne jmenovku a vezme tě za loket. Po červené niti se vracíte zpátky, "
        "cestou dopije svůj studený čaj.\n\n"
        f"Za úsvitu odcházíte z úřadu spolu: on, kdo ztratil sám sebe, a ty, kdo {s.g('ho našel', 'ho našla')}.\n"
        "„Zítra zase?“ zeptá se. A ty zjistíš, že se těšíš."
    )


def _lost_and_found(s: GameState) -> str:
    return (
        "Podíváš se na fotku a mezi tisíci vybledlými krabicemi poznáš tu svou. "
        "Na víku je tvoje jméno a pod ním: „Naděje. Nikdo nehledá.“\n\n"
        "Otevřeš ji. Je to jako první den, kdy se v zimě zase prodlužuje světlo. "
        f"Vrací se to do tebe kousek po kousku a jsi {s.g('celý', 'celá')} – víc než za celé roky.\n\n"
        f"„Teď už víte, proč jste tu práci {s.g('dostal', 'dostala')},“ usměje se Hlaváček. "
        "Do úřadu berou jen ty, kdo něco ztratili. A zůstávají, dokud nenajdou sebe.\n\n"
        "Za úsvitu vycházíte ven, dva nalezení."
    )


ENDINGS: dict[str, Ending] = {
    "resignation": Ending(1, lambda s: "Výpověď", _resignation),
    "lost_head": Ending(2, lambda s: s.g("Ztratil jsi hlavu", "Ztratila jsi hlavu"), _lost_head),
    "inventory": Ending(3, lambda s: "Inventář", _inventory),
    "nobody_searches": Ending(4, lambda s: "Nikdo nehledá", _nobody_searches),
    "director": Ending(5, lambda s: "Pan ředitel", _director),
    "time_thief": Ending(6, lambda s: s.g("Zloděj času", "Zlodějka času"), _time_thief),
    "found": Ending(7, lambda s: s.g("Nalezený", "Nalezená"), _found),
    "lost_and_found": Ending(8, lambda s: s.g("Ztracený a nalezený", "Ztracená a nalezená"), _lost_and_found),
}


def show(state: GameState, ui) -> None:
    if state.ending == "quit":
        return
    ending = ENDINGS[state.ending]
    footer = f"Čas: {fmt_time(state.minutes)} · Kousky sebe: {max(state.pieces, 0)}/5"
    ui.ending(ending.number, ending.title(state), ending.text(state), footer, art.ENDINGS[state.ending])
