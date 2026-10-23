"""Delší texty hry: úvod, nápověda, deník, konce, komentáře hlavy a úkol nahoře."""

import random

import world

HELP = """[bold]Jak se hraje[/bold]
• Napiš číslo volby a Enter. Každá akce zabere [bold]5 minut[/bold] (šedé volby nic nestojí).
• Nahoře je vždy [bold]Úkol[/bold] – co dělat dál.
• [bold]Kousky sebe[/bold] ●●●●●: chybami průhledníš. O všechny nepřijď.
• Do kapes se vejdou [bold]4 věci[/bold].
• Rčení tu platí doslova: kdo ztratil hlavu, musí ji dostat zpátky. Kdo ztratil nit, jde po niti."""

JOURNAL = """[bold]Deník služeb[/bold]
  [italic]3. 3.[/italic] Do skladu deštníků nikdy bez suchého deštníku. Ten déšť z člověka spláchne kus.
  [italic]9. 3.[/italic] Sklenice v kabinetu řečí: nejdřív poslouchat, pak otevírat!
  [italic]20. 3.[/italic] Cizí tvář se rychle přichytí. Nikdy ji nenosit dlouho.
  [italic]27. 3.[/italic] Někdo tu zase ztratil hlavu. Jdu dolů to vyřešit."""


def intro(state):
    return (
        f"Je půlnoc. Nastupuješ jako {world.g(state, 'noční úředník', 'noční úřednice')} do úřadu ztrát a nálezů "
        "pod starou poštou. Končí tu všechno, co lidé ztratí – deštníky, ale i čas, řeč nebo hlava.\n\n"
        "Tvůj předchůdce, pan Hlaváček, zmizel. Jeho poslední zápis v deníku: "
        "[italic]„Někdo tu zase ztratil hlavu. Jdu dolů to vyřešit.“[/italic]\n\n"
        "[bold yellow]Cíl: najdi pana Hlaváčka do šesti ráno.[/bold yellow]\n\n"
        + HELP
    )


# --- Úkol nahoře na obrazovce ------------------------------------------------


def objective(state):
    """Co má hráč dělat dál."""
    if state["face_worn"]:
        if not world.has_flag(state, "read_own_file"):
            return "Rychle do ředitelny a prohledej kartotéku. Pak si tvář sundej!"
        return "Sundej si ředitelovu tvář, než ti přiroste."
    if not world.has_flag(state, "headless_calm"):
        if world.has_item(state, "head") or "head" in state["room_items"]["cellar"]:
            return "Kdo ztratil hlavu, potřebuje ji vrátit. Odnes hlavu Bezhlavému do sklepa."
        if "head" not in state["room_items"]["umbrellas"]:
            return f"Vrať se pro hlavu, kterou jsi {world.g(state, 'odložil', 'odložila')}, a odnes ji do sklepa."
        if not world.has_item(state, "umbrella"):
            return "Ve skladu deštníků něco mluví. Vezmi si suchý deštník, ať tam nezmokneš."
        return "Ve skladu deštníků něco mluví. Dojdi se podívat."
    if not world.has_flag(state, "hlavacek_found"):
        if state["location"] == "hidden" and world.has_item(state, "nametag"):
            return "Kdo ztratil sám sebe, potřebuje si připomenout, kdo je. Dej Hlaváčkovi jmenovku."
        if not world.has_item(state, "nametag"):
            return "Seber Hlaváčkovu jmenovku ve sklepě a jdi po červené niti z archivu."
        return "Jdi v archivu po červené niti a dej Hlaváčkovi jeho jmenovku."
    if not world.has_flag(state, "read_own_file"):
        return f"Odejdi s Hlaváčkem – nebo nejdřív zjisti v ředitelně, proč jsi tu práci {world.g(state, 'dostal', 'dostala')}."
    if not world.has_item(state, "own_photo"):
        return "Odejdi s Hlaváčkem. Svou krabici bez vlastní fotky nepoznáš."
    return "Najdi krabici se svým jménem – nebo prostě odejdi s Hlaváčkem."


# --- Mluvící hlava ------------------------------------------------------------

