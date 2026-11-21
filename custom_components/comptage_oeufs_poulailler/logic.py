"""Fonctions pures (sans dépendance à Home Assistant), faciles à tester."""

from __future__ import annotations

from datetime import date, timedelta
import io
import re

from .const import DIFF_PIXEL_THRESHOLD, THUMB_SIZE

_OLD_FORMAT = re.compile(r"^\s*(\d{2})/(\d{2})/(\d{2,4})\s*:\s*(\d+)\s*$")


def parse_legacy_history(text: str | None) -> dict[str, int]:
    """Lit l'ancien format « 20/11/26:1;19/11/26:3;… » et retourne {AAAA-MM-JJ: n}."""
    result: dict[str, int] = {}
    if not text:
        return result
    for part in text.split(";"):
        match = _OLD_FORMAT.match(part)
        if not match:
            continue
        day, month, year, count = match.groups()
        year_i = int(year) + (2000 if len(year) == 2 else 0)
        try:
            iso = date(year_i, int(month), int(day)).isoformat()
        except ValueError:
            continue
        result[iso] = int(count)
    return result


def thumbnail(content: bytes) -> bytes | None:
    """Miniature en niveaux de gris, ou None si Pillow est absent / l'image illisible."""
    try:
        from PIL import Image  # noqa: PLC0415  (import paresseux : Pillow est optionnel)
    except ImportError:
        return None
    try:
        with Image.open(io.BytesIO(content)) as img:
            return img.convert("L").resize(THUMB_SIZE).tobytes()
    except Exception:  # noqa: BLE001
        return None


def changed_fraction(a: bytes, b: bytes) -> float:
    """Part des pixels réellement modifiés entre deux miniatures (0 à 1).

    La luminosité moyenne de chaque image est retirée avant la comparaison,
    pour qu'un simple nuage ou un changement d'exposition ne compte pas.
    """
    if not a or len(a) != len(b):
        return 1.0
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    shift = mean_a - mean_b
    changed = sum(1 for x, y in zip(a, b) if abs(x - y - shift) > DIFF_PIXEL_THRESHOLD)
    return changed / len(a)


def stats(history: dict[str, int], today: date) -> dict[str, int]:
    """Totaux utiles calculés à partir de l'historique {AAAA-MM-JJ: n}."""

    def count(day: date) -> int:
        return int(history.get(day.isoformat(), 0))

    week = sum(count(today - timedelta(days=i)) for i in range(7))
    month_prefix = today.strftime("%Y-%m")
    year_prefix = today.strftime("%Y")
    return {
        "aujourd_hui": count(today),
        "hier": count(today - timedelta(days=1)),
        "7_jours": week,
        "ce_mois": sum(v for k, v in history.items() if k.startswith(month_prefix)),
        "cette_annee": sum(v for k, v in history.items() if k.startswith(year_prefix)),
        "total": sum(history.values()),
    }


def build_prompt(template: str, nests: int) -> str:
    """Remplace {pondoirs} sans risquer d'erreur de format sur les autres accolades."""
    return (template or "").replace("{pondoirs}", str(nests))
