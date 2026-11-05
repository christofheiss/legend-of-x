#!/usr/bin/env python3
# Erzeugt aus dem Original ../legend-of-decimals eine auf LU 10/11 umgebaute Fassung in ../legend-of-x.
import base64, json, re, shutil, textwrap
from pathlib import Path
import content

ROOT = Path(__file__).resolve().parent.parent.parent
SRC, OUT = ROOT / "legend-of-decimals", ROOT / "legend-of-x"
html = (SRC / "index.html").read_text(encoding="utf-8")


def sub(old, new, count=1):
    global html
    found = html.count(old)
    assert found == count if count else found > 0, (old[:70], found)
    html = html.replace(old, new)


def rx(pattern, new, count=1, flags=re.S):
    global html
    html, found = re.subn(pattern, (lambda _: new) if isinstance(new, str) else new, html, flags=flags)
    assert (found == count if count else found > 0), (pattern[:70], found)


# ---------- Aufgabendaten ----------
data, comparison = content.build()
rx(r"const comparisonTasks = \{.*?\n\};\n", "const comparisonTasks = " + json.dumps(comparison, ensure_ascii=False) + ";\n")
rx(r"const mData = \{.*?\n\s*\};(?=\s*// Interactive measurement task)", "const mData = " + json.dumps(data, ensure_ascii=False) + ";")
rx(r"for \(const level of \['a','b'\]\) \{\s*mData\.s3m2.*?\n\s*\}\n", "\n")
rx(r"\n\s*mData\.m5\.intro=.*?\n(\s*const estimateRules=\{.*?\};\n)?\s*for\(const niveau of \['a','b','c'\]\)mData\.m5[^\n]*\n", "\n")
rx(r"\n\s*if \(dataKey === 's2m3'\) html \+= [^\n]*", "")
rx(r"\n\s*if \(dataKey === 's2m4'\) html \+= [^\n]*", "")
for key in ("s3m5", "s3m4", "s3m3"):
    rx(r"\n\s*if \(dataKey === '%s'\) \{\n[^\n]*\n\s*\}" % key, "")
rx(r'<p class="text-slate-300 mb-4">Beim Sport entscheiden.*?</p>',
   '<p class="text-slate-300 mb-4">Stell dir eine Waage vor. Setze den Wert für x links und rechts ein und vergleiche. Schreibe &lt;, = oder &gt;.</p>', count=0)
sub("Decke Krabbors Denkfehler auf. Arbeite ohne Taschenrechner. Einzelauswahl: genau eine Antwort. Mehrfachauswahl: alle richtigen Aussagen ankreuzen.",
    "Decke Krabbors Denkfehler beim Umformen auf. Einzelauswahl: genau eine Antwort. Mehrfachauswahl: alle richtigen Aussagen ankreuzen.")

# ---------- Eingaben: Minuszeichen und «x = 5» erlauben ----------
sub("function valInArr(inputVal, arr) {", "function valInArr(inputVal, arr) {\n            inputVal = String(inputVal).replace(/[−–]/g, '-').replace(/^\\s*[a-zA-Z]\\s*=\\s*/, '');")

