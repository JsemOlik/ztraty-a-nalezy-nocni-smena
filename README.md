# Ztráty a nálezy: noční směna

Textová hra do terminálu. Nastupuješ na noční směnu do Centrálního úřadu ztrát a nálezů ve sklepení pod starou poštou. Končí tu všechno, co lidé ztratí: klíče, deštníky, ale i ztracený čas, ztracená řeč, ztracené nitě myšlenek, ztracené tváře a ztracené hlavy. Tvůj předchůdce, pan Hlaváček, minulý týden beze stopy zmizel. Do šesti ráno musíš zjistit, co se mu stalo, a hlavně nedopadnout stejně.

## Instalace a spuštění

Potřebuješ Python 3.10 nebo novější.

```bash
pip install -r requirements.txt
python3 main.py
```

S [uv](https://docs.astral.sh/uv/) to jde i bez ručního instalování:

```bash
uv run --with-requirements requirements.txt main.py
```

Hra používá knihovnu [rich](https://github.com/Textualize/rich) na barvy, rámečky a animace. Terminál by měl umět UTF-8.

### Animace

Text se vypisuje jako na psacím stroji. **Libovolná klávesa** přeskočí animace až do další volby. Rychlost se dá přepnout přímo ve hře (volba *Rychlost textu*) nebo při spuštění:

```bash
python3 main.py --rychle        # rychlejší psaní
python3 main.py --bez-animaci   # bez animací
```

Když výstup nejde do terminálu (třeba při přesměrování do souboru), animace se vypnou samy.

## Jak se hraje

- **Cíl:** najdi pana Hlaváčka do 6:00 ráno. Nahoře na obrazovce je vždy **Úkol**, co dělat dál.
- Napiš číslo volby a Enter. Každá akce zabere **5 minut**. Klávesy **n** (nápověda), **r** (rychlost textu) a **k** (konec) fungují kdykoli.
- Máš pět **kousků sebe** (●). Chybami průhledníš; když přijdeš o všechny, ztratíš se.
- Do kapes se vejdou jen **čtyři** věci. Když jsou plné, hra se zeptá, co odložit.
- Rčení tu platí doslova: kdo ztratil hlavu, musí ji dostat zpátky. Kdo ztratil nit, jde po niti.

Hra se vejde do jedné obrazovky a každý tah ji překreslí na místě. Po skončení se terminál vrátí do původního stavu. Hra má **osm konců** – některé vtipné, některé temné a jeden tajný.

## Testy

```bash
python3 -m unittest
```

## Autor

Tvorba: Oliver Steiner · [jsemolik.dev](https://jsemolik.dev)
