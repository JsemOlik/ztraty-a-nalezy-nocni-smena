"""Místnosti úřadu: co v nich hráč vidí, co může dělat a co se pak stane.

Každá místnost má:
  describe_<místnost>(state)  – text, který se ukáže v rámečku,
  options_<místnost>(state)   – volby v nabídce.
Co se stane po výběru volby, řeší funkce handle(state, key). Vrací, kolik minut akce zabrala.
"""

import random

import screen
import texts
import world

# Pořadí místností v nabídce "Jít jinam…".
ROOM_ORDER = ["counter", "umbrellas", "time_dept", "speech", "threads", "faces", "cellar", "office", "hidden"]

ROOM_TITLES = {
    "counter": "Přepážka",
    "umbrellas": "Sklad deštníků",
    "time_dept": "Oddělení ztraceného času",
    "speech": "Kabinet ztracených řečí",
    "threads": "Archiv ztracených nití",
    "faces": "Galerie ztracených tváří",
    "cellar": "Sklep",
    "office": "Ředitelna",
    "hidden": "Místnost nehledaných věcí",
}

# Předměty, které popisuje už sama místnost (nepíšou se do "Na zemi leží").
NATIVE_ITEMS = {
    "counter": ["umbrella"],
    "umbrellas": ["head"],
    "threads": ["red_thread"],
    "faces": ["director_face"],
}

CLOCKS = ["Kukačky", "Starý budík", "Věžní ciferník", "Náramkové hodinky", "Kyvadlové hodiny"]
WRONG_CLOCK_PENALTY = 15
LOST_THREAD_PENALTY = 30

JARS = {
    "laugh": "malou sklenici",
    "whisper": "sklenici s cedulkou „B. H.“",
    "curses": "baňatou sklenici od zelí",
}

WRONG_THREADS = {
    "blue": ["modré", "Modrá nit vede do cizí nedokončené přednášky o termodynamice. Bloudíš v ní celou věčnost."],
    "gold": ["zlaté", "Zlatá nit vede do něčího snu o bohatství. Cesta zpátky se pořád stáčí do kruhu."],
}


# --- Kousky sebe --------------------------------------------------------------


def lose_piece(state, text):
    state["pieces"] = state["pieces"] - 1
    screen.bad(text)
    screen.flicker("Ztrácíš kousek sebe.")
    if state["pieces"] > 0:
        screen.say(world.transparency(state))


def heal(state, amount, text):
    """Vrátí kousky sebe. Vrátí False, když hráči nic nechybí."""
    if state["pieces"] >= world.MAX_PIECES:
        screen.say(f"Teď jsi {world.g(state, 'celý', 'celá')}. Necháš si to na horší chvíli.")
        return False
    state["pieces"] = min(world.MAX_PIECES, state["pieces"] + amount)
    screen.good(text)
    return True


# --- Předměty a kapsy ---------------------------------------------------------


def wear_face(state):
    state["face_worn"] = True
    state["face_turns"] = 0
    screen.say("Přiložíš si ředitelovu tvář. Přilne sama, chladně a hladce. Najednou máš chuť někoho napomenout.")
    screen.bad("Pozor: kdo nosí cizí tvář dlouho, ztratí tu svou.")


def remove_face(state):
    state["face_worn"] = False
    state["face_turns"] = 0
    screen.say("Sloupneš ředitelovu tvář. Pod ní je tvůj vlastní obličej. Uf.")


def use_item(state, item):
    if item == "lost_hour":
        world.remove_item(state, "lost_hour")
        state["deadline"] = state["deadline"] + 60
        screen.good("Rozbalíš ztracenou hodinu. Všechny hodiny v úřadu couvnou o hodinu zpátky. Noc je delší.")
    elif item == "laugh_jar":
        if heal(state, 1, "Otevřeš sklenici a ven vyprskne smích. Hned je ti líp – kousek tebe se vrátil."):
            world.remove_item(state, "laugh_jar")
    elif item == "own_photo":
        if heal(state, 2, "Zadíváš se na fotku. Vzpomeneš si, kdo jsi. Fotka u toho vybledne do bílého papíru."):
            world.remove_item(state, "own_photo")
            world.add_flag(state, "photo_used")
    elif item == "director_face":
        wear_face(state)


