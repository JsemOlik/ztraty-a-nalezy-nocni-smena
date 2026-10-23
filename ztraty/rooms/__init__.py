"""Místnosti úřadu. Každý modul má TITLE, describe(state) a actions(state)."""

from . import cellar, counter, faces, hidden, office, speech, threads, time_dept, umbrellas

ROOMS = {
    "counter": counter,
    "umbrellas": umbrellas,
    "time_dept": time_dept,
    "speech": speech,
    "threads": threads,
    "faces": faces,
    "cellar": cellar,
    "office": office,
    "hidden": hidden,
}
