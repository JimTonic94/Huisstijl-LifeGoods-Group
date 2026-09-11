# LifeGoods Group — huisstijl

Eén bestand: `huisstijl.css`. Kleuren en fonts voor alle dashboards, als CSS-tokens.
Geen buildstap, geen npm, geen submodule.

## Gebruiken in een dashboard

Haal het bestand op in de map van je app:

```bash
curl -sO https://raw.githubusercontent.com/JimTonic94/Huisstijl-LifeGoods-Group/main/huisstijl.css
```

Deze repo staat bewust publiek: dan heeft dat commando geen token nodig en kan
elk dashboard hem ophalen. Er staat niets vertrouwelijks in — kleuren en
fontnamen zijn zichtbaar in de CSS van elke gepubliceerde site. Zet je hem op
privé, dan breekt de synchronisatie in elk dashboard stil.

Commit die kopie mee. Laad hem vóór je eigen stylesheet:

```html
<link rel="stylesheet" href="huisstijl.css">
<link rel="stylesheet" href="styles.css">
```

Een kopie en geen link naar een URL, omdat de dashboards ook lokaal draaien:
een externe stylesheet breekt dan offline en houdt het renderen op.

## Bijwerken

Kleur gewijzigd hier → in elke app hetzelfde `curl`-commando opnieuw draaien en
de kopie committen. Dat is de synchronisatie: expliciet, zichtbaar in de diff,
en geen enkele app verandert van kleur zonder dat iemand het doorheeft.

## Wat hoort hier wel en niet in

Wel: merkkleuren, rollen (`--kopkleur`, `--accent-sterk`), vlakken, randen,
tekstkleuren, statuskleuren, grafiekreeksen, schaduwen, radii, de twee
fontstacks, de tekstschaal, en het donkere thema voor dat alles.

Niet: opmaakregels (knoppen, tabellen, roosters) en tokens die maar één app
kent — baankleuren van de marketingkalender bijvoorbeeld. Die horen in de
`styles.css` van die app, ná deze.

## Twee afspraken

- `huisstijl.css` laadt vóór `styles.css`.
- Het thema staat als `data-thema="licht"` of `data-thema="donker"` op `<html>`.
  Zet dat in een klein inline script in de `<head>`, vóór de eerste verf, anders
  flitst een donker scherm eerst wit op.

## Typografie

Twee families, en het onderscheid is het hele punt:

| Token | Font | Waarvoor |
|---|---|---|
| `--kop` | **Poppins** 600 | koppen en het woordmerk — de merkstem |
| `--body` | **Inter** 400/500/600 | al het andere: labels, toelichting, tabelinhoud, cijfers |

Poppins is een geometrisch displayfont. In een kop van 20px zet dat de merkstem;
in een kolomkop van 10px of in een bedrag wordt datzelfde karakter ruis. Daarom
draagt Poppins alleen de koppen.

De tekstschaal staat als `--maat-*`-tokens in het bestand (`--maat-pagina` t/m
`--maat-kolomkop`), geijkt op een datagrid. Een app met lopende tekst mag ze in
zijn eigen `styles.css` een stap ruimer zetten — dat is een app-keuze.

**Getallen krijgen altijd `font-variant-numeric: tabular-nums`.** Dat is geen
verfraaiing maar een eis: Inters proportionele `1` is 39px waar de `0` 60px is
(gemeten op 16px), dus zonder die regel springt elke kolom bij het scrollen.

⛔ **Zet er geen `slashed-zero` bij.** Dat lijkt logisch voor een dashboard, maar
de `zero`-feature zit niet in de Google-Fonts-uitlevering van Inter — gemeten op
11-09-2026: nul pixels verschil. Het is dus een regel die niets doet en die
iemand later gaat "repareren".

Laadt je app de fonts zélf (een Next-app met `next/font/google`, of een omgeving
zonder internet), laat dan de `@import` bovenaan weg en zet dezelfde twee
families in `--kop` en `--body`. Dat is geen afwijking van de huisstijl — het is
dezelfde huisstijl zonder een externe request per paginaweergave.

## Controle

Twee scripts, allebei zonder installatie.

```sh
./controleer.sh                    # in de map van een dashboard, na het ophalen
python3 controleer-contrast.py     # hier, vóór je een kleur wijzigt
```

`controleer.sh` meldt elk token dat een app gebruikt maar dat nergens meer
gedefinieerd staat — wat er stukgaat als iemand hier een kleur hernoemt.

`controleer-contrast.py` rekent elke kleurcombinatie na die in een interface
voorkomt, tegen WCAG 2.1 (4,5:1 voor tekst, 3:1 voor randen en grafische
elementen), in beide thema's. Exitcode 1 als er iets faalt. Het leest de tokens
**uit `huisstijl.css` zelf** — geen eigen kopie van het palet, want die loopt
vroeg of laat achter op het bestand dat hij zou moeten bewaken.

