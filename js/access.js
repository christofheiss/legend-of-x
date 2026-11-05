// The Legend of X: Anmeldung mit Code oder QR und verschlüsseltes Speichern (Prinzip wie MathWelt 3A).
// Die Codes und der Dongle sind dieselben wie bei MathWelt 3A; die Stände liegen getrennt.
import * as K from './crypto.js';
import { CONFIG } from './config.js';

export const APP = 'legend-of-x';
const LOCAL_PREFIX = 'legendx_';
const $ = (id) => document.getElementById(id);
let token = null, sKey = null, playerId = null;
let busy = false, lastMove = Date.now(), lastTick = Date.now();

const seal = async (state) => ({ ...(await K.sealSave({ ...state, id: playerId, lastSave: Date.now() }, sKey, CONFIG.teacherPublicKey)), app: APP });
const error = (text) => { const e = $('loginError'); e.textContent = text; e.classList.toggle('hidden', !text); };
const worker = (body) => fetch(CONFIG.saveUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ game: APP, ...body }), signal: AbortSignal.timeout(15000) });

// ---------- Anmeldung ----------
async function checkCode() {
  const norm = K.normalizeToken($('loginCode').value);
  if (norm.length < 10) { error('Bitte gib deinen ganzen Code ein (z. B. 3A07-K7QM-X2PD-9HTR).'); return false; }
  if (!CONFIG.tokenHashes.includes(await K.tokenHash(norm))) { error('Dieser Code ist nicht gültig. Kontrolliere die Buchstaben oder frage deine Lehrperson.'); return false; }
  token = norm; playerId = K.tokenId(norm); sKey = await K.studentKey(norm);
  return true;
}
function readLocal() {
  try { return JSON.parse(localStorage.getItem(LOCAL_PREFIX + playerId)); } catch { return null; }
}
async function readOnline() {
  if (!CONFIG.saveUrl) return null;
  try {
    const res = await worker({ action: 'load', token });
    if (!res.ok) return null;
    return (await res.json()).file || null;
  } catch { return null; }
}
// Übergibt den entschlüsselten Stand an die vorhandene Prüfung des Spiels
function startFromState(state) {
  const input = $('fileUpload'), box = new DataTransfer();
  box.items.add(new File([JSON.stringify(state)], 'stand.json', { type: 'application/json' }));
  input.files = box.files;
  input.dispatchEvent(new Event('change', { bubbles: true }));
}
window.legendLogin = async () => {
  if (busy) return;
  busy = true; error('');
  const button = $('legend-start-button'); button.disabled = true;
  try {
    if (!await checkCode()) return;
    const files = [readLocal(), await readOnline()].filter((f) => f && f.id === playerId);
    files.sort((a, b) => (b.saved || 0) - (a.saved || 0));
    for (const file of files) {
      try { startFromState(await K.openSaveAsStudent(file, sKey)); return; } catch (e) { console.warn('Spielstand nicht lesbar', e); }
    }
    if (!document.querySelector('input[name="loginNiveau"]:checked')) { error('Willkommen! Wähle für deinen ersten Start ein Niveau.'); return; }
    $('loginName').value = playerId;
    window.startNewGame();
  } finally { busy = false; button.disabled = false; }
};
$('secureUpload').addEventListener('change', async (e) => {
  const file = e.target.files[0]; e.target.value = '';
  if (!file) return;
  error('');
  if (!await checkCode()) return;
  try {
    const data = JSON.parse(await file.text());
    if (data.app !== APP) throw new Error('Das ist keine Spielstand-Datei von diesem Spiel.');
    if (data.id !== playerId) throw new Error(`Diese Datei gehört zur ID ${data.id}, du hast den Code von ${playerId} eingegeben.`);
    startFromState(await K.openSaveAsStudent(data, sKey));
  } catch (er) { error(er.message?.startsWith('D') ? er.message : 'Die Datei konnte nicht gelesen werden.'); }
});

