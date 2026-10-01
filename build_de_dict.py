#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build an AOSP combined-format German wordlist from a frequency list,
validated and case-restored with the hunspell de_DE dictionary."""
import argparse
import math
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FREQ = HERE / "de" / "de_full_frequency.txt"
HUNSPELL_DICT = HERE / "de" / "de_DE"
ALLOWLIST = HERE / "de" / "allowlist.txt"


def hunspell_stems(words):
    """Return {word: [stems]} for words hunspell accepts."""
    proc = subprocess.run(
        ["hunspell", "-i", "utf-8", "-d", str(HUNSPELL_DICT), "-s"],
        input="\n".join(words) + "\n",
        capture_output=True, text=True, encoding="utf-8", check=True)
    stems = {}
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts) == 2:
            stems.setdefault(parts[0], []).append(parts[1])
    return stems


def is_latin1(w):
    try:
        w.encode("iso-8859-1")
        return True
    except UnicodeEncodeError:
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--locale", nargs="+", default=["de"],
                    help="locales to write a wordlist for, e.g. de de_DE (one file each)")
    ap.add_argument("--out", default=str(HERE / "build"), help="output directory")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rejected_file = out_dir / "rejected_by_hunspell.txt"

    counts = {}
    for line in FREQ.open(encoding="utf-8"):
        parts = line.split()
        if len(parts) != 2 or not parts[0].isalpha() or not is_latin1(parts[0]):
            continue
        w = parts[0].lower()
        counts[w] = counts.get(w, 0) + int(parts[1])

    words = list(counts)
    lower = hunspell_stems(words)
    cap = hunspell_stems([w[:1].upper() + w[1:] for w in words])
    upper = hunspell_stems([w.upper() for w in words if len(w) <= 5])

    max_log = math.log(max(counts.values()))

    def freq(count):
        # log scale onto 1..255
        return max(1, min(255, round(1 + 254 * math.log(count) / max_log)))

    entries = {}
    rejected = []
    for w, n in counts.items():
        c = w[:1].upper() + w[1:]
        u = w.upper()
        lower_ok = w in lower
        # Capitalized form is only real if hunspell derives it from a capitalized stem
        cap_ok = any(s[:1].isupper() for s in cap.get(c, []))
        upper_ok = len(w) > 1 and any(s == u for s in upper.get(u, []))
        f = freq(n)
        if lower_ok:
            entries[w] = max(entries.get(w, 0), f)
        if cap_ok:
            # nominalized infinitives (das Essen, das Benutzen) are rarer than the verb
            cf = max(1, f - 20) if lower_ok and w.endswith("en") else f
            entries[c] = max(entries.get(c, 0), cf)
        if upper_ok and not (lower_ok or cap_ok):
            entries[u] = max(entries.get(u, 0), f)
        if not (lower_ok or cap_ok or upper_ok):
            rejected.append((w, n))

    for line in ALLOWLIST.open(encoding="utf-8"):
        w = line.strip()
        if w and not w.startswith("#") and w.lower() in counts:
            entries[w] = max(entries.get(w, 0), freq(counts[w.lower()]))
    allowed = {w for w in entries}
    rejected = [(w, n) for w, n in rejected if w not in allowed and w.capitalize() not in allowed]

    date = int(os.environ.get("SOURCE_DATE_EPOCH", time.time()))
    ordered = sorted(entries.items(), key=lambda x: (-x[1], x[0]))
    for locale in args.locale:
        with (out_dir / f"main_{locale}.combined").open("w", encoding="utf-8") as out:
            out.write(f"dictionary=main:{locale.lower()},locale={locale},"
                      f"description=Deutsch,date={date},version=1\n")
            for w, f in ordered:
                out.write(f" word={w},f={f}\n")

    rejected.sort(key=lambda x: -x[1])
    rejected_file.write_text("".join(f"{w} {n}\n" for w, n in rejected), encoding="utf-8")
    print(f"input words: {len(counts)}  dictionary entries: {len(entries)}  rejected: {len(rejected)}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
