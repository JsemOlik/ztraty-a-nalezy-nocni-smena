"""Přepážka – rozcestí celého úřadu."""

from ..actions import Action, heal
from ..state import MAX_PIECES, GameState

TITLE = "Přepážka"
# Předměty, které popisuje už sama místnost.
NATIVE_ITEMS = ("umbrella",)

JOURNAL = """[bold]Deník služeb[/bold]
  [italic]3. 3.[/italic] Do skladu deštníků nikdy bez suchého deštníku. Ten déšť z člověka spláchne kus.
  [italic]9. 3.[/italic] Sklenice v kabinetu řečí: nejdřív poslouchat, pak otevírat!
  [italic]20. 3.[/italic] Cizí tvář se rychle přichytí. Nikdy ji nenosit dlouho.
  [italic]27. 3.[/italic] Někdo tu zase ztratil hlavu. Jdu dolů to vyřešit."""


def _resign(state: GameState, ui) -> None:
    state.ending = "resignation"


def _read_journal(state: GameState, ui) -> None:
    ui.say(JOURNAL)


def _tea(state: GameState, ui) -> None:
    if heal(state, ui, 1, "Dopiješ Hlaváčkův studený čaj. Voní po heřmánku a vrátí ti kousek sebe."):
        state.flags.add("tea_drunk")


def leave_building(state: GameState, ui) -> int | None:
    """Dveře ven. Zevnitř je pustí jen ten, kdo má v kapsách ráno."""
    stolen = state.count("stolen_time")
    if stolen >= 2:
        state.ending = "time_thief"
        return None
    if stolen == 1:
        ui.say("Dveře se na škvírku pootevřou, ale jedna hrst ukradeného času nestačí. Zase zaklapnou.")
    else:
        ui.say("Dveře ven jsou zamčené. Zevnitř je odemkne až denní směna v šest ráno.")
    return 0


def describe(state: GameState) -> str:
    parts = ["Dřevěná přepážka se zvonkem, zaprášený telefon a deník služeb. Odtud vedou chodby do všech oddělení úřadu."]
    if "tea_drunk" not in state.flags:
        parts.append("Na přepážce stojí hrnek Hlaváčkova nedopitého čaje.")
    if "umbrella" in state.here():
        parts.append("Ve stojanu u vchodu je jediný suchý deštník.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    result = []
    if state.minutes == 0:
        result.append(Action("resign", "Dát výpověď a jít domů", _resign))
    result.append(Action("journal", "Přečíst deník služeb", _read_journal))
    if "tea_drunk" not in state.flags and state.pieces < MAX_PIECES:
        result.append(Action("tea", "Dopít Hlaváčkův čaj", _tea))
    return result
