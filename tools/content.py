# Aufgaben fuer den Umbau auf mathbuch 3, LU 11 und LU 10.
# C = Grundanspruch, B = Standard, A = Erweiterung. Loesungen werden berechnet.
import random
from fractions import Fraction as Fr


def n(v):
    v = Fr(v) if not isinstance(v, float) else Fr(str(v))
    neg = v < 0
    v = abs(v)
    if v.denominator == 1:
        s = str(v.numerator)
    else:
        s = f"{float(v):.6f}".rstrip("0")
    i, _, d = s.partition(".")
    i = f"{int(i):,}".replace(",", "'")
    return ("−" if neg else "") + i + ("." + d if d else "")


def ans(v):
    v = Fr(v) if not isinstance(v, float) else Fr(str(v))
    den = v.denominator
    while den % 2 == 0:
        den //= 2
    while den % 5 == 0:
        den //= 5
    assert den == 1, f"Antwort nicht abbrechend: {v}"
    return n(v).replace("−", "-")


def lin(a, b=0, v="x"):
    a, b = Fr(str(a)), Fr(str(b))
    s = ""
    if a != 0:
        s = v if a == 1 else "−" + v if a == -1 else n(a) + v
    if b != 0:
        s += (" + " + n(b) if b > 0 else " − " + n(-b)) if s else n(b)
    return s or "0"


def Y(year):
    return f'<span data-no-number-format>{year}</span>'


def b(s):
    return f"<strong>{s}</strong>"


def radio(rng, label, right, wrong, hint):
    opts = [right] + list(wrong)
    rng.shuffle(opts)
    return {"type": "radio", "label": label, "options": opts, "hint": hint}, opts.index(right)


def check(rng, label, items, hint):
    items = list(items)
    rng.shuffle(items)
    q = {"type": "checkbox", "label": label + "<br><br><strong>Mehrfachauswahl: Kreuze alle richtigen Aussagen an.</strong>",
         "options": [t for t, _ in items], "hint": hint}
    return q, [i for i, (_, ok) in enumerate(items) if ok]


def cloze(label, text, answers):
    return {"type": "cloze", "label": label, "text": text, "a": [[ans(x)] for x in answers]}, None


def level(items):
    return {"q": [q for q, _ in items], "a": [a for _, a in items]}


def num(text, value):
    return text, ans(value)


# ---------- Diagramme ----------
AGES = ['0–9', '10–19', '20–29', '30–39', '40–49', '50–59', '60–69', '70–79', '80+']


def pyramid(title, men, women, maxv, labels=False):
    W, H, mid, top, row, half = 460, 300, 230, 40, 25, 180
    p = [f'<svg class="lu-chart" data-no-number-format viewBox="0 0 {W} {H}" role="img" aria-label="{title}">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         f'<text x="{mid}" y="16" text-anchor="middle" font-size="13" font-weight="700" fill="#222">{title}</text>',
         f'<text x="{mid-110}" y="33" text-anchor="middle" font-size="11" fill="#2f5ea8">Männer</text>',
         f'<text x="{mid+110}" y="33" text-anchor="middle" font-size="11" fill="#c0503c">Frauen</text>']
    for v in range(0, maxv + 1, 50):
        d = v / maxv * half
        for x in (mid - 25 - d, mid + 25 + d):
            p.append(f'<line x1="{x:.1f}" y1="{top-3}" x2="{x:.1f}" y2="{top+row*9}" stroke="#ddd"/>')
            if v % 100 == 0:
                p.append(f'<text x="{x:.1f}" y="{top+row*9+12}" text-anchor="middle" font-size="9" fill="#555">{v}</text>')
    for i in range(9):
        y = top + row * (8 - i) + 3
        hh = row - 6
        wm, ww = men[i] / maxv * half, women[i] / maxv * half
        p.append(f'<rect x="{mid-25-wm:.1f}" y="{y}" width="{wm:.1f}" height="{hh}" fill="#2f5ea8"/>')
        p.append(f'<rect x="{mid+25}" y="{y}" width="{ww:.1f}" height="{hh}" fill="#c0503c"/>')
        p.append(f'<text x="{mid}" y="{y+hh-5}" text-anchor="middle" font-size="10" fill="#222">{AGES[i]}</text>')
        if labels:
            p.append(f'<text x="{mid-28-wm:.1f}" y="{y+hh-5}" text-anchor="end" font-size="9" fill="#222">{men[i]}</text>')
            p.append(f'<text x="{mid+28+ww:.1f}" y="{y+hh-5}" font-size="9" fill="#222">{women[i]}</text>')
    p.append(f'<text x="{mid}" y="{H-6}" text-anchor="middle" font-size="10" fill="#444">Anzahl Personen pro Altersklasse</text></svg>')
    return "".join(p)


