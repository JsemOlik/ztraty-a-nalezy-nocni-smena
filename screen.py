"""Všechno, co se vykresluje na obrazovku.

Ve skutečném terminálu hra běží v alternativní obrazovce a každý tah překreslí
celou obrazovku na místě: nahoře stav, pod ním místnost, pak co se právě stalo
a nakonec nabídka. Bez terminálu (přesměrovaný výstup) se vše jen vypisuje za sebou.

Hlášky (say, good, bad, ...) se neukazují hned, ale počkají v seznamu
pending_messages a vypíšou se při dalším překreslení pod místností.
"""

import os
import sys
import time

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

import art
import world

# Rychlost psaní ve znacích za sekundu; 0 = bez animace.
SPEEDS = {"normální": 90, "rychlá": 260, "vypnutá": 0}
SPEED_NAMES = ["normální", "rychlá", "vypnutá"]
MAX_WIDTH = 96
NIGHT_BAR_CELLS = 12

# Prodleva po interpunkci, v násobcích jednoho znaku.
PAUSES = {".": 9, "!": 9, "?": 9, "…": 12, ":": 5, ";": 4, ",": 3, "–": 3, "—": 3, "\n": 6}

console = Console(highlight=False)

settings = {
    "speed": "normální",
    # True, když hra běží ve skutečném terminálu.
    "interactive": False,
    # Stisk klávesy přeskočí všechny animace až do další volby.
    "skipping": False,
    # V testech se nic nevykresluje a volby se berou ze seznamu test_script.
    "test": False,
}

# Co je právě na obrazovce: místnost (scene), stav hry a úkol.
view = {"scene": None, "state": None, "goal": ""}
seen_titles = []
pending_messages = []

test_script = []
test_log = []

# Pro hlídání klávesy během animace (jen Mac a Linux).
key_watch = {"fd": None, "saved": None}


def option(key, label, cost=world.ACTION_MINUTES, hotkey=None):
    """Jedna volba v nabídce. Volby s hotkey se nečíslují a ukazují se v patičce."""
    return {"key": key, "label": label, "cost": cost, "hotkey": hotkey}


def setup(speed):
    settings["interactive"] = console.is_terminal and sys.stdin.isatty()
    if settings["interactive"]:
        settings["speed"] = speed
    else:
        settings["speed"] = "vypnutá"


def start_test(script):
    """Přepne obrazovku do testovacího režimu."""
    settings["test"] = True
    settings["speed"] = "vypnutá"
    test_script.clear()
    test_script.extend(script)
    test_log.clear()
    view["scene"] = None


def open_screen():
    if settings["interactive"]:
        console.set_alt_screen(True)


def close_screen():
    if settings["interactive"]:
        console.set_alt_screen(False)


def width():
    return min(console.width, MAX_WIDTH)


def chars_per_second():
    if settings["skipping"]:
        return 0
    return SPEEDS[settings["speed"]]


def cycle_speed():
    if settings["test"]:
        return settings["speed"]
    position = SPEED_NAMES.index(settings["speed"])
    settings["speed"] = SPEED_NAMES[(position + 1) % len(SPEED_NAMES)]
    return settings["speed"]


# --- Přeskočení animace klávesou ---------------------------------------------


def start_key_watch():
    """Během animace se klávesy nečtou jako text, ale jen hlídáme, jestli hráč něco zmáčkl."""
    if os.name == "posix" and sys.stdin.isatty():
        import termios
        import tty

        key_watch["fd"] = sys.stdin.fileno()
        key_watch["saved"] = termios.tcgetattr(key_watch["fd"])
        tty.setcbreak(key_watch["fd"])


def key_pressed():
    if os.name == "nt":
        import msvcrt

        hit = False
        while msvcrt.kbhit():
            msvcrt.getwch()
            hit = True
        return hit
    if key_watch["fd"] is None:
        return False
    import select

    ready = select.select([key_watch["fd"]], [], [], 0)[0]
    if ready:
        os.read(key_watch["fd"], 1024)
        return True
    return False


def stop_key_watch():
    if key_watch["saved"] is not None:
        import termios

        termios.tcsetattr(key_watch["fd"], termios.TCSADRAIN, key_watch["saved"])
    key_watch["fd"] = None
    key_watch["saved"] = None


# --- Animace -----------------------------------------------------------------


