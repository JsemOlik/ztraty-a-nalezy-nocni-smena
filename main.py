"""Ztráty a nálezy: noční směna. Spuštění: python3 main.py"""

import sys

try:
    import rich
except ModuleNotFoundError:
    print("Chybí knihovna rich. Nainstaluj ji:")
    print("  pip install -r requirements.txt")
    print("nebo hru spusť přes uv:")
    print("  uv run --with-requirements requirements.txt main.py")
    sys.exit(1)

import game

game.main()
