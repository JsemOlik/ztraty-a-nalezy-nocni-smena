import os
import random
import sys
import textwrap
import time

try:
    import msvcrt
except ImportError:
    msvcrt = None

# Zapne barvy ve Windows konzoli
os.system("")
USE_COLORS = sys.stdout.isatty()
ANIMATE = sys.stdout.isatty()
TYPING_DELAY = 0.012

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GRAY = "\033[90m"

MAX_LIVES = 5
POCKET_SIZE = 4
SHIFT_END = 6 * 60
OFFICE_CODE = "0600"
AUTHOR = "Vytvořil Oliver Steiner  ·  jsemolik.dev"

ITEM_NAMES = {
    "key": "klíč od skladu",
    "umbrella": "suchý deštník",
    "head": "mluvící hlava",
    "hour": "ztracená hodina",
    "note": "papírek s kódem",
    "thread": "červená nit",
    "face": "ředitelova tvář",
    "badge": "Hlaváčkova jmenovka",
    "photo": "vlastní fotka",
}

ROOM_TITLES = {
    "counter": "Přepážka",
    "umbrellas": "Sklad deštníků",
    "time": "Oddělení ztraceného času",
    "voices": "Kabinet ztracených řečí",
    "threads": "Archiv ztracených nití",
    "faces": "Galerie ztracených tváří",
    "office": "Ředitelna",
    "cellar": "Sklep",
    "hidden": "Skrytá místnost",
}

HEAD_LINES = {
    "counter": ["Tady aspoň neprší. Ale ten telefon na mě divně kouká!",
                "Nemůžeme si dát taky čaj? Teda ty. Já nemám kam ho nalít."],
    "umbrellas": ["Zase ten déšť! Mám mokré ucho!",
                  "Tady jsem seděl celý týden. V krabici. V dešti. Sám!"],
    "time": ["Tik tak! Tik tak! Slyšíš to? To se blíží šestá!",
             "Tolik hodin a žádné nejdou správně. Jako já."],
    "voices": ["Neotvírej tu, co se třese! Ta křičí celou noc!",
               "Tamta se chichotá. Tu bych bral."],
    "threads": ["Pan Hlaváček měl rád červenou. Myslím. Asi. Možná!",
                "Hlavně neztrať nit! Teda... ty víš, jak to myslím."],
    "faces": ["Nedívej se jim do očí! Ty masky na mě civí!",
              "Cizí tvář si nenasazuj dlouho. Přiroste. Viděl jsem to!"],
    "office": ["Jestli nás tu ředitel najde, jsme ztracení. Teda ještě víc.",
               "Tady to voní důležitostí. A prachem."],
    "cellar": ["To je on! To je moje tělo! Ahoj, tělo!",
               "Rychle, dej mě k němu, než zase do něčeho narazí!"],
    "hidden": ["Tady je strašné ticho. Tady nikdo nic nehledá...",
               "Pane Hlaváčku! Vydržte!"],
}

# --- ASCII obrázky ---

TITLE_LETTERS = [
    "              ´                       ´",
    "┌─┐ ┌┬┐ ┬─┐ ┌─┐ ┌┬┐ ┬ ┬   ┌─┐   ┌┐┌ ┌─┐ ┬   ┌─┐ ┌─┐ ┬ ┬",
    "┌─┘  │  ├┬┘ ├─┤  │  └┬┘   ├─┤   │││ ├─┤ │   ├┤  ┌─┘ └┬┘",
    "└─┘  ┴  ┴└─ ┴ ┴  ┴   ┴    ┴ ┴   ┘└┘ ┴ ┴ ┴─┘ └─┘ └─┘  ┴",
]

INTRO_ART = r"""
     ═══════════  STARÁ POŠTA  ═══════════
  ___
     |___
         |___                   .--------.
             |___               | ZTRÁTY |
                 |___           |   A    |
                     |___       | NÁLEZY |
                         |______|    o   |
                                '--------'
"""

ROOM_ART = {
    "counter": (YELLOW, r"""
  ___________________________________________
 |  ZTRÁTY A NÁLEZY             ~ PŘEPÁŽKA ~ |
 |___________________________________________|
 |   _n_      .----.     ________     c[_]   |
 |  (___)     |o  o|    | DENÍK  |           |
 |  zvonek    '----'    |________|    čaj    |
 |___________ telefon _______________________|
"""),
    "umbrellas": (BLUE, r"""
    ,  '  ,  '  ,  '  ,  '  ,  '  ,  '  ,  '
      .-^^^-.   '   .-^^^-.   ,   .-^^^-.
     /_______\  ,  /_______\  '  /_______\
         |     '       |     ,       |
     '  _|  ,  '  ,   _|  '  ,  _____  ,
    ,  '  ,  '  ,  '  ,  '  ,  |_____|  '
"""),
    "time": (CYAN, r"""
        .-------.        .---.    .---.    .---.
      .'   12    '.     | 3 |    | 7 |    |11 |
     |  9   o--  3 |    '---'    '---'    '---'
      '.    6    .'      tik      tak      tik
        '-------'
"""),
    "voices": (MAGENTA, r"""
      _______      _______      _______
     [_______]    [_______]    [_______]
     |  ~ ~  |    |  ha   |    | Hla-  |
     |  !!!  |    |    ha |    | váček |
     |_______|    |_______|    |_______|
"""),
    "faces": (WHITE, r"""
      .---.     .---.     .---.     #=========#
     ( o o )   ( > < )   ( - - )    #  ò _ ó  #
      ) ~ (     ) o (     ) _ (     #   ===   #
       '-'       '-'       '-'      #=========#
                                      ŘEDITEL
"""),
    "office": (YELLOW, r"""
       ____________________
      |  JEN PRO ŘEDITELE  |
      |--------------------|
      |  [====]   [====]   |
      |--------------------|
      |  [====]   [====]   |
      |____________________|
"""),
    "cellar": (RED, r"""
     .  .  .  .  .  .  .  .  .  .  .  .  .
          dup!          _|_         dup!
                       / | \
              dup!      / \     dup!
     .  .  .  .  .  .  .  .  .  .  .  .  .
"""),
    "hidden": (GRAY, r"""
          o         ?          ~          o
     ?         ~         o         ?
     _______________________________________
    | dopisy  ponožky  sny  deštník  dopisy |
    |_______________________________________|
                       .
                      (o)   <- pan Hlaváček
                      /|\
"""),
}