# ---------- Hinweise ----------
hints = {
    "compare": "Setze den Wert für x auf beiden Seiten ein. Rechne Klammern zuerst und Punkt vor Strich.",
    "s1-m1": "Setze den Wert für x ein. Klammern zuerst, dann Punkt vor Strich. Achte auf die Vorzeichen.",
    "s1-m3": "Welche Rechnung hebt + oder − auf? Führe sie auf beiden Seiten aus und mache die Probe.",
    "s1-m4": "Multiplikation und Division heben sich auf. Rechne auf beiden Seiten gleich.",
    "s1-m5": "Entferne zuerst + oder −, danach · oder :. Mache am Schluss die Probe.",
    "s2-m1": "Fasse nur gleichartige Glieder zusammen. Bei Klammern wird jedes Glied multipliziert.",
    "s2-m2": "Bringe zuerst alle x auf eine Seite, danach die Zahlen auf die andere.",
    "s2-m3": "Löse zuerst die Klammern auf. Ein Minus vor der Klammer ändert alle Vorzeichen.",
    "s2-m4": "Setze den Wert für x ein und berechne jede Seite getrennt.",
    "s2-m5": "Lege fest, was x bedeutet, und schreibe den Text Schritt für Schritt als Gleichung.",
    "s2-m6": "Löse die Gleichung selbst und mache die Probe.",
    "s3-m1": "Anteil in % = Teil : Ganzes · 100. Prozentwert = Ganzes · Prozentsatz : 100.",
    "s3-m2": "Lies den passenden Balken am Gitter ab. Die Achse zeigt Personen pro Altersklasse.",
    "s3-m3": "Kläre zuerst: Was ist der Teil und was das Ganze? Veränderung in % bezieht sich auf den alten Wert.",
    "s3-m4": "Lies die beschrifteten Punkte ab. Veränderung = späterer Wert − früherer Wert.",
    "s3-m5": "Rechne mit den Werten aus der Tabelle.",
}
sub("const LearningFeedback=(()=>{", "const LU_HINTS=" + json.dumps(hints, ensure_ascii=False) + ";\nconst LearningFeedback=(()=>{")
sub("const writing=NumberWriting.groupingHint(value,answers);if(writing)return writing;",
    "const writing=NumberWriting.groupingHint(value,answers);if(writing)return writing;\n"
    "        {const a=number(String(value).replace(/[−–]/g,'-')),e=answers.map(number).find(Number.isFinite);if(Number.isFinite(a)&&Number.isFinite(e)&&a===-e&&a!==0)return 'Prüfe das Vorzeichen deines Ergebnisses.';}\n"
    "        if(topic==='practice')return fallback||'Mache die Probe.';\n"
    "        if(LU_HINTS[topic])return LU_HINTS[topic];")
rx(r"function topic\(prefix\)\{return \(\{.*?\}\)\[prefix\]\|\|'';\}", "function topic(prefix){return prefix;}")

# ---------- Trainingsraum ----------
practice = r"""function makeAccuracyRound(niveau, number) {
    const r=(min,max)=>min+Math.floor(Math.random()*(max-min+1));
    const nz=(min,max)=>{let v;do{v=r(min,max);}while(v===0);return v;};
    const s=v=>String(v).replace('-','−');
    const term=(a,b)=>`${a===1?'':a===-1?'−':s(a)}x${b<0?' − '+(-b):b>0?' + '+b:''}`;
    const tasks=[];
    const eq=(text,x,hint)=>tasks.push({text:`${text}  x =`,unit:'',answer:String(x),hint});
    const pct=(text,value,unit,hint)=>tasks.push({text,unit,answer:String(value),hint});
    const percent=[10,20,25,50];
    const a1=()=>niveau==='C'?r(2,9):nz(-9,9)||2, x1=()=>niveau==='C'?r(1,12):nz(-12,12);
    for(let i=0;i<7;i++){
        const x=x1();
        if(i<2){const b=niveau==='C'?r(1,20):nz(-20,20);eq(`${term(1,b)} = ${s(x+b)}.`,x,'Hebe die Zahl auf beiden Seiten auf.');}
        else if(i<4){let a=a1();if(a===1||a===-1||a===0)a=3;const b=niveau==='C'?r(1,20):nz(-20,20);eq(`${term(a,b)} = ${s(a*x+b)}.`,x,'Zuerst + oder − entfernen, dann durch die Zahl vor x dividieren.');}
        else if(i<6){const c=r(1,4),a=c+r(1,4),b=niveau==='C'?r(1,15):nz(-15,15);eq(`${term(a,b)} = ${term(c,(a-c)*x+b)}.`,x,'Bringe zuerst alle x auf eine Seite.');}
        else{const a=r(2,5),b=niveau==='C'?r(1,6):nz(-6,6);eq(`${a}(${term(1,b)}) = ${s(a*(x+b))}.`,x,'Löse zuerst die Klammer auf.');}
    }
    const p=niveau==='A'?[5,15,35,40][r(0,3)]:percent[r(0,3)],g=r(2,20)*20;
    pct(`${p} % von ${g} =`,p*g/100,'','Ganzes · Prozentsatz : 100.');
    const q=percent[r(0,3)],h=r(2,12)*20;pct(`${h*q/100} von ${h} sind`,q,'%','Teil : Ganzes · 100.');
    if(niveau==='C'){const z=percent[r(0,3)],w=r(2,12)*20;pct(`Ein Dorf hat ${w} Personen. ${z} % sind Kinder. Das sind`,w*z/100,'Kinder','Ganzes · Prozentsatz : 100.');}
    else{const alt=r(2,12)*20,ch=[10,20,25,50][r(0,3)],neu=alt+alt*ch/100;pct(`Von ${alt} auf ${neu}: Zunahme um`,ch,'%','(neu − alt) : alt · 100.');}
    return {number,createdAt:new Date().toISOString(),tasks,inputs:Array(10).fill(''),checked:Array(10).fill(null),attempts:Array(10).fill(0)};
}
"""
rx(r"function makeAccuracyRound\(niveau, number\) \{.*?\n\}\n(?=function validAccuracyPractice)", practice)
sub(r"/^\d+(?:\.\d{1,2})?$/.test(t.answer)", r"/^-?\d+(?:\.\d{1,2})?$/.test(t.answer)")

