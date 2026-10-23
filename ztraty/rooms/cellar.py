"""Sklep – ve tmě tu pobíhá Bezhlavý."""

from ..actions import Action, lose_piece
from ..state import GameState

TITLE = "Sklep"


def _head_available(state: GameState) -> bool:
    return state.has("head") or "head" in state.here()


def _return_head(state: GameState, ui) -> None:
    if state.has("head"):
        state.remove_item("head")
    else:
        state.here().remove("head")
    state.flags.add("headless_calm")
    ui.say(
        "Kdo ztratil hlavu, potřebuje ji vrátit. Natáhneš ruce s hlavou do tmy. Bezhlavý se zarazí, "
        "zatápe prsty po jejím kníru – a pak si ji nasadí. Hlava zaklapne na krk jako víčko na zavařovací sklenici."
    )
    ui.say(
        "Dlouhé ticho. Pak hluboký, rozechvělý výdech. „Děkuju,“ řekne hlava, tentokrát svým tělem. "
        "„Já… já jsem v panice utíkal tmou, celé roky. Minulý týden sem slezl pan Hlaváček, chtěl mi pomoct. "
        "A já do něj v tom zmatku vrazil. On se tak nějak… rozsypal. Nevěděl najednou, kdo je. "
        "Zůstala tu po něm jen tahle jmenovka.“"
    )
    if state.give_or_drop("nametag"):
        ui.good("Dostáváš Hlaváčkovu jmenovku.")
    else:
        ui.say("Kapsy máš plné, a tak Hlaváčkova jmenovka cinkne o zem vedle tebe.")


def _flee(state: GameState, ui) -> None:
    state.location = "counter"
    if "headless_calm" in state.flags or _head_available(state):
        ui.say("Vyběhneš po schodech zpátky k přepážce.")
        if state.has("head"):
            ui.head("Proč utíkáme? Teda, utíkejme! Ale proč?!")
        return
    lose_piece(
        state,
        ui,
        "Otočíš se a utíkáš. Bezhlavý se za tebou žene, tápe, chytá tě za šos saka – a utrhne z tebe kus. "
        "Ne látky. Tebe. Vyklopýtáš nahoru k přepážce.",
    )


def _stay(state: GameState, ui) -> None:
    state.ending = "lost_head"


def _talk(state: GameState, ui) -> None:
    ui.say(
        "„Pan Hlaváček ztratil sám sebe,“ říká hlava a pořád si na krku zkouší, kam se dá otočit. "
        "„Takové věci nepadají sem do sklepa. Padají do místnosti, kam padá všechno, co už nikdo nehledá. "
        "Cesta tam vede po niti. Po červené, říkal vždycky. A kdo ztratil sám sebe, potřebuje si připomenout, "
        "kdo je. Dejte mu tu jmenovku.“"
    )
    state.flags.add("red_hint")


def describe(state: GameState) -> str:
    if "headless_calm" in state.flags:
        return (
            "Sklep je najednou jen obyčejný sklep: brambory, uhlí, rozbité kolo, sudy s nápisem „Nalezeno 1953“. "
            "Na schodu sedí Bezhlavý – teď už vlastně Hlavatý – a poprvé po letech v klidu dýchá. "
            "Občas si přejede dlaní po kníru, jako by se ujišťoval, že je pořád na místě."
        )
    parts = [
        "Schody končí ve vlhké tmě. Někde vpředu cupitají kroky – rychlé, zmatené, narážející do stěn. "
        "Pak se zastaví. A rozběhnou se tvým směrem.",
        "Z temnoty se vynoří Bezhlavý: vysoký muž v dlouhém kabátě, ruce rozhozené, místo hlavy jen "
        "naškrobený límec. Mává pažemi, tápe kolem sebe a celým tělem křičí, i když nemá čím.",
    ]
    if state.has("head"):
        parts.append("Mluvící hlava v tvé kapse ztuhne a pak zapiští: „To… to je moje tělo! Moje TĚLO!“")
    elif _head_available(state):
        parts.append("Hlava na zemi vedle tebe ječí: „To je moje tělo! Zvedněte mě! Podejte mě mu!“")
    else:
        parts.append(f"Nemáš nic, čím bys ho {state.g('uklidnil', 'uklidnila')}. Uvědomíš si, že sem jsi {state.g('přišel nepřipravený', 'přišla nepřipravená')}.")
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    if "headless_calm" in state.flags:
        return [
            Action("talk_headless", "Promluvit si s Bezhlavým", _talk),
            Action("back", "Vyjít nahoru k přepážce", _flee),
        ]
    if _head_available(state):
        return [
            Action("return_head", "Vrátit Bezhlavému jeho hlavu", _return_head),
            Action("back", "Vyběhnout zpátky nahoru", _flee),
        ]
    return [
        Action("back", "Utéct nahoru", _flee),
        Action("stay", "Zůstat a pokusit se ho uklidnit", _stay),
    ]
