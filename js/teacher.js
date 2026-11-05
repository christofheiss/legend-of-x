// The Legend of X: Masterview. Liest die verschlüsselten Stände nur mit dem Dongle.
import * as K from './crypto.js';
import { CONFIG } from './config.js';

const QUESTS = [
  ['1.1', 'Repetition', 'LZ1'], ['1.2', 'Waage-Werkstatt', 'LZ1'], ['1.3', 'Plus und Minus', 'LZ1'], ['1.4', 'Umkehr-Turm', 'LZ1'], ['1.5', 'Zwei Schritte', 'LZ1'], ['1.6', 'Boss Krabbor', 'LZ1 LZ4'],
  ['2.1', 'Repetition', 'LZ1'], ['2.2', 'Beide Seiten', 'LZ1'], ['2.3', 'Klammer-Mine', 'LZ1'], ['2.4', 'Proben-Labor', 'LZ2'], ['2.5', 'Rätsel-Bibliothek', 'LZ3'], ['2.6', 'Boss MECHATRON X', 'LZ4'],
  ['3.1', 'Repetition', 'LZ6'], ['3.2', 'Pyramiden-Museum', 'LZ5'], ['3.3', 'Prozent-Markt', 'LZ6'], ['3.4', 'Zeit-Observatorium', 'LZ7'], ['3.5', 'Faktencheck-Redaktion', 'LZ8'], ['3.6', 'Trainingsraum', 'LZ1 LZ6'], ['3.7', 'Boss NULLOX', 'LZ6 LZ8'],
].map(([key, name, lz]) => ({ key, name, lz: lz.split(' ') }));
const GOALS = { LZ1: 'Äquivalenzumformungen', LZ2: 'Probe', LZ3: 'Sachsituation → Gleichung', LZ4: 'Fehler finden', LZ5: 'Alterspyramiden', LZ6: 'Absolut / relativ', LZ7: 'Entwicklungen aus Graphen', LZ8: 'Aussagen prüfen' };

const $ = (id) => document.getElementById(id);
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
let dongle = null, priv = null;
const saves = new Map();

$('unlock').onclick = async () => {
  $('lockError').textContent = '';
  const file = $('dongleFile').files[0];
  if (!file) { $('lockError').textContent = 'Wähle zuerst die Dongle-Datei.'; return; }
  try {
    dongle = await K.openDongle(JSON.parse(await file.text()), $('pw').value);
    priv = await K.importPrivate(dongle.privateKey);
    $('pw').value = '';
    $('lock').hidden = true; $('app').hidden = false;
    render();
  } catch (e) { $('lockError').textContent = e.message || 'Der Dongle konnte nicht geöffnet werden.'; }
};

