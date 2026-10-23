"""Pomocné funkce pro texty: čas, kousky sebe, průsvitnost."""

from .state import MAX_PIECES, GameState


def fmt_time(minutes: int) -> str:
    minutes %= 24 * 60
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def pieces_bar(state: GameState) -> str:
    return "●" * state.pieces + "○" * (MAX_PIECES - state.pieces)


def transparency(state: GameState) -> str:
    """Krátká věta o tom, jak moc je hráč průhledný."""
    g = state.g
    return {
        5: f"Jsi {g('celý', 'celá')} a pevně stojíš na zemi.",
        4: f"Konečky prstů ti lehce průsvitní, jako bys je {g('držel', 'držela')} proti lampě.",
        3: "Přes ruce ti prosvítá podlaha.",
        2: "Tvůj stín je výraznější než ty. Lidé by tě přehlédli i ve frontě.",
        1: "Zrcadlo tě skoro neukazuje. Zbývá z tebe jen obrys a ozvěna.",
    }.get(state.pieces, "Nejsi tu.")
