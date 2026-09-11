#!/usr/bin/env python3
"""
Contrastcontrole op huisstijl.css van LifeGoods Group.

Leest de tokens uit huisstijl.css zelf — er staat hier geen enkele hexwaarde in
code. Dat is het hele punt: een controlescript met een eigen kopie van het palet
loopt vroeg of laat achter op het bestand dat het zou moeten bewaken, en meldt
dan niets.

    python -B controleer-contrast.py            # alle combinaties, beide thema's
    python -B controleer-contrast.py --reeksen  # onderscheid tussen grafiekreeksen
    python -B controleer-contrast.py --stil     # alleen de fouten

Exitcode 0 als elke combinatie zijn drempel haalt, 1 als er iets faalt.

Twee drempels, en het verschil ertussen is waar de meeste fouten zitten:

  4,5:1  tekst (WCAG 2.1 AA, 1.4.3) — alles wat je leest, ook een getal in een
         cel, een deltaregel of de tekst in een chip
  3,0:1  grafische elementen en de begrenzing van bedieningselementen
         (WCAG 2.1 AA, 1.4.11) — een grafieklijn, een sparkline, de rand van
         een input

Een kleur die als lijn prima werkt haalt het als tekst vaak niet: --mint is
1,93:1 op wit. Daarom heeft dit palet naast --mint ook --op, en naast --reeks-2
ook --op. Verwissel ze niet.
"""

import re
import sys
import pathlib

for _stroom in (sys.stdout, sys.stderr):
    if hasattr(_stroom, "reconfigure"):
        _stroom.reconfigure(encoding="utf-8")

CSS = pathlib.Path(__file__).with_name("huisstijl.css")


# ── WCAG 2.1, relatieve luminantie ────────────────────────────────────────────

def _kanaal(waarde: int) -> float:
    v = waarde / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminantie(kleur: str) -> float:
    h = kleur.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _kanaal(r) + 0.7152 * _kanaal(g) + 0.0722 * _kanaal(b)


def verhouding(voorgrond: str, achtergrond: str) -> float:
    a, b = luminantie(voorgrond), luminantie(achtergrond)
    licht, donker = max(a, b), min(a, b)
    return (licht + 0.05) / (donker + 0.05)


# ── Tokens uit huisstijl.css lezen ────────────────────────────────────────────

def lees_tokens():
    """Geeft (licht, donker) als twee dicts van tokennaam -> hexwaarde.

    Alleen kleurtokens: een waarde die geen hex is en niet naar een hex wijst
    (fontstacks, radii, schaduwen, tekstgroottes) valt vanzelf af.
    """
    if not CSS.exists():
        print(f"FOUT: {CSS.name} niet gevonden naast dit script.")
        raise SystemExit(2)
    tekst = CSS.read_text(encoding="utf-8")
    # commentaar eruit, anders worden voorbeelden in de toelichting meegelezen
    tekst = re.sub(r"/\*.*?\*/", "", tekst, flags=re.S)

    knip = tekst.index('html[data-thema="donker"]')
    ruw_licht = dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", tekst[:knip]))
    ruw_donker = dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", tekst[knip:]))

    def oplossen(ruw, terugval):
        uit = {}
        for naam in ruw:
            waarde = ruw[naam].strip()
            for _ in range(6):  # var(--x) doorlopen tot een hex of iets anders
                m = re.fullmatch(r"var\((--[a-z0-9-]+)\)", waarde)
                if not m:
                    break
                k = m.group(1)
                waarde = (ruw.get(k) or terugval.get(k, "")).strip()
            if re.fullmatch(r"#[0-9A-Fa-f]{6}", waarde):
                uit[naam[2:]] = waarde.upper()
        return uit

    licht = oplossen(ruw_licht, {})
    # het donkere thema overschrijft alleen wat het noemt; de rest erft
    donker = dict(licht)
    donker.update(oplossen(ruw_donker, ruw_licht))
    return licht, donker


# ── De combinaties die in een LGG-dashboard echt voorkomen ────────────────────
# (voorgrond, achtergrond, drempel, waar het staat)