```sh
python3 controleer-contrast.py --stil      # alleen de fouten
python3 controleer-contrast.py --reeksen   # onderscheid tussen grafiekreeksen
```

Eén punt staat er gemeten maar zónder toets in (de `OPEN`-lijst in het script):
de rand om de waarschuwingschip haalt 5,05:1 in donker en 2,04:1 in licht. Of
dat een fout is hangt ervan af of die rand ooit de énige markering van een
waarschuwing is; zo ja, dan moet hij naar `#BE7A17`. Vraag voor Jim.

## Wat er op 11-09-2026 is bijgekomen

Aangevuld voor de dashboards van het e-commerceteam (AssortimentManager,
Webshopportaal, HR-dashboard, Stageportaal). Dat zijn datagrids met sorteerbare
tabellen van duizenden rijen, KPI-stroken en grafieken met tot zes reeksen —
plekken die de oorspronkelijke set niet kende. **43 → 69 tokens.**

Nieuw: `--rij-hover` · `--rand-zacht` · `--rand-control` · `--focus` ·
`--vlak-op` · `--lavendel-tekst` · `--accent-tekst-zacht` · `--accent-op-vlak` ·
`--tegel-op-vlak` + `--tegel-op-vlak-tekst` · `--reeks-1` t/m `--reeks-6` ·
`--op-op-vlak` + `--neer-op-vlak` · `--balk` + `--balk-hover` · `--schaduw-midden` · `--radius-chip` ·
`--maat-*` (8 tekstgroottes).

**`--op-op-vlak` en `--neer-op-vlak` verdienen een aparte zin**, want ze zijn
niet zomaar twee kleuren erbij. `--op` en `--neer` zijn gekozen voor een licht
oppervlak en halen op `--accent-sterk` 1,33:1 en 1,40:1 — op een gevulde kaart
zijn ze dus onbruikbaar. Wie dat gat niet ziet pakt `--accent-op-vlak` (mint)
voor allebei, en dan staat een dáling in het groen. Dat is precies wat er in de
AssortimentManager gebeurde. Deze twee zijn op luminantie tegen elkaar gelegd
(1,3% uit elkaar), zodat een stijging en een daling op zo'n kaart even zwaar
wegen — dezelfde regel als bij `--op`/`--neer` zelf.

Gewijzigd, elk om een gemeten contrastfout te sluiten — de reden staat bij de
token zelf in het bestand:

| Token | Was | Wordt | Waarom |
|---|---|---|---|
| `--op` (licht) | `#01865D` | `#01724F` | 3,49:1 op een geselecteerde rij |
| `--neer` (licht) | `#C0392B` | `#B53629` | 4,13:1 op een geselecteerde rij |
| `--waarschuwing` (licht) | `#B26B00` | `#9B5D00` | 3,97:1 in zijn eigen chip |
| `--tekst-zacht` (licht) | `#5A6685` | `#586381` | 4,34:1 op lavendel |
| `--accent-sterk` (donker) | `#4A5C9E` | `#384678` | mint erop haalde 3,14:1 |
| `--body` | Lexend | **Inter** | zie Typografie |

`--kanaal-*` wijst nu naar `--reeks-*`, zodat een kleur op één plek staat.
Daarbij verandert er één echt: `--kanaal-organisch` was mint (`#02D090`), wat
als lijn op wit 1,93:1 haalt en dus onder de 3:1 voor een grafisch element zit.

**Mint is geen lijnkleur op een licht vlak** — dat geldt overal, niet alleen in
de kanaalbalk. Voor een positieve lijn of vulling (een sparkline, de tint achter
een weekblok) is `--op` het antwoord, en niet omdat het moet: `--op` en `--neer`
hebben nagenoeg dezelfde luminantie, dus groen en rood wegen naast elkaar even
zwaar. Met mint weegt het groen 3,7x zo licht en schreeuwt elke stijging terwijl
elke daling fluistert. Voor een neutrale reeks in een grafiek met meerdere
lijnen: `--reeks-2`. Mint blijft wat het altijd was — de merkaccentkleur, voor
vlakken en voor een detail óp een donker vlak (`--accent-op-vlak`).

⚠️ **Drie hiervan zijn zichtbaar in de marketingkalender**: de tekst gaat van
Lexend naar Inter, `--accent-sterk` wordt in het donkere thema een tint
donkerder, en de organische kanaalkleur wordt het donkerder groen. Draai na het
ophalen `./controleer.sh` in de kalendermap — dan zie je meteen of er een token
gebruikt wordt die hier niet meer bestaat.