HEAD_GENERAL = [
    "Kam jdeme? Proč jdeme? Nemůžeme prostě zůstat? Nebo utéct? Hlavně ne zůstat!",
    "Je tu průvan. Cítím průvan na krku. Teda tam, kde jsem míval krk.",
    "Neupusťte mě. Říkal jsem to už? Neupusťte mě.",
    "Slyšel jste to? Já jsem něco slyšel. Teda, slyšela jste… slyšeli jste? Bojím se.",
    "V téhle kapse je drobek. Proč je v kapse drobek? Já mám alergii na drobky!",
    "Kdybych měl ruce, kousal bych si nehty. Takhle si kousám knír.",
    "Já jsem kdysi někomu patřil. Myslím. Byl to někdo vysoký. Nebo jsem byl já vysoký?",
]

HEAD_BY_LOCATION = {
    "counter": [
        "Ten čaj na přepážce. Pan Hlaváček ho nikdy nedopil. To je špatné znamení, že?",
        "Pan Hlaváček tu sedával a luštil křížovky. Pak šel dolů. Dolů se nechodí!",
    ],
    "umbrellas": [
        "Prší mi do ucha! Do UCHA!",
        "Tady jsem seděl tři roky v krabici na klobouk. Tři roky! Ve vlhku! Víte, co to dělá s knírem?",
    ],
    "time_dept": [
        "To tikání! Každé hodiny tikají jinak a já nevím, které poslouchat!",
        "Kolik je hodin? Ne, neříkejte mi to. Ano, řekněte mi to! Ne!",
    ],
    "speech": [
        "Ty sklenice na mě koukají. Sklenice nemají oči, ale tyhle koukají.",
        "Hlavně neotvírejte tu od zelí. Tam jsou slova, která nesmím slyšet, mám slabé uši.",
    ],
    "threads": [
        "Nitě! Všude nitě! Kdo se v tom má vyznat? Já ztrácím nit! Ne, to jsem neřekl, to se tu neříká!",
        "Jdeme po niti? Po které? Po té červené, viďte? Řekněte, že po té červené.",
    ],
    "faces": [
        "Tamta maska na mě mrkla. Nemrkejte na mě, masko!",
        "Neberte si cizí tvář. Já vím, o čem mluvím, já jsem přišel o celý zbytek.",
    ],
    "cellar": [
        "To je on! To je moje tělo! Ještě pořád nosí ten kabát!",
        "Ať se nebojí! Řekněte mu, ať se nebojí! Já se bojím za nás oba!",
    ],
    "office": [
        "Ředitelna? Sem se nesmí! Sem se nikdy nesmělo! Co když přijde pan ředitel? Co když JSTE pan ředitel?",
    ],
    "hidden": [
        "Tady je to smutné. Takové… zapomenuté. Pojďme pryč, než si nás někdo přestane pamatovat.",
        "Sněží tu věci. Na nos mi spadl něčí slib. Fuj.",
    ],
}

HEAD_FACE_WORN = [
    "Vy… vy jste pan ředitel? Ne, to jste vy! Sundejte to, prosím, vypadáte hrozně důležitě!",
    "Ta tvář se vám přisává. Vidím to. Sundejte ji, než bude pozdě!",
]

HEAD_STOLEN_TIME = [
    "Ten čas v kapse tiká jako bomba. Cizí bomba! Vraťte ho!",
]


def head_comment(state):
    """Náhodná panická poznámka hlavy. Věci k místnosti a k situaci mají větší šanci."""
    pool = HEAD_GENERAL + HEAD_BY_LOCATION[state["location"]] * 2
    if state["face_worn"]:
        pool = pool + HEAD_FACE_WORN * 3
    if world.has_item(state, "stolen_time"):
        pool = pool + HEAD_STOLEN_TIME * 2
    return random.choice(pool)


# --- Konce --------------------------------------------------------------------

# Číslo konce a jeho název (pro úředníka, pro úřednici).
ENDINGS = {
    "resignation": [1, "Výpověď", "Výpověď"],
    "lost_head": [2, "Ztratil jsi hlavu", "Ztratila jsi hlavu"],
    "inventory": [3, "Inventář", "Inventář"],
    "nobody_searches": [4, "Nikdo nehledá", "Nikdo nehledá"],
    "director": [5, "Pan ředitel", "Pan ředitel"],
    "time_thief": [6, "Zloděj času", "Zlodějka času"],
    "found": [7, "Nalezený", "Nalezená"],
    "lost_and_found": [8, "Ztracený a nalezený", "Ztracená a nalezená"],
}