# ---------- NULLOX ----------
num_field = lambda fid, label: (f'<span class="thanos-number" style="display:block;width:100%"><label for="{fid}" class="block mb-1">{label}</label><span><input type="text" inputmode="decimal" autocomplete="off" id="{fid}" aria-describedby="{fid}-feedback" class="mcu-input p-2 text-center w-24"> %</span><p id="{fid}-feedback" class="text-sm mt-2" aria-live="polite"></p></span>')
tbl = content.table(["Gemeinde Talwil", content.Y(2010), content.Y(2020)], [["Einwohner total", 5000, 6000], ["davon über 65", 800, 1080]])
def text_block(fid, question, note, model):
    return (f'<label for="{fid}" class="block font-bold">{question}</label><p class="text-sm text-slate-400">{note}</p>'
            f'<textarea id="{fid}" rows="3" class="mcu-input p-3 w-full" aria-describedby="{fid}-feedback"></textarea><p id="{fid}-feedback" class="text-sm mt-2" aria-live="polite"></p>'
            f'<div id="{fid}-model" hidden class="thanos-model bg-slate-800 border border-sky-800 rounded p-4 space-y-2"><p class="font-bold text-sky-300">Musterlösung zum Vergleichen</p><p>{model}</p></div>')
M_FOIL = "Ja. Die Anzahl stieg von 800 auf 1'080, also um 280 Personen. Das sind 35 % und damit mehr als ein Drittel."
M_JUDGE = "Auch die Bevölkerung wuchs von 5'000 auf 6'000. Der Anteil stieg nur von 16 % auf 18 %, also um 2 Prozentpunkte. «Explodiert» übertreibt die Entwicklung."
nullox = f"""<div id="s3-m7-content" class="mission-content hidden space-y-6 pb-8">
                    <div class="bg-slate-900 border border-purple-800 rounded p-4 space-y-3">
                        <p>Diese Vertiefung verbindet absolute und relative Angaben mit einer kritischen Beurteilung.</p>
                        <p><strong>Bearbeite die drei Aufträge. Ein Taschenrechner ist erlaubt.</strong> Du kannst erst korrigieren, wenn du alle Felder ausgefüllt hast.</p>
                        <p>Nach «Korrektur» vergleichst du deine Textantworten mit Musterlösungen und überarbeitest sie direkt.</p>
                    </div>
                    <div class="space-y-3">
                        <p>Die erfundene Gemeinde Talwil veröffentlicht diese Zahlen:</p>{tbl}
                        <p>NULLOX verbreitet die Schlagzeile:<br><strong>«Talwil vergreist: Die Zahl der Alten explodiert um mehr als ein Drittel!»</strong></p>
                    </div>
                    <section class="bg-slate-900 border border-slate-700 rounded p-4 space-y-4">
                        <h3 class="text-lg text-purple-300">1. Berechne.</h3>
                        <div class="space-y-3">{num_field('thanos-length', 'Anteil der über 65-Jährigen ' + content.Y(2010))}{num_field('thanos-width', 'Anteil der über 65-Jährigen ' + content.Y(2020))}{num_field('thanos-area', 'Zunahme der Anzahl über 65-Jähriger in Prozent')}</div>
                        <p class="director-solution">Lösung: 16 %, 18 %, 35 %.</p>
                    </section>
                    <section class="bg-slate-900 border border-slate-700 rounded p-4 space-y-4">
                        <h3 class="text-lg text-purple-300">2. Beurteile die Schlagzeile.</h3>
                        {text_block('thanos-foil', 'Stimmt die Zahl in der Schlagzeile?', 'Antworte mit Ja oder Nein und begründe mit einer Rechnung.', M_FOIL)}
                        {text_block('thanos-judgement', 'Weshalb vermittelt die Schlagzeile trotzdem einen falschen Eindruck?', 'Vergleiche die absoluten und die relativen Angaben.', M_JUDGE)}
                        <p class="director-solution">Beispiel: Die Zahl stimmt, aber der Anteil stieg nur um 2 Prozentpunkte.</p>
                    </section>
                    <section class="bg-slate-900 border border-slate-700 rounded p-4 space-y-4">
                        <h3 class="text-lg text-purple-300">3. Stelle eine kritische Frage.</h3>
                        {text_block('thanos-recommendation', 'Welche Frage würdest du stellen, um die Entwicklung besser beurteilen zu können?', 'Die Frage soll sich mit Daten beantworten lassen.', 'Zum Beispiel: Wie haben sich die anderen Altersgruppen entwickelt? Wie sieht die Entwicklung über einen längeren Zeitraum aus? Wie verändert sich der Anteil in den Nachbargemeinden?')}
                        <p class="director-solution">Beispiel: Wie entwickelten sich die anderen Altersgruppen über einen längeren Zeitraum?</p>
                    </section>
                    """
