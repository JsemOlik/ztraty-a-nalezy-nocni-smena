"""Přepážka – rozcestí celého úřadu."""

from ..actions import Action, go, heal, lose_piece
from ..state import GameState
from ..text import mirror

# Předměty, které popisuje už sama místnost.
NATIVE_ITEMS = ("umbrella", "storage_key")
TITLE = "Přepážka"

JOURNAL = """[bold]Deník služeb[/bold] – poslední zapsané stránky:

  [italic]3. 3., 23:40[/italic] – Deštníky zase nanesly déšť až ke dveřím skladu. Nikdy tam nechodit bez suchého deštníku. Ten déšť z člověka spláchne kus.
  [italic]9. 3., 01:15[/italic] – V kabinetu řečí jsem otevřel sklenici s nadávkami. Ještě teď mi zvoní v uších. Nejdřív poslouchat, pak otevírat!
  [italic]14. 3., 02:50[/italic] – Archiv. Po cizí niti nechodit. Kdo ztratí nit, musí jít po té své – a držet ji pevně v ruce.
  [italic]20. 3., 04:10[/italic] – V galerii zase někdo zkoušel masky. Cizí tvář se rychle přichytí. Nikdy ji nenosit dlouho.
  [italic]22. 3., 03:30[/italic] – Bezhlavý ve sklepě je zase neklidný. Bez jeho hlavy za ním nelézt. Kde jen ta hlava je? Ve skladu prý něco mluví.
  [italic]27. 3., 00:05[/italic] – Někdo tu zase ztratil hlavu. Jdu dolů to vyřešit.

Písmo posledního zápisu je bledší než ostatní, jako by inkoust mizel spolu s pisatelem."""

BELL_LINES = [
    "Zvuk se rozběhne chodbami a vrátí se o chvíli později, trochu jiný. Jako by si ho někdo vypůjčil.",
    "Odněkud z hloubi úřadu se ozve: „Hned jsem u vás!“ Nikdo nepřijde.",
    "Ve skladu deštníků na chvíli přestane pršet. Pak začne znovu, o to víc.",
    "Zvonek zní jako tramvaj, na kterou jsi kdysi nestihl(a) doběhnout.",
]


def phone_hint(state: GameState) -> str:
    flags = state.flags
    if "headless_calm" not in flags:
        if "umbrellas_unlocked" not in flags and not state.has("storage_key"):
            return "Klíč od skladu visí na háčku za přepážkou. A do skladu nikdy bez suchého deštníku, slyšíte?"
        if not state.has("head") and "head" in state.room_items["umbrellas"]:
            return "Ve skladu deštníků je krabice na klobouk. To, co je v ní, se ztratilo dole ve sklepě. Vezměte to s sebou."
        return "Kdo ztratil hlavu, potřebuje ji vrátit. Sklep. A nechoďte tam s prázdnýma rukama."
    if "red_hint" not in flags:
        return "Pan Hlaváček chodil za hlasy do kabinetu řečí. Sklenice si pamatují, co lidé nedořekli. Nejdřív poslouchat."
    if "hlavacek_found" not in flags:
        if "read_own_file" not in flags:
            return (
                "Ředitelna se otevře jen panu řediteli. Jeho tvář visí v galerii. Ale nenoste ji dlouho. "
                "V kartotéce je spis i na vás, víte?"
            )
        return "Kdo ztratil nit, musí jít po niti. Po té červené. A až ho najdete, připomeňte mu, kdo je. Sám si nevzpomene."
    return "Teď už víte všechno, co já. Pospěšte si, ráno je blíž, než se zdá."


def _resign(state: GameState, ui) -> None:
    state.ending = "resignation"


def _read_journal(state: GameState, ui) -> None:
    ui.say(JOURNAL)


def _phone(state: GameState, ui) -> None:
    ui.sfx("Tůůů… tůůů… cvak.")
    ui.say(
        "Zvedneš zaprášené sluchátko. Chvíli je slyšet jen šum, jako když někdo dýchá přes celé město. "
        "Pak hlas, který odněkud znáš, ale nevíš odkud:"
    )
    ui.say(f"[italic]„Ztráty a nálezy, noční linka. {phone_hint(state)}“[/italic]")
    ui.say("Cvak. Tón.")


def _bell(state: GameState, ui) -> None:
    ui.sfx("* CINK *")
    line = state.rng.choice(BELL_LINES)
    ui.say(line.replace("nestihl(a)", state.g("nestihl", "nestihla")))


def _tea(state: GameState, ui) -> None:
    if heal(
        state,
        ui,
        1,
        "Dopiješ Hlaváčkův čaj. Je studený, přeslazený a voní po heřmánku a starých novinách. "
        "Je v něm kus obyčejné noční služby a ten kus se usadí v tobě.",
    ):
        state.flags.add("tea_drunk")


