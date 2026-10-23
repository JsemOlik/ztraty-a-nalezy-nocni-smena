"""Mluvící hlava v kapse neustále panikaří a komentuje."""

from .state import GameState

GENERAL = [
    "Kam jdeme? Proč jdeme? Nemůžeme prostě zůstat? Nebo utéct? Hlavně ne zůstat!",
    "Je tu průvan. Cítím průvan na krku. Teda tam, kde jsem míval krk.",
    "Neupusťte mě. Říkal jsem to už? Neupusťte mě.",
    "Slyšel jste to? Já jsem něco slyšel. Teda, slyšela jste… slyšeli jste? Bojím se.",
    "V téhle kapse je drobek. Proč je v kapse drobek? Já mám alergii na drobky!",
    "Kdybych měl ruce, kousal bych si nehty. Takhle si kousám knír.",
    "Já jsem kdysi někomu patřil. Myslím. Byl to někdo vysoký. Nebo jsem byl já vysoký?",
]

BY_LOCATION = {
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

FACE_WORN = [
    "Vy… vy jste pan ředitel? Ne, to jste vy! Sundejte to, prosím, vypadáte hrozně důležitě!",
    "Ta tvář se vám přisává. Vidím to. Sundejte ji, než bude pozdě!",
]

STOLEN_TIME = [
    "Ten čas v kapse tiká jako bomba. Cizí bomba! Vraťte ho!",
]


def comment(state: GameState) -> str:
    pool = list(GENERAL) + BY_LOCATION.get(state.location, []) * 2
    if state.face_worn:
        pool += FACE_WORN * 3
    if state.has("stolen_time"):
        pool += STOLEN_TIME * 2
    return state.rng.choice(pool)
