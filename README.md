# The Legend of X

Mathematik-Abenteuerspiel zu mathbuch 3, LU 11 «Gleichungen lösen» und LU 10 «Alt und Jung».
Umbau von «The Legend of Decimals» v2.1. Die Spielidee, das Spielsystem, die Welten und die Grafiken stammen von R. Behrens. Die Inhalte zu LU 10/11 stammen von C. Heiss.

## Starten
`index.html` über einen Webserver öffnen oder den Ordnerinhalt auf GitHub Pages stellen. Es gibt keinen Build-Schritt und keinen Server.

```bash
python3 -m http.server 8771
```

## Aufbau
| Chapter | Inhalt | Quests |
|---|---|---|
| 1 The Island | LU 11: Term berechnen, Waage, +/−, ·/:, zwei Schritte, Krabbor | 6 |
| 2 Robotown | LU 11: Zusammenfassen, x auf beiden Seiten, Klammern, Probe, Rätsel, Fehler finden | 6 |
| 3 Moonbase | LU 10: Prozent, Alterspyramiden, absolut/relativ, Graphen, Faktencheck, Training, NULLOX | 7 |

Niveau C = Grundanspruch, B = Standard, A = Erweiterung. Alle Gemeinden und Daten sind fiktiv.

## Inhalte ändern
Aufgaben stehen in `tools/content.py`. `tools/build.py` erzeugt daraus `index.html` und braucht daneben das Original im Ordner `../legend-of-decimals` (nicht in diesem Repo).

## Offen
- Zwischenstopps: Das Spiel fragt nach Punkten aus LearningView. Die Lehrperson muss diese drei Zwischenstopps dort anlegen. Die Maximalpunktzahl ist vorläufig 8 (`maxPoints`).
- Die sechs Eastereggs behalten die Rätsel aus dem Originalspiel.
- Der lokale Testzugang des Originals ist weiterhin im Code enthalten und kein Schutz.