def linechart(title, years, values, ylabel, lo, hi, step, labels=True):
    W, H, L, R, T, B = 460, 260, 54, 16, 30, 36
    X = lambda i: L + (W - L - R) * i / (len(years) - 1)
    Yp = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo))
    p = [f'<svg class="lu-chart" data-no-number-format viewBox="0 0 {W} {H}" role="img" aria-label="{title}">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         f'<text x="{W/2}" y="16" text-anchor="middle" font-size="13" font-weight="700" fill="#222">{title}</text>']
    v = lo
    while v <= hi:
        p.append(f'<line x1="{L}" y1="{Yp(v):.1f}" x2="{W-R}" y2="{Yp(v):.1f}" stroke="#ddd"/>')
        p.append(f'<text x="{L-5}" y="{Yp(v)+3:.1f}" text-anchor="end" font-size="9" fill="#555">{n(v)}</text>')
        v += step
    for i, y in enumerate(years):
        p.append(f'<text x="{X(i):.1f}" y="{H-B+14}" text-anchor="middle" font-size="9" fill="#555">{y}</text>')
    pts = " ".join(f"{X(i):.1f},{Yp(x):.1f}" for i, x in enumerate(values))
    p.append(f'<polyline points="{pts}" fill="none" stroke="#c0503c" stroke-width="2"/>')
    for i, x in enumerate(values):
        p.append(f'<circle cx="{X(i):.1f}" cy="{Yp(x):.1f}" r="3" fill="#c0503c"/>')
        if labels:
            anchor = "start" if i == 0 else "end" if i == len(years) - 1 else "middle"
            p.append(f'<text x="{X(i)+(3 if i == 0 else 0):.1f}" y="{Yp(x)-7:.1f}" text-anchor="{anchor}" font-size="9" fill="#222">{n(x)}</text>')
    p.append(f'<text x="{W/2}" y="{H-6}" text-anchor="middle" font-size="10" fill="#444">Jahr · {ylabel}</text></svg>')
    return "".join(p)


def table(head, rows):
    h = "".join(f"<th>{c}</th>" for c in head)
    r = "".join("<tr>" + "".join(f"<td>{c if isinstance(c, str) else n(c)}</td>" for c in row) + "</tr>" for row in rows)
    return f'<table class="lu-table"><tr>{h}</tr>{r}</table>'


def build():
    R = lambda key: random.Random(key)
    D = {}

    # ===== Chapter 1: LU 11, Grundlagen =====
    D["s1m1"] = {
        "intro": "<p>Bevor du Gleichungen löst, musst du Terme sicher berechnen.</p><p>Setze für x den angegebenen Wert ein. Es gilt: Klammern zuerst, dann Punkt vor Strich.</p><p>Beispiel: 3x + 2 für x = 4 ergibt 3 · 4 + 2 = 14.</p><p>Negative Ergebnisse kannst du mit - eingeben.</p>",
        "c": level([num("5 + 2 · 3 =", 11), num("10 − 3 · 2 =", 4), num("Berechne 3x + 2 für x = 4.", 14), num("Berechne 2x − 5 für x = 6.", 7), num("Berechne x + 8 für x = 7.", 15)]),
        "b": level([num("−3 + 8 =", 5), num("−2 · (−5) =", 10), num("Berechne 4x − 7 für x = −2.", -15), num("Berechne 2(x + 3) für x = 4.", 14), num("Berechne 5 − 3x für x = 3.", -4)]),
        "a": level([num("Berechne 2.5x − 1 für x = 4.", 9), num("Berechne −3(x − 2) für x = −1.", 9), num("Berechne x : 4 + 3 für x = −8.", 1), num("Berechne 3x − 2(x + 1) für x = 5.", 3), num("Berechne 0.5x + 1.5 für x = −3.", 0)]),
    }

    # Vergleich: Zeichen zwischen linker und rechter Waagschale
    def cmp_task(text, left, right):
        return {"text": text, "answer": "<" if left < right else ">" if left > right else "="}
    comparison = {
        "base": [cmp_task("x = 3: 2x + 1 ___ 8", 7, 8), cmp_task("x = 5: x + 4 ___ 9", 9, 9), cmp_task("x = 4: 3x ___ 10", 12, 10)],
        "c": [cmp_task("x = 2: 5x ___ 10", 10, 10), cmp_task("x = 6: x + 3 ___ 10", 9, 10), cmp_task("x = 7: 2x ___ 12", 14, 12)],
        "b": [cmp_task("x = −2: 3x + 4 ___ −2", -2, -2), cmp_task("x = −3: 2x ___ x − 1", -6, -4), cmp_task("x = 4: 2(x + 1) ___ 3x − 3", 10, 9)],
        "a": [cmp_task("x = −1.5: 2x + 5 ___ 2", 2, 2), cmp_task("x = 0.5: 4x − 3 ___ −2x", -1, -1), cmp_task("x = −2: 3(x − 1) ___ 2(x − 3)", -9, -10)],
    }

    D["m3"] = {
        "intro": "<p>Eine Gleichung ist wie eine Waage im Gleichgewicht. Was du auf einer Seite tust, musst du auch auf der anderen Seite tun.</p><p>Umformung mit + und −: x + 7 = 12 | − 7 ergibt x = 5.</p><p>Ziel: x steht am Schluss allein.</p>",
        "c": level([num("x + 7 = 12<br>x =", 5), num("x + 9 = 15<br>x =", 6), num("x − 4 = 11<br>x =", 15), num("x − 8 = 20<br>x =", 28), num("13 + x = 30<br>x =", 17)]),
        "b": level([num("x + 12 = 5<br>x =", -7), num("x − 6 = −14<br>x =", -8), num("−9 + x = 4<br>x =", 13), num("20 − x = 8<br>x =", 12), num("15 − x = 21<br>x =", -6)]),
        "a": level([num("x + 3.5 = 1.2<br>x =", -2.3), num("x − 2.75 = −4<br>x =", -1.25), num("7.2 − x = 9<br>x =", -1.8), num("x + 1/2 = 2<br>x = (als Dezimalzahl)", 1.5), num("x − 3/4 = 1/4<br>x =", 1)]),
    }
    D["m4"] = {
        "intro": "<p>Multiplikation und Division heben sich gegenseitig auf.</p><p>4x = 20 | : 4 ergibt x = 5.</p><p>x : 3 = 6 | · 3 ergibt x = 18.</p><p>Durch 0 darfst du nie dividieren.</p>",
        "c": level([num("4x = 20<br>x =", 5), num("7x = 63<br>x =", 9), num("x : 3 = 6<br>x =", 18), num("x : 5 = 12<br>x =", 60), num("12x = 144<br>x =", 12)]),
        "b": level([num("−4x = 20<br>x =", -5), num("6x = −42<br>x =", -7), num("x : (−3) = 5<br>x =", -15), num("−x = 9<br>x =", -9), num("8x = 12<br>x =", 1.5)]),
        "a": level([num("0.5x = 6<br>x =", 12), num("2.5x = −10<br>x =", -4), num("x : 0.2 = 15<br>x =", 3), num("−1.5x = −9<br>x =", 6), num("3/4 · x = 6<br>x =", 8)]),
    }
    D["m5"] = {
        "intro": "<p>Bei zwei Schritten gehst du rückwärts vor: zuerst + oder − entfernen, dann · oder : entfernen.</p><p>3x + 5 = 20 | − 5<br>3x = 15 | : 3<br>x = 5</p>",
        "c": level([num("2x + 3 = 11<br>x =", 4), num("3x + 5 = 20<br>x =", 5), num("4x − 7 = 13<br>x =", 5), num("5x − 2 = 28<br>x =", 6), num("x : 2 + 1 = 6<br>x =", 10)]),
        "b": level([num("3x + 14 = 2<br>x =", -4), num("2x − 9 = −15<br>x =", -3), num("−4x + 3 = 19<br>x =", -4), num("12 − 3x = 3<br>x =", 3), num("x : 4 − 5 = −2<br>x =", 12)]),
        "a": level([num("0.5x − 3 = 2<br>x =", 10), num("x : 3 + 4 = −1<br>x =", -15), num("−3x + 5 = −7<br>x =", 4), num("12 − 2x = 18<br>x =", -3), num("1.5x + 0.5 = 5<br>x =", 3)]),
    }

    def krabbor(lvl):
        r = R("krabbor" + lvl)
        q1 = radio(r, "Krabbor löst x + 7 = 12 so: «Ich rechne + 7 und erhalte x = 19.»<br><br>Was muss er richtig machen?",
                   "Auf beiden Seiten 7 subtrahieren, dann ist x = 5.", ["Auf beiden Seiten 12 subtrahieren, dann ist x = 7.", "Nur links 7 subtrahieren, rechts bleibt alles gleich."],
                   "Welche Rechnung hebt «+ 7» auf?")
        q2 = check(r, "Welche Umformungen ändern die Lösung einer Gleichung <strong>nicht</strong>?", [
            ("Auf beiden Seiten 3 addieren.", True), ("Beide Seiten mit 2 multiplizieren.", True), ("Beide Seiten durch −1 dividieren.", True),
            ("Nur auf der linken Seite 3 subtrahieren.", False), ("Beide Seiten durch 0 dividieren.", False)],
            "Eine Umformung muss auf beiden Seiten gleich sein. Durch 0 darf nie dividiert werden.")
        q3 = radio(r, "Krabbor löst −4x = 20 und behauptet: «x = 5.»<br><br>Welche Aussage stimmt?",
                   "Falsch: Durch −4 geteilt ergibt x = −5.", ["Richtig: 20 : 4 = 5.", "Falsch: Es gilt x = 80."],
                   "Setze deine Lösung zur Kontrolle in −4x ein.")
        q4 = radio(r, "Krabbor rechnet bei 3x + 6 = 21 zuerst «: 3» und schreibt x + 6 = 7.<br><br>Wo liegt sein Denkfehler?",
                   "Er hat nur 3x durch 3 geteilt. Auch die 6 muss geteilt werden: x + 2 = 7.", ["Man darf nie durch 3 teilen.", "Die Umformung ist richtig, die Lösung ist x = 1."],
                   "Beim Dividieren wird jeder Summand einer Seite geteilt.")
        return level({"c": [q1, q2], "b": [q1, q2, q3], "a": [q1, q2, q3, q4]}[lvl])
    D["s1m6"] = {"intro": "<p>Decke Krabbors Denkfehler auf.</p>", "c": krabbor("c"), "b": krabbor("b"), "a": krabbor("a")}

    # ===== Chapter 2: LU 11, Vertiefung =====
    D["s2m1"] = {
        "intro": "<p>Gleichartige Glieder darfst du zusammenfassen: 3x + 2x = 5x.</p><p>Klammern löst du auf, indem du jedes Glied multiplizierst: 4(x + 3) = 4x + 12.</p>",
        "c": level([num("3x + 2x = ___x", 5), num("7x − 4x = ___x", 3), num("4(x + 3) = 4x + ___", 12), num("2(x + 5) = 2x + ___", 10)]),
        "b": level([num("5x − 8x = ___x", -3), num("3(x − 4) = 3x − ___", 12), num("−2(x + 3) = −2x − ___", 6), num("2x + 5 + 3x − 1 = 5x + ___", 4)]),
        "a": level([num("2.5x − 4x = ___x", -1.5), num("−3(x − 4) = −3x + ___", 12), num("2(x + 1) − (x − 3) = x + ___", 5), num("4x − 2(x − 5) = 2x + ___", 10)]),
    }

    def both(a, s, c, x):
        return num(f"{lin(a, s)} = {lin(c, (a-c)*x + s)}<br>x =", x)
    D["s2m2"] = {
        "intro": "<p>Steht x auf beiden Seiten, bringst du zuerst alle x auf eine Seite.</p><p>5x + 2 = 3x + 10 | − 3x<br>2x + 2 = 10 | − 2<br>2x = 8 | : 2<br>x = 4</p>",
        "c": level([both(5, 2, 3, 4), both(4, 1, 1, 3), both(6, 3, 2, 5), both(3, 7, 2, 2), both(7, -2, 4, 6)]),
        "b": level([both(5, -3, 2, -4), both(3, 8, 7, -2), both(6, -5, 8, 3), both(2, 9, -3, -1), both(4, -7, 9, -3)]),
        "a": level([both(Fr(5, 2), 3, Fr(1, 2), -2), both(Fr(3, 2), -4, 3, -6), both(-2, 5, 3, Fr(1, 2)), both(Fr(1, 2), 7, Fr(5, 2), 4), both(4, Fr(3, 2), 2, Fr(-1, 2))]),
    }

    def kl1(a, s, x):
        return num(f"{a}({lin(1, s)}) = {n(a*(x+s))}<br>x =", x)

    def kl2(a, s, c, x):
        return num(f"{a}({lin(1, s)}) = {lin(c, a*(x+s)-c*x)}<br>x =", x)

    def kl3(a, s, c, d, e, x):
        assert a - c - e != 0
        return num(f"{a}({lin(1, s)}) − {c}({lin(1, -d)}) = {lin(e, a*(x+s)-c*(x-d)-e*x)}<br>x =", x)
    D["s2m3"] = {
        "intro": "<p>Löse zuerst die Klammern auf. Multipliziere jedes Glied in der Klammer.</p><p>3(x + 2) = x + 14<br>3x + 6 = x + 14 | − x<br>2x + 6 = 14 | − 6<br>2x = 8 | : 2<br>x = 4</p><p>Achtung: Ein Minus vor der Klammer ändert alle Vorzeichen in der Klammer.</p>",
        "c": level([kl1(3, 2, 5), kl1(4, 1, 3), kl1(2, -3, 8), kl1(5, 2, 1), kl1(6, -1, 4)]),
        "b": level([kl2(3, 2, 1, 4), kl2(2, -4, 5, 3), kl2(4, 3, 1, -2), kl2(5, -2, 2, 6), kl2(3, -5, 7, -1)]),
        "a": level([kl3(4, 2, 2, 3, 1, 3), kl3(5, -1, 3, 2, 1, -4), kl3(3, 4, 2, -1, 4, 2), kl3(6, 1, 2, 5, 1, -2), kl3(4, -3, 3, 2, 2, 5)]),
    }

    def probe_vals(lbl, eq, k, left, right):
        return cloze(lbl, f"Setze x = {n(k)} in {eq} ein.<br>Linke Seite: *l* Rechte Seite: *r*", [left, right])

    def probe_judge(r, eq, k, ok, sol):
        right = f"Ja, x = {n(k)} stimmt." if ok else f"Nein, x = {n(k)} stimmt nicht."
        wrong = f"Nein, x = {n(k)} stimmt nicht." if ok else f"Ja, x = {n(k)} stimmt."
        return radio(r, f"Mache die Probe: Ist x = {n(k)} die Lösung von {eq}?", right, [wrong, "Das lässt sich ohne Lösungsweg nicht entscheiden."],
                     f"Setze x = {n(k)} auf beiden Seiten ein und vergleiche die Werte. {sol}")
    r = R("probe")
    D["s2m4"] = {
        "intro": "<p>Mit der Probe kontrollierst du jede Lösung selbst: Setze den Wert für x in die ursprüngliche Gleichung ein und berechne beide Seiten getrennt. Sind beide Seiten gleich, stimmt die Lösung.</p>",
        "c": level([probe_vals("Probe", "2x + 3 = 11", 4, 11, 11), probe_vals("Probe", "5x − 2 = 13", 3, 13, 13), probe_judge(r, "3x + 1 = 16", 5, True, ""), probe_judge(r, "4x − 3 = 21", 5, False, ""), probe_vals("Probe", "x + 9 = 2x + 4", 5, 14, 14)]),
        "b": level([probe_vals("Probe", "3x − 4 = x + 6", 5, 11, 11), probe_vals("Probe", "2x + 7 = 5x − 2", 2, 11, 8), probe_judge(r, "4x + 3 = 2x − 5", -4, True, ""), probe_judge(r, "6 − x = 2x + 9", 1, False, ""), probe_vals("Probe", "5x − 3 = 2x + 9", 4, 17, 17)]),
        "a": level([probe_vals("Probe", "3(x − 2) = x + 4", 5, 9, 9), probe_vals("Probe", "2(x + 3) = 4x − 5", -1, 4, -9), probe_judge(r, "4(x + 1) − 2x = 3x + 7", -3, True, ""), probe_judge(r, "0.5x + 2 = 2(x − 1)", 2, False, ""), probe_vals("Probe", "2.5x − 1 = x + 2", 2, 4, 4)]),
    }

    r = R("raetsel")
    D["s2m5"] = {
        "intro": "<p>So übersetzt du einen Text in eine Gleichung:</p><p>1. Lege fest, was x bedeutet.<br>2. Schreibe den Text Schritt für Schritt als Term auf.<br>3. Löse die Gleichung und mache die Probe.</p><p>Wird zuerst addiert und danach multipliziert, braucht es eine Klammer.</p>",
        "c": level([
            radio(r, "«Ich denke mir eine Zahl. Ich multipliziere sie mit 3 und addiere 4. Ich erhalte 19.»<br>Welche Gleichung passt?", "3x + 4 = 19", ["3(x + 4) = 19", "3x − 4 = 19", "x + 3 · 4 = 19"], "Was passiert zuerst mit x?"),
            num("Löse das Rätsel oben: Die gedachte Zahl heisst", 5),
            radio(r, "«Das Doppelte einer Zahl vermindert um 5 ergibt 11.»<br>Welche Gleichung passt?", "2x − 5 = 11", ["2(x − 5) = 11", "5 − 2x = 11", "2x + 5 = 11"], "«Vermindert um 5» bedeutet: 5 subtrahieren."),
            num("Löse das zweite Rätsel: Die Zahl heisst", 8)]),
        "b": level([
            num("«Ich addiere zu einer Zahl 6 und multipliziere das Ergebnis mit 4. Ich erhalte 44.»<br>Die Zahl heisst", 5),
            num("«Das Fünffache einer Zahl vermindert um 7 ergibt 28.»<br>Die Zahl heisst", 7),
            num("«Wenn ich vom Dreifachen einer Zahl 8 subtrahiere, erhalte ich das Doppelte der Zahl plus 1.»<br>Die Zahl heisst", 9),
            radio(r, "«Eine Zahl wird um 3 vergrössert. Das Ergebnis wird halbiert. Man erhält 7.»<br>Welche Gleichung passt?", "(x + 3) : 2 = 7", ["x + 3 : 2 = 7", "2(x + 3) = 7", "x : 2 + 3 = 7"], "Zuerst wird vergrössert, dann halbiert.")]),
        "a": level([
            num("Eine Mutter ist 4-mal so alt wie ihre Tochter. Zusammen sind sie 55 Jahre alt.<br>Die Tochter ist (in Jahren)", 11),
            num("Die Summe von drei aufeinanderfolgenden natürlichen Zahlen ist 96.<br>Die kleinste Zahl heisst", 31),
            num("Lena ist 3 Jahre älter als Tim. Mia ist doppelt so alt wie Tim. Zusammen sind die drei 47 Jahre alt.<br>Tim ist (in Jahren)", 11),
            num("Ein Vater ist heute 38 Jahre alt. In 4 Jahren ist er doppelt so alt wie sein Sohn.<br>Der Sohn ist heute (in Jahren)", 17)]),
    }

    def steps(lines):
        return "".join(f"<br>Zeile {i+1}: {t}" for i, t in enumerate(lines))
    r = R("detektiv")

    def fehler(eq_lines, wrong_line, hint):
        n_lines = len(eq_lines)
        opts = [f"Zeile {i}" for i in range(2, n_lines + 1)]
        return {"type": "radio", "label": "In welcher Zeile steckt der Fehler?" + steps(eq_lines), "options": opts, "hint": hint}, wrong_line - 2
    D["s2m6"] = {
        "intro": "<p>Prüfe jede Zeile: Wurde die Umformung auf beiden Seiten richtig ausgeführt? Wurde bei Klammern jedes Glied multipliziert?</p><p>Eine Probe mit dem Endergebnis zeigt dir, ob der Lösungsweg stimmen kann.</p>",
        "c": level([
            fehler(["5x + 2 = 3x + 10 | − 3x", "8x + 2 = 10 | − 2", "8x = 8 | : 8", "x = 1"], 2, "5x − 3x ist nicht 8x."), num("Richtige Lösung von 5x + 2 = 3x + 10: x =", 4),
            fehler(["4x + 6 = 2x + 14 | − 2x", "2x + 6 = 14 | − 6", "2x = 20 | : 2", "x = 10"], 3, "14 − 6 ist nicht 20."), num("Richtige Lösung von 4x + 6 = 2x + 14: x =", 4)]),
        "b": level([
            fehler(["7x − 4 = 3x + 12 | − 3x", "4x − 4 = 12 | + 4", "4x = 8 | : 4", "x = 2"], 3, "Beim Addieren von 4 wird 12 + 4 gerechnet."), num("Richtige Lösung von 7x − 4 = 3x + 12: x =", 4),
            fehler(["3x + 5 = 6x − 7 | − 6x", "−3x + 5 = −7 | − 5", "−3x = −12 | : (−3)", "x = −4"], 4, "Minus geteilt durch Minus ergibt Plus."), num("Richtige Lösung von 3x + 5 = 6x − 7: x =", 4)]),
        "a": level([
            fehler(["3(x + 4) = x + 18 | Klammer auflösen", "3x + 4 = x + 18 | − x", "2x + 4 = 18 | − 4", "2x = 14 | : 2", "x = 7"], 2, "Auch die 4 in der Klammer wird mit 3 multipliziert."), num("Richtige Lösung von 3(x + 4) = x + 18: x =", 3),
            fehler(["5x − 2(x − 3) = 18 | Klammer auflösen", "5x − 2x − 6 = 18 | zusammenfassen", "3x − 6 = 18 | + 6", "3x = 24 | : 3", "x = 8"], 2, "Minus mal Minus ergibt Plus: − 2 · (− 3) = + 6."), num("Richtige Lösung von 5x − 2(x − 3) = 18: x =", 4)]),
    }

    # ===== Chapter 3: LU 10 =====
    D["s3m1"] = {
        "intro": "<p>Eine <strong>absolute</strong> Angabe nennt eine Anzahl, zum Beispiel 200 Personen. Eine <strong>relative</strong> Angabe nennt einen Anteil, zum Beispiel 25 %.</p><p>Anteil in % = Teil : Ganzes · 100</p>",
        "c": level([num("25 % von 80 =", 20), num("10 % von 350 =", 35), num("30 von 120 sind ___ %", 25), num("0.4 = ___ %", 40), num("3/4 = ___ %", 75)]),
        "b": level([num("15 % von 240 =", 36), num("8 % von 1'500 =", 120), num("54 von 300 sind ___ %", 18), num("1/8 = ___ %", 12.5), num("20 % sind 90. Das Ganze ist", 450)]),
        "a": level([num("12.5 % von 4'800 =", 600), num("117 von 650 sind ___ %", 18), num("35 % sind 420. Das Ganze ist", 1200), num("Von 800 auf 1'000: Zunahme um ___ %", 25), num("Von 1'000 auf 800: Abnahme um ___ %", 20)]),
    }

    M1 = [150, 200, 250, 250, 300, 250, 200, 100, 50]
    W1 = [150, 200, 200, 300, 300, 250, 200, 150, 100]
    M2 = [340, 310, 290, 260, 220, 170, 120, 70, 20]
    W2 = [330, 300, 280, 250, 230, 190, 150, 100, 40]
    M3 = [160, 180, 210, 260, 310, 330, 280, 180, 50]
    W3 = [150, 170, 200, 250, 310, 340, 300, 220, 100]
    pc = pyramid("Alterspyramide Talwil (fiktive Daten)", M1, W1, 300)
    pb = pyramid("Alterspyramide Seedorf (fiktive Daten)", M2, W2, 350, True)
    pa = pyramid("Alterspyramide Bergmatt (fiktive Daten)", M3, W3, 350, True)
    r = R("pyramide")
    ta, ga = sum(M3) + sum(W3), sum(M3[6:]) + sum(W3[6:])
    assert ta == 4000
    ym = sum(M3[:2]) + sum(W3[:2])
    D["s3m2"] = {
        "intro": "<p>Eine Alterspyramide zeigt, wie viele Männer (links) und Frauen (rechts) in jeder Altersklasse leben.</p><p>Pyramide: viele Junge, wenige Alte. Glocke: ähnlich viele bis ins mittlere Alter. Urne: weniger Junge als Personen mittleren Alters.</p><p>Alle Gemeinden und Zahlen sind erfunden.</p>",
        "c": level([
            cloze("Ablesen", pc + "<br>Wie viele Frauen sind 30–39 Jahre alt? *a*", [W1[3]]),
            cloze("Ablesen", pc + "<br>Wie viele Männer sind 0–9 Jahre alt? *a*", [M1[0]]),
            radio(r, pc + "<br>In welcher Altersklasse leben am meisten Männer?", "40–49 Jahre", ["0–9 Jahre", "30–39 Jahre", "70–79 Jahre"], "Suche den längsten Balken links."),
            cloze("Addieren", pc + "<br>Wie viele Personen sind 80 Jahre oder älter? *a*", [M1[8] + W1[8]]),
            radio(r, pc + "<br>In welcher Altersklasse leben mehr Frauen als Männer?", "70–79 Jahre", ["20–29 Jahre", "40–49 Jahre", "60–69 Jahre"], "Vergleiche beide Balken einer Zeile.")]),
        "b": level([
            radio(r, pb + "<br>Welche Form hat diese Alterspyramide?", "Pyramide", ["Glocke", "Urne"], "Vergleiche die untersten mit den obersten Balken."),
            cloze("Addieren", pb + "<br>Wie viele Personen sind 20–29 Jahre alt? *a*", [M2[2] + W2[2]]),
            cloze("Zählen", pb + "<br>In wie vielen Altersklassen leben mehr Frauen als Männer? *a*", [sum(1 for m, w in zip(M2, W2) if w > m)]),
            cloze("Addieren", pb + "<br>Wie viele Personen sind jünger als 20 Jahre? *a*", [sum(M2[:2]) + sum(W2[:2])]),
            cloze("Addieren", pb + "<br>Wie viele Personen sind 60 Jahre oder älter? *a*", [sum(M2[6:]) + sum(W2[6:])])]),
        "a": level([
            radio(r, pa + "<br>Welche Form hat diese Alterspyramide?", "Urne", ["Pyramide", "Glocke"], "Vergleiche die untersten Balken mit den Balken der 40- bis 69-Jährigen."),
            cloze("Gesamtzahl", pa + "<br>Wie viele Personen leben insgesamt in Bergmatt? *a*", [ta]),
            cloze("Anteil", pa + f"<br>Wie viel Prozent der Bevölkerung sind jünger als 20 Jahre? Das sind {n(ym)} von {n(ta)} Personen. *a* %", [Fr(ym * 100, ta)]),
            cloze("Anzahl", pa + "<br>Wie viele Personen sind 60 Jahre oder älter? *a*", [ga]),
            radio(r, pa + "<br>Welche Aussage folgt direkt aus diesem Diagramm?", "Es leben mehr 50- bis 59-Jährige als 0- bis 19-Jährige.", ["Die Geburtenzahl wird weiter sinken.", "Viele Junge sind weggezogen.", "Die Frauen werden überall älter als die Männer."], "Das Diagramm zeigt Anzahlen, keine Gründe und keine Zukunft.")]),
    }

    r = R("markt")
    t1 = table(["", "Einwohner total", "davon über 65"], [["Gemeinde A", 10000, 1600], ["Gemeinde B", 4000, 800]])
    D["s3m3"] = {
        "intro": "<p>Die grössere Anzahl bedeutet nicht automatisch den grösseren Anteil.</p><p>Berechne immer: Anteil = Teil : Ganzes. Veränderung in % = (neu − alt) : alt · 100.</p><p>Alle Zahlen sind erfunden.</p>",
        "c": level([num("In Talwil leben 2'000 Personen. 300 sind über 65 Jahre alt. Das sind ___ %", 15), num("In Seedorf leben 500 Personen. 100 sind jünger als 20 Jahre. Das sind ___ %", 20), num("In Grünau leben 4'000 Personen. 25 % sind über 65. Das sind ___ Personen", 1000), num("In Hohfluh leben 800 Personen. 10 % sind unter 10 Jahre alt. Das sind ___ Personen", 80),
                    radio(r, "«150 Personen» ist eine …", "absolute Angabe", ["relative Angabe", "Prozentangabe"], "Absolut = Anzahl, relativ = Anteil.")]),
        "b": level([num("In Talwil leben 3'600 Personen. 18 % sind über 65. Das sind ___ Personen", 648), num("In Bergmatt sind 240 Personen unter 10 Jahre alt. Das sind 8 % der Bevölkerung. Bergmatt hat ___ Einwohner", 3000), num("Von 6'000 Personen sind 1'080 über 65. Das sind ___ %", 18),
                    radio(r, t1 + "In welcher Gemeinde ist der <strong>Anteil</strong> der über 65-Jährigen grösser?", "Gemeinde B", ["Gemeinde A", "Beide gleich"], "Rechne für beide Gemeinden den Anteil in Prozent aus."),
                    radio(r, t1 + "In welcher Gemeinde ist die <strong>Anzahl</strong> der über 65-Jährigen grösser?", "Gemeinde A", ["Gemeinde B", "Beide gleich"], "Hier zählt die Anzahl, nicht der Anteil.")]),
        "a": level([num("Die Zahl der Jugendlichen sinkt von 1'200 auf 900. Abnahme um ___ %", 25), num("Die Zahl der über 80-Jährigen steigt von 250 auf 400. Zunahme um ___ %", 60), num("Gemeinde A: 1'600 von 10'000. Gemeinde B: 800 von 4'000. Der Anteil in B ist um ___ Prozentpunkte grösser", 4),
                    num("Ein Anteil steigt von 10 % auf 15 %. Das sind ___ Prozentpunkte mehr", 5),
                    radio(r, "Ein Anteil steigt von 10 % auf 15 %. Welche Aussage stimmt?", "Der Anteil ist um 5 Prozentpunkte beziehungsweise um 50 % gestiegen.", ["Der Anteil ist um 5 % gestiegen.", "Der Anteil ist um 15 % gestiegen.", "Die Anzahl Personen ist sicher um 50 % gestiegen."], "Prozentpunkte vergleichen zwei Prozentwerte direkt. Die Veränderung in % bezieht sich auf den alten Wert.")]),
    }

    yrs = [1970, 1980, 1990, 2000, 2010, 2020]
    ew = [2400, 2800, 3100, 3100, 3500, 4200]
    alt = [10, 11, 13, 15, 18, 22]
    geb = [380, 320, 300, 260, 240, 250]
    lew = linechart("Einwohner einer Gemeinde (fiktiv)", yrs, ew, "Einwohner", 2000, 4500, 500)
    lalt = linechart("Anteil über 65-Jährige in % (fiktiv)", yrs, alt, "Anteil in %", 8, 24, 4)
    lgeb = linechart("Geburten pro Jahr in einer Region (fiktiv)", yrs, geb, "Geburten", 200, 400, 50)
    r = R("zeit")
    D["s3m4"] = {
        "intro": "<p>Ein Liniendiagramm zeigt eine Entwicklung über die Zeit. Lies zuerst Titel und Achsen.</p><p>Veränderung = späterer Wert − früherer Wert. Je steiler die Linie, desto schneller die Veränderung. Abnahmen gibst du mit Minus an.</p>",
        "c": level([
            cloze("Ablesen", lew + f"<br>Wie viele Einwohner hatte die Gemeinde im Jahr {Y(1990)}? *a*", [3100]),
            cloze("Ablesen", lew + f"<br>Wie viele Einwohner hatte die Gemeinde im Jahr {Y(2020)}? *a*", [4200]),
            cloze("Unterschied", lew + f"<br>Um wie viele Einwohner wuchs die Gemeinde von {Y(2010)} bis {Y(2020)}? *a*", [700]),
            radio(r, lew + f"<br>Zwischen welchen Jahren blieb die Einwohnerzahl gleich?", f"{Y(1990)} und {Y(2000)}", [f"{Y(1970)} und {Y(1980)}", f"{Y(2000)} und {Y(2010)}"], "Suche das waagrechte Stück der Linie."),
            cloze("Ablesen", lalt + f"<br>Wie gross war der Anteil im Jahr {Y(2010)}? *a* %", [18])]),
        "b": level([
            cloze("Veränderung", lgeb + f"<br>Veränderung der Geburten von {Y(1970)} bis {Y(2010)}: *a*", [-140]),
            cloze("Veränderung", lgeb + f"<br>Veränderung der Geburten von {Y(2010)} bis {Y(2020)}: *a*", [10]),
            radio(r, lew + "<br>In welchem Zeitraum war die Zunahme am grössten?", f"{Y(2010)} bis {Y(2020)}", [f"{Y(1970)} bis {Y(1980)}", f"{Y(1980)} bis {Y(1990)}", f"{Y(2000)} bis {Y(2010)}"], "Berechne die Unterschiede benachbarter Punkte."),
            cloze("Veränderung", lalt + f"<br>Um wie viele Prozentpunkte stieg der Anteil von {Y(1970)} bis {Y(2020)}? *a*", [12]),
            radio(r, lgeb + "<br>Welche Beschreibung passt?", f"Die Geburten sanken bis {Y(2010)} und stiegen danach leicht.", ["Die Geburten sanken ständig.", "Die Geburten stiegen ständig.", "Die Geburten blieben ungefähr gleich."], "Betrachte auch den letzten Abschnitt der Linie.")]),
        "a": level([
            cloze("Durchschnitt", lew + f"<br>Durchschnittliche Zunahme pro Jahr von {Y(1970)} bis {Y(2020)}: *a* Einwohner", [Fr(1800, 50)]),
            cloze("Durchschnitt", lalt + f"<br>Durchschnittliche Zunahme pro Jahrzehnt von {Y(1970)} bis {Y(2020)}: *a* Prozentpunkte", [Fr(12, 5)]),
            cloze("Prozent", lew + f"<br>Zunahme der Einwohner von {Y(1970)} bis {Y(2020)} in Prozent: *a* %", [75]),
            radio(r, lalt + "<br>Welche Aussage stimmt?", "Der Anteil hat sich von 10 % auf 22 % mehr als verdoppelt.", ["Der Anteil stieg in jedem Jahrzehnt gleich stark.", "Der Anteil sank zwischendurch.", "Die Anzahl der über 65-Jährigen hat sich sicher verdoppelt."], "Prüfe die Unterschiede und unterscheide Anteil und Anzahl."),
            radio(r, lew + f"<br>Darf man aus dem Diagramm schliessen, dass die Gemeinde {Y(2030)} genau 4'900 Einwohner hat?", "Nein, das Diagramm zeigt nur die Vergangenheit. Eine Fortsetzung bleibt eine Annahme.", ["Ja, die Linie steigt immer gleich.", "Ja, denn die Zunahme beträgt immer 700."], "Eine Prognose braucht zusätzliche Annahmen.")]),
    }

    MC = ["Die Aussage stimmt.", "Die Aussage stimmt nicht.", "Mit diesen Daten nicht überprüfbar."]

    def fact(rng_unused, tbl, claim, truth, hint):
        return {"type": "radio", "label": f"{tbl}<strong>«{claim}»</strong>", "options": MC, "hint": hint}, truth
    tb = table(["Gemeinde Talwil", Y(2010), Y(2020)], [["Einwohner total", 5000, 6000], ["davon über 65", 800, 1080]])
    tc = table(["Gemeinde Seedorf", Y(2014), Y(2024)], [["Jugendliche (10–19)", 600, 300], ["über 80-Jährige", 120, 200]])
    r = R("fakten")

    def crit(head, good, bad):
        return radio(r, f"Schlagzeile: <strong>«{head}»</strong><br>Welche Frage hilft, die Schlagzeile mit Daten zu prüfen?", good, bad, "Eine statistische Frage fragt nach Zahlen, Anteilen, Zeiträumen oder Quellen.")
    D["s3m5"] = {
        "intro": "<p>Prüfe Aussagen mit den Daten. Unterscheide:</p><p>Stimmt die Aussage? Stimmt sie nicht? Oder sagen die Daten dazu gar nichts, zum Beispiel über Gründe?</p><p>Alle Zahlen sind erfunden.</p>",
        "c": level([
            fact(r, tc, "Die Anzahl der Jugendlichen hat sich halbiert.", 0, "Halbiert heisst: 600 : 2."),
            fact(r, tc, "Die Anzahl der über 80-Jährigen hat sich verdoppelt.", 1, "Verdoppelt hiesse: 120 · 2."),
            fact(r, tb, f"In Talwil leben {Y(2020)} mehr Personen als {Y(2010)}.", 0, "Vergleiche die erste Zeile."),
            fact(r, tb, "Die Anzahl der über 65-Jährigen ist gesunken.", 1, "Vergleiche die zweite Zeile."),
            fact(r, tc, "Die Jugendlichen sind weggezogen, weil Lehrstellen fehlen.", 2, "Zeigt die Tabelle Gründe?")]),
        "b": level([
            fact(r, tb, "Der Anteil der über 65-Jährigen ist gestiegen.", 0, "Früher 800 von 5'000, später 1'080 von 6'000."),
            fact(r, tb, f"Der Anteil der über 65-Jährigen beträgt {Y(2020)} genau 20 %.", 1, "Rechne 1'080 : 6'000."),
            fact(r, tb, "Die Bevölkerung wuchs um 20 %.", 0, "Zunahme 1'000 im Verhältnis zu 5'000."),
            fact(r, tb, "Viele junge Familien sind weggezogen.", 2, "Zeigt die Tabelle Umzüge?"),
            crit("Immer mehr alte Menschen!", "Ist nur die Anzahl oder auch der Anteil gestiegen, und in welchem Zeitraum?", ["Warum schreibt die Zeitung so etwas?", "Sind alte Menschen glücklich?", "Wie heisst die Journalistin?"])]),
        "a": level([
            fact(r, tb, "Die Anzahl der über 65-Jährigen stieg um 35 %.", 0, "Zunahme 280 im Verhältnis zu 800."),
            fact(r, tb, "Der Anteil der über 65-Jährigen stieg um 35 %.", 1, "Der Anteil stieg von 16 % auf 18 %."),
            fact(r, tc, "Die Gesamtbevölkerung von Seedorf ist gesunken.", 2, "Enthält die Tabelle die Gesamtbevölkerung?"),
            crit("Jugendliche verschwinden aus den Dörfern!", "Wie viele Jugendliche lebten früher und heute dort, und wie gross ist ihr Anteil?", ["Ist das Dorf schön?", "Welche Zeitung hat das geschrieben?", "Wollen Jugendliche lieber in der Stadt wohnen?"]),
            crit("Geburten brechen ein – die Schweiz stirbt aus!", "Um wie viel sind die Geburten gesunken, und wie entwickelt sich die Gesamtbevölkerung?", ["Ist die Schlagzeile übertrieben?", "Wollen die Leute keine Kinder mehr?", "Wie viele Kinder hat die Journalistin?"])]),
    }
    return D, comparison


LEARNING_GOALS = [
    "LZ1: Gleichungen mit Äquivalenzumformungen lösen, auch mit Klammern und mit x auf beiden Seiten.",
    "LZ2: Eine Lösung mit der Probe überprüfen.",
    "LZ3: Sachsituationen und Zahlenrätsel in Gleichungen übersetzen.",
    "LZ4: Lösungsschritte dokumentieren und Fehler in Lösungswegen finden.",
    "LZ5: Alterspyramiden lesen und interpretieren.",
    "LZ6: Absolute und relative Angaben unterscheiden und berechnen.",
    "LZ7: Entwicklungen aus Tabellen und Graphen ablesen und beschreiben.",
    "LZ8: Statistische Aussagen mit Daten prüfen und kritische Fragen stellen.",
]

# Abschnitte der Theoriehefte: (Titel, Zeilen). Niveau: alle / nur B und A / nur A.
PDF_COMMON = [
    ("Gleichungen umformen", ["Was du auf einer Seite tust, tust du auch auf der anderen Seite.", "x + 7 = 12 | - 7   ergibt   x = 5", "4x = 20 | : 4   ergibt   x = 5", "x : 3 = 6 | · 3   ergibt   x = 18"]),
    ("Zwei Schritte", ["Zuerst + oder - entfernen, dann · oder : entfernen.", "3x + 5 = 20 | - 5", "3x = 15 | : 3", "x = 5"]),
    ("x auf beiden Seiten", ["Bringe zuerst alle x auf eine Seite.", "5x + 2 = 3x + 10 | - 3x", "2x + 2 = 10 | - 2", "2x = 8 | : 2", "x = 4"]),
    ("Klammern", ["Jedes Glied in der Klammer wird multipliziert.", "3(x + 2) = 3x + 6"]),
    ("Probe", ["Setze die Lösung in die ursprüngliche Gleichung ein.", "Sind beide Seiten gleich, stimmt die Lösung.", "Beispiel: 2x + 3 = 11 mit x = 4. Links 2 · 4 + 3 = 11, rechts 11."]),
    ("Text in Gleichung übersetzen", ["1. Festlegen, was x bedeutet.  2. Text als Term schreiben.  3. Lösen und Probe machen."]),
    ("Alterspyramiden", ["Links Männer, rechts Frauen, jede Zeile eine Altersklasse.", "Pyramide: viele Junge. Glocke: ähnlich viele bis ins mittlere Alter. Urne: wenige Junge."]),
    ("Absolut und relativ", ["Absolut = Anzahl. Relativ = Anteil.", "Anteil in % = Teil : Ganzes · 100.  Beispiel: 300 von 2'000 sind 15 %."]),
    ("Graphen lesen", ["Zuerst Titel und Achsen lesen. Veränderung = späterer Wert - früherer Wert."]),
    ("Aussagen prüfen", ["Stimmt die Aussage, stimmt sie nicht, oder sagen die Daten gar nichts dazu?", "Daten zeigen meistens keine Gründe. Frage nach Zahlen, Anteilen, Zeiträumen und Quellen."]),
]
PDF_BA = [
    ("Negative Zahlen und Minus vor der Klammer", ["-4x = 20 | : (-4)   ergibt   x = -5", "-2(x + 3) = -2x - 6"]),
    ("Veränderung in Prozent", ["(neu - alt) : alt · 100.  Von 800 auf 1'000: 200 : 800 = 25 %."]),
]
PDF_A = [
    ("Dezimalzahlen und Brüche in Gleichungen", ["0.5x - 3 = 2 | + 3", "0.5x = 5 | : 0.5", "x = 10"]),
    ("Prozent und Prozentpunkte", ["Von 10 % auf 15 %: plus 5 Prozentpunkte, das ist eine Zunahme um 50 %."]),
]
