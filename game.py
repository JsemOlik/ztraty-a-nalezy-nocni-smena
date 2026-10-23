"""Hlavní smyčka hry: ukaž místnost, nech hráče vybrat, proveď volbu, posuň čas."""

import sys

import art
import rooms
import screen
import texts
import world

FACE_DAMAGE_TURNS = [4, 7]
FACE_LIMIT = 10
TIME_WARNINGS = {
    60: "Odbila pátá. Do příchodu denní směny zbývá hodina.",
    30: "Obloha šedne. Zbývá půl hodiny.",
    15: "Venku zpívají ptáci. Zbývá čtvrthodina!",
}


def meta_options():
    """Volby, které fungují pořád: nápověda, rychlost textu a konec."""
    return [
        screen.option("help", "nápověda", 0, "n"),
        screen.option("speed", f"rychlost textu ({screen.settings['speed']})", 0, "r"),
        screen.option("quit", "konec", 0, "k"),
    ]


def face_tick(state):
    """Ředitelova tvář přirůstá s každou akcí, kterou ji hráč nosí."""
    state["face_turns"] = state["face_turns"] + 1
    if state["face_turns"] >= FACE_LIMIT:
        state["ending"] = "director"
    elif state["face_turns"] in FACE_DAMAGE_TURNS:
        rooms.lose_piece(state, "Ředitelova tvář ti přirůstá k lícím. Tvoje vlastní tvář pod ní bledne.")
    elif state["face_turns"] == FACE_DAMAGE_TURNS[-1] + 1:
        screen.bad("Okraje tváře už skoro nenahmatáš. Sundej ji, dokud to jde!")


def pass_time(state, minutes):
    """Posune čas a vyhodnotí vše, co se děje mezi akcemi."""
    left_before = state["deadline"] - state["minutes"]
    state["minutes"] = state["minutes"] + minutes
    if state["face_worn"]:
        face_tick(state)
    if state["ending"] is not None:
        return
    if state["pieces"] <= 0:
        state["ending"] = "nobody_searches"
        return
    left = state["deadline"] - state["minutes"]
    if left <= 0:
        if not world.has_item(state, "lost_hour"):
            state["ending"] = "inventory"
            return
        # Ztracená hodina v kapse hráče zachrání.
        world.remove_item(state, "lost_hour")
        state["deadline"] = state["deadline"] + 60
        left = state["deadline"] - state["minutes"]
        left_before = left + minutes
        screen.good("Odbíjí šestá, když ti v kapse praskne ztracená hodina. Všechny hodiny couvnou o hodinu zpátky!")
    for threshold in TIME_WARNINGS:
        if left_before > threshold >= left:
            screen.sfx("Bim… bam…")
            screen.bad(TIME_WARNINGS[threshold])
    if world.has_item(state, "head"):
        screen.head(texts.head_comment(state))


def show_ending(state):
    if state["ending"] == "quit":
        return
    ending = state["ending"]
    number = texts.ENDINGS[ending][0]
    title = world.g(state, texts.ENDINGS[ending][1], texts.ENDINGS[ending][2])
    footer = f"Čas: {world.fmt_time(state['minutes'])} · Kousky sebe: {max(state['pieces'], 0)}/5"
    screen.ending(number, title, texts.ending_text(state, ending), footer, art.ENDINGS[ending])


def play(state):
    """Hraje jednu směnu, dokud nenastane nějaký konec."""
    while state["ending"] is None:
        location = state["location"]
        screen.set_scene(
            state,
            rooms.ROOM_TITLES[location],
            rooms.describe_room(state),
            art.ROOMS[location],
            texts.objective(state),
        )
        options = rooms.room_options(state) + rooms.item_options(state) + meta_options()
        key = screen.choose(options)
        if key == "help":
            screen.say(texts.HELP)
            minutes = 0
        elif key == "speed":
            screen.say(f"Rychlost textu: {screen.cycle_speed()}.")
            minutes = 0
        elif key == "quit":
            state["ending"] = "quit"
            minutes = 0
        else:
            minutes = rooms.handle(state, key)
        if state["ending"] is not None:
            state["minutes"] = state["minutes"] + minutes
        elif minutes > 0:
            pass_time(state, minutes)
    show_ending(state)
    return state


def new_game():
    screen.title_screen()
    key = screen.choose(
        [
            screen.option("male", "Nastupuji jako noční úředník", 0),
            screen.option("female", "Nastupuji jako noční úřednice", 0),
        ],
        "Kdo nastupuje na směnu?",
    )
    state = world.new_state(key == "female")
    screen.page("Noční směna", texts.intro(state))
    screen.pause()
    return state


def main():
    # Rychlost textu se dá nastavit při spuštění: python3 main.py --rychle / --bez-animaci
    speed = "normální"
    if "--rychle" in sys.argv:
        speed = "rychlá"
    if "--bez-animaci" in sys.argv:
        speed = "vypnutá"
    screen.setup(speed)
    screen.open_screen()
    try:
        while True:
            state = play(new_game())
            if state["ending"] == "quit":
                break
            key = screen.choose(
                [
                    screen.option("again", "Nastoupit na další směnu", 0),
                    screen.option("end", "Jít domů", 0),
                ],
                "A teď?",
            )
            if key == "end":
                break
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        screen.close_screen()
    screen.farewell("Díky za noční směnu. Na shledanou!")
