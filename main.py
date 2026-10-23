"""Ztráty a nálezy: noční směna. Spuštění: python3 main.py"""

import sys

try:
    import rich  # noqa: F401
except ModuleNotFoundError:
    sys.exit(
        "Chybí knihovna rich. Nainstaluj ji:\n"
        "  pip install -r requirements.txt\n"
        "nebo hru spusť přes uv:\n"
        "  uv run --with-requirements requirements.txt main.py"
    )

from ztraty.game import main

if __name__ == "__main__":
    main()