CALM_CELLAR_ART = r"""
                         O
                        /|\    „Děkuju.“
                        / \
"""

PHOTO_ART = r"""
        .-------------.
        |   \(^o^)/   |
        |     | |     |
        '-------------'
"""

ENDING_ART = {
    1: r"""
       _______
      |VÝCHOD |     \o/
      |   ►   |      |     hurá domů!
      |_______|     / \
""",
    2: r"""
       _|_        _|_
      / | \      / | \
       / \        / \
     dup dup    dup dup
""",
    3: r"""
       ____________________________
      /  o   NALEZENO              |
      \      noční úředník, 1 kus  |
       '---------------------------'
""",
    4: r"""
        .        .
       (o)      (o)
       /|\      /|\
       / \      / \
     . . . . . . . . .
""",
    5: r"""
        _/\_/\_/\_
       |__________|
         ( ò_ó )
          \___/
""",
    6: r"""
        _______
        \:::::/
         \:::/
          )|(
         /   \
        /_____\
""",
    7: r"""
         \   |   /
       --  .-'-.  --
      ____/_____\____
          o      o
         /|\    /|\
         / \    / \
""",
    8: r"""
         \   |   /
       --  .-'-.  --
      ____/_____\____
          o      o
         /|\ ♥  /|\
         / \    / \
""",
}


def new_game():
    return {
        "time": 0,
        "lives": MAX_LIVES,
        "inventory": [],
        "used_items": [],
        "last_room": "",
        "over": False,
        "free_action": False,
        "late_warning": False,
        "tea_drunk": False,
        "riddle_solved": False,
        "jar_scream_opened": False,
        "jar_laugh_opened": False,
        "jar_voice_opened": False,
        "office_unlocked": False,
        "files_read": False,
        "photo_healed": False,
        "head_returned": False,
        "cellar_visits": 0,
        "face_worn": False,
        "face_turns": 0,
    }


# --- Vzhled ---

def paint(text, *styles):
    if not USE_COLORS:
        return text
    return "".join(styles) + text + RESET


def wrap_lines(text, width=72):
    lines = []
    for paragraph in text.split("\n"):
        lines.extend(textwrap.wrap(paragraph, width) or [""])
    return lines


def key_pressed():
    if msvcrt and msvcrt.kbhit():
        msvcrt.getwch()
        return True
    return False


def say(text, *styles):
    # Text se vypisuje jako na psacím stroji, stisk klávesy ho dopíše najednou
    skipping = not ANIMATE
    for line in wrap_lines(text, 76):
        if skipping:
            print(paint(line, *styles))
            continue
        print("".join(styles), end="")
        for index, char in enumerate(line):
            print(char, end="", flush=True)
            if key_pressed():
                print(line[index + 1:], end="")
                skipping = True
                break
            if char in ".!?":
                time.sleep(TYPING_DELAY * 8)
            elif char in ",:;":
                time.sleep(TYPING_DELAY * 3)
            else:
                time.sleep(TYPING_DELAY)
        print(RESET)


def draw_art(art, color):
    for line in art.strip("\n").split("\n"):
        print(paint(line, color), flush=True)
        if ANIMATE:
            time.sleep(0.03)


def draw_box(lines, color, double=False, text_style=WHITE):
    if double:
        top_left, top_right, bottom_left, bottom_right, flat, side = "╔", "╗", "╚", "╝", "═", "║"
    else:
        top_left, top_right, bottom_left, bottom_right, flat, side = "┌", "┐", "└", "┘", "─", "│"
    width = max(len(line) for line in lines)
    print(paint("  " + top_left + flat * (width + 2) + top_right, color))
    for line in lines:
        print(paint("  " + side + " ", color) + paint(line.ljust(width), text_style) + paint(" " + side, color))
    print(paint("  " + bottom_left + flat * (width + 2) + bottom_right, color))


def clear_screen():
    if USE_COLORS:
        print("\033[2J\033[H", end="")


def draw_title():
    clear_screen()
    print()
    width = len(TITLE_LETTERS[1])
    lines = [""]
    for row in TITLE_LETTERS:
        lines.append(row)
    lines.append("")
    lines.append("N O Č N Í   S M Ě N A".center(width))
    lines.append("")
    draw_box(lines, YELLOW, double=True, text_style=BOLD + YELLOW)
    print(paint(AUTHOR.center(width + 6), GRAY))
    print()