def drop_item(state, item):
    """Odloží předmět na zem. Vrátí False, když to nejde."""
    if item == "director_face" and state["face_worn"]:
        screen.say("Tvář máš pořád na obličeji. Nejdřív ji sundej.")
        return False
    if item == "red_thread" and state["location"] == "hidden":
        screen.bad(f"Kdybys tu {world.g(state, 'pustil', 'pustila')} nit, už nenajdeš cestu zpátky.")
        return False
    world.remove_item(state, item)
    if item == "stolen_time":
        screen.say("Ukradený čas se ti rozsype a uteče zpátky do oddělení ztraceného času.")
        return True
    world.items_here(state).append(item)
    screen.say(f"Odložíš {world.ITEMS[item]['accusative']}.")
    if item == "head":
        screen.head("Cože? Na zem? Nenechávejte mě tu!")
    return True


def make_room(state):
    """Když jsou kapsy plné, zeptá se, co odložit. Vrátí True, pokud je místo."""
    if not world.pockets_full(state):
        return True
    options = []
    for item in world.unique(state["pockets"]):
        options.append(screen.option(f"drop:{item}", f"Odložit {world.ITEMS[item]['accusative']}", 0))
    options.append(screen.option("keep", "Nic, nechám to být", 0))
    key = screen.choose(options, "Kapsy máš plné. Co odložíš?")
    if key == "keep":
        return False
    return drop_item(state, key.split(":")[1])


def take_item(state, item):
    if not make_room(state):
        return False
    world.items_here(state).remove(item)
    world.add_item(state, item)
    if item == "head":
        screen.say("Zvedneš hlavu z krabice. Okamžitě začne mluvit: „Konečně! Hlavně mě neupusťte!“")
    else:
        screen.say(f"Vezmeš si {world.ITEMS[item]['accusative']}.")
    return True


def open_pockets(state):
    """Podnabídka: prohlédnout, použít nebo odložit věci z kapes."""
    for item in world.unique(state["pockets"]):
        screen.say(f"• {world.ITEMS[item]['name']}: {world.ITEMS[item]['description']}")
    options = []
    for item in world.unique(state["pockets"]):
        use_label = world.ITEMS[item]["use"]
        if use_label is not None and not (item == "director_face" and state["face_worn"]):
            options.append(screen.option(f"use:{item}", f"{use_label} {world.ITEMS[item]['accusative']}"))
    for item in world.unique(state["pockets"]):
        options.append(screen.option(f"drop:{item}", f"Odložit {world.ITEMS[item]['accusative']}", 0))
    options.append(screen.option("back", "Zpět", 0))
    key = screen.choose(options, "Co s tím?")
    if key.startswith("use:"):
        use_item(state, key.split(":")[1])
        return world.ACTION_MINUTES
    if key.startswith("drop:"):
        drop_item(state, key.split(":")[1])
    return 0


def item_options(state):
    """Braní předmětů ležících v místnosti a práce s kapsami."""
    options = []
    for item in world.unique(world.items_here(state)):
        # Tvář a nit se na svém místě berou vlastní akcí (nasadit tvář, jít po niti).
        special = (state["location"] == "faces" and item == "director_face") or (
            state["location"] == "threads" and item == "red_thread"
        )
        if not special:
            options.append(screen.option(f"take:{item}", f"Vzít {world.ITEMS[item]['accusative']}"))
    if state["face_worn"]:
        options.append(screen.option("remove_face", "Sundat si ředitelovu tvář"))
    if state["pockets"]:
        options.append(screen.option("pockets", "Sáhnout do kapes…", 0))
    return options


# --- Cestování ------------------------------------------------------------------


def can_travel(state):
    """Před Bezhlavým se nedá jen tak odkráčet a ze skryté místnosti se chodí po niti."""
    if state["location"] == "cellar" and not world.has_flag(state, "headless_calm"):
        return False
    if state["location"] == "hidden":
        return False
    return True