async function add(text) {
  const data = JSON.parse(text);
  if (data.app !== 'legend-of-x') throw new Error('falsche Datei');
  const state = await K.openSaveAsTeacher(data, priv);
  const old = saves.get(data.id);
  if (!old || (data.saved || 0) >= old.saved) saves.set(data.id, { saved: data.saved || 0, state });
}
$('files').onchange = async (e) => {
  let ok = 0, bad = 0;
  for (const f of e.target.files) { try { await add(await f.text()); ok++; } catch { bad++; } }
  e.target.value = '';
  $('status').textContent = `${ok} Datei(en) geladen${bad ? `, ${bad} nicht lesbar` : ''}.`;
  render();
};
async function github(path, accept) {
  return fetch(`https://api.github.com/repos/${dongle.cloud.repo}/contents/${path}`, { headers: { Authorization: `Bearer ${dongle.cloud.token}`, Accept: accept, 'X-GitHub-Api-Version': '2022-11-28' }, cache: 'no-store' });
}
async function loadOnline() {
  $('online').disabled = true; $('status').textContent = 'Lade …';
  try {
    const list = await github('saves-lox', 'application/vnd.github+json');
    if (list.status === 404) { $('status').textContent = 'Es sind noch keine Online-Stände vorhanden.'; return; }
    if (!list.ok) throw new Error('GitHub ' + list.status);
    let ok = 0, bad = 0;
    for (const f of (await list.json()).filter((x) => x.name.endsWith('.lox'))) {
      try { const res = await github('saves-lox/' + encodeURIComponent(f.name), 'application/vnd.github.raw+json'); await add(await res.text()); ok++; } catch { bad++; }
    }
    $('status').textContent = `${ok} Online-Stand/Stände geladen${bad ? `, ${bad} nicht lesbar` : ''}.`;
    render();
  } catch (e) { $('status').textContent = 'Laden nicht möglich: ' + e.message; }
  finally { $('online').disabled = false; }
}
$('online').onclick = () => {
  if (dongle.cloud?.token && dongle.cloud?.repo) return loadOnline();
  $('clRepo').value = dongle.cloud?.repo || CONFIG.dataRepo || '';
  $('clToken').value = ''; $('clError').textContent = '';
  $('cloudBox').hidden = false; $('clToken').focus();
};
$('clClose').onclick = () => { $('cloudBox').hidden = true; };
$('clSave').onclick = async () => {
  const repo = $('clRepo').value.trim(), tok = $('clToken').value.trim();
  if (!/^[\w.-]+\/[\w.-]+$/.test(repo)) { $('clError').textContent = 'Das Repo braucht die Form name/repo.'; return; }
  if (!tok) { $('clError').textContent = 'Bitte den Lese-Schlüssel eingeben.'; return; }
  const before = dongle.cloud; dongle.cloud = { repo, token: tok };
  let res;
  try { res = await github('', 'application/vnd.github+json'); } catch { res = null; }
  if (!res?.ok) {
    dongle.cloud = before;
    $('clError').textContent = !res ? 'GitHub ist nicht erreichbar.' : res.status === 401 ? 'Dieser Schlüssel ist ungültig oder abgelaufen.' : res.status === 403 || res.status === 404 ? 'Dieser Schlüssel darf das Repo nicht lesen. Prüfe das Repo und die Berechtigung.' : 'GitHub meldet Fehler ' + res.status + '.';
    return;
  }
  $('clToken').value = ''; $('cloudBox').hidden = true;
  await loadOnline();
  $('status').append(' Wichtig: Klicke jetzt auf «Dongle speichern», sonst musst du den Schlüssel beim nächsten Mal wieder eingeben.');
  $('dongleBox').hidden = false;
};
$('dongleBtn').onclick = () => { $('dgError').textContent = ''; $('dongleBox').hidden = false; $('pw1').focus(); };
$('dgClose').onclick = () => { $('dongleBox').hidden = true; };
$('dgSave').onclick = async () => {
  const a = $('pw1').value, b = $('pw2').value;
  if (a.length < 10) { $('dgError').textContent = 'Das Passwort braucht mindestens 10 Zeichen.'; return; }
  if (a !== b) { $('dgError').textContent = 'Die beiden Passwörter sind verschieden.'; return; }
  const file = await K.makeDongle({ ...dongle, updated: Date.now() }, a);
  const url = URL.createObjectURL(new Blob([JSON.stringify(file)], { type: 'application/json' }));
  const link = document.createElement('a'); link.href = url; link.download = 'MathWelt3A_Lehrer.dongle.mw3akey'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
  $('pw1').value = ''; $('pw2').value = ''; $('dongleBox').hidden = true;
  $('status').textContent = 'Neuer Dongle heruntergeladen.';
};

function questDone(st, key) {
  const [s, m] = key.split('.').map(Number);
  return !!st[`sector${s}Completed`]?.[m - 1];
}
function questStats(st, key) {
  const items = (st.lernLog || []).filter((e) => e.q === key && e.a === 'check');
  return { tries: items.length, wrong: items.reduce((n, e) => n + (e.wrong || 0), 0) };
}
const usedOverride = (st) => (st.lernLog || []).some((e) => e.a === 'override');
const minutes = (st) => Math.round((Number(st.lernZeit) || 0) / 60);
const stamp = (t) => t ? new Date(t).toLocaleString('de-CH', { dateStyle: 'short', timeStyle: 'short' }) : '–';
const checkpoint = (st, c) => st.learningViewChecks?.results?.[c]?.points ?? '–';
const ids = () => [...new Set([...(dongle.tokens || []).map((t) => t.id), ...saves.keys()])].sort();
const nameOf = (id) => dongle.names?.[id] || '';