def format_time(minutes):
    return f"{minutes // 60}:{minutes % 60:02d}"


def describe_self(lives):
    if lives >= 5:
        return "Cítíš se celistvě. Všechny kousky tebe jsou na svém místě."
    elif lives == 4:
        return "Konečky prstů ti lehce prosvítají. Asi jen únava."
    elif lives == 3:
        return "Přes ruce ti prosvítá podlaha. Tohle únava není."
    elif lives == 2:
        return "Když míjíš zrcadlo, skoro v něm nejsi vidět."
    else:
        return "Zbývá z tebe jen obrys. I vlastní stín tě přestává poznávat."


def show_status(game):
    if game["time"] < 4 * 60:
        time_color = GREEN
    elif game["time"] < 5 * 60:
        time_color = YELLOW
    else:
        time_color = RED
    if game["lives"] >= 4:
        lives_color = CYAN
    elif game["lives"] >= 2:
        lives_color = YELLOW
    else:
        lives_color = RED
    lives_bar = "●" * game["lives"] + "○" * (MAX_LIVES - game["lives"])
    pockets_bar = "■" * len(game["inventory"]) + "□" * (POCKET_SIZE - len(game["inventory"]))
    separator = paint("  │  ", GRAY)
    print("  " + paint("Čas ", GRAY) + paint(format_time(game["time"]), BOLD, time_color)
          + separator + paint("Kousky sebe ", GRAY) + paint(lives_bar, lives_color)
          + separator + paint("Kapsy ", GRAY) + paint(pockets_bar, YELLOW))


def has(game, item):
    return item in game["inventory"]


def available(game, item):
    return item not in game["inventory"] and item not in game["used_items"]


def print_option(number, label, style=WHITE):
    print("  " + paint(f"[{number}]", BOLD, CYAN) + " " + paint(label, style))


def read_number(count):
    while True:
        answer = input(paint("  > ", BOLD, CYAN)).strip()
        if answer.isdigit() and 1 <= int(answer) <= count:
            print()
            return int(answer)
        print(paint("  Zadej číslo z nabídky.", GRAY))


def simple_choice(options):
    for number, option in enumerate(options, start=1):
        print_option(number, option[1])
    return options[read_number(len(options)) - 1][0]


def choose(game, options):
    # Kapsy a sundání tváře jsou zdarma, nestojí žádný čas
    print()
    for number, option in enumerate(options, start=1):
        print_option(number, option[1])
    pockets_number = len(options) + 1
    print_option(pockets_number, "Prohlédnout kapsy", GRAY)
    count = pockets_number
    if game["face_worn"]:
        print_option(pockets_number + 1, "Sundat ředitelovu tvář", MAGENTA)
        count += 1

    number = read_number(count)
    if number <= len(options):
        return options[number - 1][0]
    if number == pockets_number:
        show_pockets(game)
    else:
        take_off_face(game)
    game["free_action"] = True
    return "refresh"


def head_comment(game, room):
    if has(game, "head"):
        say("  (°o°) „" + random.choice(HEAD_LINES[room]) + "“", MAGENTA)


def draw_room_art(game, room):
    if room == "threads":
        for color, length in [(BLUE, 30), (GREEN, 24), (RED, 36)]:
            print(paint("    (@)" + "~" * length + ">", color))
    elif room == "cellar" and game["head_returned"]:
        draw_art(CALM_CELLAR_ART, GREEN)
    else:
        color, art = ROOM_ART[room]
        draw_art(art, color)


def enter_room(game, room, description):
    print()
    if game["last_room"] != room:
        draw_box(["◆  " + ROOM_TITLES[room].upper() + "  ◆"], CYAN, double=True, text_style=BOLD + WHITE)
        draw_room_art(game, room)
        print()
        say(description)
        head_comment(game, room)
        game["last_room"] = room
    else:
        print(paint("  ── " + ROOM_TITLES[room] + " ──", BOLD, CYAN))
    show_status(game)


def ending(game, number, title, text, color):
    print()
    draw_box(["", f"KONEC {number}/8".center(40), title.upper().center(40), ""], color, double=True,
             text_style=BOLD + color)
    draw_art(ENDING_ART[number], color)
    print()
    say(text)
    game["over"] = True


def lose_life(game, reason):
    say(reason)
    game["lives"] -= 1
    if game["lives"] <= 0:
        ending(game, 4, "Nikdo nehledá",
               "Poslední kousek tebe zmizí. Probouzíš se v místnosti, kam padá všechno, "
               "co už nikdo nehledá. Vedle tebe sedí pan Hlaváček a smutně ti kývne na pozdrav. "
               "Blednete spolu.", GRAY)
    else:
        say("  ✗ Ztrácíš kousek sebe. " + describe_self(game["lives"]), RED)


def gain_life(game, reason):
    say(reason)
    if game["lives"] < MAX_LIVES:
        game["lives"] += 1
        say("  ✓ Kousek tebe se vrací. " + describe_self(game["lives"]), GREEN)
    else:
        say("  Víc sebe už mít nemůžeš, ale i tak to potěší.", GREEN)