def travel(state):
    """Podnabídka "Jít jinam…". Do skryté místnosti se dá dojít jen po niti."""
    options = []
    for room in ROOM_ORDER:
        if room != state["location"] and room != "hidden":
            options.append(screen.option(f"go:{room}", ROOM_TITLES[room]))
    options.append(screen.option("go:out", "Odejít z úřadu domů"))
    options.append(screen.option("back", "Zpět", 0))
    key = screen.choose(options, "Kam půjdeš?")
    if key == "back":
        return 0
    if key == "go:out":
        return leave_building(state)
    return enter_room(state, key.split(":")[1])


def enter_room(state, room):
    if room == "umbrellas":
        state["location"] = "umbrellas"
        screen.sfx("Šššššššššš…")
        if world.has_item(state, "umbrella"):
            screen.say("Rozevřeš suchý deštník. Na tebe nedopadne ani kapka.")
        else:
            lose_piece(state, "Vejdeš bez deštníku a spustí se na tebe liják. Ten déšť z tebe smývá kus tebe samotného.")
    elif room == "office":
        if not state["face_worn"]:
            screen.say("Ředitelna je zamčená. Na dveřích je kukátko a cedule: „Jen pro pana ředitele. Poznám ho po tváři.“")
            return 0
        state["location"] = "office"
        screen.say("Kukátko si tě prohlédne a zámek cvakne: „Dobrý večer, pane řediteli.“")
    elif room == "cellar":
        state["location"] = "cellar"
        if not world.has_flag(state, "headless_calm"):
            screen.sfx("cup cup cup… cupcupcup…")
    else:
        state["location"] = room
    return world.ACTION_MINUTES


def leave_building(state):
    """Dveře ven. Zevnitř je pustí jen ten, kdo má v kapsách ráno."""
    stolen = world.count_item(state, "stolen_time")
    if stolen >= 2:
        state["ending"] = "time_thief"
        return world.ACTION_MINUTES
    if stolen == 1:
        screen.say("Dveře se na škvírku pootevřou, ale jedna hrst ukradeného času nestačí. Zase zaklapnou.")
    else:
        screen.say("Dveře ven jsou zamčené. Zevnitř je odemkne až denní směna v šest ráno.")
    return 0


# --- Popisy místností -----------------------------------------------------------


def describe_counter(state):
    parts = ["Dřevěná přepážka se zvonkem, zaprášený telefon a deník služeb. Odtud vedou chodby do všech oddělení úřadu."]
    if not world.has_flag(state, "tea_drunk"):
        parts.append("Na přepážce stojí hrnek Hlaváčkova nedopitého čaje.")
    if "umbrella" in world.items_here(state):
        parts.append("Ve stojanu u vchodu je jediný suchý deštník.")
    return "\n".join(parts)


def describe_umbrellas(state):
    parts = ["Ve skladu prší – přímo uvnitř. Každý zapomenutý deštník si s sebou přinesl své počasí."]
    if "head" in world.items_here(state):
        parts.append("Na suchém ostrůvku stojí krabice na klobouk a v ní hlava: „Haló? Je tam někdo? Mám mokrý knír!“")
    return "\n".join(parts)


def describe_time_dept(state):
    parts = ["Stovky hodin na stěnách i na zemi a každé jdou jinak. Na pultě se v miskách třpytí volné minuty. Nikdo je nehlídá."]
    if not world.has_flag(state, "lost_hour_found"):
        parts.append("Cedule: „Kdo najde hodiny, které jdou správně, tomu se odvděčí.“")
    return "\n".join(parts)


def describe_speech(state):
    return (
        "Na policích stojí zavařovací sklenice a v každé je hlas, který někomu došel uprostřed věty. "
        "Stranou stojí tři sklenice, jako by na tebe čekaly."
    )


def describe_threads(state):
    return (
        "Regály plné klubek od lidí, kteří „ztratili nit“. Tři nitě se táhnou přes podlahu a mizí ve zdi: "
        "červená, modrá a zlatá."
    )


def describe_faces(state):
    parts = ["Masky lidí, kteří se kdysi ztrapnili. Tiše rudnou a uhýbají pohledem."]
    if "director_face" in world.items_here(state):
        parts.append("V pozlaceném rámu visí tvář pana ředitele. Jako jediná se nestydí. Ředitelna by ji jistě poznala.")
    return "\n".join(parts)