def make_panel(body, frame):
    """Zabalí text do rámečku. frame je slovník s titulkem, barvou a okraji, nebo None."""
    if frame is None:
        return body
    return Panel(
        body,
        title=frame["title"],
        subtitle=frame.get("subtitle"),
        border_style=frame["color"],
        padding=frame["padding"],
        width=width(),
    )


def type_text(text, frame=None, text_width=None, speed=1.0):
    """Vypíše text postupně jako psací stroj. Libovolná klávesa animaci přeskočí."""
    if text_width is None:
        text_width = width()
    if chars_per_second() == 0:
        console.print(make_panel(text, frame), width=width())
        return
    # Text se zalomí předem, aby slova během psaní neskákala mezi řádky.
    text = Text("\n").join(text.wrap(console, text_width))
    if text.plain.count("\n") + 6 > console.height:
        # Živé překreslování by u textu vyššího než terminál zanechalo duplicitní řádky.
        console.print(make_panel(text, frame))
        return
    delay = 1 / (chars_per_second() * speed)
    start_key_watch()
    try:
        with Live(make_panel(Text(), frame), console=console, auto_refresh=False, vertical_overflow="visible") as live:
            for position in range(len(text)):
                live.update(make_panel(text[: position + 1], frame), refresh=True)
                if key_pressed():
                    settings["skipping"] = True
                    break
                char = text.plain[position]
                time.sleep(delay * (1 + PAUSES.get(char, 0)))
            live.update(make_panel(text, frame), refresh=True)
    except KeyboardInterrupt:
        settings["skipping"] = True
        console.print(make_panel(text, frame))
    stop_key_watch()


def reveal_art(picture, color):
    """Vykreslí obrázek řádek po řádku."""
    start_key_watch()
    for line in picture.strip("\n").split("\n"):
        console.print(Text(line, style=color))
        if chars_per_second() and key_pressed():
            settings["skipping"] = True
        if chars_per_second():
            time.sleep(0.025 * SPEEDS["normální"] / chars_per_second())
    stop_key_watch()


def flicker_text(text, styles, final_style, frames, delay):
    """Text chvíli bliká mezi několika styly a pak zůstane ve finálním stylu."""
    if chars_per_second() == 0:
        console.print(Text(text, style=final_style))
        return
    with Live(Text(text, style=styles[0]), console=console, auto_refresh=False) as live:
        for frame in range(frames):
            live.update(Text(text, style=styles[frame % len(styles)]), refresh=True)
            time.sleep(delay)
        live.update(Text(text, style=final_style), refresh=True)


# --- Hlášky (ukážou se pod místností při dalším překreslení) -----------------


def add_message(text, speed=1.0, flicker=False):
    pending_messages.append({"text": text, "speed": speed, "flicker": flicker})


def say(text):
    if settings["test"]:
        test_log.append(text)
        return
    add_message(Text.from_markup(text))


def good(text):
    if settings["test"]:
        test_log.append(text)
        return
    add_message(Text(text, style="green"))


def bad(text):
    if settings["test"]:
        test_log.append(text)
        return
    add_message(Text(text, style="bold red"))


def sfx(text):
    """Zvukový efekt: pomalu a kurzívou."""
    if settings["test"]:
        test_log.append(text)
        return
    add_message(Text(text, style="italic magenta"), speed=0.5)


def flicker(text):
    """Text, který bliká a mizí – jako hráč, když ztrácí kousek sebe."""
    if settings["test"]:
        test_log.append(text)
        return
    add_message(Text(text, style="bold red"), flicker=True)


def head(text):
    """Co říká mluvící hlava v kapse."""
    if settings["test"]:
        test_log.append(f"Hlava: {text}")
        return
    line = Text()
    line.append("Hlava: ", style="bold yellow")
    line.append(text, style="italic yellow")
    add_message(line, speed=1.6)


def show_messages():
    if not pending_messages:
        return
    console.print()
    for message in pending_messages:
        if message["flicker"]:
            styles = ["bold red", "dim red", "bold red", "grey23", "dim red"]
            flicker_text(message["text"].plain, styles, "bold red", 10, 0.07)
        else:
            type_text(message["text"], speed=message["speed"])
    pending_messages.clear()


# --- Obrazovky ---------------------------------------------------------------


def clear():
    if settings["interactive"]:
        console.clear()


