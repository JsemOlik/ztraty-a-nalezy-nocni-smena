"""Vstup a výstup: rich konzole pro hráče, skriptované UI pro testy."""

from collections.abc import Callable, Sequence

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from .actions import Action
from .items import ITEMS
from .state import MAX_POCKETS, GameState
from .text import fmt_time, pieces_bar, transparency


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


class ConsoleUI:
    def __init__(self, console: Console | None = None):
        self.console = console or Console(highlight=False)

    def title(self, text: str, subtitle: str = "") -> None:
        self.console.print(
            Panel(Text(subtitle, justify="center"), title=f"[bold]{text}[/bold]", border_style="magenta", padding=(1, 4))
        )

    def room(self, title: str, text: str) -> None:
        self.console.print()
        self.console.print(Panel(text, title=f"[bold cyan]{title}[/bold cyan]", border_style="cyan", padding=(0, 1)))

    def hud(self, state: GameState) -> None:
        left = state.deadline - state.minutes
        time_style = "bold red" if left <= 30 else "bold yellow" if left <= 60 else "bold"
        line = Text()
        line.append("Čas ", style="dim")
        line.append(fmt_time(state.minutes), style=time_style)
        line.append(f" (konec v {fmt_time(state.deadline)})", style="dim")
        line.append("   Kousky sebe ", style="dim")
        line.append(pieces_bar(state), style="bold green" if state.pieces > 2 else "bold red")
        line.append(f"   Kapsy ({len(state.pockets)}/{MAX_POCKETS}) ", style="dim")
        line.append(pockets_summary(state))
        self.console.print(line)
        self.console.print(Text(transparency(state), style="italic dim"))

    def say(self, text: str) -> None:
        self.console.print(text)

    def good(self, text: str) -> None:
        self.console.print(Text(text, style="green"))

    def bad(self, text: str) -> None:
        self.console.print(Text(text, style="bold red"))

    def head(self, text: str) -> None:
        line = Text()
        line.append("Hlava: ", style="bold yellow")
        line.append(text, style="italic yellow")
        self.console.print(line)

    def ending(self, number: int, title: str, text: str, footer: str) -> None:
        self.console.print()
        self.console.print(Rule(style="magenta"))
        self.console.print(
            Panel(
                text,
                title=f"[bold magenta]Konec {number} z 8: {title}[/bold magenta]",
                subtitle=footer,
                border_style="magenta",
                padding=(1, 2),
            )
        )

    def pause(self) -> None:
        self.console.input("[dim](Enter pro pokračování)[/dim] ")

    def choose(self, actions: Sequence[Action], prompt: str = "Co uděláš?") -> Action:
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

    def __init__(self, script: Sequence[str | Callable[[Sequence[Action]], Action]]):
        self.script = list(script)
        self.log: list[str] = []

    def _out(self, text: str) -> None:
        self.log.append(text)

    def title(self, text: str, subtitle: str = "") -> None:
        self._out(f"{text}\n{subtitle}")

    def room(self, title: str, text: str) -> None:
        self._out(f"[{title}] {text}")

    def hud(self, state: GameState) -> None:
        self._out(f"{fmt_time(state.minutes)} {pieces_bar(state)} {pockets_summary(state)}")

    say = good = bad = _out

    def head(self, text: str) -> None:
        self._out(f"Hlava: {text}")

    def ending(self, number: int, title: str, text: str, footer: str) -> None:
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