def ending_text(state, ending):
    if ending == "resignation":
        return (
            "Pověsíš sako na věšák a necháš na přepážce lísteček: „Dávám výpověď. Hezkou noc.“\n\n"
            f"Do historie úřadu ses {world.g(state, 'zapsal', 'zapsala')} jako {world.g(state, 'zaměstnanec', 'zaměstnankyně')} "
            "s nejkratší pracovní smlouvou všech dob: pět minut."
        )
    if ending == "lost_head":
        return (
            "Jak chceš uklidnit někoho, kdo ztratil hlavu? Bezhlavý do tebe vrazí a jeho panika přeskočí na tebe. "
            "Nevíš, kde je nahoře ani dole. Nevíš, kde máš hlavu. A pak zjistíš, že ji opravdu nemáš.\n\n"
            "Ráno ve sklepě pobíhají dva."
        )
    if ending == "inventory":
        return (
            f"Odbije šestá a po schodech sestupuje denní směna. {world.g(state, 'Nestihl', 'Nestihla')} jsi to. "
            "Úřednice o tebe zakopne, zvedne obočí a sáhne po razítku.\n\n"
            "V deníku služeb přibude nový zápis:\n"
            f"[italic]„Nalezeno: {world.g(state, 'noční úředník', 'noční úřednice')}, 1 kus. Nikdo se nehlásí.“[/italic]"
        )
    if ending == "nobody_searches":
        if world.has_flag(state, "hlavacek_found"):
            place = f"do místnosti, ze které jsi pana Hlaváčka {world.g(state, 'vyvedl', 'vyvedla')}. Teď tu blednou jiní – a ty s nimi."
        else:
            place = "vedle pana Hlaváčka. Smutně se na tebe usměje a posune se."
        return (
            f"Poslední kousek tebe se odloupne. Už nevrháš stín a nejsi si {world.g(state, 'jistý', 'jistá')}, jak se jmenuješ.\n\n"
            f"Padáš jako sníh do místnosti, kam padá všechno, co nikdo nehledá. Dopadneš {place}\n\n"
            "Blednete spolu. Nikdo nehledá."
        )
    if ending == "director":
        return (
            "Ředitelova tvář ti přirostla. Když ji chceš sundat, nahmatáš jen kůži – a ta už není tvoje.\n\n"
            "Usedneš do křesla s vysokým opěradlem. Najednou víš, kdo co ztratil a kolik by za to dal. "
            "Všechny ztracené věci se ti pokloní.\n\n"
            "Navždy vládneš všemu ztracenému. Jen sebe už nenajdeš."
        )
    if ending == "time_thief":
        return (
            "Dveře se před tebou otevřou – v kapsách máš totiž už ráno. Jdeš domů a ukradený čas ti vydrží "
            "na dlouhý, předlouhý život.\n\n"
            "Až ve sto čtyřech letech ti sestřička v nemocnici vypráví o mamince, která se nestihla rozloučit s tátou. "
            "Chybělo jí pár minut. Ten den jí prostě zmizelo odpoledne.\n\n"
            "Ty víš, komu ty hodiny chybí."
        )
    if ending == "found":
        return (
            "Pan Hlaváček si připne jmenovku a vezme tě za loket. Po červené niti se vracíte zpátky, "
            "cestou dopije svůj studený čaj.\n\n"
            f"Za úsvitu odcházíte z úřadu spolu: on, kdo ztratil sám sebe, a ty, kdo {world.g(state, 'ho našel', 'ho našla')}.\n"
            "„Zítra zase?“ zeptá se. A ty zjistíš, že se těšíš."
        )
    # Poslední, tajný konec: "lost_and_found".
    return (
        "Podíváš se na fotku a mezi tisíci vybledlými krabicemi poznáš tu svou. "
        "Na víku je tvoje jméno a pod ním: „Naděje. Nikdo nehledá.“\n\n"
        "Otevřeš ji. Je to jako první den, kdy se v zimě zase prodlužuje světlo. "
        f"Vrací se to do tebe kousek po kousku a jsi {world.g(state, 'celý', 'celá')} – víc než za celé roky.\n\n"
        f"„Teď už víte, proč jste tu práci {world.g(state, 'dostal', 'dostala')},“ usměje se Hlaváček. "
        "Do úřadu berou jen ty, kdo něco ztratili. A zůstávají, dokud nenajdou sebe.\n\n"
        "Za úsvitu vycházíte ven, dva nalezení."
    )