def credits_text():
    text = Text(justify="center", style="dim")
    text.append(f"{art.CREDITS_LABEL} {art.CREDITS_NAME} · ")
    text.append(art.CREDITS_SITE, style=f"bold link https://{art.CREDITS_SITE}")
    return text


def title_screen():
    if settings["test"]:
        test_log.append(art.TITLE)
        return
    view["scene"] = None
    clear()
    console.print()
    reveal_art(art.TITLE, "bold magenta")
    # Zářivka nad přepážkou chvíli bliká, než chytne.
    styles = ["dim", "bold white", "dim", "dim", "bold white", "dim"]
    flicker_text(art.SUBTITLE.center(48), styles, "bold white", 9, 0.09)
    console.print(Text("Textová hra o všem, co lidé ztratí".center(48), style="italic dim"))
    console.print()
    console.print(credits_text(), width=48, justify="center")
    if chars_per_second():
        console.print(Text("(Animaci textu přeskočíš libovolnou klávesou.)".center(48), style="dim"))


def page(title, text):
    """Samostatná stránka textu (úvod)."""
    if settings["test"]:
        test_log.append(f"[{title}] {text}")
        return
    view["scene"] = None
    clear()
    frame = {"title": f"[bold cyan]{title}[/bold cyan]", "color": "cyan", "padding": (1, 2)}
    type_text(Text.from_markup(text), frame, width() - 6)


def pockets_summary(state):
    if not state["pockets"]:
        return "prázdné"
    parts = []
    for item in world.unique(state["pockets"]):
        name = world.ITEMS[item]["name"]
        if item == "director_face" and state["face_worn"]:
            name = name + " (nasazená)"
        count = world.count_item(state, item)
        if count > 1:
            name = f"{name} ×{count}"
        parts.append(name)
    return ", ".join(parts)


def night_bar(state):
    filled = min(NIGHT_BAR_CELLS, round(state["minutes"] / state["deadline"] * NIGHT_BAR_CELLS))
    return "▕" + "█" * filled + "░" * (NIGHT_BAR_CELLS - filled) + "▏"


def set_scene(state, title, text, picture, goal):
    """Nastaví, jaká místnost je na obrazovce. Vykreslí se až při další volbě."""
    view["state"] = state
    view["goal"] = goal
    scene = view["scene"]
    if settings["test"]:
        if scene is None or scene["title"] != title or scene["text"] != text:
            test_log.append(f"[{title}] {text}")
        bar = world.pieces_bar(state)
        test_log.append(f"{world.fmt_time(state['minutes'])} {bar} {pockets_summary(state)} | Úkol: {goal}")
    if scene is not None and scene["title"] == title and scene["text"] == text:
        return
    # Popis se píše animovaně jen při první návštěvě, pak už se jen ukáže.
    view["scene"] = {
        "title": title,
        "text": text,
        "picture": picture,
        "animate": title not in seen_titles,
        "shown": False,
    }
    if title not in seen_titles:
        seen_titles.append(title)


def header():
    state = view["state"]
    left = state["deadline"] - state["minutes"]
    if left <= 30:
        time_style = "bold red"
    elif left <= 60:
        time_style = "bold yellow"
    else:
        time_style = "bold"
    line = Text()
    line.append("Čas ", style="dim")
    line.append(world.fmt_time(state["minutes"]), style=time_style)
    line.append(f" {night_bar(state)} {world.fmt_time(state['deadline'])}", style="dim")
    line.append("   Kousky sebe ", style="dim")
    if state["pieces"] > 2:
        line.append(world.pieces_bar(state), style="bold green")
    else:
        line.append(world.pieces_bar(state), style="bold red")
    console.print(line, width=width())
    pockets = Text()
    pockets.append(f"Kapsy {len(state['pockets'])}/{world.MAX_POCKETS}: ", style="dim")
    pockets.append(pockets_summary(state))
    console.print(pockets, width=width())
    goal = Text()
    goal.append("Úkol: ", style="bold yellow")
    goal.append(view["goal"], style="yellow")
    console.print(goal, width=width())
    if state["pieces"] < world.MAX_PIECES:
        console.print(Text(world.transparency(state), style="italic dim"), width=width())
    console.print(Rule(style="dim"), width=width())


def line_count(text, text_width):
    return len(text.wrap(console, text_width))


