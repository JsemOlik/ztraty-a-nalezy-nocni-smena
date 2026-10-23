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
        "Rozhlédneš se po zaprášené přepážce, po telefonu, po deníku s bledým písmem. Pak si sundáš "
        "služební sako, pověsíš ho na věšák a napíšeš na lísteček: „Dávám výpověď. Hezkou noc.“\n\n"
        f"Venku je chladno a obyčejná noc. {s.g('Zapsal ses', 'Zapsala ses')} do historie Centrálního úřadu "
        f"ztrát a nálezů jako {s.g('zaměstnanec', 'zaměstnankyně')} s nejkratší pracovní smlouvou všech dob: pět minut.\n\n"
        "Na nástěnce v kanceláři personálního oddělení pak ještě roky visí tvoje fotka s nápisem "
        "„Rekord, který nikdo nepřekoná“. Nikdo ji nikdy nehledal."
    )


def _lost_head(s: GameState) -> str:
    return (
        "Natáhneš ruce do tmy a mluvíš na Bezhlavého klidným hlasem. Jenže čím chceš uklidnit někoho, "
        "kdo ztratil hlavu? Bezhlavý se k tobě rozběhne, narazí do tebe – a jeho panika přeskočí na tebe "
        "jako jiskra.\n\n"
        f"Najednou nevíš, kde je nahoře. Nevíš, kde je dole. Nevíš, kde máš hlavu. A pak zjistíš, "
        "že ji opravdu nemáš.\n\n"
        "Když ráno přijde denní směna, ve sklepě pobíhají dva."
    )


def _inventory(s: GameState) -> str:
    return (
        "Ručičky všech hodin v úřadu se naráz spojí v šest. Nahoře zarachotí klíč, rozsvítí se světla "
        "a po schodech sestupuje denní směna s termoskami a rohlíky.\n\n"
        f"Nestihl{s.g('', 'a')} jsi to. Stojíš u přepážky a nikdo si tě nevšímá – dokud jedna z úřednic "
        "nezakopne o tvoje boty, nezvedne obočí a nesáhne po razítku.\n\n"
        "V deníku služeb přibude nový zápis:\n"
        f"[italic]„Nalezeno: {s.g('noční úředník', 'noční úřednice')}, 1 kus. Nikdo se nehlásí.“[/italic]\n\n"
        "Dostaneš visačku s číslem a místo na polici mezi deštníky."
    )


def _nobody_searches(s: GameState) -> str:
    if "hlavacek_found" in s.flags:
        beside = (
            f"do místnosti, ze které jsi pana Hlaváčka {s.g('vyvedl', 'vyvedla')}. "
            f"Teď tu sedíš {s.g('sám', 'sama')} místo něj."
        )
    else:
        beside = (
            "vedle pana Hlaváčka. Ten se na tebe smutně usměje a posune se, "
            f"abys {s.g('měl', 'měla')} víc místa."
        )
    return (
        "Poslední kousek tebe se odloupne a tiše odplachtí pryč. Už nevrháš stín. Už se neodrážíš. "
        f"Už si nejsi {s.g('jistý', 'jistá')}, jak se jmenuješ.\n\n"
        f"Padáš, pomalu jako sníh, do místnosti, kam padá všechno, co už nikdo nehledá. Dopadneš {beside}\n\n"
        "Blednete spolu. Shora na vás tiše sněží cizí rukavice, dopisy a sliby. Nikdo nehledá."
    )


def _director(s: GameState) -> str:
    return (
        "Ředitelova tvář ti přirostla. Když se ji pokusíš sundat, nahmatáš jen vlastní kůži – a vlastní kůže "
        "už není tvoje.\n\n"
        "Usedneš do křesla s vysokým opěradlem. Sedí se v něm skvěle. Najednou přesně víš, kde co v úřadu je, "
        "kdo co ztratil a kolik by za to byl ochoten dát. Natáhneš ruku a všechny ztracené věci se ti pokloní.\n\n"
        "Ráno denní směna najde v ředitelně pana ředitele. Po letech zase přišel. Nikdo se neodváží zeptat, "
        "kde byl. A ty už si nevzpomeneš, kým jsi byl" + s.g("", "a") + " předtím.\n\n"
        "Navždy vládneš všem ztraceným věcem. Jen sebe už nenajdeš nikdy."
    )