def head_available(state):
    return world.has_item(state, "head") or "head" in world.items_here(state)


def describe_cellar(state):
    if world.has_flag(state, "headless_calm"):
        return "Obyčejný sklep: brambory, uhlí, rozbité kolo. Na schodu sedí Bezhlavý s hlavou na krku a poprvé po letech v klidu dýchá."
    parts = ["Ve tmě cupitají zmatené kroky. Vynoří se Bezhlavý: muž v kabátě, místo hlavy jen límec, v nekonečné panice."]
    if world.has_item(state, "head"):
        parts.append("Hlava v kapse zapiští: „To je moje tělo!“")
    elif not head_available(state):
        parts.append(f"Nemáš nic, čím bys ho {world.g(state, 'uklidnil', 'uklidnila')}.")
    return "\n".join(parts)


def describe_office(state):
    return "Mahagonový stůl, zelená lampa a křeslo s vysokým opěradlem, které na někoho čeká. V rohu stojí kartotéka."


def describe_hidden(state):
    parts = ["Místnost bez stropu. Shora sem jako sníh padají věci, které už nikdo nehledá, a všechno tu bledne."]
    if world.has_flag(state, "hlavacek_found"):
        parts.append("Pan Hlaváček stojí vedle tebe, zase barevný, a leští si jmenovku.")
    else:
        parts.append("Mezi hromadami sedí skoro průhledný muž v úředním saku. Pan Hlaváček.")
    if world.has_flag(state, "read_own_file"):
        parts.append("Někde tady je i krabice s tvým jménem.")
    return "\n".join(parts)


def describe_room(state):
    """Popis místnosti, kde hráč je, i s věcmi, které tu leží na zemi."""
    location = state["location"]
    if location == "counter":
        text = describe_counter(state)
    elif location == "umbrellas":
        text = describe_umbrellas(state)
    elif location == "time_dept":
        text = describe_time_dept(state)
    elif location == "speech":
        text = describe_speech(state)
    elif location == "threads":
        text = describe_threads(state)
    elif location == "faces":
        text = describe_faces(state)
    elif location == "cellar":
        text = describe_cellar(state)
    elif location == "office":
        text = describe_office(state)
    else:
        text = describe_hidden(state)
    native = NATIVE_ITEMS.get(location, [])
    loose = []
    for item in world.unique(world.items_here(state)):
        if item not in native:
            loose.append(world.ITEMS[item]["name"])
    if loose:
        text = text + "\nNa zemi leží: " + ", ".join(loose) + "."
    return text


# --- Volby v místnostech ----------------------------------------------------------


def options_counter(state):
    options = []
    if state["minutes"] == 0:
        options.append(screen.option("resign", "Dát výpověď a jít domů"))
    options.append(screen.option("journal", "Přečíst deník služeb"))
    if not world.has_flag(state, "tea_drunk") and state["pieces"] < world.MAX_PIECES:
        options.append(screen.option("tea", "Dopít Hlaváčkův čaj"))
    return options


def options_time_dept(state):
    options = []
    if not world.has_flag(state, "lost_hour_found"):
        options.append(screen.option("clock_puzzle", "Hledat hodiny, které jdou správně"))
    if not world.pockets_full(state):
        options.append(screen.option("steal_time", "Nacpat si kapsy ukradeným časem"))
    if world.has_item(state, "stolen_time"):
        options.append(screen.option("return_time", "Vrátit ukradený čas"))
    return options


def options_speech(state):
    options = [screen.option("listen", "Poslouchat u sklenic")]
    for jar in JARS:
        if not world.has_flag(state, f"jar_{jar}_gone"):
            options.append(screen.option(f"open:{jar}", f"Otevřít {JARS[jar]}"))
    return options


def options_threads(state):
    return [
        screen.option("follow:red", "Jít po červené niti"),
        screen.option("follow:blue", "Jít po modré niti"),
        screen.option("follow:gold", "Jít po zlaté niti"),
    ]


