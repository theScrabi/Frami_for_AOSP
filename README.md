# German dictionary for AOSP keyboards

A German main dictionary in the AOSP binary `.dict` format. It works with
[HeliBoard](https://github.com/Helium314/HeliBoard) and other keyboards based
on the AOSP LatinIME (OpenBoard, FUTO Keyboard, …), both for suggestions and
for the system spell checker.

It combines word frequencies from real-world text with the Hunspell German
dictionary to filter out misspellings and junk.

## Building

Requirements: `bash`, `python3`, `hunspell` and a Java runtime (`java`).

```sh
./build.sh
```

This produces:

| File                   | Use for keyboard language    |
|------------------------|------------------------------|
| `build/main_de.dict`    | German (`de`)                |
| `build/main_de_DE.dict` | German (Germany) (`de-DE`)   |

Both files contain the same words and differ only in the locale written
to their header.

Intermediate files (`build/main_*.combined`, the text form of the dictionary)
and `build/rejected_by_hunspell.txt` (every word that was dropped, with its
count) are kept for inspection.

Set `SOURCE_DATE_EPOCH` to get a reproducible header date.

## Installing in HeliBoard

Settings → Dictionaries → *Add dictionary from file*, then pick the `.dict`
file that matches the keyboard language you actually use.

HeliBoard keeps a separate dictionary for each locale. A dictionary
imported for German (`de`) is **not** used by a German (Germany) (`de-DE`)
keyboard, which keeps using HeliBoard's built-in dictionary. Check the
language shown in the import dialog; you can change it there with
*Select language*.

For the spell checker, choose HeliBoard under Android Settings → System →
Languages → Spell checker.

## How the dictionary is made

`build_de_dict.py` does the following:

1. Reads the frequency list (`de/de_full_frequency.txt`) and keeps purely
   alphabetic Latin-1 words.
2. **Runs every word through Hunspell** (`de/de_DE.dic` / `de/de_DE.aff`)
   in lowercase, capitalized and (for short words) uppercase form. Only
   forms Hunspell accepts are kept, and the correct casing is restored, so
   nouns end up capitalized. This rules out misspellings, typos, names, and
   other bad or non-German words from the subtitle corpus.
   A capitalized form is only accepted if Hunspell derives it from a
   capitalized stem.
3. Adds the words in `de/allowlist.txt`. These are common colloquial
   words that Hunspell rejects, such as *ok*, *hey* and *naja*.
4. Maps word counts to AOSP frequencies 1–255 on a logarithmic scale.
   Nominalized infinitives (*das Essen*) get a lower frequency than the
   verb (*essen*).
5. Writes the AOSP "combined" wordlist format. `build.sh` then compiles it
   to a binary dictionary with `dicttool_aosp makedict`.

## Sources and credits

- **`dicttool_aosp`, `dicttool_aosp.jar`** were built from the
  [Android Open Source Project](https://source.android.com/) source code
  by running `mm` in the dicttool package
  (`packages/inputmethods/LatinIME/tools/dicttool`). They are included
  here so the dictionary can be built without an AOSP checkout. They are
  licensed under the Apache License 2.0.
- **`de/de_DE.dic`, `de/de_DE.aff`** were taken from the Fedora
  `hunspell-de` package (version 20240224). They are based on
  [igerman98](https://www.j3e.de/ispell/igerman98/) by Björn Jacke, with
  the *frami* extension by Franz Michael Baumann, and are licensed under
  GPL-2.0 or GPL-3.0.
- **`de/de_full_frequency.txt`** is `content/2016/de/de_full.txt` from
  [FrequencyWords](https://github.com/hermitdave/FrequencyWords) by
  Hermit Dave. It contains word frequencies built from
  [OpenSubtitles](https://www.opensubtitles.org/) and is licensed under
  CC BY-SA 4.0. Many thanks for making this list available!

## License

This project, including the generated dictionaries, is licensed under the
GNU General Public License v3.0, see [LICENSE](LICENSE). The third-party
files listed above remain under their own licenses, all of which are
compatible with GPL-3.0.