rx(r'<div id="s3-m7-content" class="mission-content hidden space-y-6 pb-8">.*?(?=<p id="thanos-fill-note")', nullox)
rx(r"function gradeThanosField\(index,inputs\) \{.*?\n\}\n", """function gradeThanosField(index,inputs) {
    const value=inputs[index];
    if(!value.trim())return {correct:false,hint:'Fülle dieses Feld zuerst aus.'};
    const expected=[['16','Rechne 800 : 5\\'000 · 100.'],['18','Rechne 1\\'080 : 6\\'000 · 100.'],['35','Rechne (1\\'080 − 800) : 800 · 100.']][index];
    if(expected)return {correct:valInArr(value,[expected[0]]),hint:expected[1]};
    return {correct:null,hint:'Vergleiche deine Antwort mit der Musterlösung und ergänze oder verbessere sie direkt im Eingabefeld.'};
}
""")

# ---------- Namen und Texte ----------
names = [
    ("{id:2,name:'Vergleichen',short:'VERGLEICHEN',", "{id:2,name:'Waage-Werkstatt',short:'WAAGE',"),
    ("{id:3,name:'Darstellen',short:'DARSTELLEN',", "{id:3,name:'Plus und Minus',short:'PLUS & MINUS',"),
    ("{id:4,name:'Runden',short:'RUNDEN',", "{id:4,name:'Umkehr-Turm',short:'UMKEHR-TURM',"),
    ("{id:5,name:'Überschlagen',short:'ÜBERSCHLAGEN',", "{id:5,name:'Zwei Schritte',short:'ZWEI SCHRITTE',"),
    ("{id:2,name:'Addieren und Subtrahieren',lines:['ADDIEREN &','SUBTRAHIEREN'],", "{id:2,name:'Beide Seiten',lines:['BEIDE','SEITEN'],"),
    ("{id:3,name:'Multiplizieren',lines:['MULTIPLIZIEREN'],", "{id:3,name:'Klammer-Mine',lines:['KLAMMER-MINE'],"),
    ("{id:4,name:'Dividieren',lines:['DIVIDIEREN'],", "{id:4,name:'Proben-Labor',lines:['PROBEN-LABOR'],"),
    ("{id:5,name:'Rechnung wählen',lines:['RECHNUNG WÄHLEN'],", "{id:5,name:'Rätsel-Bibliothek',lines:['RÄTSEL-','BIBLIOTHEK'],"),
    ("{id:2,name:'Messen',lines:['MESSEN'],", "{id:2,name:'Pyramiden-Museum',lines:['PYRAMIDEN-','MUSEUM'],"),
    ("{id:3,name:'Längen umrechnen',lines:['LÄNGEN','UMRECHNEN'],", "{id:3,name:'Prozent-Markt',lines:['PROZENT-','MARKT'],"),
    ("{id:4,name:'Flächen und Volumen',lines:['FLÄCHEN &','VOLUMEN'],", "{id:4,name:'Zeit-Observatorium',lines:['ZEIT-','OBSERVATORIUM'],"),
    ("{id:5,name:'Grössen berechnen',lines:['GRÖSSEN','BERECHNEN'],", "{id:5,name:'Faktencheck-Redaktion',lines:['FAKTENCHECK-','REDAKTION'],"),
    ("{id:6,name:'Genauigkeit üben',lines:['GENAUIGKEIT','ÜBEN'],", "{id:6,name:'Trainingsraum',lines:['TRAININGS-','RAUM'],"),
]
for old, new in names:
    sub(old, new)
