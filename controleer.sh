#!/bin/sh
# Draai dit in de map van een dashboard, na het ophalen van een nieuwe
# huisstijl.css. Het zegt of er een token gebruikt wordt dat nergens meer
# gedefinieerd staat — precies wat er stukgaat als iemand in de huisstijl een
# kleur hernoemt of weghaalt.
set -e
cat huisstijl.css styles.css > /tmp/huisstijl-check.css
grep -o -- "var(--[a-z0-9-]*" /tmp/huisstijl-check.css | sed 's/var(//' | sort -u > /tmp/hc-gebruikt
{ grep -o -- "--[a-z0-9-]*:" /tmp/huisstijl-check.css
  [ -f app.js ] && grep -o -- 'setProperty("--[a-z0-9-]*' app.js | sed 's/setProperty("//;s/$/:/'
} | tr -d ' ' | sed 's/:$//' | sort -u > /tmp/hc-gedefinieerd
ontbreekt=$(comm -23 /tmp/hc-gebruikt /tmp/hc-gedefinieerd)
if [ -n "$ontbreekt" ]; then
  echo "ONTBREKENDE TOKENS:"; echo "$ontbreekt"; exit 1
fi
echo "ok — alle $(wc -l < /tmp/hc-gebruikt | tr -d ' ') gebruikte tokens zijn gedefinieerd"
