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
        Item("umbrella", "suchý deštník", "suchý deštník", "Jediný suchý deštník v celém úřadu. Chrání před deštěm ve skladu."),
        Item("head", "mluvící hlava", "mluvící hlavu", "Hlava pána s knírem. Pořád mluví a bojí se. Patří někomu ve sklepě."),
        Item(
            "lost_hour",
            "ztracená hodina",
            "ztracenou hodinu",
            "Hodina, kterou kdosi prostál ve frontě. Prodlouží noc o hodinu.",
            usable=True,
        ),
        Item(
            "laugh_jar",
            "sklenice se smíchem",
            "sklenici se smíchem",
            "Něčí ztracený smích. Když ji otevřeš, vrátí ti kousek sebe.",
            usable=True,
            use_label="Otevřít",
        ),
        Item("stolen_time", "hrst ukradeného času", "hrst ukradeného času", "Cizí minuty. Lepí se na prsty a tikají."),
        Item("red_thread", "červená nit", "červenou nit", "Konec červené niti. Dokud ji držíš, neztratíš se."),
        Item(
            "director_face",
            "ředitelova tvář",
            "ředitelovu tvář",
            "Tvář pana ředitele. Otevře ředitelnu. Nenos ji dlouho.",
            usable=True,
            use_label="Nasadit si",
        ),
        Item("nametag", "Hlaváčkova jmenovka", "Hlaváčkovu jmenovku", "„Bohumil Hlaváček – noční služba.“ Připomene mu, kdo je."),
        Item(
            "own_photo",
            "vlastní fotka",
            "vlastní fotku",
            "Tvoje stará fotka. Připomene ti, kdo jsi (vrátí 2 kousky sebe, ale vybledne).",
            usable=True,
            use_label="Zadívat se na",
        ),
    ]
}