COMBINATIES = [
    # tekst op een oppervlak
    ("tekst", "page", 4.5, "body-tekst op de pagina"),
    ("tekst", "surface", 4.5, "body-tekst op een kaart of tabelrij"),
    ("tekst", "surface-zacht", 4.5, "de getypte waarde in een input"),
    ("tekst", "rij-hover", 4.5, "body-tekst op de rij onder de cursor"),
    ("tekst", "lavendel", 4.5, "body-tekst op een geselecteerde rij"),
    ("tekst-zacht", "page", 4.5, "labels en metadata op de pagina"),
    ("tekst-zacht", "surface", 4.5, "labels en metadata op een kaart of rij"),
    ("tekst-zacht", "surface-zacht", 4.5, "kolomkoppen in de tabelkop"),
    ("tekst-zacht", "rij-hover", 4.5, "metadata op de rij onder de cursor"),
    ("tekst-zacht", "lavendel", 4.5, "metadata op een geselecteerde rij"),

    # merk
    ("kopkleur", "surface", 4.5, "kop, nadrukgetal, tertiaire knop op een kaart"),
    ("kopkleur", "page", 4.5, "kop op de pagina"),
    ("lavendel-tekst", "lavendel", 4.5, "tekst op een actieve tab of geselecteerde rij"),
    ("accent-tekst", "accent-sterk", 4.5, "tekst op een gevuld vlak"),
    ("accent-tekst", "accent-sterk-hover", 4.5, "tekst op een gevuld vlak onder de cursor"),
    ("accent-tekst-zacht", "accent-sterk", 4.5, "bijregel of teller op een gevuld vlak"),
    ("accent-op-vlak", "accent-sterk", 4.5, "mintmarkering op een gevuld vlak"),
    ("op-op-vlak", "accent-sterk", 4.5, "positieve delta op een gevulde KPI-kaart"),
    ("neer-op-vlak", "accent-sterk", 4.5, "negatieve delta op een gevulde KPI-kaart"),
    ("op-op-vlak", "accent-sterk-hover", 4.5, "positieve delta op zo'n kaart onder de cursor"),
    ("neer-op-vlak", "accent-sterk-hover", 4.5, "negatieve delta op zo'n kaart onder de cursor"),

    # de zwevende appbalk. --balk en niet --accent-sterk sinds 14-09-2026: in het
    # donkere thema is de balk chrome (--surface) en geen merkvlak meer.
    ("accent-tekst", "balk", 4.5, "woordmerk en appnaam op de appbalk"),
    ("accent-tekst-zacht", "balk", 4.5, "inactieve tab en secundaire link op de appbalk"),
    ("accent-tekst", "balk-hover", 4.5, "tab onder de cursor op de appbalk"),
    ("accent-tekst-zacht", "balk-hover", 4.5, "secundaire link onder de cursor"),
    ("tegel-op-vlak", "balk", 3.0, "de actieve tegel moet van de balk loskomen (grafisch, 1.4.11)"),

    # de zwevende navy topbar
    ("tegel-op-vlak-tekst", "tegel-op-vlak", 4.5, "tekst op de actieve tab van de navy topbar"),
    ("accent-tekst", "accent-sterk", 4.5, "woordmerk en appnaam op de navy topbar"),
    ("accent-tekst-zacht", "accent-sterk", 4.5, "inactieve tab op de navy topbar"),
    ("accent-tekst-zacht", "accent-sterk-hover", 4.5, "inactieve tab onder de cursor"),
    ("accent-tekst", "accent-sterk-hover", 4.5, "tab onder de cursor, en de verversingschip"),

    # statustekst
    ("op", "surface", 4.5, "positieve waarde op een kaart of rij"),
    ("op", "page", 4.5, "positieve deltaregel op de pagina"),
    ("op", "surface-zacht", 4.5, "positieve waarde in de tabelkop-tint"),
    ("op", "rij-hover", 4.5, "positieve waarde op de rij onder de cursor"),
    ("op", "lavendel", 4.5, "positieve waarde op een geselecteerde rij"),
    ("op", "vlak-op", 4.5, "tekst in de positieve chip"),
    ("neer", "surface", 4.5, "negatieve waarde op een kaart of rij"),
    ("neer", "page", 4.5, "negatieve deltaregel op de pagina"),
    ("neer", "surface-zacht", 4.5, "negatieve waarde in de tabelkop-tint"),
    ("neer", "rij-hover", 4.5, "negatieve waarde op de rij onder de cursor"),
    ("neer", "lavendel", 4.5, "negatieve waarde op een geselecteerde rij"),
    ("neer", "vlak-fout", 4.5, "tekst in de foutchip"),
    ("neer", "vlak-fout-sterk", 4.5, "tekst in de nadrukkelijke foutchip"),
    ("waarschuwing", "surface", 4.5, "waarschuwingstekst op een kaart"),
    ("waarschuwing", "page", 4.5, "waarschuwingstekst op de pagina"),
    ("waarschuwing", "vlak-waarschuwing", 4.5, "tekst in de waarschuwingschip"),
    ("waarschuwing", "vlak-waarschuwing-sterk", 4.5, "tekst in de nadrukkelijke waarschuwingschip"),

    # randen en grafische elementen (1.4.11)
    ("rand-control", "surface", 3.0, "rand van een input in een kaart"),
    ("rand-control", "surface-zacht", 3.0, "rand van een input tegen zijn eigen vulling"),
    ("rand-control", "page", 3.0, "rand van een uitgeschakelde knop op de pagina"),
    ("focus", "surface", 3.0, "focusring op een kaart"),
    ("focus", "page", 3.0, "focusring op de pagina"),
    ("focus", "surface-zacht", 3.0, "focusring om een input"),
    ("focus", "lavendel", 3.0, "focusring op een geselecteerde rij"),

    # grafiekreeksen tegen hun achtergrond (1.4.11)
    ("reeks-1", "surface", 3.0, "eerste grafiekreeks op een kaart"),
    ("reeks-2", "surface", 3.0, "tweede grafiekreeks op een kaart"),
    ("reeks-3", "surface", 3.0, "derde grafiekreeks op een kaart"),
    ("reeks-4", "surface", 3.0, "vierde grafiekreeks op een kaart"),
    ("reeks-5", "surface", 3.0, "vijfde grafiekreeks op een kaart"),
    ("reeks-6", "surface", 3.0, "zesde grafiekreeks op een kaart"),
    ("reeks-1", "page", 3.0, "eerste grafiekreeks op de pagina"),
    ("reeks-2", "page", 3.0, "tweede grafiekreeks op de pagina"),
    ("reeks-3", "page", 3.0, "derde grafiekreeks op de pagina"),
    ("reeks-4", "page", 3.0, "vierde grafiekreeks op de pagina"),
    ("reeks-5", "page", 3.0, "vijfde grafiekreeks op de pagina"),
    ("reeks-6", "page", 3.0, "zesde grafiekreeks op de pagina"),
]

