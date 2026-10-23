"""Sklad deštníků – uvnitř pořád prší."""

from ..actions import Action, lose_piece
from ..state import GameState

TITLE = "Sklad deštníků"
NATIVE_ITEMS = ("head",)


def enter(state: GameState, ui) -> None:
    state.location = "umbrellas"
    ui.sfx("Šššššššššš…")
    if state.has("umbrella"):
        ui.say("Rozevřeš suchý deštník. Na tebe nedopadne ani kapka.")
    else:
        lose_piece(state, ui, "Vejdeš bez deštníku a spustí se na tebe liják. Ten déšť z tebe smývá kus tebe samotného.")


def describe(state: GameState) -> str:
    parts = ["Ve skladu prší – přímo uvnitř. Každý zapomenutý deštník si s sebou přinesl své počasí."]
    if "head" in state.here():
        parts.append("Na suchém ostrůvku stojí krabice na klobouk a v ní hlava: „Haló? Je tam někdo? Mám mokrý knír!“")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    return []