def options_faces(state):
    if "director_face" in world.items_here(state):
        return [screen.option("wear_face", "Nasadit si ředitelovu tvář")]
    return []


def options_cellar(state):
    if world.has_flag(state, "headless_calm"):
        return []
    if head_available(state):
        return [
            screen.option("return_head", "Vrátit Bezhlavému jeho hlavu"),
            screen.option("flee", "Vyběhnout nahoru"),
        ]
    return [
        screen.option("flee", "Utéct nahoru"),
        screen.option("stay", "Zůstat a zkusit ho uklidnit"),
    ]


def options_office(state):
    return [
        screen.option("files", "Prohledat kartotéku"),
        screen.option("chair", "Sednout si do ředitelova křesla"),
    ]


def options_hidden(state):
    options = []
    if not world.has_flag(state, "hlavacek_found"):
        if world.has_item(state, "nametag"):
            options.append(screen.option("give_nametag", "Dát mu Hlaváčkovu jmenovku"))
        else:
            options.append(screen.option("talk_hlavacek", "Promluvit s ním"))
    else:
        if world.has_flag(state, "read_own_file"):
            options.append(screen.option("search_box", "Hledat krabici se svým jménem"))
        options.append(screen.option("leave_together", "Odejít s panem Hlaváčkem"))
    options.append(screen.option("back", "Vrátit se po niti do archivu"))
    return options


def room_options(state):
    """Volby místnosti, kde hráč je, plus "Jít jinam…"."""
    location = state["location"]
    if location == "counter":
        options = options_counter(state)
    elif location == "time_dept":
        options = options_time_dept(state)
    elif location == "speech":
        options = options_speech(state)
    elif location == "threads":
        options = options_threads(state)
    elif location == "faces":
        options = options_faces(state)
    elif location == "cellar":
        options = options_cellar(state)
    elif location == "office":
        options = options_office(state)
    elif location == "hidden":
        options = options_hidden(state)
    else:
        options = []
    if can_travel(state):
        options.append(screen.option("travel", "Jít jinam…", 0))
    return options


# --- Co se stane po výběru volby --------------------------------------------------


def clock_puzzle(state):
    """Hádanka: které hodiny ukazují stejný čas jako nahoře na obrazovce?"""
    offsets = random.sample([-60, -25, -10, 10, 20, 45, 60], 3)
    times = [state["minutes"]]
    for offset in offsets:
        times.append(state["minutes"] + offset)
    faces = random.sample(CLOCKS, 4)
    options = []
    for index in range(4):
        if index == 0:
            key = "clock:right"
        else:
            key = f"clock:wrong{index}"
        options.append(screen.option(key, f"{faces[index]}: {world.fmt_time(times[index])}"))
    random.shuffle(options)
    screen.sfx("Tik. Tak. Tik. Tak.")
    screen.say("Většina hodin lže. Jen jedny ukazují přesně tvůj čas – ten nahoře na obrazovce.")
    key = screen.choose(options, "Které hodiny jdou správně?")
    if key == "clock:right":
        world.add_flag(state, "lost_hour_found")
        screen.good("Správně! Z dvířek hodin vypadne ztracená hodina. Použij ji, až bude čas docházet.")
        if not world.give_or_drop(state, "lost_hour"):
            screen.say("Kapsy máš plné, tak hodina cinkne o podlahu vedle tebe.")
        return world.ACTION_MINUTES
    screen.sfx("CRRRRR! Kuku! Kuku!")
    screen.bad("Špatné hodiny! Rozdrnčí se a ukousnou ti čtvrthodinu.")
    return world.ACTION_MINUTES + WRONG_CLOCK_PENALTY


def open_jar(state, jar):
    screen.sfx("Pšššš!")
    if jar == "curses":
        lose_piece(state, "Ven vyletí hejno nadávek a zalezou ti do uší. Kus tebe se studem schová a už ho nenajdeš.")
    elif jar == "whisper":
        world.add_flag(state, "jar_whisper_gone")
        world.add_flag(state, "red_hint")
        screen.say("Vyletí hlas pana Hlaváčka: „Kdyby se mi něco stalo, jdi po červené niti. A přines mi něco, podle čeho se poznám.“")
    elif state["pieces"] >= world.MAX_PIECES:
        world.add_flag(state, "jar_laugh_gone")
        world.give_or_drop(state, "laugh_jar")
        screen.say("Uvnitř se něco chichotá. Teď ti nic nechybí, tak si sklenici se smíchem schováš na později.")
    else:
        world.add_flag(state, "jar_laugh_gone")
        heal(state, 1, "Ven vyprskne smích a rozběhne se po kabinetu. Kousek tebe se vrátil.")


