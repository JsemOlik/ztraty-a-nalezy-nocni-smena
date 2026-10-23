"""Úkol, který hráč vidí nahoře na obrazovce – co má dělat dál."""

from .state import GameState


def objective(state: GameState) -> str:
    flags = state.flags
    g = state.g
    if state.face_worn:
        if "read_own_file" not in flags:
            return "Rychle do ředitelny a prohledej kartotéku. Pak si tvář sundej!"
        return "Sundej si ředitelovu tvář, než ti přiroste."
    if "headless_calm" not in flags:
        if state.has("head") or "head" in state.room_items["cellar"]:
            return "Kdo ztratil hlavu, potřebuje ji vrátit. Odnes hlavu Bezhlavému do sklepa."
        if "head" not in state.room_items["umbrellas"]:
            return f"Vrať se pro hlavu, kterou jsi {g('odložil', 'odložila')}, a odnes ji do sklepa."
        if not state.has("umbrella"):
            return "Ve skladu deštníků něco mluví. Vezmi si suchý deštník, ať tam nezmokneš."
        return "Ve skladu deštníků něco mluví. Dojdi se podívat."
    if "hlavacek_found" not in flags:
        if state.location == "hidden" and state.has("nametag"):
            return "Kdo ztratil sám sebe, potřebuje si připomenout, kdo je. Dej Hlaváčkovi jmenovku."
        if not state.has("nametag"):
            return "Seber Hlaváčkovu jmenovku ve sklepě a jdi po červené niti z archivu."
        return "Jdi v archivu po červené niti a dej Hlaváčkovi jeho jmenovku."
    if "read_own_file" not in flags:
        return f"Odejdi s Hlaváčkem – nebo nejdřív zjisti v ředitelně, proč jsi tu práci {g('dostal', 'dostala')}."
    if not state.has("own_photo"):
        return "Odejdi s Hlaváčkem. Svou krabici bez vlastní fotky nepoznáš."
    return "Najdi krabici se svým jménem – nebo prostě odejdi s Hlaváčkem."
