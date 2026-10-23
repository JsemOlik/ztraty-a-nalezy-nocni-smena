"""Galerie ztracených tváří – masky lidí, kteří se kdysi ztrapnili."""

from ..actions import Action, go
from ..state import GameState

# Předměty, které popisuje už sama místnost.
NATIVE_ITEMS = ("director_face",)
TITLE = "Galerie ztracených tváří"

MASKS = [
    "Maska pána, který na vlastní svatbě oslovil nevěstu jménem své bývalé. Pořád je trochu rudá.",
    "Maska slečny, která na maturitním plese zakopla o vlastní šaty a strhla s sebou ředitele gymnázia.",
    "Maska muže, který zamával na někoho, kdo mával na člověka za ním. Ten výraz zná každý.",
    "Maska paní, která celou cestu tramvají mluvila do telefonu, který jí mezitím vypadl z kapsy.",
    "Maska s cedulkou „Ředitel úřadu – ztratil tvář 1987“. Prázdná. Pod ní někdo připsal tužkou: "
    "„Ztratil městskou zakládací listinu. Na vlastním úřadě. Od té doby se neukázal.“",
]


def _look_masks(state: GameState, ui) -> None:
    ui.say(state.rng.choice(MASKS))


def describe(state: GameState) -> str:
    parts = [
        "Dlouhá chodba plná rámů. V každém visí maska – tvář, kterou někdo ztratil, když se před lidmi ztrapnil. "
        "Masky tiše rudnou, uhýbají pohledem a některé se pořád ještě omlouvají. Je tu dusno jako na školní besídce."
    ]
    if "director_face" in state.here():
        parts.append(
            "Na čestném místě, v pozlaceném rámu, visí tvář samotného pana ředitele. Jako jediná se nestydí. "
            "Dívá se na tebe a čeká."
        )
    else:
        parts.append("Po ředitelově tváři zbyl na zdi světlejší obdélník.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    return [
        Action("look_masks", "Prohlížet si masky", _look_masks),
        Action("back", "Vrátit se k přepážce", go("counter")),
    ]
