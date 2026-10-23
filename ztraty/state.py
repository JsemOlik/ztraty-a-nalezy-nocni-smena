"""Stav hry: čas, kousky sebe, kapsy, příznaky."""

import random
from dataclasses import dataclass, field

MAX_POCKETS = 4
MAX_PIECES = 5
SHIFT_END = 6 * 60
ACTION_MINUTES = 5


def _initial_room_items() -> dict[str, list[str]]:
    return {
        "counter": ["umbrella", "storage_key"],
        "umbrellas": ["head"],
        "time_dept": [],
        "speech": [],
        "threads": ["red_thread"],
        "faces": ["director_face"],
        "cellar": [],
        "office": [],
        "hidden": [],
    }


@dataclass
class GameState:
    feminine: bool = False
    location: str = "counter"
    minutes: int = 0
    deadline: int = SHIFT_END
    pieces: int = MAX_PIECES
    pockets: list[str] = field(default_factory=list)
    room_items: dict[str, list[str]] = field(default_factory=_initial_room_items)
    flags: set[str] = field(default_factory=set)
    face_worn: bool = False
    face_turns: int = 0
    ending: str | None = None
    rng: random.Random = field(default_factory=random.Random)

    def g(self, masculine: str, feminine: str) -> str:
        """Vrátí tvar slova podle rodu hráče."""
        return feminine if self.feminine else masculine

    def has(self, item_id: str) -> bool:
        return item_id in self.pockets

    def count(self, item_id: str) -> int:
        return self.pockets.count(item_id)

    def free_pockets(self) -> int:
        return MAX_POCKETS - len(self.pockets)

    def pockets_full(self) -> bool:
        return self.free_pockets() <= 0

    def add_item(self, item_id: str) -> bool:
        if self.pockets_full():
            return False
        self.pockets.append(item_id)
        return True

    def remove_item(self, item_id: str) -> None:
        self.pockets.remove(item_id)

    def give_or_drop(self, item_id: str) -> bool:
        """Dá předmět do kapsy, a když se nevejde, položí ho na zem v místnosti."""
        if self.add_item(item_id):
            return True
        self.room_items[self.location].append(item_id)
        return False

    def here(self) -> list[str]:
        return self.room_items[self.location]