def spend_time(game):
    game["time"] += 5
    if game["face_worn"]:
        game["face_turns"] += 1
        if game["face_turns"] == 3:
            say("Ředitelova tvář ti začíná přirůstat k lícím. Bylo by načase ji sundat.", MAGENTA)
        elif game["face_turns"] == 4:
            lose_life(game, "Cizí tvář si bere kus té tvojí.")
        elif game["face_turns"] == 5:
            say("Už si skoro nepamatuješ, jak vypadáš bez ní.", MAGENTA)
        elif game["face_turns"] >= 6:
            ending(game, 5, "Pan ředitel",
                   "Zkusíš si tvář sundat, ale nejde to. Už to není maska, je to tvůj obličej. "
                   "Přepážka se před tebou uctivě sklání, sklenice ztichnou, hodiny se srovnají. "
                   "Od této noci vládneš všem ztraceným věcem. Jen tvou vlastní tvář už nikdo "
                   "nikdy nenajde.", MAGENTA)
    if game["over"]:
        return
    if game["time"] >= SHIFT_END:
        ending(game, 3, "Inventář",
               "Odbíjí šest. Dveře cvaknou a přichází denní směna. Najdou jen prázdnou přepážku "
               "a v deníku nový zápis: „Nalezeno: noční úředník, 1 kus. Nikdo se nehlásí.“", RED)
    elif game["time"] >= SHIFT_END - 30 and not game["late_warning"]:
        game["late_warning"] = True
        print()
        say("  ⚠ Hodiny na zdi ukazují půl šesté. Denní směna se blíží!", BOLD, RED)


# --- Kapsy ---

def pick_up(game, item):
    inventory = game["inventory"]
    if len(inventory) >= POCKET_SIZE:
        say("Kapsy máš plné. Co v nich uvolníš?", YELLOW)
        options = []
        for thing in inventory:
            options.append((thing, ITEM_NAMES[thing]))
        options.append(("nothing", f"Nic, nová věc ({ITEM_NAMES[item]}) zůstane ležet"))
        choice = simple_choice(options)
        if choice == "nothing":
            say("Necháváš to ležet. Počká to tu na tebe.")
            return False
        drop_item(game, choice)
    inventory.append(item)
    say(f"  + Do kapsy saka si dáváš: {ITEM_NAMES[item]}.", BOLD, YELLOW)
    return True


def drop_item(game, item):
    game["inventory"].remove(item)
    if item == "face":
        game["face_worn"] = False
        game["face_turns"] = 0
    say(f"  − Odkládáš: {ITEM_NAMES[item]}. Věc se vrátí na své místo, tady se nic neztratí nadobro.",
        GRAY)
    if item == "head":
        say("  (°o°) „Ne! Nenechávej mě tady! ...No dobře, počkám v krabici. Ale pospěš si!“", MAGENTA)


def take_off_face(game):
    game["face_worn"] = False
    game["face_turns"] = 0
    say("S mlasknutím si stahuješ ředitelovu tvář. Pod ní je zase ta tvoje. Uf.", MAGENTA)


def show_pockets(game):
    lines = ["KAPSY SAKA", ""]
    for slot in range(POCKET_SIZE):
        if slot < len(game["inventory"]):
            item = game["inventory"][slot]
            note = " (na obličeji)" if item == "face" and game["face_worn"] else ""
            lines.append(f"[■] {ITEM_NAMES[item]}{note}")
        else:
            lines.append("[□] prázdná kapsa")
    draw_box(lines, YELLOW, text_style=YELLOW)
    say(describe_self(game["lives"]), CYAN)
    print()

    options = []
    if has(game, "hour"):
        options.append(("hour", "Použít ztracenou hodinu"))
    if has(game, "note"):
        options.append(("note", "Přečíst papírek"))
    if game["inventory"]:
        options.append(("drop", "Odložit nějakou věc"))
    options.append(("close", "Zavřít kapsy"))
    choice = simple_choice(options)

    if choice == "hour":
        game["inventory"].remove("hour")
        game["used_items"].append("hour")
        game["time"] = max(0, game["time"] - 60)
        game["late_warning"] = False
        say(f"Ztracená hodina se rozvine a ručičky všech hodin couvnou. Je {format_time(game['time'])}.",
            CYAN)
    elif choice == "note":
        draw_box([f"Ředitelna: {OFFICE_CODE}", "Jako konec směny."], YELLOW, text_style=BOLD + WHITE)
    elif choice == "drop":
        options = []
        for item in game["inventory"]:
            options.append((item, ITEM_NAMES[item]))
        options.append(("nothing", "Nic, nechám si všechno"))
        item = simple_choice(options)
        if item != "nothing":
            drop_item(game, item)


# --- Pohyb po úřadu ---