// ---------- QR-Code ----------
async function scanQr() {
  if (!('BarcodeDetector' in window)) { error('Dein Browser kann keine QR-Codes lesen. Tippe den Code unter dem QR-Code ein.'); return; }
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } }); }
  catch { error('Die Kamera ist nicht freigegeben. Tippe den Code ein.'); return; }
  const wrap = $('qrWrap'), video = $('qrVideo');
  wrap.hidden = false; video.srcObject = stream; await video.play();
  const detector = new window.BarcodeDetector({ formats: ['qr_code'] });
  let stop = false;
  $('qrCancel').onclick = () => { stop = true; };
  while (!stop) {
    try {
      const codes = await detector.detect(video);
      if (codes.length) {
        const value = codes[0].rawValue, m = value.match(/[#?&]t=([A-Za-z0-9-]+)/);
        $('loginCode').value = m ? m[1] : value;
        stop = true;
      }
    } catch { /* weiter versuchen */ }
    await new Promise((r) => setTimeout(r, 250));
  }
  stream.getTracks().forEach((t) => t.stop()); wrap.hidden = true;
  if ($('loginCode').value) await checkCode().then((ok) => { if (ok) error(''); });
}
$('qrButton').addEventListener('click', scanQr);
if (!('BarcodeDetector' in window)) $('qrButton').title = 'In diesem Browser nicht verfügbar: Code bitte eintippen.';
const hash = location.hash.match(/t=([A-Za-z0-9-]+)/);
if (hash) { $('loginCode').value = hash[1]; history.replaceState(null, '', location.pathname); }

// ---------- Speichern ----------
function currentState() {
  appState.lernZeit = Number(appState.lernZeit) || 0;
  const state = window.directorTestCoins.snapshotForSave();
  return { ...state, saveFileId: undefined };
}
async function storeLocal(file) {
  try { localStorage.setItem(LOCAL_PREFIX + playerId, JSON.stringify(file)); }
  catch (e) { console.warn('Lokales Speichern nicht möglich', e); }
}
function downloadFile(file) {
  const d = new Date(), stamp = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const url = URL.createObjectURL(new Blob([JSON.stringify(file)], { type: 'application/json' }));
  const a = document.createElement('a'); a.href = url; a.download = `The_Legend_of_X_${playerId}_${stamp}.lox`;
  document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
}
function notice(text, ok = true) {
  const n = $('saveNotice'); n.textContent = text; n.hidden = false; n.dataset.ok = String(ok);
  clearTimeout(notice.timer); notice.timer = setTimeout(() => { n.hidden = true; }, ok ? 3500 : 20000);
}
let saving = false;
async function save() {
  if (saving || !sKey) return false;
  saving = true;
  const button = $('btn-save-progress'); button.disabled = true;
  try {
    const state = currentState(), file = await seal(state);
    await storeLocal(file);
    let online = false, reason = '';
    if (CONFIG.saveUrl) {
      try {
        const res = await worker({ token, file });
        online = res.ok;
        if (!online) reason = `${res.status} ${(await res.json().catch(() => ({}))).error || ''}`.trim();
      } catch (e) { reason = e.name || 'Netzwerk'; console.warn('Online-Speichern nicht möglich', e); }
    }
    if (online) notice('Spielstand online gespeichert.');
    else {
      downloadFile(file);
      notice(`Online-Speichern hat nicht geklappt (${reason || 'kein Server'}). Dein Stand wurde als Datei heruntergeladen. Gib sie deiner Lehrperson ab.`, false);
    }
    window.saveSafety?.downloaded(JSON.stringify(state));
    return true;
  } catch (e) {
    console.warn(e); notice('Speichern hat nicht geklappt. Versuche es nochmals.', false);
    return false;
  } finally { saving = false; button.disabled = false; }
}
window.gameFileSave.save = save;
window.gameFileSave.isSaving = () => saving;

// Sichert den Stand verschlüsselt auf diesem Gerät, auch ohne Klick.
async function autoLocal() {
  if (!sKey || !appState.agentName || saving) return;
  try { await storeLocal(await seal(currentState())); } catch (e) { console.warn(e); }
}
setInterval(autoLocal, 30000);
document.addEventListener('visibilitychange', () => { if (document.hidden) autoLocal(); });

// ---------- Lernaktivitäten ----------
function log(entry) {
  if (!appState.agentName) return;
  const list = Array.isArray(appState.lernLog) ? appState.lernLog : (appState.lernLog = []);
  list.push({ t: Date.now(), ...entry });
  if (list.length > 2000) list.splice(0, list.length - 2000);
}
const questOf = (prefix) => { const m = /^s([123])-m([1-7])$/.exec(prefix || ''); return m ? `${m[1]}.${m[2]}` : prefix; };
function wrongCount(prefix) {
  const root = $(prefix + '-forms');
  return root ? root.querySelectorAll('[aria-invalid="true"]').length : 0;
}
function done(prefix) {
  const m = /^s([123])-m([1-7])$/.exec(prefix);
  return !!(m && appState[`sector${m[1]}Completed`]?.[m[2] - 1]);
}
const levelCheck = window.checkLevelGeneric;
window.checkLevelGeneric = function (prefix, key, ...args) {
  const result = levelCheck.call(this, prefix, key, ...args);
  log({ q: questOf(prefix), a: 'check', ok: done(prefix), wrong: wrongCount(prefix) });
  return result;
};
const genericCheck = window.checkGeneric;
window.checkGeneric = function (prefix, ...args) {
  const result = genericCheck.call(this, prefix, ...args);
  log({ q: questOf(prefix), a: 'check', ok: done(prefix), wrong: wrongCount(prefix) });
  return result;
};
const practiceCheck = window.checkAccuracyPractice;
window.checkAccuracyPractice = function (...args) {
  const result = practiceCheck.apply(this, args), round = window.currentAccuracyRound?.();
  const wrong = round ? round.tasks.filter((_, i) => window.accuracyStatus(round, i) === 'incorrect').length : 0;
  log({ q: '3.6', a: 'check', ok: wrong === 0, wrong });
  return result;
};
const practiceMaster = window.masterAccuracyPractice;
window.masterAccuracyPractice = function (...args) { const result = practiceMaster.apply(this, args); log({ q: '3.6', a: 'mastered', ok: true }); return result; };
const finalCheck = window.checkThanosMission;
window.checkThanosMission = function (...args) {
  const result = finalCheck.apply(this, args);
  const wrong = [0, 1, 2].filter((i) => !window.gradeThanosField(i, window.getThanosState().inputs).correct).length;
  log({ q: '3.7', a: 'check', ok: wrong === 0, wrong });
  return result;
};
const finalDone = window.completeThanosMission;
window.completeThanosMission = function (...args) { const result = finalDone.apply(this, args); log({ q: '3.7', a: 'done', ok: !!appState.sector3Completed[6] }); return result; };
const override = window.checkDirectorPassword;
window.checkDirectorPassword = function (...args) {
  const before = directorMode, result = override.apply(this, args);
  if (!before && directorMode) log({ a: 'override' });
  return result;
};

// Lernzeit: zählt nur, wenn das Spiel sichtbar ist und kürzlich bedient wurde.
for (const type of ['keydown', 'pointerdown', 'input']) document.addEventListener(type, () => { lastMove = Date.now(); }, true);
setInterval(() => {
  const now = Date.now(), step = (now - lastTick) / 1000; lastTick = now;
  if (appState.agentName && !document.hidden && now - lastMove < 120000) appState.lernZeit = (Number(appState.lernZeit) || 0) + step;
}, 15000);
