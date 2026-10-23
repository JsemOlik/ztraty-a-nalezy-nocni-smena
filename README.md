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

- Akce vybíráš zadáním čísla. Každá akce zabere **5 minut**. Šedé akce (rozhlédnout se, nápověda, kapsy) jsou zadarmo.
- Směna začíná o půlnoci a v **6:00** přijde denní směna. V oddělení ztraceného času se dá získat *ztracená hodina*, která noc o hodinu prodlouží.
- Máš pět **kousků sebe**. S každou chybou trochu zprůhledníš. Když přijdeš o všechny, úplně se ztratíš.
- Do kapes saka se vejdou jen **čtyři** věci.
- Hádanky stojí na tom, že česká rčení platí doslova. Kdo ztratil hlavu, potřebuje ji vrátit. Kdo ztratil nit, musí jít po niti.
- Když nevíš kudy kam, zvedni u přepážky telefon.

Hra má **osm konců**. Některé jsou vtipné, některé temné a jeden je tajný.

## Testy

```bash
python3 -m unittest
```
