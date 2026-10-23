"""Archiv ztracených nití – klubka lidí, kteří ztratili nit."""

from ..actions import Action, go, lose_piece
from ..state import ACTION_MINUTES, GameState

# Předměty, které popisuje už sama místnost.
NATIVE_ITEMS = ("red_thread",)
TITLE = "Archiv ztracených nití"

LOST_PENALTY = 30

WRONG_THREADS = {
    "blue": (
        "modré",
        "Modrá nit tě vede do cizí přednášky o termodynamice, kterou kdosi před čtyřiceti lety nedořekl. "
        "Bloudíš mezi nedokončenými větami a vzorci, až zapomeneš, proč jsi sem vůbec {went}.",
    ),
    "grey": (
        "šedé",
        "Šedá nit vede do nekonečné porady. Někdo tu kdysi ztratil nit uprostřed bodu sedm „Různé“. "
        "Bod sedm trvá dodnes a ty v něm sedíš celou věčnost, než se ti podaří odplížit.",
    ),
    "gold": (
        "zlaté",
        "Zlatá nit tě dovede do něčího nedokončeného snu o bohatství. Zlato se ti drolí pod prsty "
        "a cesta zpátky se pořád stáčí do kruhu.",
    ),
}


def _follow_red(state: GameState, ui) -> None:
    if not state.has("red_thread"):
        ui.say(
            f"Vydáš se podél červené niti, ale bez toho, abys ji {state.g('držel', 'držela')} v ruce, "
            "se ti po pár krocích ztratí ve tmě. Kdo jde po niti, musí ji držet. Vrátíš se."
        )
        return
    state.location = "hidden"
    ui.say(
        "Pevně sevřeš červenou nit a jdeš. Nit vede mezi regály, pak zdí, která se rozestoupí, pak chodbou, "
        "která není na žádném plánku. Je tu ticho a pomalu tu sněží."
    )


def _follow_wrong(color: str):
    genitive, text = WRONG_THREADS[color]

    def handler(state: GameState, ui) -> int:
        ui.say(f"Chytíš se {genitive} niti a vydáš se za ní.")
        lose_piece(state, ui, text.format(went=state.g("šel", "šla")))
        state.location = "threads"
        ui.say("Když se konečně vymotáš zpátky do archivu, uběhla spousta času.")
        return ACTION_MINUTES + LOST_PENALTY

    return handler


def describe(state: GameState) -> str:
    parts = [
        "Regály až ke stropu a na nich klubka všech barev a velikostí. Každé patří někomu, kdo uprostřed hovoru, "
        "přednášky nebo života „ztratil nit“. Některé nitě se táhnou z klubek ven, přes podlahu, "
        "a mizí ve zdi – tam, kde podle plánu budovy žádné dveře nejsou.",
        "Čtyři nitě jsou napnuté víc než ostatní: červená, modrá, šedá a zlatá.",
    ]
    if "red_thread" in state.here():
        parts.append("Konec červené niti leží na zemi, jako by na někoho čekal.")
    elif state.has("red_thread"):
        parts.append("Konec červené niti máš v kapse. Jemně tahá směrem ke zdi.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    return [
        Action("follow:red", "Jít po červené niti", _follow_red),
        Action("follow:blue", "Jít po modré niti", _follow_wrong("blue")),
        Action("follow:grey", "Jít po šedé niti", _follow_wrong("grey")),
        Action("follow:gold", "Jít po zlaté niti", _follow_wrong("gold")),
        Action("back", "Vrátit se k přepážce", go("counter")),
    ]
