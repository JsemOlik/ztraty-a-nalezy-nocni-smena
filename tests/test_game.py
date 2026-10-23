import random
import unittest

from ztraty.game import pass_time, play
from ztraty.state import MAX_PIECES, SHIFT_END, GameState
from ztraty.ui import ScriptedUI

GET_HEAD = ["take:umbrella", "take:storage_key", "go_umbrellas", "take:head", "back"]
CALM_HEADLESS = GET_HEAD + ["go_cellar", "return_head", "back"]
READ_OWN_FILE = ["go_faces", "take:director_face", "back", "pockets", "use:director_face",
                 "go_office", "own_file", "remove_face", "pockets", "drop:director_face", "back"]
TO_HIDDEN = ["go_threads", "take:red_thread", "follow:red"]


def run(script, **state_kwargs):
    ui = ScriptedUI(script)
    state = play(ui, GameState(rng=random.Random(7), **state_kwargs))
    return state, ui


class EndingTests(unittest.TestCase):
    def test_resignation(self):
        state, _ = run(["resign"])
        self.assertEqual(state.ending, "resignation")
        self.assertEqual(state.minutes, 5)

    def test_resign_only_at_start(self):
        state, ui = run(["journal", "quit"])
        self.assertEqual(state.ending, "quit")
        self.assertNotIn("resign", ui.text())

    def test_lost_head(self):
        state, _ = run(["go_cellar", "stay"])
        self.assertEqual(state.ending, "lost_head")

    def test_inventory_when_time_runs_out(self):
        state, _ = run(["bell"] * (SHIFT_END // 5))
        self.assertEqual(state.ending, "inventory")
        self.assertEqual(state.minutes, SHIFT_END)

    def test_nobody_searches(self):
        state, _ = run(["go_speech"] + ["open:curses"] * MAX_PIECES)
        self.assertEqual(state.ending, "nobody_searches")

    def test_director_by_chair(self):
        state, _ = run(["go_faces", "take:director_face", "pockets", "use:director_face",
                        "back", "go_office", "chair"])
        self.assertEqual(state.ending, "director")

    def test_director_by_wearing_too_long(self):
        state, _ = run(["go_faces", "take:director_face", "pockets", "use:director_face"] + ["look_masks"] * 10)
        self.assertEqual(state.ending, "director")
        self.assertEqual(state.pieces, MAX_PIECES - 2)

    def test_time_thief(self):
        state, _ = run(["go_time", "steal_time", "back", "exit_door"])
        self.assertEqual(state.ending, "time_thief")

    def test_found(self):
        state, _ = run(CALM_HEADLESS + TO_HIDDEN + ["give_nametag", "leave_together"])
        self.assertEqual(state.ending, "found")

    def test_lost_and_found(self):
        script = (
            ["take:umbrella", "take:storage_key", "go_umbrellas", "pockets", "drop:storage_key",
             "take:head", "back", "pockets", "drop:umbrella", "go_cellar", "return_head", "back"]
            + READ_OWN_FILE + TO_HIDDEN + ["give_nametag", "search_box"]
        )
        state, _ = run(script, feminine=True)
        self.assertEqual(state.ending, "lost_and_found")

    def test_secret_needs_photo(self):
        script = CALM_HEADLESS + ["pockets", "drop:storage_key", "pockets", "drop:umbrella"] + READ_OWN_FILE
        script += ["go_speech", "open:curses", "back", "pockets", "use:own_photo"]
        script += TO_HIDDEN + ["give_nametag", "search_box", "quit"]
        state, ui = run(script)
        self.assertEqual(state.ending, "quit")
        self.assertIn("bílý papír", ui.text())


class MechanicTests(unittest.TestCase):
    def test_rain_costs_a_piece_without_umbrella(self):
        state, _ = run(["take:storage_key", "go_umbrellas", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES - 1)

    def test_umbrella_protects(self):
        state, _ = run(["take:storage_key", "take:umbrella", "go_umbrellas", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES)

    def test_pockets_limit(self):
        state, ui = run(GET_HEAD + ["go_threads", "take:red_thread", "back",
                                    "go_faces", "take:director_face", "quit"])
        self.assertEqual(len(state.pockets), 4)
        self.assertIn("director_face", state.room_items["faces"])
        self.assertIn("Kapsy saka máš plné", ui.text())

    def test_heal_is_capped(self):
        state, _ = run(["tea", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES)
        self.assertNotIn("tea_drunk", state.flags)

    def test_tea_heals(self):
        state, _ = run(["go_speech", "open:curses", "back", "tea", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES)

    def test_clock_puzzle_and_lost_hour(self):
        state, _ = run(["go_time", "clock_puzzle", "clock:right", "pockets", "use:lost_hour", "quit"])
        self.assertEqual(state.deadline, SHIFT_END + 60)

    def test_wrong_clock_costs_time(self):
        state, _ = run(["go_time", "clock_puzzle", "clock:wrong1", "quit"])
        self.assertEqual(state.minutes, 5 + 5 + 15)

    def test_lost_hour_saves_at_deadline(self):
        ui = ScriptedUI([])
        state = GameState(rng=random.Random(1), minutes=SHIFT_END - 5, pockets=["lost_hour"])
        pass_time(state, ui, 5)
        self.assertIsNone(state.ending)
        self.assertEqual(state.deadline, SHIFT_END + 60)

    def test_wrong_thread(self):
        state, _ = run(["go_threads", "follow:blue", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES - 1)
        self.assertEqual(state.minutes, 5 + 35)

    def test_red_thread_needs_holding(self):
        state, _ = run(["go_threads", "follow:red", "quit"])
        self.assertEqual(state.location, "threads")

    def test_fleeing_headless_costs_piece(self):
        state, _ = run(["go_cellar", "back", "quit"])
        self.assertEqual(state.pieces, MAX_PIECES - 1)
        self.assertEqual(state.location, "counter")

    def test_office_locked_without_face(self):
        state, _ = run(["go_office", "quit"])
        self.assertEqual(state.location, "counter")

    def test_head_comments_from_pocket(self):
        _, ui = run(GET_HEAD + ["bell", "quit"])
        self.assertIn("Hlava: ", ui.text())


if __name__ == "__main__":
    unittest.main()