def follow_red_thread(state):
    if not world.has_item(state, "red_thread"):
        if not make_room(state):
            screen.say("Kdo jde po niti, musí ji držet. Bez volné kapsy to nepůjde.")
            return 0
        world.items_here(state).remove("red_thread")
        world.add_item(state, "red_thread")
    state["location"] = "hidden"
    screen.say("Sevřeš červenou nit a jdeš. Zeď se rozestoupí a nit tě vede chodbou, která není na žádném plánku.")
    return world.ACTION_MINUTES


def follow_wrong_thread(state, color):
    genitive = WRONG_THREADS[color][0]
    text = WRONG_THREADS[color][1]
    screen.say(f"Chytíš se {genitive} niti a jdeš za ní.")
    lose_piece(state, text)
    screen.say("Než se vymotáš zpátky do archivu, uběhne půl hodiny.")
    return world.ACTION_MINUTES + LOST_THREAD_PENALTY


def return_head(state):
    if world.has_item(state, "head"):
        world.remove_item(state, "head")
    else:
        world.items_here(state).remove("head")
    world.add_flag(state, "headless_calm")
    world.add_flag(state, "red_hint")
    screen.say("Kdo ztratil hlavu, potřebuje ji vrátit. Podáš ji Bezhlavému a hlava mu zaklapne na krk jako víčko.")
    screen.say(
        "„Děkuju,“ vydechne. „Minulý týden sem slezl pan Hlaváček. V panice jsem do něj vrazil a on… ztratil sám sebe. "
        "Spadl tam, kam padá všechno, co nikdo nehledá – po červené niti z archivu. Zůstala tu po něm jmenovka.“"
    )
    if world.give_or_drop(state, "nametag"):
        screen.good("Dostáváš Hlaváčkovu jmenovku.")
    else:
        screen.say("Kapsy máš plné, tak jmenovka cinkne o zem vedle tebe.")


def search_files(state):
    screen.say(
        "[italic]Spis: Bohumil Hlaváček. Ztratil sám sebe. Uloženo: Místnost nehledaných věcí, "
        "přístup po červené niti.[/italic]"
    )
    accepted = world.g(state, "Přijat", "Přijata")
    alone = world.g(state, "sám", "sama")
    lost = world.g(state, "ztratil", "ztratila")
    screen.say(
        f"[italic]Spis s tvým jménem: {accepted}, protože {alone} něco {lost}. "
        "Předmět ztráty: naděje. Uloženo: Místnost nehledaných věcí, krabice se jménem. Nikdo nehledá.[/italic]"
    )
    screen.say("Do úřadu berou jen lidi, kteří sami něco ztratili. Tahle práce nebyla náhoda.")
    world.add_flag(state, "red_hint")
    if not world.has_flag(state, "read_own_file"):
        world.add_flag(state, "read_own_file")
        if world.give_or_drop(state, "own_photo"):
            screen.good("Ke spisu je připnutá tvoje fotka. Vezmeš si ji – podle ní poznáš svou krabici.")
        else:
            screen.say("Ke spisu je připnutá tvoje fotka. Kapsy máš plné, tak ji necháš na stole.")


def search_box(state):
    if world.has_item(state, "own_photo"):
        state["ending"] = "lost_and_found"
        return
    if world.has_flag(state, "photo_used"):
        reason = "fotka už je jen bílý papír"
    else:
        reason = "nemáš u sebe svou fotku"
    screen.say(f"Krabic se jmény jsou tu tisíce a všechny vybledly. Tu svou bez fotky nepoznáš – a {reason}.")