def _time_thief(s: GameState) -> str:
    handfuls = s.count("stolen_time")
    return (
        "Dveře ven se před tebou otevřou samy. V tvých kapsách je totiž už ráno – "
        f"{handfuls} hrsti cizího času tikají tak hlasitě, že tě dveře považují za denní směnu.\n\n"
        "Jdeš domů. A ten čas ti vydrží. Žiješ dlouhý, předlouhý život. Stihneš všechno: knihy, cesty, "
        "pozdní snídaně, nedělní odpoledne, která se táhnou jako med.\n\n"
        "Až v nemocnici, ve sto čtyřech letech, ti mladá sestřička vypráví o své mamince. Ta prý nestihla "
        "rozloučit se s tátou – chybělo jí pár minut. Ten den jí prostě, nevysvětlitelně, zmizelo odpoledne. "
        "„Jako by jí ho někdo ukradl,“ říká a usmívá se, protože tomu sama nevěří.\n\n"
        "Ty víš, komu ty hodiny chybí."
    )


def _found(s: GameState) -> str:
    return (
        "Pan Hlaváček si připne jmenovku, zastrčí si ji za klopu a vezme tě za loket. Jdete spolu po červené "
        "niti zpátky, archivem, chodbami, kolem přepážky. Hlaváček cestou dopije studený čaj a poznamená, "
        "že ten zvonek by chtěl promazat.\n\n"
        "V šest ráno se nahoře otevřou dveře. Denní směna vás pozdraví, jako by se nic nedělo. "
        "Za úsvitu odcházíte z úřadu spolu: on, kdo ztratil sám sebe, a ty, kdo " + s.g("ho našel", "ho našla") + ".\n\n"
        "Venku je studené, jasné ráno. „Zítra zase?“ zeptá se Hlaváček.\n"
        "A ty zjistíš, že se docela těšíš."
    )


def _lost_and_found(s: GameState) -> str:
    return (
        "Vytáhneš fotku a podíváš se na ni. Pak na hromady. Pak zase na fotku. A mezi tisíci vybledlými krabicemi "
        "uvidíš jednu, na které je tvoje tvář. Ta samá, která se usmívá z fotky.\n\n"
        "Na víku je tvoje jméno. Pod ním drobným písmem: „Naděje. Nikdo nehledá.“\n\n"
        "Otevřeš ji. Uvnitř není nic, co by se dalo popsat. Jen pocit, jako když v zimě poprvé ucítíš, "
        "že se den zase prodlužuje. Jako když ti někdo po letech zavolá jen tak. Vrací se to do tebe, pomalu, "
        "kousek po kousku, a ty jsi najednou " + s.g("celý", "celá") + " – víc než za celé roky.\n\n"
        "Pan Hlaváček stojí vedle tebe a tiše se usmívá. „Teď už to víte, viďte? Proč jste tu práci dostal"
        + s.g("", "a") + ".“\n\n"
        "Do úřadu berou jen lidi, kteří sami něco ztratili. Ale nezůstávají tu proto, aby hledali věci "
        "pro ostatní. Zůstávají, dokud nenajdou sebe.\n\n"
        "Za úsvitu vycházíte ven, dva nalezení. A ten hlas z telefonu, který ti celou noc radil? "
        "Teď už ho poznáváš. Byl to tvůj vlastní."
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
        ui.say("Odkládáš sako na věšák. Směna počká. Na shledanou!")
        return
    ending = ENDINGS[state.ending]
    footer = f"Čas: {fmt_time(state.minutes)} · Kousky sebe: {max(state.pieces, 0)}/5"
    ui.ending(ending.number, ending.title(state), ending.text(state), footer, art.ENDINGS[state.ending])