def draw_signpost(options):
    width = 0
    for option in options:
        width = max(width, len(option[1]) + 12)
    middle = width // 2
    post = " " * (3 + middle) + "║"
    print(paint(" " * (3 + middle) + "▲", YELLOW))
    print(paint(post, YELLOW))
    print(paint("  ┌" + "─" * middle + "╨" + "─" * (width - middle - 1) + "┐", YELLOW))
    for number, option in enumerate(options, start=1):
        text = f"[{number}] {option[1]}"
        if number % 2 == 1:
            line = (" ◄ " + text).ljust(width)
        else:
            line = (text + " ► ").rjust(width)
        print(paint("  │", YELLOW) + paint(line, BOLD, WHITE) + paint("│", YELLOW))
        if number < len(options):
            print(paint("  ├" + "─" * width + "┤", YELLOW))
    print(paint("  └" + "─" * middle + "╥" + "─" * (width - middle - 1) + "┘", YELLOW))
    print(paint(post, YELLOW))
    print(paint(post, YELLOW))
    print(paint(" " * (middle - 4) + r"\\|//|\\|//|\\", GREEN))


def go_somewhere(game, current):
    places = [("counter", "K přepážce"), ("umbrellas", "Do skladu deštníků"),
              ("time", "Do oddělení ztraceného času"), ("voices", "Do kabinetu ztracených řečí"),
              ("threads", "Do archivu ztracených nití"), ("faces", "Do galerie ztracených tváří"),
              ("office", "Do ředitelny"), ("cellar", "Dolů do sklepa")]
    if has(game, "thread"):
        places.append(("hidden", "Po červené niti hluboko pod sklep"))
    options = []
    for place in places:
        if place[0] != current:
            options.append(place)
    options.append(("stay", "Zůstat tady"))

    print(paint("  Kam se vydáš?", BOLD))
    draw_signpost(options)
    target = options[read_number(len(options)) - 1][0]

    if target == "stay":
        game["free_action"] = True
        return current

    if target == "umbrellas":
        if not has(game, "key"):
            say("Dveře skladu jsou zamčené. Zpoza nich je slyšet déšť.")
            return current
        if has(game, "umbrella"):
            say("Odemykáš a rozevíráš deštník. Kapky bubnují, ale ty zůstáváš v suchu.", BLUE)
        else:
            lose_life(game, "Odemykáš a vcházíš. Uvnitř leje jako z konve a déšť z tebe smývá víc než jen prach.")

    if target == "office" and not game["office_unlocked"]:
        say("Dveře ředitelny hlídá číselný zámek.")
        draw_box(["[ _ ] [ _ ] [ _ ] [ _ ]"], GRAY, text_style=BOLD + WHITE)
        if has(game, "note"):
            say(f"Vytahuješ papírek. Stojí na něm: {OFFICE_CODE}.", YELLOW)
        code = input(paint("  Zadej čtyřmístný kód: ", BOLD, CYAN)).strip()
        if code != OFFICE_CODE:
            say("Zámek nespokojeně zabzučí. Dveře zůstávají zavřené.", RED)
            return current
        game["office_unlocked"] = True
        say("Cvak. Dveře se otevírají.", GREEN)

    if target == "cellar" and not has(game, "head") and not game["head_returned"]:
        game["cellar_visits"] += 1
        if game["cellar_visits"] == 1:
            lose_life(game, "Ve tmě se na tebe něco řítí. Bezhlavý! Tluče kolem sebe, naráží do zdí "
                            "i do tebe. Utíkáš po schodech nahoru, ale kousek tebe zůstal dole.")
            return current
        ending(game, 2, "Ztratil jsi hlavu",
               "Ve tmě se do tebe Bezhlavý znovu opře. Tentokrát utéct nestihneš. Ráno najde denní "
               "směna ve sklepě dva pobíhající a ani jeden z nich nemá hlavu.", RED)
        return current

    return target


# --- Místnosti ---

def room_counter(game):
    description = ("Přepážka s mosazným zvonkem, zaprášený telefon a deník služeb. Na pultu stojí "
                   "hrnek s nedopitým čajem pana Hlaváčka.")
    if available(game, "key"):
        description += " Na háčku pod pultem visí klíč s visačkou „Sklad“."
    if available(game, "umbrella"):
        description += " Ve stojanu stojí jediný suchý deštník."
    enter_room(game, "counter", description)

    options = [("diary", "Přečíst deník služeb")]
    if not game["tea_drunk"]:
        options.append(("tea", "Dopít Hlaváčkův čaj"))
    if available(game, "key"):
        options.append(("key", "Vzít klíč od skladu"))
    if available(game, "umbrella"):
        options.append(("umbrella", "Vzít suchý deštník"))
    options.append(("go", "Jít jinam"))
    choice = choose(game, options)

    if choice == "diary":
        lines = ["DENÍK SLUŽEB, poslední zápisy pana Hlaváčka", ""]
        entries = ["– Do skladu deštníků nikdy bez deštníku. Prší tam celý rok.",
                   "– Ve sklepě běhá Bezhlavý. Bez jeho hlavy tam nelezte!",
                   "– Kód do ředitelny mám na papírku. Papírek je někde u hlasů.",
                   "– Moje nit je červená. Kdyby něco, jděte po ní.",
                   "– Někdo tu zase ztratil hlavu. Jdu dolů to vyřešit."]
        for entry in entries:
            lines.extend(wrap_lines(entry, 64))
        draw_box(lines, YELLOW)
    elif choice == "tea":
        game["tea_drunk"] = True
        gain_life(game, "Čaj je studený, ale chutná jako domov.")
    elif choice == "key":
        pick_up(game, "key")
    elif choice == "umbrella":
        pick_up(game, "umbrella")
    elif choice == "go":
        return go_somewhere(game, "counter")
    return "counter"


