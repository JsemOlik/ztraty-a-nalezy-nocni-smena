"""Vstup a výstup: rich konzole s animacemi pro hráče, skriptované UI pro testy.

Ve skutečném terminálu hra běží v alternativní obrazovce a každý tah překreslí
celou obrazovku na místě: nahoře stav, pod ním místnost, pak co se právě stalo
a nakonec nabídka. Bez terminálu (přesměrovaný výstup) se vše jen vypisuje za sebou.
"""

import os
import sys
import time
from bisect import bisect_right
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from rich.console import Console, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from . import art
from .actions import Action
from .items import ITEMS
from .state import MAX_PIECES, MAX_POCKETS, GameState
from .text import fmt_time, pieces_bar, transparency

# Rychlost psaní ve znacích za sekundu; 0 = bez animace.
SPEEDS = {"normální": 90, "rychlá": 260, "vypnutá": 0}
FRAME = 1 / 60
MAX_WIDTH = 96
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


def credits_text() -> Text:
    text = Text(justify="center", style="dim")
    text.append(f"{art.CREDITS_LABEL} {art.CREDITS_NAME} · ")
    text.append(art.CREDITS_SITE, style=f"bold link https://{art.CREDITS_SITE}")
    return text


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


@dataclass
class Scene:
    title: str
    text: str
    picture: str | None
    animate: bool
    shown: bool = False


@dataclass
class Message:
    text: Text
    speed: float = 1.0
    flicker: bool = False


