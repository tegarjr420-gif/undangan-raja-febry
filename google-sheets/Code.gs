/**
 * Penghubung undangan Raja & Febri <-> Google Sheets.
 * Tempel seluruh isi file ini di Extensions > Apps Script, lalu Deploy sebagai Web app
 * (Execute as: Me, Who has access: Anyone).
 * Setiap ucapan tamu masuk sebagai satu baris di tab "Ucapan".
 */
const SHEET_NAME = 'Ucapan';
const HEADERS = ['Waktu', 'Nama', 'Kehadiran', 'Jumlah orang', 'Ucapan & doa'];

function sheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME, 0);
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
  }
  return sh;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// Mencegah isian tamu dibaca sebagai rumus spreadsheet
function clean_(s, max) {
  s = String(s || '').replace(/\s+/g, ' ').trim().slice(0, max);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

// Undangan membaca daftar ucapan (terbaru di atas)
function doGet() {
  // Daftar disimpan sementara di cache Google, jadi tamu tidak perlu menunggu sheet dibaca ulang
  const cache = CacheService.getScriptCache();
  const hit = cache.get('list');
  if (hit) return ContentService.createTextOutput(hit).setMimeType(ContentService.MimeType.JSON);
  const sh = sheet_();
  const last = sh.getLastRow();
  if (last < 2) return json_({ ok: true, data: [] });  // sheet kosong
  const start = Math.max(2, last - 499);
  const rows = sh.getRange(start, 1, last - start + 1, 5).getValues();
  const data = rows
    .filter(r => String(r[1]).trim())
    .map(r => {
      const t = r[0] instanceof Date ? r[0] : new Date(r[0]);
      return {
        id: (isNaN(t) ? '' : t.getTime()) + '|' + String(r[1]).slice(0, 20),
        waktu: isNaN(t) ? '' : t.toISOString(),
        nama: String(r[1]).replace(/^'/, ''),
        hadir: String(r[2]) === 'Tidak hadir' ? 'Tidak hadir' : 'Hadir',
        jumlah: Number(r[3]) || 1,
        ucapan: String(r[4]).replace(/^'/, '')
      };
    })
    .reverse();
  const out = JSON.stringify({ ok: true, data: data });
  try { cache.put('list', out, 300); } catch (err) { /* daftar terlalu besar untuk cache, tetap dikirim */ }
  return ContentService.createTextOutput(out).setMimeType(ContentService.MimeType.JSON);
}

// Undangan mengirim ucapan baru
function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const b = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const nama = clean_(b.nama, 60);
    const ucapan = clean_(b.ucapan, 500);
    if (nama.length < 2 || ucapan.length < 2) return json_({ ok: false, error: 'Nama dan ucapan minimal 2 huruf' });
    const hadir = b.hadir === 'Tidak hadir' ? 'Tidak hadir' : 'Hadir';
    const jumlah = hadir === 'Hadir' ? Math.min(10, Math.max(1, parseInt(b.jumlah, 10) || 1)) : 0;
    sheet_().appendRow([new Date(), nama, hadir, jumlah, ucapan]);
    CacheService.getScriptCache().remove('list');
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// Kalau isi sheet diubah manual (misalnya menghapus baris), web langsung memakai data terbaru
function onEdit() {
  CacheService.getScriptCache().remove('list');
}
