"""Vstup a výstup: rich konzole s animacemi pro hráče, skriptované UI pro testy."""

import os
import sys
import time
from bisect import bisect_right
from collections.abc import Callable, Sequence

from rich.console import Console, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from . import art
from .actions import Action
from .items import ITEMS
from .state import MAX_POCKETS, GameState
from .text import fmt_time, pieces_bar, transparency

# Rychlost psaní ve znacích za sekundu; 0 = bez animace.
SPEEDS = {"normální": 90, "rychlá": 260, "vypnutá": 0}
FRAME = 1 / 60
NIGHT_BAR_CELLS = 12

# Prodleva po interpunkci, v násobcích jednoho znaku.
PAUSES = {".": 9, "!": 9, "?": 9, "…": 12, ":": 5, ";": 4, ",": 3, "–": 3, "—": 3, "\n": 6}


def pockets_summary(state: GameState) -> str:
    if not state.pockets:
        return "prázdné"
    parts = []
    for item_id in dict.fromkeys(state.pockets):
        count = state.count(item_id)
        name = ITEMS[item_id].name
        if item_id == "director_face" and state.face_worn:
            name += " (nasazená)"
        parts.append(f"{name} ×{count}" if count > 1 else name)
    return ", ".join(parts)


def night_bar(state: GameState) -> str:
    filled = min(NIGHT_BAR_CELLS, round(state.minutes / state.deadline * NIGHT_BAR_CELLS))
    return "▕" + "█" * filled + "░" * (NIGHT_BAR_CELLS - filled) + "▏"


class _SkipKeys:
    """Během animace hlídá stisk klávesy, aby šla animace přeskočit."""

    def __init__(self) -> None:
        self.fd: int | None = None
        self.saved = None

    def __enter__(self) -> "_SkipKeys":
        if os.name == "posix" and sys.stdin.isatty():
            import termios
            import tty

            self.fd = sys.stdin.fileno()
            self.saved = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
        return self

    def pressed(self) -> bool:
        if os.name == "nt":
            import msvcrt

            hit = False
            while msvcrt.kbhit():
                msvcrt.getwch()
                hit = True
            return hit
        if self.fd is None:
            return False
        import select

        if select.select([self.fd], [], [], 0)[0]:
            os.read(self.fd, 1024)
            return True
        return False

    def __exit__(self, *exc) -> None:
        if self.saved is not None:
            import termios

            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.saved)


def _schedule(plain: str) -> list[int]:
    """Kdy (v jednotkách znaků) se má objevit který znak, včetně pauz po interpunkci."""
    moments, clock = [], 0
    for char in plain:
        clock += 1 + PAUSES.get(char, 0)
        moments.append(clock)
    return moments