function render() {
  const states = [...saves.values()].map((v) => v.state);
  $('tiles').innerHTML = Object.entries(GOALS).map(([lz, title]) => {
    const quests = QUESTS.filter((q) => q.lz.includes(lz));
    const done = states.reduce((n, st) => n + quests.filter((q) => questDone(st, q.key)).length, 0);
    const all = states.length * quests.length;
    return `<div class="tile"><span>${lz} · ${esc(title)}</span><b>${all ? Math.round(done / all * 100) : 0} %</b><span class="muted">${done} von ${all} Quests</span></div>`;
  }).join('');
  const head = `<tr><th class="left">ID</th><th class="left">Name</th><th>Niveau</th><th>Coins</th><th>Quests</th><th>Min.</th><th>Zuletzt</th><th>ZS 1</th><th>ZS 2</th><th>ZS 3</th>${QUESTS.map((q) => `<th class="q" title="${esc(q.lz.join(', '))}">${q.key} ${esc(q.name)}</th>`).join('')}</tr>`;
  const rows = ids().map((id) => {
    const entry = saves.get(id), label = `<td class="left"><b>${esc(id)}</b></td><td class="left">${esc(nameOf(id))}</td>`;
    if (!entry) return `<tr>${label}<td colspan="${8 + QUESTS.length}" class="muted left">noch kein Stand</td></tr>`;
    const st = entry.state;
    const cells = QUESTS.map((q) => {
      const s = questStats(st, q.key), d = questDone(st, q.key);
      return `<td class="${d ? 'ok' : s.tries ? 'try' : ''}">${d || s.tries ? s.wrong : ''}</td>`;
    }).join('');
    const count = QUESTS.filter((q) => questDone(st, q.key)).length;
    return `<tr data-id="${esc(id)}">${label}<td>${esc(st.agentNiveau)}</td><td>${esc(st.shop?.balance ?? 0)}</td><td>${count}/19${usedOverride(st) ? ' <span class="flag" title="Testzugang genutzt">!</span>' : ''}</td><td>${minutes(st)}</td><td>${stamp(entry.saved)}</td><td>${esc(checkpoint(st, 1))}</td><td>${esc(checkpoint(st, 2))}</td><td>${esc(checkpoint(st, 3))}</td>${cells}</tr>`;
  }).join('');
  $('overview').innerHTML = `<table><thead>${head}</thead><tbody>${rows}</tbody></table>`;
  document.querySelectorAll('#overview tr[data-id]').forEach((tr) => { tr.onclick = () => showDetail(tr.dataset.id); });
}
function showDetail(id) {
  const { state: st, saved } = saves.get(id), box = $('detail');
  const log = (st.lernLog || []).slice(-200).reverse().map((e) => {
    const q = QUESTS.find((x) => x.key === e.q);
    const what = e.a === 'override' ? 'Testzugang aktiviert' : e.a === 'check' ? (e.ok ? 'richtig gelöst' : `geprüft, ${e.wrong || 0} falsch`) : e.a === 'mastered' ? 'als beherrscht markiert' : 'abgeschlossen';
    return `<tr><td>${stamp(e.t)}</td><td class="left">${esc(q ? `${q.key} ${q.name}` : '')}</td><td class="left">${esc(what)}</td></tr>`;
  }).join('');
  box.hidden = false;
  box.innerHTML = `<h2 style="margin-top:0">${esc(id)} ${esc(nameOf(id))}</h2>
    <p>Niveau ${esc(st.agentNiveau)} · ${minutes(st)} Min. Lernzeit · gespeichert ${stamp(saved)} · Astrostutz: ${esc(st.shop?.astroRedemptions?.length ?? 0)}</p>
    ${usedOverride(st) ? '<p class="flag">Der Testzugang wurde genutzt. Abschlüsse sind deshalb nicht aussagekräftig.</p>' : ''}
    <div class="scroll"><table><thead><tr><th>Zeit</th><th class="left">Quest</th><th class="left">Aktivität</th></tr></thead><tbody>${log || '<tr><td colspan="3" class="muted">Noch keine Aktivitäten.</td></tr>'}</tbody></table></div>`;
  box.scrollIntoView({ behavior: 'smooth' });
}
$('csv').onclick = () => {
  const cell = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const rows = [['ID', 'Name', 'Niveau', 'Coins', 'Quests', 'Lernzeit_min', 'Testzugang', 'ZS1', 'ZS2', 'ZS3', 'Gespeichert', ...QUESTS.map((q) => `${q.key} ${q.name}`)]];
  for (const id of ids()) {
    const e = saves.get(id); if (!e) { rows.push([id, nameOf(id)]); continue; }
    const st = e.state;
    rows.push([id, nameOf(id), st.agentNiveau, st.shop?.balance ?? 0, QUESTS.filter((q) => questDone(st, q.key)).length, minutes(st), usedOverride(st) ? 'ja' : 'nein', checkpoint(st, 1), checkpoint(st, 2), checkpoint(st, 3), new Date(e.saved).toISOString(),
      ...QUESTS.map((q) => { const s = questStats(st, q.key); return `${questDone(st, q.key) ? 'fertig' : s.tries ? 'begonnen' : 'offen'} (${s.wrong} falsch)`; })]);
  }
  const url = URL.createObjectURL(new Blob(['﻿' + rows.map((r) => r.map(cell).join(';')).join('\n')], { type: 'text/csv' }));
  const a = document.createElement('a'); a.href = url; a.download = 'The_Legend_of_X_Lernstand.csv'; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
};