class ConsoleUI:
    def __init__(self, console: Console | None = None, speed: str = "normální"):
        self.console = console or Console(highlight=False)
        self.interactive = self.console.is_terminal and sys.stdin.isatty()
        self.speed = speed if self.interactive else "vypnutá"
        # Stisk klávesy přeskočí všechny animace až do další volby.
        self.skipping = False
        self.scene: Scene | None = None
        self.seen_titles: set[str] = set()
        self.state: GameState | None = None
        self.goal = ""
        self.pending: list[Message] = []

    def __enter__(self) -> "ConsoleUI":
        if self.interactive:
            self.console.set_alt_screen(True)
        return self

    def __exit__(self, *exc) -> None:
        if self.interactive:
            self.console.set_alt_screen(False)

    @property
    def width(self) -> int:
        return min(self.console.width, MAX_WIDTH)

    # --- animace -----------------------------------------------------------

    @property
    def cps(self) -> int:
        return 0 if self.skipping else SPEEDS[self.speed]

    def cycle_speed(self) -> str:
        names = list(SPEEDS)
        self.speed = names[(names.index(self.speed) + 1) % len(names)]
        return self.speed

    def _type(self, text: Text, render: Callable[[Text], RenderableType] = lambda t: t,
              width: int | None = None, speed: float = 1.0) -> None:
        """Vypíše text postupně jako psací stroj. Libovolná klávesa animaci přeskočí."""
        if not self.cps:
            self.console.print(render(text), width=self.width)
            return
        # Text se zalomí předem, aby slova během psaní neskákala mezi řádky.
        text = Text("\n").join(text.wrap(self.console, width or self.width))
        if text.plain.count("\n") + 6 > self.console.height:
            # Živé překreslování by u textu vyššího než terminál zanechalo duplicitní řádky.
            self.console.print(render(text))
            return
        moments = _schedule(text.plain)
        cps = self.cps * speed
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
        with _SkipKeys() as keys:
            for line in picture.strip("\n").split("\n"):
                self.console.print(Text(line, style=style))
                if self.cps and keys.pressed():
                    self.skipping = True
                if self.cps:
                    time.sleep(0.025 * SPEEDS["normální"] / self.cps)

    def _flicker(self, text: str, styles: Sequence[str], final: str, frames: int, delay: float) -> None:
        if not self.cps:
            self.console.print(Text(text, style=final))
            return
        with Live(Text(text, style=styles[0]), console=self.console, auto_refresh=False) as live:
            for frame in range(frames):
                live.update(Text(text, style=styles[frame % len(styles)]), refresh=True)
                time.sleep(delay)
            live.update(Text(text, style=final), refresh=True)

    # --- zprávy (ukážou se pod místností při dalším překreslení) -------------

    def say(self, text: str) -> None:
        self.pending.append(Message(Text.from_markup(text)))

    def good(self, text: str) -> None:
        self.pending.append(Message(Text(text, style="green")))

    def bad(self, text: str) -> None:
        self.pending.append(Message(Text(text, style="bold red")))

    def sfx(self, text: str) -> None:
        """Zvukový efekt: pomalu a kurzívou."""
        self.pending.append(Message(Text(text, style="italic magenta"), speed=0.5))

    def flicker(self, text: str) -> None:
        """Text, který bliká a mizí – jako hráč, když ztrácí kousek sebe."""
        self.pending.append(Message(Text(text, style="bold red"), flicker=True))

    def head(self, text: str) -> None:
        line = Text()
        line.append("Hlava: ", style="bold yellow")
        line.append(text, style="italic yellow")
        self.pending.append(Message(line, speed=1.6))

    def _flush_messages(self) -> None:
        if not self.pending:
            return
        self.console.print()
        for message in self.pending:
            if message.flicker:
                styles = ["bold red", "dim red", "bold red", "grey23", "dim red"]
                self._flicker(message.text.plain, styles, "bold red", frames=10, delay=0.07)
            else:
                self._type(message.text, speed=message.speed)
        self.pending.clear()

    # --- obrazovky ---------------------------------------------------------

    def _clear(self) -> None:
        if self.interactive:
            self.console.clear()

    def title_screen(self) -> None:
        self.scene = None
        self._clear()
        self.console.print()
        self._reveal_art(art.TITLE, "bold magenta")
        # Zářivka nad přepážkou chvíli bliká, než chytne.
        flicker_styles = ["dim", "bold white", "dim", "dim", "bold white", "dim"]
        self._flicker(art.SUBTITLE.center(48), flicker_styles, "bold white", frames=9, delay=0.09)
        self.console.print(Text("Textová hra o všem, co lidé ztratí".center(48), style="italic dim"))
        self.console.print()
        self.console.print(credits_text(), width=48, justify="center")
        if self.cps:
            self.console.print(Text("(Animaci textu přeskočíš libovolnou klávesou.)".center(48), style="dim"))

    def page(self, title: str, text: str) -> None:
        """Samostatná stránka textu (úvod)."""
        self.scene = None
        self._clear()
        render = lambda body: Panel(body, title=f"[bold cyan]{title}[/bold cyan]", border_style="cyan",
                                    padding=(1, 2), width=self.width)
        self._type(Text.from_markup(text), render, width=self.width - 6)

    def set_scene(self, state: GameState, title: str, text: str, picture: str | None, goal: str) -> None:
        """Nastaví, co je na obrazovce za místnost. Vykreslí se až při další volbě."""
        self.state, self.goal = state, goal
        if self.scene and (self.scene.title, self.scene.text) == (title, text):
            return
        # Popis se píše animovaně jen při první návštěvě, pak už se jen ukáže.
        self.scene = Scene(title, text, picture, animate=title not in self.seen_titles)
        self.seen_titles.add(title)

    def _header(self) -> None:
        state = self.state
        left = state.deadline - state.minutes
        time_style = "bold red" if left <= 30 else "bold yellow" if left <= 60 else "bold"
        line = Text()
        line.append("Čas ", style="dim")
        line.append(fmt_time(state.minutes), style=time_style)
        line.append(f" {night_bar(state)} {fmt_time(state.deadline)}", style="dim")
        line.append("   Kousky sebe ", style="dim")
        line.append(pieces_bar(state), style="bold green" if state.pieces > 2 else "bold red")
        self.console.print(line, width=self.width)
        pockets = Text()
        pockets.append(f"Kapsy {len(state.pockets)}/{MAX_POCKETS}: ", style="dim")
        pockets.append(pockets_summary(state))
        self.console.print(pockets, width=self.width)
        goal = Text()
        goal.append("Úkol: ", style="bold yellow")
        goal.append(self.goal, style="yellow")
        self.console.print(goal, width=self.width)
        if state.pieces < MAX_PIECES:
            self.console.print(Text(transparency(state), style="italic dim"), width=self.width)
        self.console.print(Rule(style="dim"), width=self.width)

    def _fits_with_art(self, scene: Scene, menu_lines: int) -> bool:
        def lines(text: Text, width: int) -> int:
            return len(text.wrap(self.console, width))

        art_lines = scene.picture.strip("\n").count("\n") + 1
        header = 5 + (self.state.pieces < MAX_PIECES)
        panel = lines(Text.from_markup(scene.text), self.width - 4) + 2
        messages = sum(lines(m.text, self.width) for m in self.pending) + bool(self.pending)
        return header + art_lines + panel + messages + menu_lines + 4 <= self.console.height

    def _draw_scene(self, menu_lines: int) -> None:
        scene = self.scene
        first_time = scene.animate and not scene.shown
        self._header()
        if scene.picture and (not self.interactive or self._fits_with_art(scene, menu_lines)):
            if first_time:
                self._reveal_art(scene.picture, "cyan")
            else:
                self.console.print(Text(scene.picture.strip("\n"), style="cyan"))
        render = lambda body: Panel(body, title=f"[bold cyan]{scene.title}[/bold cyan]", border_style="cyan",
                                    padding=(0, 1), width=self.width)
        body = Text.from_markup(scene.text)
        if first_time:
            self._type(body, render, width=self.width - 4, speed=1.4)
        else:
            self.console.print(render(body))
        scene.shown = True

    def ending(self, number: int, title: str, text: str, footer: str, picture: str | None = None) -> None:
        self.scene = None
        self._clear()
        self._flush_messages()
        self.console.print()
        if picture:
            self._reveal_art(picture, "magenta")
        render = lambda body: Panel(
            body,
            title=f"[bold magenta]Konec {number} z 8: {title}[/bold magenta]",
            subtitle=footer,
            border_style="magenta",
            padding=(1, 2),
            width=self.width,
        )
        self._type(Text.from_markup(text), render, width=self.width - 6, speed=0.9)
        self.console.print(credits_text(), width=self.width, justify="center")

    def pause(self) -> None:
        self.skipping = False
        self.console.input("[dim](Enter pro pokračování)[/dim] ")

    def farewell(self, text: str) -> None:
        self.console.print(text)
        self.console.print(credits_text(), width=48, justify="center")

    def choose(self, actions: Sequence[Action], prompt: str = "Co uděláš?") -> Action:
        self.skipping = False
        numbered = [action for action in actions if not action.hotkey]
        hotkeys = {action.hotkey: action for action in actions if action.hotkey}
        menu_lines = len(numbered) + (2 if hotkeys else 0)
        if self.scene:
            if self.interactive:
                # Celá obrazovka se překreslí na místě, nic se nehromadí pod sebou.
                self._clear()
                self._draw_scene(menu_lines)
            elif not self.scene.shown:
                self._draw_scene(menu_lines)
            else:
                self._header()
        self._flush_messages()
        self.console.print()
        for number, action in enumerate(numbered, start=1):
            label = f"[dim]{action.label}[/dim]" if action.cost == 0 else action.label
            self.console.print(f"  [bold]{number:>2}[/bold]) {label}")
        if hotkeys:
            footer = "   ·   ".join(f"[bold]{key}[/bold] {action.label}" for key, action in hotkeys.items())
            self.console.print(f"\n  [dim]{footer}[/dim]")
        while True:
            answer = self.console.input(f"[bold]{prompt}[/bold] ").strip().lower()
            if answer.isdigit() and 1 <= int(answer) <= len(numbered):
                return numbered[int(answer) - 1]
            if answer in hotkeys:
                return hotkeys[answer]
            self.console.print(f"[red]Napiš číslo od 1 do {len(numbered)}.[/red]")


class ScriptedUI:
    """UI pro testy: vybírá akce podle klíčů a ukládá si veškerý výstup."""

    speed = "vypnutá"

    def __init__(self, script: Sequence[str | Callable[[Sequence[Action]], Action]]):
        self.script = list(script)
        self.log: list[str] = []
        self.scene: tuple[str, str] | None = None

    def __enter__(self) -> "ScriptedUI":
        return self

    def __exit__(self, *exc) -> None:
        pass

    def _out(self, text: str) -> None:
        self.log.append(text)

    def cycle_speed(self) -> str:
        return self.speed

    def title_screen(self) -> None:
        self._out(art.TITLE)

    def page(self, title: str, text: str) -> None:
        self._out(f"[{title}] {text}")

    def set_scene(self, state: GameState, title: str, text: str, picture: str | None, goal: str) -> None:
        if self.scene != (title, text):
            self.scene = (title, text)
            self._out(f"[{title}] {text}")
        self._out(f"{fmt_time(state.minutes)} {pieces_bar(state)} {pockets_summary(state)} | Úkol: {goal}")

    say = good = bad = sfx = flicker = farewell = _out

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