# Combinaties met een ondergrens die géén WCAG-eis is, maar wel een werkbaarheidseis:
# een hover-rij die je niet ziet is geen hover-rij.
ZICHTBAARHEID = [
    ("rij-hover", "surface", 1.12, "de rij onder de cursor tegen een gewone rij"),
    ("lavendel", "surface", 1.10, "een geselecteerde rij tegen een gewone rij"),
    ("rand-zacht", "surface", 1.03, "de rijscheiding binnen een tabel"),
    ("balk", "page", 1.10, "de appbalk tegen de pagina — leunt daarnaast op de schaduw"),
    ("balk-hover", "balk", 1.10, "de tab onder de cursor tegen de balk"),
]

REEKSEN = ["reeks-1", "reeks-2", "reeks-3", "reeks-4", "reeks-5", "reeks-6"]

# Gemeten, gerapporteerd, maar bewust geen toets — omdat de eis afhangt van een
# keuze die nog niet gemaakt is. Deze lijst hoort leeg te lopen, niet te groeien:
# staat er iets te lang in, dan is dat een besluit dat niemand neemt.
OPEN = [
    ("waarschuwing-rand", "vlak-waarschuwing", 3.0,
     "rand om de waarschuwingschip. In het donkere thema 5,05:1, in het lichte "
     "2,04:1 — de twee thema's behandelen deze rand dus verschillend. Of dat "
     "erg is hangt af van hoe hij gebruikt wordt: is de rand het enige wat een "
     "melding als waarschuwing markeert, dan geldt WCAG 1.4.11 en moet hij naar "
     "#BE7A17 (3,01:1 op het slechtste van de vier oppervlakken). Staat er "
     "altijd tekst in --waarschuwing bij, dan is de rand decoratie en is 2,04:1 "
     "prima. Vraag voor Jim; niet eenzijdig wijzigen, want #BE7A17 is zichtbaar "
     "donkerder en raakt de kalender."),
]