def room_umbrellas(game):
    description = "Stovky zapomenutých deštníků a nad nimi jejich vlastní mraky. Prší tu bez přestání."
    if available(game, "head"):
        description += " Mezi deštníky stojí krabice na klobouk a ozývá se z ní vzlykání."
    enter_room(game, "umbrellas", description)

    options = []
    if available(game, "head"):
        options.append(("box", "Otevřít krabici na klobouk"))
    options.append(("go", "Jít jinam"))
    choice = choose(game, options)

    if choice == "box":
        say("V krabici je hlava. Živá, ukecaná a k smrti vyděšená.")
        say("  (°o°) „Konečně někdo! Já jsem hlava Bezhlavého. On ztratil hlavu, chápeš? Doslova! "
            "Vezmi mě dolů do sklepa, prosím, prosím, prosím!“", MAGENTA)
        pick_up(game, "head")
    elif choice == "go":
        return go_somewhere(game, "umbrellas")
    return "umbrellas"


def room_time(game):
    description = ("Stovky hodin tikají a každé jdou jinak. Jedny se předbíhají, jiné jdou pozpátku. "
                   "Uprostřed visí obří hodiny, které stojí.")
    enter_room(game, "time", description)

    options = []
    if not game["riddle_solved"]:
        options.append(("riddle", "Prohlédnout si stojící hodiny"))
    elif available(game, "hour"):
        options.append(("hour", "Vzít ztracenou hodinu"))
    options.append(("steal", "Nacpat si kapsy cizím časem a jít domů"))
    options.append(("go", "Jít jinam"))
    choice = choose(game, options)

    if choice == "riddle":
        say("Na ciferníku je vyryto:")
        draw_box(["Kolikrát za den ukážu přesný čas?"], CYAN, text_style=BOLD + WHITE)
        answer = input(paint("  Tvoje odpověď: ", BOLD, CYAN)).strip().lower()
        if "2" in answer or "dva" in answer:
            game["riddle_solved"] = True
            say("Hodiny cvaknou a z dvířek vypadne ztracená hodina. Malá, teplá a tikající. "
                "Dá se s ní prodloužit noc.", GREEN)
            pick_up(game, "hour")
        else:
            say("Hodiny se ani nehnou. Možná to chce chvíli přemýšlet.", GRAY)
    elif choice == "hour":
        pick_up(game, "hour")
    elif choice == "steal":
        say("Opravdu si chceš odnést čas, který patří jiným?", BOLD)
        if simple_choice([("yes", "Ano, čas jsou peníze"), ("no", "Ne, to by nebylo správné")]) == "yes":
            ending(game, 6, "Zloděj času",
                   "Cpeš si do kapes minuty, hodiny i celé roky a zadním východem mizíš domů. "
                   "Žiješ dlouho, předlouho. Až na sklonku života ti dojde, komu ty hodiny chybí: "
                   "všem těm lidem, kteří si celý život stěžovali, že nemají čas.", MAGENTA)
        else:
            say("Necháváš hodiny tikat dál. Patří jiným.")
    elif choice == "go":
        return go_somewhere(game, "time")
    return "time"


def room_voices(game):
    description = ("Na policích stojí zavařovací sklenice a v každé je zavřený hlas, který někomu "
                   "došel uprostřed věty. Tři sklenice stojí blíž než ostatní.")
    enter_room(game, "voices", description)

    options = []
    if not game["jar_scream_opened"]:
        options.append(("scream", "Otevřít sklenici, které poskakuje víčko"))
    if not game["jar_laugh_opened"]:
        options.append(("laugh", "Otevřít sklenici, ve které se něco tiše chichotá"))
    if not game["jar_voice_opened"]:
        options.append(("voice", "Otevřít sklenici se štítkem „Hlaváček“"))
    elif available(game, "note"):
        options.append(("note", "Vzít papírek s kódem"))
    options.append(("go", "Jít jinam"))
    choice = choose(game, options)

    if choice == "scream":
        game["jar_scream_opened"] = True
        print(paint("    AAAAAAAAAAAAAAAAAAAAAA!!!", BOLD, RED))
        lose_life(game, "Ze sklenice vyletí něčí výkřik, proletí tebou a kus tebe si odnese s sebou.")
    elif choice == "laugh":
        game["jar_laugh_opened"] = True
        print(paint("    cha cha chi chi hi hi ha ha!", BOLD, GREEN))
        gain_life(game, "Místností se rozlije ztracený smích. Nedá se mu nesmát.")
    elif choice == "voice":
        game["jar_voice_opened"] = True
        say("Ze sklenice zazní známý hlas:")
        say("„...a kód do ředitelny jsem si napsal na papírek a strčil ho pod tuhle sklenici, abych—“",
            MAGENTA)
        say("Hlas utichne uprostřed věty. Pod sklenicí opravdu leží zmačkaný papírek.")
        pick_up(game, "note")
    elif choice == "note":
        pick_up(game, "note")
    elif choice == "go":
        return go_somewhere(game, "voices")
    return "voices"