for old, new in {"Vergleichen": "Waage-Werkstatt", "Darstellen": "Plus und Minus", "Runden": "Umkehr-Turm", "Überschlagen": "Zwei Schritte",
                 "Addieren und Subtrahieren": "Beide Seiten", "Multiplizieren": "Klammer-Mine", "Dividieren": "Proben-Labor", "Rechnung wählen": "Rätsel-Bibliothek",
                 "Messen": "Pyramiden-Museum", "Längen umrechnen": "Prozent-Markt", "Flächen und Volumen": "Zeit-Observatorium", "Grössen berechnen": "Faktencheck-Redaktion",
                 "Genauigkeit üben": "Trainingsraum"}.items():
    html = html.replace(f'title="{old}"', f'title="{new}"')
rx(r"(Messdaten verifiziert|Längen umgerechnet|Flächen und Volumen umgerechnet|Grössen berechnet) – Feld \d ist freigeschaltet!", "Quest abgeschlossen – die nächste Quest ist frei!", count=0)

rx(r'(<ul class="list-disc pl-5 text-slate-200 space-y-3 font-mono text-sm marker:text-yellow-600">).*?(</ul>)',
   '<ul class="list-disc pl-5 text-slate-200 space-y-3 font-mono text-sm marker:text-yellow-600">' + "".join(f"<li>{g}</li>" for g in content.LEARNING_GOALS) + "</ul>")