def fits_with_art(menu_lines):
    """Vejde se na obrazovku i obrázek místnosti? Když ne, obrázek vynecháme."""
    scene = view["scene"]
    state = view["state"]
    art_lines = scene["picture"].strip("\n").count("\n") + 1
    header_lines = 5
    if state["pieces"] < world.MAX_PIECES:
        header_lines = 6
    panel_lines = line_count(Text.from_markup(scene["text"]), width() - 4) + 2
    message_lines = 0
    for message in pending_messages:
        message_lines = message_lines + line_count(message["text"], width())
    if pending_messages:
        message_lines = message_lines + 1
    total = header_lines + art_lines + panel_lines + message_lines + menu_lines + 4
    return total <= console.height


def draw_scene(menu_lines):
    scene = view["scene"]
    first_time = scene["animate"] and not scene["shown"]
    header()
    picture = scene["picture"]
    if picture and (not settings["interactive"] or fits_with_art(menu_lines)):
        if first_time:
            reveal_art(picture, "cyan")
        else:
            console.print(Text(picture.strip("\n"), style="cyan"))
    frame = {"title": f"[bold cyan]{scene['title']}[/bold cyan]", "color": "cyan", "padding": (0, 1)}
    body = Text.from_markup(scene["text"])
    if first_time:
        type_text(body, frame, width() - 4, speed=1.4)
    else:
        console.print(make_panel(body, frame))
    scene["shown"] = True


def ending(number, title, text, footer, picture):
    if settings["test"]:
        test_log.append(f"KONEC {number}: {title}\n{text}\n{footer}")
        return
    view["scene"] = None
    clear()
    show_messages()
    console.print()
    reveal_art(picture, "magenta")
    frame = {
        "title": f"[bold magenta]Konec {number} z 8: {title}[/bold magenta]",
        "subtitle": footer,
        "color": "magenta",
        "padding": (1, 2),
    }
    type_text(Text.from_markup(text), frame, width() - 6, speed=0.9)
    console.print(credits_text(), width=width(), justify="center")


def pause():
    if settings["test"]:
        return
    settings["skipping"] = False
    console.input("[dim](Enter pro pokračování)[/dim] ")


def farewell(text):
    if settings["test"]:
        test_log.append(text)
        return
    console.print(text)
    console.print(credits_text(), width=48, justify="center")


def choose(options, prompt="Co uděláš?"):
    """Ukáže nabídku a vrátí klíč volby, kterou hráč vybral."""
    if settings["test"]:
        return choose_in_test(options)
    settings["skipping"] = False
    numbered = []
    hotkeys = []
    for choice in options:
        if choice["hotkey"] is None:
            numbered.append(choice)
        else:
            hotkeys.append(choice)
    menu_lines = len(numbered)
    if hotkeys:
        menu_lines = menu_lines + 2
    scene = view["scene"]
    if scene is not None:
        if settings["interactive"]:
            # Celá obrazovka se překreslí na místě, nic se nehromadí pod sebou.
            clear()
            draw_scene(menu_lines)
        elif not scene["shown"]:
            draw_scene(menu_lines)
        else:
            header()
    show_messages()
    console.print()
    number = 1
    for choice in numbered:
        label = choice["label"]
        if choice["cost"] == 0:
            label = f"[dim]{label}[/dim]"
        console.print(f"  [bold]{number:>2}[/bold]) {label}")
        number = number + 1
    if hotkeys:
        parts = []
        for choice in hotkeys:
            parts.append(f"[bold]{choice['hotkey']}[/bold] {choice['label']}")
        console.print("\n  [dim]" + "   ·   ".join(parts) + "[/dim]")
    while True:
        answer = console.input(f"[bold]{prompt}[/bold] ").strip().lower()
        if answer.isdigit() and 1 <= int(answer) <= len(numbered):
            return numbered[int(answer) - 1]["key"]
        for choice in hotkeys:
            if answer == choice["hotkey"]:
                return choice["key"]
        console.print(f"[red]Napiš číslo od 1 do {len(numbered)}.[/red]")


def choose_in_test(options):
    """V testech se volba bere ze seznamu test_script."""
    if not test_script:
        raise AssertionError("Skript došel. Nabídka: " + str(option_keys(options)))
    key = test_script.pop(0)
    if key not in option_keys(options):
        raise AssertionError(f"Akce '{key}' není v nabídce: " + str(option_keys(options)))
    return key


def option_keys(options):
    keys = []
    for choice in options:
        keys.append(choice["key"])
    return keys
