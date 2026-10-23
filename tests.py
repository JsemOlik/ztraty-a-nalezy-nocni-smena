"""Testy hry. Spuštění: python3 tests.py

Každý test zahraje kus hry podle připraveného seznamu voleb a zkontroluje výsledek.
"""

import random

import art
import game
import rooms
import screen
import texts
import world

GET_HEAD = ["take:umbrella", "travel", "go:umbrellas", "take:head"]
CALM_HEADLESS = GET_HEAD + ["travel", "go:cellar", "return_head"]
READ_OWN_FILE = ["travel", "go:faces", "wear_face", "travel", "go:office", "files", "remove_face"]


def run(script, feminine=False):
    """Zahraje hru podle seznamu voleb a vrátí konečný stav."""
    random.seed(7)
    screen.start_test(script)
    state = world.new_state(feminine)
    game.play(state)
    return state


def output():
    """Všechno, co hra během testu vypsala, jako jeden text."""
    return "\n".join(screen.test_log)


# --- Konce --------------------------------------------------------------------


def test_resignation():
    state = run(["resign"])
    assert state["ending"] == "resignation"
    assert state["minutes"] == 5


def test_lost_head():
    state = run(["travel", "go:cellar", "stay"])
    assert state["ending"] == "lost_head"


def test_inventory_when_time_runs_out():
    state = run(["journal"] * (world.SHIFT_END // 5))
    assert state["ending"] == "inventory"
    assert state["minutes"] == world.SHIFT_END


def test_nobody_searches():
    state = run(["travel", "go:speech"] + ["open:curses"] * world.MAX_PIECES)
    assert state["ending"] == "nobody_searches"


def test_director_by_chair():
    state = run(["travel", "go:faces", "wear_face", "travel", "go:office", "chair"])
    assert state["ending"] == "director"


def test_director_by_wearing_too_long():
    state = run(["travel", "go:faces", "wear_face"] + ["travel", "go:time_dept", "travel", "go:speech"] * 5)
    assert state["ending"] == "director"
    assert state["pieces"] == world.MAX_PIECES - 2


def test_time_thief():
    state = run(["travel", "go:time_dept", "steal_time", "travel", "go:out"])
    assert state["ending"] == "time_thief"


def test_found():
    state = run(CALM_HEADLESS + ["travel", "go:threads", "follow:red", "give_nametag", "leave_together"])
    assert state["ending"] == "found"


def test_lost_and_found():
    script = CALM_HEADLESS + READ_OWN_FILE + [
        "travel", "go:threads", "follow:red", "drop:umbrella", "give_nametag", "search_box",
    ]
    state = run(script, feminine=True)
    assert state["ending"] == "lost_and_found"


def test_secret_needs_photo():
    script = CALM_HEADLESS + READ_OWN_FILE + [
        "travel", "go:speech", "open:curses", "pockets", "use:own_photo",
        "travel", "go:threads", "follow:red", "give_nametag", "search_box", "quit",
    ]
    state = run(script)
    assert state["ending"] == "quit"
    assert "bílý papír" in output()


# --- Mechaniky ----------------------------------------------------------------


def test_menus_stay_short():
    for location in rooms.ROOM_ORDER:
        state = world.new_state(False)
        state["location"] = location
        state["pockets"] = ["umbrella", "head"]
        options = rooms.room_options(state) + rooms.item_options(state)
        assert len(options) <= 6, location


def test_objective_guides_player():
    run(GET_HEAD + ["quit"])
    assert "Úkol: Kdo ztratil hlavu" in output()


def test_rain_costs_a_piece_without_umbrella():
    state = run(["travel", "go:umbrellas", "quit"])
    assert state["pieces"] == world.MAX_PIECES - 1


def test_umbrella_protects():
    state = run(["take:umbrella", "travel", "go:umbrellas", "quit"])
    assert state["pieces"] == world.MAX_PIECES


def test_full_pockets_ask_what_to_drop():
    state = run(["take:umbrella", "travel", "go:time_dept", "steal_time",
                 "travel", "go:umbrellas", "take:head", "drop:umbrella", "quit"])
    assert "head" in state["pockets"]
    assert "umbrella" in state["room_items"]["umbrellas"]


def test_full_pockets_can_keep_everything():
    state = run(["take:umbrella", "travel", "go:time_dept", "steal_time",
                 "travel", "go:umbrellas", "take:head", "keep", "quit"])
    assert "head" not in state["pockets"]


def test_tea_heals():
    state = run(["travel", "go:speech", "open:curses", "travel", "go:counter", "tea", "quit"])
    assert state["pieces"] == world.MAX_PIECES


def test_clock_puzzle_and_lost_hour():
    state = run(["travel", "go:time_dept", "clock_puzzle", "clock:right", "pockets", "use:lost_hour", "quit"])
    assert state["deadline"] == world.SHIFT_END + 60


def test_wrong_clock_costs_time():
    state = run(["travel", "go:time_dept", "clock_puzzle", "clock:wrong1", "quit"])
    assert state["minutes"] == 5 + 5 + 15


def test_lost_hour_saves_at_deadline():
    screen.start_test([])
    state = world.new_state(False)
    state["minutes"] = world.SHIFT_END - 5
    state["pockets"] = ["lost_hour"]
    game.pass_time(state, 5)
    assert state["ending"] is None
    assert state["deadline"] == world.SHIFT_END + 60


def test_wrong_thread():
    state = run(["travel", "go:threads", "follow:blue", "quit"])
    assert state["pieces"] == world.MAX_PIECES - 1
    assert state["minutes"] == 5 + 35


def test_following_red_thread_takes_it():
    state = run(["travel", "go:threads", "follow:red", "quit"])
    assert state["location"] == "hidden"
    assert "red_thread" in state["pockets"]


def test_fleeing_headless_costs_piece():
    state = run(["travel", "go:cellar", "flee", "quit"])
    assert state["pieces"] == world.MAX_PIECES - 1
    assert state["location"] == "counter"


def test_office_locked_without_face():
    state = run(["travel", "go:office", "quit"])
    assert state["location"] == "counter"
    assert state["minutes"] == 0


def test_every_room_and_ending_has_art():
    for room in rooms.ROOM_ORDER:
        assert room in art.ROOMS, room
    for ending in texts.ENDINGS:
        assert ending in art.ENDINGS, ending


def test_head_comments_from_pocket():
    run(GET_HEAD + ["travel", "go:counter", "quit"])
    assert "Hlava: " in output()


# Spustí všechny testy výše a vypíše, jak dopadly.
ALL_TESTS = [
    test_resignation,
    test_lost_head,
    test_inventory_when_time_runs_out,
    test_nobody_searches,
    test_director_by_chair,
    test_director_by_wearing_too_long,
    test_time_thief,
    test_found,
    test_lost_and_found,
    test_secret_needs_photo,
    test_menus_stay_short,
    test_objective_guides_player,
    test_rain_costs_a_piece_without_umbrella,
    test_umbrella_protects,
    test_full_pockets_ask_what_to_drop,
    test_full_pockets_can_keep_everything,
    test_tea_heals,
    test_clock_puzzle_and_lost_hour,
    test_wrong_clock_costs_time,
    test_lost_hour_saves_at_deadline,
    test_wrong_thread,
    test_following_red_thread_takes_it,
    test_fleeing_headless_costs_piece,
    test_office_locked_without_face,
    test_every_room_and_ending_has_art,
    test_head_comments_from_pocket,
]

failed = 0
for test in ALL_TESTS:
    try:
        test()
        print(f"OK      {test.__name__}")
    except AssertionError as error:
        failed = failed + 1
        print(f"CHYBA   {test.__name__}: {error}")
print()
if failed == 0:
    print(f"Všech {len(ALL_TESTS)} testů prošlo.")
else:
    print(f"{failed} z {len(ALL_TESTS)} testů selhalo.")
