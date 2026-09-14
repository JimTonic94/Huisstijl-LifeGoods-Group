# LifeGoods Group — huisstijl

Eén bestand: `huisstijl.css`. Kleuren en fonts voor alle dashboards, als CSS-tokens.
Geen buildstap, geen npm, geen submodule. lol

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
tekstkleuren, statuskleuren, schaduwen, radii, de twee fontstacks, en het
donkere thema voor dat alles.

Niet: opmaakregels (knoppen, tabellen, roosters) en tokens die maar één app
kent — baankleuren van de marketingkalender bijvoorbeeld. Die horen in de
`styles.css` van die app, ná deze.

## Twee afspraken

- `huisstijl.css` laadt vóór `styles.css`.
- Het thema staat als `data-thema="licht"` of `data-thema="donker"` op `<html>`.
  Zet dat in een klein inline script in de `<head>`, vóór de eerste verf, anders
  flitst een donker scherm eerst wit op.

## Controle

`controleer.sh` in de map van een dashboard draaien na het ophalen van een
nieuwe versie. Het meldt elk token dat de app gebruikt maar dat nergens meer
gedefinieerd staat — wat er stukgaat als iemand hier een kleur hernoemt.