class ConsoleUI:
    def __init__(self, console: Console | None = None, speed: str = "normální"):
        self.console = console or Console(highlight=False)
        interactive = self.console.is_terminal and sys.stdin.isatty()
        self.speed = speed if interactive else "vypnutá"
        # Stisk klávesy přeskočí všechny animace až do další volby.
        self.skipping = False

    # --- animace -----------------------------------------------------------

    @property
    def cps(self) -> int:
        return 0 if self.skipping else SPEEDS[self.speed]

    def cycle_speed(self) -> str:
        names = list(SPEEDS)
        self.speed = names[(names.index(self.speed) + 1) % len(names)]
        return self.speed

    def _type(self, text: Text, render: Callable[[Text], RenderableType] = lambda t: t,
              width: int | None = None, cps_factor: float = 1.0) -> None:
        """Vypíše text postupně jako psací stroj. Libovolná klávesa animaci přeskočí."""
        if not self.cps:
            self.console.print(render(text))
            return
        # Text se zalomí předem, aby slova během psaní neskákala mezi řádky.
        text = Text("\n").join(text.wrap(self.console, width or self.console.width))
        if text.plain.count("\n") + 6 > self.console.height:
            # Živé překreslování by u textu vyššího než terminál zanechalo duplicitní řádky.
            self.console.print(render(text))
            return
        moments = _schedule(text.plain)
        cps = self.cps * cps_factor
        with _SkipKeys() as keys, Live(
            render(Text()), console=self.console, auto_refresh=False, vertical_overflow="visible"
        ) as live:
            start = time.monotonic()
            try:
                shown = 0
                while shown < len(text):
                    shown = bisect_right(moments, (time.monotonic() - start) * cps)
                    live.update(render(text[:shown]), refresh=True)
                    if keys.pressed():
                        self.skipping = True
                        break
                    time.sleep(FRAME)
            except KeyboardInterrupt:
                self.skipping = True
            live.update(render(text), refresh=True)

    def _reveal_art(self, picture: str, style: str) -> None:
        """Vykreslí obrázek řádek po řádku."""
        lines = picture.strip("\n").split("\n")
        with _SkipKeys() as keys:
            for line in lines:
                self.console.print(Text(line, style=style))
                if self.cps and keys.pressed():
                    self.skipping = True
                if self.cps:
                    time.sleep(0.03 * SPEEDS["normální"] / self.cps)

    def _flicker(self, text: Text, styles: Sequence[str], final: str, frames: int, delay: float) -> None:
        if not self.cps:
            self.console.print(Text(text.plain, style=final))
            return
        with Live(Text(text.plain, style=styles[0]), console=self.console, auto_refresh=False) as live:
            for frame in range(frames):
                live.update(Text(text.plain, style=styles[frame % len(styles)]), refresh=True)
                time.sleep(delay)
            live.update(Text(text.plain, style=final), refresh=True)

    # --- obrazovky ---------------------------------------------------------

    def title_screen(self) -> None:
        self.console.print()
        self._reveal_art(art.TITLE, "bold magenta")
        # Zářivka nad přepážkou chvíli bliká, než chytne.
        self._flicker(
            Text(art.SUBTITLE.center(48)),
            ["dim", "bold white", "dim", "dim", "bold white", "dim"],
            "bold white",
            frames=9,
            delay=0.09,
        )
        self.console.print(Text("Textová hra o všem, co lidé ztratí".center(48), style="italic dim"))
        if self.cps:
            self.console.print(Text("(Animaci textu přeskočíš libovolnou klávesou.)".center(48), style="dim"))
        self.console.print()

    def room(self, title: str, text: str, picture: str | None = None, animate: bool = True) -> None:
        self.console.print()
        if picture:
            self._reveal_art(picture, "cyan")
        render = lambda body: Panel(body, title=f"[bold cyan]{title}[/bold cyan]", border_style="cyan", padding=(0, 1))
        body = Text.from_markup(text)
        if animate:
            self._type(body, render, width=self.console.width - 4, cps_factor=1.4)
        else:
            self.console.print(render(body))

    def hud(self, state: GameState) -> None:
        left = state.deadline - state.minutes
        time_style = "bold red" if left <= 30 else "bold yellow" if left <= 60 else "bold"
        line = Text()
        line.append("Čas ", style="dim")
        line.append(fmt_time(state.minutes), style=time_style)
        line.append(f" {night_bar(state)} {fmt_time(state.deadline)}", style="dim")
        line.append("   Kousky sebe ", style="dim")
        line.append(pieces_bar(state), style="bold green" if state.pieces > 2 else "bold red")
        line.append(f"   Kapsy ({len(state.pockets)}/{MAX_POCKETS}) ", style="dim")
        line.append(pockets_summary(state))
        self.console.print(line)
        self.console.print(Text(transparency(state), style="italic dim"))

    def say(self, text: str) -> None:
        self._type(Text.from_markup(text))

    def good(self, text: str) -> None:
        self._type(Text(text, style="green"))

    def bad(self, text: str) -> None:
        self._type(Text(text, style="bold red"))

    def sfx(self, text: str) -> None:
        """Zvukový efekt: pomalu a kurzívou."""
        self._type(Text(text, style="italic magenta"), cps_factor=0.5)

    def flicker(self, text: str) -> None:
        """Text, který bliká a mizí – jako hráč, když ztrácí kousek sebe."""
        self._flicker(Text(text), ["bold red", "dim red", "bold red", "grey23", "dim red"], "bold red", 10, 0.07)

    def head(self, text: str) -> None:
        line = Text()
        line.append("Hlava: ", style="bold yellow")
        line.append(text, style="italic yellow")
        self._type(line, cps_factor=1.6)

    def ending(self, number: int, title: str, text: str, footer: str, picture: str | None = None) -> None:
        self.console.print()
        self.console.print(Rule(style="magenta"))
        if picture:
            self._reveal_art(picture, "magenta")
        render = lambda body: Panel(
            body,
            title=f"[bold magenta]Konec {number} z 8: {title}[/bold magenta]",
            subtitle=footer,
            border_style="magenta",
            padding=(1, 2),
        )
        self._type(Text.from_markup(text), render, width=self.console.width - 6, cps_factor=0.9)

    def pause(self) -> None:
        self.skipping = False
        self.console.input("[dim](Enter pro pokračování)[/dim] ")

    def farewell(self, text: str) -> None:
        self.console.print(text)

    def choose(self, actions: Sequence[Action], prompt: str = "Co uděláš?") -> Action:
        self.skipping = False
        self.console.print()
        for number, action in enumerate(actions, start=1):
            label = f"[dim]{action.label}[/dim]" if action.cost == 0 else action.label
            self.console.print(f"  [bold]{number:>2}[/bold]) {label}")
        while True:
            answer = self.console.input(f"[bold]{prompt}[/bold] ").strip()
            if answer.isdigit() and 1 <= int(answer) <= len(actions):
                return actions[int(answer) - 1]
            self.console.print(f"[red]Napiš číslo od 1 do {len(actions)}.[/red]")


class ScriptedUI:
    """UI pro testy: vybírá akce podle klíčů a ukládá si veškerý výstup."""

    speed = "vypnutá"

    def __init__(self, script: Sequence[str | Callable[[Sequence[Action]], Action]]):
        self.script = list(script)
        self.log: list[str] = []

    def _out(self, text: str) -> None:
        self.log.append(text)

    def cycle_speed(self) -> str:
        return self.speed

    def title_screen(self) -> None:
        self._out(art.TITLE)

    def room(self, title: str, text: str, picture: str | None = None, animate: bool = True) -> None:
        self._out(f"[{title}] {text}")

    def hud(self, state: GameState) -> None:
        self._out(f"{fmt_time(state.minutes)} {pieces_bar(state)} {pockets_summary(state)}")

    say = good = bad = sfx = flicker = _out

    def head(self, text: str) -> None:
        self._out(f"Hlava: {text}")

    def ending(self, number: int, title: str, text: str, footer: str, picture: str | None = None) -> None:
        self._out(f"KONEC {number}: {title}\n{text}\n{footer}")

    def pause(self) -> None:
        pass

    def choose(self, actions: Sequence[Action], prompt: str = "Co uděláš?") -> Action:
        if not self.script:
            raise AssertionError(f"Skript došel. Nabídka: {[a.key for a in actions]}")
        step = self.script.pop(0)
        if callable(step):
            return step(actions)
        for action in actions:
            if action.key == step:
                return action
        raise AssertionError(f"Akce {step!r} není v nabídce: {[a.key for a in actions]}")

    def text(self) -> str:
        return "\n".join(self.log)