rx(r"<section><h3>Zahlen eingeben und runden</h3>.*?</section>",
   "<section><h3>Zahlen eingeben</h3><p>Schreibe nur die Zahl ins Feld. «x = 5» und «5» zählen beide. Negative Zahlen gibst du mit einem Minus ein, zum Beispiel -3. Dezimalpunkt und Dezimalkomma sind erlaubt. Zahlen ab 1'000 schreibst du mit Apostroph. Mache bei Gleichungen die Probe.</p></section>")
sub("<title>THE LEGEND OF DECIMALS</title>", "<title>THE LEGEND OF X</title>")
sub('aria-label="THE LEGEND OF DECIMALS"', 'aria-label="THE LEGEND OF X"')
sub('<span class="legend-logo-main">DECIMALS</span>', '<span class="legend-logo-main">X</span>')
sub('<span id="game-brand">THE LEGEND OF DECIMALS</span>', '<span id="game-brand">THE LEGEND OF X</span>')
sub('<p class="legend-author">developed by R. Behrens</p>', '<p class="legend-author">developed by R. Behrens · Inhalte mathbuch 3, LU 10/11: C. Heiss</p>')
sub('data-game-version="2.1"', 'data-game-version="LU 10/11"')
html = html.replace("The_Legend_of_Decimals", "The_Legend_of_X").replace("legend-of-decimals-file-targets", "legend-of-x-file-targets")
sub("name:'Komma-Könner',title:'Komma-Könner'", "name:'Variablen-Könner',title:'Variablen-Könner'")
sub("leuchtende Kommaspur.'", "leuchtende Spur.'")
sub("name:'Dezimal-Profi',title:'Dezimal-Profi'", "name:'Gleichungs-Profi',title:'Gleichungs-Profi'")
html = html.replace("Komma-Könner hinterlässt eine leuchtende Kommaspur", "Variablen-Könner hinterlässt eine leuchtende Spur").replace("Dezimal-Profi erhöht", "Gleichungs-Profi erhöht")
sub("maxPoints:{A:{1:7,2:8,3:8},B:{1:7,2:7,3:8},C:{1:5,2:6,3:7}}", "maxPoints:{A:{1:8,2:8,3:8},B:{1:8,2:8,3:8},C:{1:8,2:8,3:8}}")
sub("</head>", """<style>
.lu-chart { display:block; width:100%; max-width:460px; height:auto; margin:8px 0 12px; border-radius:4px; }
.lu-table { border-collapse:collapse; margin:8px 0 12px; background:#fff; color:#222; font-size:14px; }
.lu-table th,.lu-table td { border:1px solid #bbb; padding:4px 10px; text-align:right; }
.lu-table th:first-child,.lu-table td:first-child { text-align:left; }
</style>
</head>""")


# ---------- Fenstertitel, Fehlermeldungen, Bossintros ----------
for old, new in {"VERGLEICHEN": "WAAGE-WERKSTATT", "DARSTELLEN": "PLUS UND MINUS", "RUNDEN": "UMKEHR-TURM", "ÜBERSCHLAGEN": "ZWEI SCHRITTE",
                 "ADDIEREN UND SUBTRAHIEREN": "BEIDE SEITEN", "MULTIPLIZIEREN": "KLAMMER-MINE", "DIVIDIEREN": "PROBEN-LABOR", "RECHNUNG WÄHLEN": "RÄTSEL-BIBLIOTHEK",
                 "MESSEN": "PYRAMIDEN-MUSEUM", "LÄNGEN UMRECHNEN": "PROZENT-MARKT", "FLÄCHEN & VOLUMEN": "ZEIT-OBSERVATORIUM", "GRÖSSEN BERECHNEN": "FAKTENCHECK-REDAKTION",
                 "GENAUIGKEIT ÜBEN": "TRAININGSRAUM"}.items():
    for q in ('"', "'", "`"):
        html = html.replace(q + old + q, q + new + q)
    html = html.replace(">" + old + "<", ">" + new + "<")