# ── Rapportage ────────────────────────────────────────────────────────────────

def rapporteer(naam, palet, stil=False):
    breed = 96
    if not stil:
        print("─" * breed)
        print(f"  {naam.upper()}")
        print("─" * breed)
    gefaald = ontbrekend = 0
    for vg, ag, eis, waar in COMBINATIES + [
        (a, b, c, d) for a, b, c, d in ZICHTBAARHEID
    ]:
        if vg not in palet or ag not in palet:
            ontbrekend += 1
            print(f"  ONBEKEND  --{vg} of --{ag} bestaat niet in het palet   ({waar})")
            continue
        r = verhouding(palet[vg], palet[ag])
        ok = r >= eis
        if not ok:
            gefaald += 1
        if not ok or not stil:
            merk = "  " if ok else "X "
            print(f"  {merk}{r:5.2f}:1  (eis {eis:>4})  --{vg} op --{ag}")
            print(f"              {waar}")
    if not stil:
        totaal = len(COMBINATIES) + len(ZICHTBAARHEID)
        print(f"\n  {totaal - gefaald - ontbrekend} van {totaal} gehaald"
              f"{', ' + str(gefaald) + ' GEFAALD' if gefaald else ''}"
              f"{', ' + str(ontbrekend) + ' onbekend' if ontbrekend else ''}\n")
    return gefaald + ontbrekend


def rapporteer_open(naam, palet):
    """Gemeten punten zonder toets. Laten de exitcode met opzet op 0."""
    if not OPEN:
        return
    print("─" * 96)
    print(f"  {naam.upper()} — gemeten, wacht op een besluit (telt niet mee in de exitcode)")
    print("─" * 96)
    for vg, ag, eis, waarom in OPEN:
        if vg not in palet or ag not in palet:
            continue
        r = verhouding(palet[vg], palet[ag])
        print(f"  ?  {r:5.2f}:1  (zou {eis} zijn als het een eis is)  --{vg} op --{ag}")
        for regel in _wrap(waarom, 88):
            print(f"        {regel}")
    print()


def _wrap(tekst, breedte):
    regels, huidig = [], ""
    for woord in tekst.split():
        if len(huidig) + len(woord) + 1 > breedte:
            regels.append(huidig)
            huidig = woord
        else:
            huidig = f"{huidig} {woord}".strip()
    if huidig:
        regels.append(huidig)
    return regels


def rapporteer_reeksen(naam, palet):
    print("─" * 96)
    print(f"  {naam.upper()} — onderscheid tussen grafiekreeksen (informatief, geen eis)")
    print("─" * 96)
    laag = 0
    for i in range(len(REEKSEN)):
        for j in range(i + 1, len(REEKSEN)):
            a, b = REEKSEN[i], REEKSEN[j]
            if a not in palet or b not in palet:
                continue
            r = verhouding(palet[a], palet[b])
            if r < 1.3:
                laag += 1
            print(f"  {'.' if r < 1.3 else ' '} --{a} vs --{b}   {r:5.2f}:1")
    print(f"\n  {laag} paren onder 1,30:1 — die leunen op tint en legenda, niet op helderheid.\n")


def main():
    vlaggen = set(sys.argv[1:])
    licht, donker = lees_tokens()
    print(f"\n  huisstijl.css — {len(licht)} kleurtokens licht, {len(donker)} donker\n")

    if "--reeksen" in vlaggen:
        rapporteer_reeksen("licht", licht)
        rapporteer_reeksen("donker", donker)
        return 0

    stil = "--stil" in vlaggen
    fout = rapporteer("licht thema", licht, stil)
    fout += rapporteer("donker thema", donker, stil)
    if not stil:
        rapporteer_open("licht thema", licht)

    if fout:
        print(f"  {fout} combinatie(s) haalt de drempel niet. Repareer dat in huisstijl.css")
        print("  vóór je hem publiceert — elke app haalt dit bestand op.\n")
        return 1
    print("  Alles gehaald. huisstijl.css mag gepubliceerd worden.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
