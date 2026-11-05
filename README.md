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

## Anmeldung und Lernstand
- SuS melden sich mit dem Code oder QR-Code ihrer MathWelt-3A-Karte an. Es erscheint nur die ID, kein Name. Prüfwerte und öffentlicher Schlüssel stehen in `js/config.js` und sind eine Kopie aus `mathwelt-3a`. Neue Codes müssen in beiden Repos eingetragen werden.
- SPEICHERN verschlüsselt den Stand und schickt ihn an den Worker. Klappt das nicht, wird eine `.lox`-Datei heruntergeladen. Zusätzlich liegt der verschlüsselte Stand im Browser.
- Die Masterview ist `lehrer.html`. Sie öffnet sich mit dem Dongle von MathWelt 3A und liest die Online-Stände aus `saves-lox/` im Daten-Repo. Der Lese-Schlüssel lässt sich direkt dort einrichten und im Dongle speichern.

### Einmalige Einrichtung: Worker aktualisieren
Bei Cloudflare den Worker `mathwelt-3a-save` öffnen → **Edit code** → alles durch `worker/worker.js` aus diesem Repo ersetzen → **Deploy**. Die Variablen bleiben. MathWelt 3A läuft unverändert weiter. Der Code in `mathwelt-3a/worker/worker.js` ist danach älter als der laufende Worker.

## Inhalte ändern
Aufgaben stehen in `tools/content.py`. `tools/build.py` erzeugt daraus `index.html` und braucht daneben das Original im Ordner `../legend-of-decimals` (nicht in diesem Repo).

## Offen
- Zwischenstopps: Das Spiel fragt nach Punkten aus LearningView. Die Lehrperson muss diese drei Zwischenstopps dort anlegen. Die Maximalpunktzahl ist vorläufig 8 (`maxPoints`).
- Die sechs Eastereggs behalten die Rätsel aus dem Originalspiel.
- Der lokale Testzugang des Originals ist weiterhin im Code enthalten und kein Schutz. Die Masterview markiert seine Nutzung.
