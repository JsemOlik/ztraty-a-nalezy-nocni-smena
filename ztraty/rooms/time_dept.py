"""Oddělení ztraceného času – stovky hodin a každé jdou jinak."""

from ..actions import Action, go
from ..state import ACTION_MINUTES, GameState
from ..text import fmt_time

TITLE = "Oddělení ztraceného času"

CLOCKS = [
    "Kukačky nad dveřmi",
    "Starý budík s ohnutou ručičkou",
    "Věžní ciferník opřený o zeď",
    "Náramkové hodinky v krabici od bot",
    "Kyvadlové hodiny po babičce",
]
WRONG_CLOCK_PENALTY = 15


def _clock_puzzle(state: GameState, ui) -> int | None:
    offsets = state.rng.sample([-60, -25, -10, 10, 20, 45, 60], 3)
    times = [state.minutes] + [state.minutes + offset for offset in offsets]
    faces = state.rng.sample(CLOCKS, 4)
    options = [
        Action("clock:right" if index == 0 else f"clock:wrong{index}", f"{face} ukazují {fmt_time(time)}", lambda s, u: None)
        for index, (face, time) in enumerate(zip(faces, times))
    ]
    state.rng.shuffle(options)
    ui.sfx("Tik. Tak. Tik. Tak. Tik.")
    ui.say(
        "Procházíš mezi hodinami a nasloucháš. Většina z nich lže – některé o minutu, některé o celý život. "
        "Jen jedny jdou přesně tak, jak jde tvoje noc."
    )
    chosen = ui.choose(options, "Které hodiny jdou správně?")
    if chosen.key == "clock:right":
        state.flags.add("lost_hour_found")
        ui.good(
            "Položíš dlaň na správný ciferník. Hodiny se zachvějí, cvaknou a z jejich dvířek vypadne malá, "
            "teplá, tikající věc: ztracená hodina. Někdo ji kdysi prostál ve frontě na úřadě. Teď je tvoje."
        )
        if not state.give_or_drop("lost_hour"):
            ui.say("Kapsy máš plné, a tak ztracená hodina tiše cinkne o podlahu u tvých nohou.")
        return None
    ui.sfx("CRRRRRRR! Kuku! Kuku! Kuku!")
    ui.bad(
        "Sáhneš na špatné hodiny. Rozdrnčí se, posměšně zakukají a ukousnou ti čtvrthodinu. "
        "Ručičky na všech ostatních ciferníkách poskočí dopředu."
    )
    return ACTION_MINUTES + WRONG_CLOCK_PENALTY


def _steal_time(state: GameState, ui) -> None:
    while state.add_item("stolen_time"):
        pass
    ui.say(
        "Nabíráš z misek na pultě hrsti volných minut a cpeš si je do kapes. Lepí se na prsty a šimrají. "
        "Kdesi ve městě někomu právě uteklo odpoledne a neví proč."
    )
    if state.has("head"):
        ui.head("Co to děláte?! To není naše! Tohle někomu chybí, vrať… vraťte to! Teda, nechte si to, ale mě do toho netahejte!")


def _return_time(state: GameState, ui) -> None:
    while state.has("stolen_time"):
        state.remove_item("stolen_time")
    ui.say("Vysypeš ukradený čas zpátky do misek. Minuty se spokojeně rozkutálí a kdesi ve městě se někomu vrátí kus dne.")


def describe(state: GameState) -> str:
    parts = [
        "Stovky hodin. Na stěnách, na policích, na zemi i na stropě. Kukačky, budíky, věžní ciferníky, "
        "náramkové hodinky v krabicích od bot. Každé jdou jinak – jedny pozpátku, jedny dvakrát rychleji, "
        "jedny stojí a tváří se, že ne. Tikání je tak husté, že se v něm dá skoro plavat.",
    ]
    if "lost_hour_found" in state.flags:
        parts.append("Správné hodiny teď spokojeně tikají v rytmu tvého srdce.")
    else:
        parts.append("Na stěně visí cedule: „Kdo najde hodiny, které jdou správně, tomu se odvděčí.“")
    parts.append(
        "Na pultě se v miskách třpytí volné minuty a celé hodiny, které si nikdo nevyzvedl. Nikdo je nehlídá."
    )
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    result = []
    if "lost_hour_found" not in state.flags:
        result.append(Action("clock_puzzle", "Hledat hodiny, které jdou správně", _clock_puzzle))
    if not state.pockets_full():
        result.append(Action("steal_time", "Nacpat si kapsy ukradeným časem", _steal_time))
    if state.has("stolen_time"):
        result.append(Action("return_time", "Vrátit ukradený čas", _return_time))
    result.append(Action("back", "Vrátit se k přepážce", go("counter")))
    return result