def room_threads(game):
    description = ("Všude se válí klubka od lidí, kteří ztratili nit. Do tmy mezi regály vedou tři "
                   "nitě: modrá, zelená a červená.")
    enter_room(game, "threads", description)

    options = [("blue", "Jít po modré niti"), ("green", "Jít po zelené niti")]
    if available(game, "thread"):
        options.append(("red", "Jít po červené niti"))
    options.append(("go", "Jít jinam"))
    choice = choose(game, options)

    if choice == "blue":
        game["time"] += 10
        lose_life(game, "Modrá nit tě vodí dokola, až nevíš, kde je nahoře. Než najdeš cestu zpátky, "
                        "uplyne čtvrt hodiny a kus tebe zůstane mezi regály.")
    elif choice == "green":
        game["time"] += 10
        lose_life(game, "Zelená nit končí na místě, které není na žádné mapě. Bloudíš, dokud tě "
                        "nevyplivne zpátky do archivu. Něco ti chybí.")
    elif choice == "red":
        say("Červená nit je pevná a teplá. Na jejím konci visí cedulka „Hlaváček“. Vede kamsi "
            "hluboko pod sklep. Namotáváš si klubko, teď tě dovede, kam bude potřeba.", RED)
        pick_up(game, "thread")
    elif choice == "go":
        return go_somewhere(game, "threads")
    return "threads"


def room_faces(game):
    description = ("Na stěnách visí masky lidí, kteří se kdysi ztrapnili. Rudé tváře, zaskočené "
                   "tváře, tváře po špatném vtipu.")
    if available(game, "face"):
        description += " Uprostřed ve zlatém rámu visí tvář samotného ředitele."
    enter_room(game, "faces", description)

    options = [("look", "Prohlédnout si masky")]
    if available(game, "face"):
        options.append(("face", "Vzít ředitelovu tvář"))
    options.append(("go", "Jít jinam"))
    choice = choose(game, options)

    if choice == "look":
        say("Masky tě sledují prázdnýma očima. Jedna se pořád červená, druhá se omlouvá. "
            "Pod zlatým rámem je cedulka:")
        draw_box(["Kdo si nasadí cizí tvář, riskuje, že ztratí tu svou."], YELLOW)
    elif choice == "face":
        pick_up(game, "face")
    elif choice == "go":
        return go_somewhere(game, "faces")
    return "faces"


def take_photo(game):
    draw_art(PHOTO_ART, YELLOW)
    if pick_up(game, "photo") and not game["photo_healed"]:
        game["photo_healed"] = True
        gain_life(game, "Fotka ti připomene, kdo jsi.")


def room_office(game):
    description = "Těžký stůl, zelená lampa a kovová kartotéka se štítkem „Jen pro ředitele“."
    enter_room(game, "office", description)

    options = []
    if has(game, "face") and not game["face_worn"]:
        options.append(("wear", "Nasadit si ředitelovu tvář"))
    options.append(("files", "Otevřít kartotéku"))
    options.append(("go", "Jít jinam"))
    choice = choose(game, options)

    if choice == "wear":
        game["face_worn"] = True
        game["face_turns"] = 0
        say("Tvář přilne k obličeji jako vlhký papír. Najednou máš chuť někoho úkolovat.", MAGENTA)
    elif choice == "files":
        if not game["face_worn"]:
            say("Kartotéka si tě prohlédne a ani se nehne. Pozná, že nejsi ředitel.", GRAY)
        elif not game["files_read"]:
            game["files_read"] = True
            say("Zásuvky se poslušně vysunou. Uvnitř jsou dva spisy.")
            draw_box(["SPIS: Hlaváček, noční úředník"] +
                     wrap_lines("Ztraceno: sám sebe. Uloženo: místnost, kam padá, co už nikdo nehledá.", 56),
                     GRAY)
            draw_box(["SPIS: (tvoje jméno), noční úředník, nový"] +
                     wrap_lines("Přijat(a), protože něco ztratil(a). Do úřadu bereme jen ty, kdo něco "
                                "ztratili.", 56), GRAY)
            say("Ve spisu je přicvaknutá fotka. Jsi na ní ty, ještě jako dítě, a směješ se od ucha "
                "k uchu. Ten smích si už ani nepamatuješ.")
            take_photo(game)
        elif available(game, "photo"):
            say("Ve spisu pořád leží tvoje fotka.")
            take_photo(game)
        else:
            say("Spisy už znáš. Nic nového v nich není.", GRAY)
    elif choice == "go":
        return go_somewhere(game, "office")
    return "office"


def room_cellar(game):
    if game["head_returned"]:
        description = "Bývalý Bezhlavý sedí v koutě a spokojeně si prohlíží svět vlastníma očima."
    else:
        description = "Tma, vlhko a dupot. Bezhlavý pobíhá v kruzích a máchá rukama kolem sebe."
    enter_room(game, "cellar", description)

    options = []
    if has(game, "head"):
        options.append(("head", "Vrátit Bezhlavému jeho hlavu"))
    if game["head_returned"] and available(game, "badge"):
        options.append(("badge", "Vzít Hlaváčkovu jmenovku"))
    options.append(("go", "Jít jinam"))
    choice = choose(game, options)

    if choice == "head":
        game["inventory"].remove("head")
        game["used_items"].append("head")
        game["head_returned"] = True
        draw_art(CALM_CELLAR_ART, GREEN)
        say("Hlava radostně vypískne a s mlasknutím zapadne na krk. Bezhlavý se poprvé po letech "
            "zastaví.\n„Děkuju,“ řekne hlava, tentokrát konečně klidně. „Tohle tu nechal jeden pán, "
            "co mě šel hledat. Pak se nějak... vytratil.“")
        draw_box(["HLAVÁČEK", "noční úředník"], YELLOW, text_style=BOLD + WHITE)
        say("Podává ti zmačkanou jmenovku.")
        pick_up(game, "badge")
    elif choice == "badge":
        pick_up(game, "badge")
    elif choice == "go":
        return go_somewhere(game, "cellar")
    return "cellar"


