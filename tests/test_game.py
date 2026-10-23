import random
import unittest

from ztraty import art
from ztraty.actions import item_actions
from ztraty.endings import ENDINGS
from ztraty.game import pass_time, play
from ztraty.rooms import ROOMS, room_actions
from ztraty.state import MAX_PIECES, SHIFT_END, GameState
from ztraty.ui import ScriptedUI

GET_HEAD = ["take:umbrella", "travel", "go:umbrellas", "take:head"]
CALM_HEADLESS = GET_HEAD + ["travel", "go:cellar", "return_head"]
READ_OWN_FILE = ["travel", "go:faces", "wear_face", "travel", "go:office", "files", "remove_face"]


def run(script, **state_kwargs):
    ui = ScriptedUI(script)
    state = play(ui, GameState(rng=random.Random(7), **state_kwargs))
    return state, ui


class EndingTests(unittest.TestCase):
    def test_resignation(self):
        state, _ = run(["resign"])
        self.assertEqual(state.ending, "resignation")
        self.assertEqual(state.minutes, 5)

    def test_lost_head(self):
        state, _ = run(["travel", "go:cellar", "stay"])
        self.assertEqual(state.ending, "lost_head")

    def test_inventory_when_time_runs_out(self):
        state, _ = run(["journal"] * (SHIFT_END // 5))
        self.assertEqual(state.ending, "inventory")
        self.assertEqual(state.minutes, SHIFT_END)

    def test_nobody_searches(self):
        state, _ = run(["travel", "go:speech"] + ["open:curses"] * MAX_PIECES)
        self.assertEqual(state.ending, "nobody_searches")

    def test_director_by_chair(self):
        state, _ = run(["travel", "go:faces", "wear_face", "travel", "go:office", "chair"])
        self.assertEqual(state.ending, "director")

    def test_director_by_wearing_too_long(self):
        state, _ = run(["travel", "go:faces", "wear_face"] + ["travel", "go:time_dept", "travel", "go:speech"] * 5)
        self.assertEqual(state.ending, "director")
        self.assertEqual(state.pieces, MAX_PIECES - 2)

    def test_time_thief(self):
        state, _ = run(["travel", "go:time_dept", "steal_time", "travel", "go:out"])
        self.assertEqual(state.ending, "time_thief")

    def test_found(self):
        state, _ = run(CALM_HEADLESS + ["travel", "go:threads", "follow:red", "give_nametag", "leave_together"])
        self.assertEqual(state.ending, "found")

    def test_lost_and_found(self):
        script = CALM_HEADLESS + READ_OWN_FILE + [
            "travel", "go:threads", "follow:red", "drop:umbrella", "give_nametag", "search_box",
        ]
        state, _ = run(script, feminine=True)
        self.assertEqual(state.ending, "lost_and_found")

    def test_secret_needs_photo(self):
        script = CALM_HEADLESS + READ_OWN_FILE + [
            "travel", "go:speech", "open:curses", "pockets", "use:own_photo",
            "travel", "go:threads", "follow:red", "give_nametag", "search_box", "quit",
        ]
        state, ui = run(script)
        self.assertEqual(state.ending, "quit")
        self.assertIn("bílý papír", ui.text())


class MechanicTests(unittest.TestCase):
    def test_menus_stay_short(self):
        states = [GameState()] + [GameState(location=location, pockets=["umbrella", "head"]) for location in ROOMS]
        for state in states:
            numbered = room_actions(state) + item_actions(state)
            self.assertLessEqual(len(numbered), 6, state.location)

    def test_objective_guides_player(self):
        _, ui = run(GET_HEAD + ["quit"])
        self.assertIn("Úkol: Kdo ztratil hlavu", ui.text())

    def test_rain_costs_a_piece_without_umbrella(self):
        state, _ = run(["travel", "go:umbrellas", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES - 1)

    def test_umbrella_protects(self):
        state, _ = run(["take:umbrella", "travel", "go:umbrellas", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES)

    def test_full_pockets_ask_what_to_drop(self):
        state, _ = run(["take:umbrella", "travel", "go:time_dept", "steal_time",
                        "travel", "go:umbrellas", "take:head", "drop:umbrella", "quit"])
        self.assertIn("head", state.pockets)
        self.assertIn("umbrella", state.room_items["umbrellas"])

    def test_full_pockets_can_keep_everything(self):
        state, _ = run(["take:umbrella", "travel", "go:time_dept", "steal_time",
                        "travel", "go:umbrellas", "take:head", "keep", "quit"])
        self.assertNotIn("head", state.pockets)

    def test_tea_heals(self):
        state, _ = run(["travel", "go:speech", "open:curses", "travel", "go:counter", "tea", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES)

    def test_clock_puzzle_and_lost_hour(self):
        state, _ = run(["travel", "go:time_dept", "clock_puzzle", "clock:right", "pockets", "use:lost_hour", "quit"])
        self.assertEqual(state.deadline, SHIFT_END + 60)

    def test_wrong_clock_costs_time(self):
        state, _ = run(["travel", "go:time_dept", "clock_puzzle", "clock:wrong1", "quit"])
        self.assertEqual(state.minutes, 5 + 5 + 15)

    def test_lost_hour_saves_at_deadline(self):
        ui = ScriptedUI([])
        state = GameState(rng=random.Random(1), minutes=SHIFT_END - 5, pockets=["lost_hour"])
        pass_time(state, ui, 5)
        self.assertIsNone(state.ending)
        self.assertEqual(state.deadline, SHIFT_END + 60)

    def test_wrong_thread(self):
        state, _ = run(["travel", "go:threads", "follow:blue", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES - 1)
        self.assertEqual(state.minutes, 5 + 35)

    def test_following_red_thread_takes_it(self):
        state, _ = run(["travel", "go:threads", "follow:red", "quit"])
        self.assertEqual(state.location, "hidden")
        self.assertIn("red_thread", state.pockets)

    def test_fleeing_headless_costs_piece(self):
        state, _ = run(["travel", "go:cellar", "flee", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES - 1)
        self.assertEqual(state.location, "counter")

    def test_office_locked_without_face(self):
        state, _ = run(["travel", "go:office", "quit"])
        self.assertEqual(state.location, "counter")
        self.assertEqual(state.minutes, 0)

    def test_every_room_and_ending_has_art(self):
        self.assertEqual(set(art.ROOMS), set(ROOMS))
        self.assertEqual(set(art.ENDINGS), set(ENDINGS))

    def test_head_comments_from_pocket(self):
        _, ui = run(GET_HEAD + ["travel", "go:counter", "quit"])
        self.assertIn("Hlava: ", ui.text())


if __name__ == "__main__":
    unittest.main()
