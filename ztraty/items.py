"""Předměty, které se vejdou do kapes saka."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    id: str
    name: str
    accusative: str
    description: str
    usable: bool = False
    use_label: str = "Použít"


ITEMS: dict[str, Item] = {
    item.id: item
    for item in [
        Item(
            "storage_key",
            "klíč od skladu",
            "klíč od skladu",
            "Těžký mosazný klíč s visačkou „SKLAD DEŠTNÍKŮ – NEVSTUPOVAT BEZ“. Zbytek visačky je rozmočený.",
        ),
        Item(
            "umbrella",
            "suchý deštník",
            "suchý deštník",
            "Černý deštník s dřevěnou rukojetí. Jediný suchý deštník v celém úřadu. Někdo ho tu zapomněl za slunečného dne.",
        ),
        Item(
            "head",
            "mluvící hlava",
            "mluvící hlavu",
            "Hlava pána s pěstěným knírem. Neustále mluví, mrká a bojí se. Tvrdí, že ji někdo ztratil, ale nepamatuje si kdo.",
        ),
        Item(
            "lost_hour",
            "ztracená hodina",
            "ztracenou hodinu",
            "Hodina, kterou kdysi někdo ztratil čekáním na tramvaj. Je teplá a tiše tiká. Dá se použít k prodloužení noci.",
            usable=True,
        ),
        Item(
            "laugh_jar",
            "sklenice se ztraceným smíchem",
            "sklenici se ztraceným smíchem",
            "Zavařovací sklenice, ve které se něco chichotá. Když ji otevřeš, smích se vrátí na svět – a kousek z něj i do tebe.",
            usable=True,
            use_label="Otevřít",
        ),
        Item(
            "stolen_time",
            "hrst ukradeného času",
            "hrst ukradeného času",
            "Hrst minut, které nejsou tvoje. Lepí se na prsty a pořád se snaží utéct zpátky k majiteli.",
        ),
        Item(
            "red_thread",
            "červená nit",
            "červenou nit",
            "Konec červené niti. Druhý konec vede kamsi pryč, za hranu všech map. Dokud ji držíš, neztratíš se.",
        ),
        Item(
            "director_face",
            "ředitelova tvář",
            "ředitelovu tvář",
            "Tvář pana ředitele. Přísné obočí, tenké rty, výraz člověka, který se nikdy nesmál. Je nepříjemně teplá.",
            usable=True,
            use_label="Nasadit",
        ),
        Item(
            "nametag",
            "Hlaváčkova jmenovka",
            "Hlaváčkovu jmenovku",
            "Plechová jmenovka: „Bohumil Hlaváček – noční služba“. Na zadní straně je vyškrábáno: „Nezapomeň, kdo jsi.“",
        ),
        Item(
            "own_photo",
            "vlastní fotka",
            "vlastní fotku",
            "Tvoje fotka z doby, kdy byl tvůj smích ještě slyšet přes celou ulici. Připomíná ti, kdo jsi. Když se do ní zadíváš, kus tebe se vrátí – ale fotka u toho vybledne.",
            usable=True,
            use_label="Zadívat se na",
        ),
    ]
}