def room_hidden(game):
    description = ("Červená nit tě vede po schodech, které nejsou na žádném plánku, až do místnosti, "
                   "kam padá všechno, co už nikdo nehledá. Dopisy bez adresy, nedokončené sny, "
                   "jedna levá ponožka za druhou. V rohu sedí pan Hlaváček. Je skoro průhledný a bledne.")
    enter_room(game, "hidden", description)

    options = []
    if has(game, "badge"):
        options.append(("badge", "Vrátit Hlaváčkovi jmenovku"))
    else:
        options.append(("talk", "Promluvit s Hlaváčkem"))
    options.append(("go", "Jít jinam"))
    choice = choose(game, options)

    if choice == "talk":
        say("„Kdo jsem?“ zašeptá Hlaváček. „Měl jsem jméno... ztratil jsem ho tam dole, kde běhá ten "
            "chudák bez hlavy.“", GRAY)
    elif choice == "badge":
        text = ("Připínáš mu jmenovku na sako. Hlaváček zhoustne, zčervená a nakonec je z něj zase "
                "celý člověk. „Hlaváček,“ přečte si nahlas a usměje se.\n")
        if has(game, "photo"):
            text += ("Když se chystáte odejít, všimneš si mezi hromadami krabice s tvým jménem. "
                     "Fotka v kapse se zahřeje. V krabici je tvůj starý smích, ten z fotky, který se "
                     "ti kdysi někam zatoulal. Bereš si ho zpátky a poprvé po dlouhé době se směješ "
                     "nahlas.\nTeprve teď chápeš, proč tě sem vzali: kdo sám něco ztratil, umí to "
                     "najít i u druhých. Ráno odcházíte dva a oba celí.")
            ending(game, 8, "Ztracený a nalezený", text, YELLOW)
        else:
            text += ("Za úsvitu spolu vycházíte z úřadu. Denní směna v deníku najde jediný nový "
                     "zápis: „Nalezeno: pan Hlaváček. Vyzvednuto.“")
            ending(game, 7, "Nalezený", text, GREEN)
    elif choice == "go":
        return go_somewhere(game, "hidden")
    return "hidden"


def run_room(game, room):
    if room == "counter":
        return room_counter(game)
    elif room == "umbrellas":
        return room_umbrellas(game)
    elif room == "time":
        return room_time(game)
    elif room == "voices":
        return room_voices(game)
    elif room == "threads":
        return room_threads(game)
    elif room == "faces":
        return room_faces(game)
    elif room == "office":
        return room_office(game)
    elif room == "cellar":
        return room_cellar(game)
    else:
        return room_hidden(game)


# --- Hra ---

def play_game():
    game = new_game()
    draw_title()
    draw_art(INTRO_ART, CYAN)
    print()
    say("Je půlnoc. Scházíš po schodech do sklepení pod starou poštou, kde sídlí Centrální úřad "
        "ztrát a nálezů. Přepážka, zvonek, zaprášený telefon a deník služeb. Nic zvláštního.\n"
        "Jenže sem nekončí jen zapomenuté klíče a deštníky. Končí tu všechno, co lidé ztratí: "
        "ztracený čas, ztracená řeč, ztracené nitě, ztracené tváře, a dokonce i ztracené hlavy.\n"
        "Tvůj předchůdce, pan Hlaváček, minulý týden beze stopy zmizel. Úřad otevírá v šest ráno. "
        "Do té doby musíš zjistit, co se mu stalo, a nedopadnout stejně.")
    print()
    rules = ["Každá akce zabere 5 minut. Směna končí v 6:00.",
             "Máš 5 kousků sebe ●●●●● a v saku 4 kapsy □□□□."]
    if msvcrt and ANIMATE:
        rules.append("Psaný text dopíšeš najednou libovolnou klávesou.")
    draw_box(rules, GRAY, text_style=WHITE)
    print()
    choice = simple_choice([("start", "Nastoupit na směnu"), ("leave", "Potichu odejít zadním východem")])
    if choice == "leave":
        ending(game, 1, "Výpověď",
               "Otáčíš se na podpatku a zadním východem mizíš do noci. Do historie úřadu se "
               "zapisuješ jako zaměstnanec s nejkratší pracovní smlouvou: pět minut.", CYAN)
        return

    room = "counter"
    while not game["over"]:
        room = run_room(game, room)
        if game["over"]:
            break
        if game["free_action"]:
            game["free_action"] = False
        else:
            spend_time(game)


def main():
    playing = True
    while playing:
        play_game()
        print()
        answer = input(paint("  Hrát znovu? (a/n) ", BOLD, CYAN)).strip().lower()
        playing = answer == "a"
    print()
    print(paint("  Díky za směnu. Dobrou noc.", BOLD, YELLOW))
    print(paint("  " + AUTHOR, GRAY))
    print()


main()
