// Renders lengkung.html / kotak.html to print PDF (vector text, fonts embedded) and 300 dpi PNG per side,
// and checks that no text crosses the safe area.
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const path = require('path');
const MM = 96 / 25.4;
const B = 3;
const jobs = [
  { name: 'lengkung', w: 146, h: 216, arch: true, safe: 6.6 + 1.5, sides: ['depan', 'belakang', 'garis-potong'] },
  { name: 'kotak', w: 154, h: 216, arch: false, safe: 8 + 2, sides: ['depan', 'belakang'] },
];
(async () => {
  const b = await chromium.launch();
  for (const j of jobs) {
    const p = await b.newPage({ viewport: { width: Math.ceil(j.w * MM), height: Math.ceil(j.h * MM) }, deviceScaleFactor: 300 / 96 });
    await p.goto('file://' + path.join(__dirname, j.name + '.html'));
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    // safe-area check on every text-bearing leaf element of the printed sides
    const issues = await p.evaluate(({ j, MM, B }) => {
      const out = [];
      const secs = [...document.querySelectorAll('.pg')].slice(0, 2);
      secs.forEach((s, si) => {
        const top0 = s.getBoundingClientRect().top;
        const W = j.w - 2 * B, r = W / 2;
        s.querySelectorAll('div,p,li,span').forEach(el => {
          if (el.children.length && !el.matches('li,p')) return;
          if (!el.textContent.trim()) return;
          for (const rc of el.getClientRects()) {
            // text extent: use a range for real glyph width
          }
          const range = document.createRange(); range.selectNodeContents(el);
          for (const rc of range.getClientRects()) {
            if (!rc.width) continue;
            const x1 = rc.left / MM, x2 = rc.right / MM, y1 = (rc.top - top0) / MM, y2 = (rc.bottom - top0) / MM;
            const cx = j.w / 2; const sf = j.safe;
            let bad = x1 < B + sf || x2 > j.w - B - sf || y1 < B + sf || y2 > j.h - B - sf;
            if (j.arch && !bad && y1 < B + r) {
              const dy = (B + r) - y1, half = Math.sqrt(Math.max(0, (r - sf) ** 2 - dy ** 2));
              if (Math.max(cx - x1, x2 - cx) > half) bad = true;
            }
            if (bad) out.push(`side ${si + 1}: "${el.textContent.trim().slice(0, 40)}" box ${x1.toFixed(1)},${y1.toFixed(1)}–${x2.toFixed(1)},${y2.toFixed(1)}`);
          }
        });
        // also report how far the lowest text sits from the safe bottom
        let maxY = 0;
        s.querySelectorAll('li,p,div').forEach(el => { const rc = el.getBoundingClientRect(); if (el.textContent.trim() && rc.height) maxY = Math.max(maxY, (rc.bottom - top0) / MM); });
        out.push(`side ${si + 1}: lowest text at ${maxY.toFixed(1)} mm (safe limit ${(j.h - B - j.safe).toFixed(1)})`);
      });
      return out;
    }, { j, MM, B });
    console.log(j.name, '\n ' + issues.join('\n '));
    const secs = await p.$$('.pg');
    for (let i = 0; i < secs.length; i++) await secs[i].screenshot({ path: path.join(__dirname, 'out', `${j.name}-${j.sides[i]}.png`) });
    await p.pdf({ path: path.join(__dirname, 'out', `${j.name}.pdf`), preferCSSPageSize: true, printBackground: true });
    await p.close();
  }
  await b.close();
})();
