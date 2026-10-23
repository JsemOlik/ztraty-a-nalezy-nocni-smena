"""Sklad deštníků – uvnitř pořád prší."""

from ..actions import Action, go
from ..state import GameState

# Předměty, které popisuje už sama místnost.
NATIVE_ITEMS = ("head",)
TITLE = "Sklad deštníků"


def _look_umbrellas(state: GameState, ui) -> None:
    ui.say(state.rng.choice([
        "Jeden deštník má na rukojeti vyryto „Pro Marii, ať nezmokne“. Prší z něj teplý letní déšť.",
        "Dětský deštník s kachničkami. Kape z něj jarní přeháňka a voní to po bahnitých loužích.",
        "Pánský deštník z roku 1968. Prší z něj tak smutně, že se radši podíváš jinam.",
        "Deštník z tramvaje číslo 22. Prší z něj přesně v okamžiku, kdy by člověk vystupoval.",
    ]))


def describe(state: GameState) -> str:
    parts = [
        "Ve skladu deštníků prší. Ne venku – tady uvnitř. Ze stropu, z regálů, z vlastních deštníků. "
        "Každý zapomenutý deštník si s sebou přinesl své počasí: mrholení z Vršovic, slejvák ze Zlína, "
        "studenou listopadovou plískanici odněkud z nádraží. Podlaha je jedna velká louže."
    ]
    if "head" in state.here():
        parts.append(
            "Uprostřed, na jediném suchém ostrůvku, stojí kulatá krabice na klobouk. Z krabice se ozývá hlas: "
            "„Haló? Je tam někdo? Prší sem? Já nesnáším déšť! Mám mokrý knír!“"
        )
    else:
        parts.append("Na suchém ostrůvku zbyla prázdná krabice na klobouk.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    return [
        Action("look_umbrellas", "Prohlédnout si deštníky", _look_umbrellas),
        Action("back", "Vrátit se k přepážce", go("counter")),
    ]