def handle(state, key):
    """Provede vybranou volbu. Vrátí, kolik minut zabrala."""
    # Společné volby
    if key == "travel":
        return travel(state)
    if key == "pockets":
        return open_pockets(state)
    if key == "remove_face":
        remove_face(state)
        return world.ACTION_MINUTES
    if key.startswith("take:"):
        if take_item(state, key.split(":")[1]):
            return world.ACTION_MINUTES
        return 0

    # Přepážka
    if key == "resign":
        state["ending"] = "resignation"
    elif key == "journal":
        screen.say(texts.JOURNAL)
    elif key == "tea":
        if heal(state, 1, "Dopiješ Hlaváčkův studený čaj. Voní po heřmánku a vrátí ti kousek sebe."):
            world.add_flag(state, "tea_drunk")

    # Oddělení ztraceného času
    elif key == "clock_puzzle":
        return clock_puzzle(state)
    elif key == "steal_time":
        while world.add_item(state, "stolen_time"):
            pass
        screen.say("Cpeš si do kapes hrsti cizích minut. Kdesi ve městě někomu právě zmizelo odpoledne.")
        if world.has_item(state, "head"):
            screen.head("To není naše! Tohle někomu chybí!")
    elif key == "return_time":
        while world.has_item(state, "stolen_time"):
            world.remove_item(state, "stolen_time")
        screen.say("Vysypeš ukradený čas zpátky do misek. Někomu ve městě se vrátí kus dne.")

    # Kabinet ztracených řečí
    elif key == "listen":
        screen.say("Přikládáš ucho ke sklenicím:")
        if not world.has_flag(state, "jar_laugh_gone"):
            screen.say("• Malá sklenice: tiché chichotání. Něčí ztracený smích.")
        if not world.has_flag(state, "jar_whisper_gone"):
            screen.say("• Sklenice „B. H.“: unavený hlas šeptá „…jdi po červené niti…“")
        screen.say("• Baňatá sklenice od zelí: syčení a sprostá slova. Tu radši neotvírat.")
    elif key.startswith("open:"):
        open_jar(state, key.split(":")[1])

    # Archiv ztracených nití
    elif key == "follow:red":
        return follow_red_thread(state)
    elif key.startswith("follow:"):
        return follow_wrong_thread(state, key.split(":")[1])

    # Galerie ztracených tváří
    elif key == "wear_face":
        if not make_room(state):
            return 0
        world.items_here(state).remove("director_face")
        world.add_item(state, "director_face")
        wear_face(state)

    # Sklep
    elif key == "return_head":
        return_head(state)
    elif key == "flee":
        state["location"] = "counter"
        if head_available(state):
            screen.say("Vyběhneš zpátky nahoru k přepážce.")
        else:
            lose_piece(state, "Utíkáš. Bezhlavý tě chytí za šos a utrhne z tebe kus – ne látky, tebe.")
    elif key == "stay":
        state["ending"] = "lost_head"

    # Ředitelna
    elif key == "files":
        search_files(state)
    elif key == "chair":
        if state["face_worn"]:
            state["ending"] = "director"
        else:
            screen.say("Křeslo pod tebou nespokojeně zavrže, jako by čekalo někoho jiného.")

    # Místnost nehledaných věcí
    elif key == "talk_hlavacek":
        screen.say("„Byl jsem tu úředníkem? Nebo jsem něco, co někdo ztratil?“ Muž se dívá skrz vlastní ruce. „Kdybych aspoň věděl, jak se jmenuju…“")
    elif key == "give_nametag":
        world.remove_item(state, "nametag")
        world.add_flag(state, "hlavacek_found")
        screen.good("Podáš mu jmenovku. „Bohumil Hlaváček!“ přečte nahlas a do tváře se mu vrací barva.")
        screen.say(
            f"„Děkuju. A vy… vy jste tu taky {world.g(state, 'nebyl', 'nebyla')} jen tak náhodou, viďte? "
            "Sem berou jen ty, kdo něco ztratili.“"
        )
    elif key == "leave_together":
        state["ending"] = "found"
    elif key == "search_box":
        search_box(state)
    elif key == "back":
        state["location"] = "threads"
        screen.say("Jdeš po niti zpátky do archivu.")

    return world.ACTION_MINUTES