html = html.replace('title="Längen Umrechnen"', 'title="Prozent-Markt"').replace('title="Grössen Berechnen"', 'title="Faktencheck-Redaktion"')
rx(r'(<p id="s[123]-m[1-6]-error" class="text-red-500 text-center hidden">)[^<]*(</p>)',
   lambda m: m.group(1) + "Noch nicht alles stimmt. Prüfe die rot markierten Antworten." + m.group(2), count=0)
sub("Hier trainierst du die Inhalte aus Chapter 3: Messen, Längen, Flächen, Volumen und Grössen berechnen.", "Hier trainierst du Gleichungen und Prozentrechnen.")
sub("zeige, dass du Dezimalzahlen sicher einschätzen kannst", "zeige, dass du Gleichungen sicher umformen kannst")
sub("Löse seine Rechenaufträge und bringe die Maschine aus dem Takt. Präzise Rechnungen", "Finde die Fehler in seinen Lösungswegen und bringe die Maschine aus dem Takt. Saubere Lösungswege")
sub("Prüfe Stellenwerte, Rechenzeichen und die verlangte Einheit.", "Prüfe Rechenzeichen und Vorzeichen.")
sub("Ein Überschlag hilft dir, die Grössenordnung einzuschätzen.", "Mache die Probe.")

# ---------- Theorieheft als einfaches PDF ----------
def make_pdf(title, sections):
    lines = [("B", 16, title), ("N", 10, "mathbuch 3, LU 11 Gleichungen lösen und LU 10 Alt und Jung"), ("N", 10, "")]
    for head, body in sections:
        lines.append(("B", 12, head))
        for b in body:
            for w in textwrap.wrap(b, 88):
                lines.append(("N", 11, w))
        lines.append(("N", 8, ""))
    pages, cur, y = [], [], 800
    for font, size, text in lines:
        if y < 50:
            pages.append(cur); cur, y = [], 800
        cur.append((font, size, y, text)); y -= size + 5
    pages.append(cur)
    esc = lambda s: s.encode("cp1252").replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
    objs = {1: b"<< /Type /Catalog /Pages 2 0 R >>",
            3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
            4: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"}
    kids, nxt = [], 5
    for page in pages:
        stream = b"BT\n" + b"".join(b"/F%s %d Tf 1 0 0 1 50 %d Tm (%s) Tj\n" % (b"2" if f == "B" else b"1", s, yy, esc(t)) for f, s, yy, t in page) + b"ET"
        objs[nxt] = b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents %d 0 R >>" % (nxt + 1)
        objs[nxt + 1] = b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream)
        kids.append(b"%d 0 R" % nxt); nxt += 2
    objs[2] = b"<< /Type /Pages /Kids [%s] /Count %d >>" % (b" ".join(kids), len(kids))
    out, offs = b"%PDF-1.4\n", {}
    for i in sorted(objs):
        offs[i] = len(out); out += b"%d 0 obj\n%s\nendobj\n" % (i, objs[i])
    xref = len(out); count = len(objs) + 1
    out += b"xref\n0 %d\n0000000000 65535 f \n" % count + b"".join(b"%010d 00000 n \n" % offs[i] for i in sorted(objs))
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (count, xref)
    return out


pdfs = {"C": content.PDF_COMMON, "B": content.PDF_COMMON + content.PDF_BA, "A": content.PDF_COMMON + content.PDF_BA + content.PDF_A}
payload = {k: base64.b64encode(make_pdf(f"Theoriemerkheft Niveau {k}", v)).decode() for k, v in pdfs.items()}
rx(r"const LEARNING_PDF_DATA=\{.*?\};", "const LEARNING_PDF_DATA=" + json.dumps(payload) + ";")

# ---------- Ausgabe ----------
OUT.mkdir(exist_ok=True)
for name in ("sprites", "assets"):
    if not (OUT / name).exists():
        shutil.copytree(SRC / name, OUT / name)
(OUT / "index.html").write_text(html, encoding="utf-8")
print("OK", len(html))
