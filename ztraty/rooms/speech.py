"""Kabinet ztracených řečí – v každé sklenici je hlas, který někomu došel uprostřed věty."""

from dataclasses import dataclass

from ..actions import Action, go, heal, lose_piece
from ..state import MAX_PIECES, GameState

TITLE = "Kabinet ztracených řečí"


@dataclass(frozen=True)
class Jar:
    id: str
    name: str
    listen: str


JARS = [
    Jar(
        "curses",
        "baňatá sklenice od kyselého zelí",
        "Uvnitř to bublá a syčí. Slyšíš útržky slov, za která by se styděl i dlaždič. "
        "Někdo tu ztratil nervy – a s nimi i slušnou řeč.",
    ),
    Jar(
        "laugh",
        "malá sklenička od dětské přesnídávky",
        "Uvnitř se něco tiše chichotá. Pak to vyprskne smíchy a zase se to stydlivě ztiší. "
        "Tohle je něčí ztracený smích. Opatrně ho sundáš z police.",
    ),
    Jar(
        "silence",
        "sklenice od hořčice se zrezivělým víčkem",
        "Nic. Úplné, husté ticho. Takové, které zůstane v místnosti, když někomu dojdou slova uprostřed věty. "
        "Z toho ticha ti naskočí husí kůže.",
    ),
    Jar(
        "whisper",
        "vysoká sklenice od švestkových povidel s cedulkou „B. H.“",
        "Šepot. Unavený, laskavý hlas: „…kdyby se mi něco stalo, jdi po červené. Jen červená vede tam, "
        "kam padá všechno, co už nikdo…“ Věta se utrhne a začne znovu od začátku.",
    ),
]


def _listen(jar: Jar):
    def handler(state: GameState, ui) -> None:
        ui.say(f"Přiložíš ucho ke sklenici ({jar.name}).")
        ui.say(jar.listen)
        if jar.id == "laugh":
            state.flags.add("jar_laugh_gone")
            if state.give_or_drop("laugh_jar"):
                ui.say("Strčíš si sklenici se ztraceným smíchem do kapsy.")
            else:
                ui.say("Kapsy máš plné, tak sklenici postavíš na zem vedle sebe.")
        if jar.id == "whisper":
            state.flags.add("red_hint")

    return handler


def _open(jar: Jar):
    def handler(state: GameState, ui) -> None:
        ui.sfx("Pšššš!")
        if jar.id == "curses":
            lose_piece(
                state,
                ui,
                "Víčko odskočí a ven vyletí hejno nadávek. Zalétnou ti do uší, do kapes i za límec. "
                "Než je nacpeš zpátky do sklenice, kus tebe se studem schová tak hluboko, že ho už nenajdeš.",
            )
        elif jar.id == "silence":
            lose_piece(
                state,
                ui,
                "Ticho se vyvalí ven jako mlha a spolkne ti hlas. Chvíli otvíráš pusu naprázdno. "
                "Když se ti řeč vrátí, není celá – a ty taky ne.",
            )
            if state.has("head"):
                ui.say("I mluvící hlava je na chvíli zticha. Poprvé za celou noc. Pak to vynahradí.")
        elif jar.id == "laugh" and state.pieces >= MAX_PIECES:
            ui.say("Pootevřeš víčko a zevnitř se ozve chichotání. Teď ti nic nechybí, tak víčko zase zašroubuješ.")
            _listen(jar)(state, ui)
        elif jar.id == "laugh":
            state.flags.add("jar_laugh_gone")
            ui.say("Odšroubuješ víčko a smích vyletí ven. Rozběhne se po kabinetu a všechny sklenice se na chvíli rozcinkají.")
            heal(state, ui, 1, "Smích se ti usadí v hrudi. Kus tebe, který chyběl, se vrátí na své místo.")
        elif jar.id == "whisper":
            state.flags.add("red_hint")
            state.flags.add("jar_whisper_gone")
            ui.say(
                "Ze sklenice vyletí hlas pana Hlaváčka, tentokrát jasně: „Kdyby se mi něco stalo, jdi po červené niti. "
                "Jen červená vede tam, kam padá všechno, co už nikdo nehledá. A vezmi mi tam, prosím, něco, "
                "podle čeho se poznám.“ Hlas zakrouží pod stropem a rozplyne se."
            )

    return handler


def _shelf(state: GameState) -> list[tuple[int, Jar]]:
    """Sklenice, které ještě stojí na polici, s jejich stálým číslem."""
    return [(number, jar) for number, jar in enumerate(JARS, start=1) if f"jar_{jar.id}_gone" not in state.flags]


def describe(state: GameState) -> str:
    parts = [
        "Kabinet ztracených řečí voní octem a starým papírem. Na policích stojí stovky zavařovacích sklenic "
        "a v každé je uzavřený hlas, který někomu došel uprostřed věty. Sklenice se jemně chvějí. "
        "Některé šeptají, některé mlčí tak hlasitě, že to bolí."
    ]
    shelf = _shelf(state)
    if shelf:
        names = "; ".join(f"{number}. {jar.name}" for number, jar in shelf)
        parts.append(f"Na nejbližší polici stojí stranou pár sklenic, jako by na tebe čekaly: {names}.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    result = []
    for number, jar in _shelf(state):
        result.append(Action(f"listen:{jar.id}", f"Přiložit ucho ke sklenici {number}", _listen(jar)))
        result.append(Action(f"open:{jar.id}", f"Otevřít sklenici {number}", _open(jar)))
    result.append(Action("back", "Vrátit se k přepážce", go("counter")))
    return result