def _mirror(state: GameState, ui) -> None:
    ui.say(mirror(state))


def _exit_door(state: GameState, ui) -> None:
    stolen = state.count("stolen_time")
    if stolen >= 2:
        state.ending = "time_thief"
        return
    if stolen == 1:
        ui.say(
            "Dveře se na škvírku pootevřou – v kapse ti tiká kus cizího rána. Ale jedna hrst času nestačí, "
            "aby se pro tebe rozednilo. Dveře zase zaklapnou."
        )
        return
    ui.say("Dveře ven jsou zamčené. Zevnitř je odemyká jen denní směna, v šest ráno. Na klice visí cedulka: „Kdo odchází dřív, něco tu nechává.“")


def _umbrellas(state: GameState, ui) -> None:
    if "umbrellas_unlocked" not in state.flags:
        if not state.has("storage_key"):
            ui.say("Dveře skladu deštníků jsou zamčené. Zpod nich vytéká pramínek dešťové vody.")
            return
        state.flags.add("umbrellas_unlocked")
        ui.say("Klíč se v zámku otočí ztuha, jako by zrezivěl. Dveře se otevřou a ty ucítíš vůni mokrého asfaltu.")
    state.location = "umbrellas"
    ui.sfx("Šššššššššš…")
    if state.has("umbrella"):
        ui.say("Rozevřeš suchý deštník. Déšť po něm bubnuje, ale na tebe nedopadne ani kapka.")
    else:
        lose_piece(
            state,
            ui,
            "Vkročíš do skladu bez deštníku. Na hlavu ti spustí liják – a ten déšť nesmývá jen prach. "
            "Spolu s vodou z tebe stéká kus tebe samotného.",
        )


def _office(state: GameState, ui) -> None:
    if state.face_worn:
        state.location = "office"
        ui.say("Zámek ředitelny se na tebe podívá kukátkem a cvakne. „Dobrý večer, pane řediteli,“ zavrže pant.")
    else:
        ui.say(
            "Dveře ředitelny jsou zamčené. Místo zámku mají kukátko a pod ním mosaznou ceduli: "
            "„Vstup pouze pro pana ředitele. Poznám ho po tváři.“"
        )


def _cellar(state: GameState, ui) -> None:
    state.location = "cellar"
    if "headless_calm" not in state.flags:
        ui.sfx("cup cup cup… cup… cupcupcup…")
    ui.say("Sejdeš po vrzajících schodech do sklepa. Světlo shora po pár krocích vzdá svou práci.")


def describe(state: GameState) -> str:
    parts = [
        "Centrální úřad ztrát a nálezů, sklepení pod starou poštou. Dřevěná přepážka se sklem, "
        "mosazný zvonek, zaprášený telefon a otevřený deník služeb. Zářivka bzučí, jako by si pobrukovala.",
    ]
    if "tea_drunk" not in state.flags:
        parts.append("Na přepážce stojí hrnek Hlaváčkova nedopitého čaje. Je pořád trochu vlažný.")
    if "umbrella" in state.here():
        parts.append("U vchodu stojí stojan a v něm jediný suchý deštník.")
    if "storage_key" in state.here():
        parts.append("Za přepážkou visí na háčku klíč od skladu.")
    parts.append(
        "Chodby odtud vedou do skladu deštníků, do oddělení ztraceného času, do kabinetu ztracených řečí, "
        "do archivu ztracených nití a do galerie ztracených tváří. Za rohem jsou dveře ředitelny "
        "a schody dolů do sklepa. Na stěně visí zrcadlo."
    )
    return "\n".join(parts)


def actions(state: GameState) -> list[Action]:
    result = []
    if state.minutes == 0:
        result.append(Action("resign", "Dát výpověď a jít domů", _resign))
    result += [
        Action("journal", "Přečíst deník služeb", _read_journal),
        Action("phone", "Zvednout telefon", _phone),
        Action("bell", "Zazvonit na zvonek", _bell),
    ]
    if "tea_drunk" not in state.flags:
        result.append(Action("tea", "Dopít Hlaváčkův čaj", _tea))
    result += [
        Action("mirror", "Podívat se do zrcadla", _mirror),
        Action("go_umbrellas", "Jít do skladu deštníků", _umbrellas),
        Action("go_time", "Jít do oddělení ztraceného času", go("time_dept")),
        Action("go_speech", "Jít do kabinetu ztracených řečí", go("speech")),
        Action("go_threads", "Jít do archivu ztracených nití", go("threads")),
        Action("go_faces", "Jít do galerie ztracených tváří", go("faces")),
        Action("go_office", "Zkusit dveře ředitelny", _office),
        Action("go_cellar", "Sejít do sklepa", _cellar),
        Action("exit_door", "Zkusit odejít dveřmi ven", _exit_door),
    ]
    return result
