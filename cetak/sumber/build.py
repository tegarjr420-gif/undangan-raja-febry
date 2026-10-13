"""Builds the two print invitations (HTML) that render.js turns into PDF + PNG.
Units are millimetres throughout; every page carries 3 mm bleed on each side."""
import math, html, pathlib, re

HERE = pathlib.Path(__file__).parent
SRC = pathlib.Path("/home/claude/undangan/index.html").read_text()
TURUT = re.findall(r'^\s*"([^"]+)",?\s*$', SRC.split("const TURUT_MENGUNDANG = [")[1].split("];")[0], re.M)
assert len(TURUT) == 40, len(TURUT)
QR = (HERE / "qr.svg").read_text()

B = 3  # bleed

FONTS = """
@font-face{font-family:Pinyon;src:url(node_modules/@fontsource/pinyon-script/files/pinyon-script-latin-400-normal.woff2)}
@font-face{font-family:Corm;font-weight:400;src:url(node_modules/@fontsource/cormorant-garamond/files/cormorant-garamond-latin-400-normal.woff2)}
@font-face{font-family:Corm;font-weight:500;src:url(node_modules/@fontsource/cormorant-garamond/files/cormorant-garamond-latin-500-normal.woff2)}
@font-face{font-family:Corm;font-weight:600;src:url(node_modules/@fontsource/cormorant-garamond/files/cormorant-garamond-latin-600-normal.woff2)}
@font-face{font-family:Corm;font-weight:400;font-style:italic;src:url(node_modules/@fontsource/cormorant-garamond/files/cormorant-garamond-latin-400-italic.woff2)}
@font-face{font-family:Corm;font-weight:500;font-style:italic;src:url(node_modules/@fontsource/cormorant-garamond/files/cormorant-garamond-latin-500-italic.woff2)}
@font-face{font-family:Jost;font-weight:400;src:url(node_modules/@fontsource/jost/files/jost-latin-400-normal.woff2)}
@font-face{font-family:Jost;font-weight:500;src:url(node_modules/@fontsource/jost/files/jost-latin-500-normal.woff2)}
"""

# Same sprig that crowns the "Mempelai" and closing sections online
ORN = """<svg class="orn" viewBox="0 0 160 40"><g fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round">
<path d="M8 31 Q80 -2 152 31"/><path d="M38 20 q-7 -10 -17 -9 q4 10 17 9z"/><path d="M58 13 q-4 -11 -14 -13 q1 11 14 13z"/>
<path d="M102 13 q4 -11 14 -13 q-1 11 -14 13z"/><path d="M122 20 q7 -10 17 -9 q-4 10 -17 9z"/>
<circle cx="80" cy="15.5" r="3"/><circle cx="80" cy="15.5" r="6.5" stroke-opacity=".45"/></g></svg>"""

def star(cx, cy, r):
    k = r * 0.32
    return (f"M{cx},{cy-r} L{cx+k*.45},{cy-k*.45} L{cx+r},{cy} L{cx+k*.45},{cy+k*.45} L{cx},{cy+r} "
            f"L{cx-k*.45},{cy+k*.45} L{cx-r},{cy} L{cx-k*.45},{cy-k*.45} Z")

def arch_path(x0, y0, w, h, inset=0.0):
    """Arch-topped rectangle (full semicircle on top), optionally inset."""
    x0 += inset; y0 += inset; w -= 2 * inset; h -= 2 * inset
    r = w / 2
    return (f"M{x0:.2f},{y0+h:.2f} L{x0:.2f},{y0+r:.2f} A{r:.2f},{r:.2f} 0 0 1 {x0+w:.2f},{y0+r:.2f} "
            f"L{x0+w:.2f},{y0+h:.2f} Z")

def photo_window(x, y, w, h, gold, vw, vh, offs=(2.4, 4.0), spark=True):
    """Photo in an arch window with the double gilded outline used online."""
    lines = "".join(
        f'<path d="{arch_path(x-o, y-o, w+2*o, h+2*o)}" fill="none" stroke="{gold}" '
        f'stroke-width="{0.32 if i == 0 else 0.2}" stroke-opacity="{1 if i == 0 else .55}"/>'
        for i, o in enumerate(offs))
    sp = f'<path d="{star(x + w/2, y - offs[1] - 3.2, 2.2)}" fill="{gold}"/>' if spark else ""
    return f"""
<div class="photo" style="left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm;border-radius:{w/2}mm {w/2}mm 0 0"></div>
<svg class="ov" viewBox="0 0 {vw} {vh}">{lines}{sp}</svg>"""

def seal(cx, cy, d, night):
    return f"""<div class="seal" style="left:{cx-d/2}mm;top:{cy-d/2}mm;width:{d}mm;height:{d}mm">
<span style="color:{night}">R<i>&amp;</i>F</span></div>"""

def turut_list():
    return "".join(f"<li>{html.escape(n)}</li>" for n in TURUT)

def page(w, h, body, cls):
    return f'<section class="pg {cls}" style="width:{w}mm;height:{h}mm">{body}</section>'

def doc(title, W, H, css, pages):
    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8"><title>{title}</title><style>
{FONTS}
@page{{size:{W}mm {H}mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#777}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;text-rendering:geometricPrecision}}
.pg{{position:relative;overflow:hidden;break-after:page}}
.ov{{position:absolute;inset:0;width:100%;height:100%;overflow:visible}}
.photo{{position:absolute;background:url(couple.jpg) 56% 62%/auto 100% no-repeat;background-size:cover}}
.seal{{position:absolute;border-radius:50%;display:grid;place-items:center;
  background:radial-gradient(circle at 34% 28%,#efd8a6 0%,#d4ad6e 45%,#97713f 100%);
  box-shadow:0 0 0 .5mm rgba(255,255,255,.12) inset,0 1.2mm 2.4mm rgba(0,0,0,.35)}}
.seal::before{{content:"";position:absolute;inset:1.6mm;border-radius:50%;border:.18mm dashed rgba(23,32,27,.5)}}
.seal span{{font-family:Pinyon;font-size:17pt;line-height:1;padding-top:1.2mm}}
.seal i{{font-style:normal;font-size:10pt;opacity:.7;margin:0 .2mm}}
.c{{position:absolute;left:0;right:0;text-align:center}}
.eye{{font-family:Jost;font-weight:500;text-transform:uppercase}}
.script{{font-family:Pinyon;font-weight:400;line-height:1}}
.serif{{font-family:Corm}}
.pg{{font-variant-numeric:lining-nums;font-feature-settings:"lnum" 1}}
.orn{{display:block;margin:0 auto}}
{css}
</style></head><body>{''.join(pages)}</body></html>"""


# ===================================================================== LENGKUNG (die-cut arch, dark)
LW, LH = 140, 210            # finished size
PW, PH = LW + 2*B, LH + 2*B  # with bleed
NIGHT = "#17201b"; GOLD = "#d4ad6e"; BLUSH = "#e6b8ad"; IVORY = "#f3ece0"; MUTED = "#c4bdb0"

def l_frame():
    out = ""
    for i, k in enumerate((5.0, 6.6)):
        out += (f'<path d="{arch_path(B, B, LW, LH, k)}" fill="none" stroke="{GOLD}" '
                f'stroke-width="{0.32 if i == 0 else 0.2}" stroke-opacity="{.9 if i == 0 else .5}"/>')
    # small star sitting on the apex of the outer frame
    out += f'<circle cx="{PW/2}" cy="{B+5}" r="2.6" fill="#1a2620"/><path d="{star(PW/2, B+5, 2.1)}" fill="{GOLD}"/>'
    return f'<svg class="ov" viewBox="0 0 {PW} {PH}">{out}</svg>'

L_CSS = f"""
.dark{{background:radial-gradient(ellipse 85% 60% at 50% 34%,#24372d 0%,#1b2a22 52%,#151f19 100%);color:{IVORY}}}
.dark .eye{{color:{BLUSH}}}
.dark .muted{{color:{MUTED}}}
.dark .gold{{color:{GOLD}}}
.lf .names{{font-size:41pt;color:{IVORY}}}
.lf .names .amp{{color:{GOLD};font-size:30pt;margin:0 1.2mm}}
.lf .date{{font-family:Jost;font-weight:500;font-size:8pt;letter-spacing:.42em;color:{GOLD};padding-left:.42em}}
.lf .loc{{font-family:Corm;font-style:italic;font-weight:500;font-size:9.5pt;color:{MUTED}}}
.kepada{{font-family:Jost;font-weight:500;font-size:6.3pt;letter-spacing:.22em;text-transform:uppercase;color:{BLUSH}}}
.dots{{width:78mm;margin:4.2mm auto 0;border-bottom:.25mm dotted rgba(212,173,110,.75);height:0}}
.ditempat{{font-family:Corm;font-style:italic;font-size:9pt;color:{MUTED};margin-top:2.6mm}}
.lb .orn{{width:34mm;color:{GOLD};opacity:.85}}
.lb .salam{{font-size:6.2pt;letter-spacing:.2em;line-height:1.7;width:84mm;margin:2.2mm auto 0;color:{BLUSH}}}
.lb p{{font-family:Corm;font-weight:500}}
.lb .intro{{font-size:9.4pt;line-height:1.35;width:98mm;margin:2mm auto 0}}
.pair{{display:grid;grid-template-columns:1fr 9mm 1fr;align-items:center;width:118mm;margin:3.2mm auto 0}}
.pair .nm{{font-size:21pt;color:{GOLD}}}
.pair .full{{font-family:Corm;font-weight:600;font-size:10.2pt;margin-top:.8mm}}
.pair .par{{font-family:Corm;font-weight:500;font-size:8.2pt;line-height:1.3;color:{MUTED};margin-top:.6mm}}
.pair .and{{font-family:Pinyon;font-size:20pt;color:{GOLD};opacity:.8}}
.rule{{display:flex;align-items:center;gap:2mm;width:56mm;margin:3.4mm auto 0;color:{GOLD}}}
.rule::before,.rule::after{{content:"";flex:1;height:.2mm;background:currentColor;opacity:.6}}
.rule b{{width:1.5mm;height:1.5mm;transform:rotate(45deg);border:.2mm solid currentColor}}
.ev .t{{font-size:6.3pt;letter-spacing:.3em;margin-top:2.6mm;padding-left:.3em}}
.ev .day{{font-family:Corm;font-weight:600;font-size:14.5pt;margin-top:.6mm}}
.ev .hj{{font-family:Jost;font-weight:500;font-size:6pt;letter-spacing:.2em;color:{GOLD};margin-top:.4mm}}
.ev .jam{{font-family:Corm;font-weight:500;font-size:9.6pt;margin-top:.8mm}}
.ev .rumah{{font-family:Corm;font-weight:600;font-size:12.5pt;letter-spacing:.05em;margin-top:1.4mm;line-height:1.15}}
.ev .at{{font-family:Corm;font-weight:500;font-size:9.6pt;margin-top:.2mm}}
.ev .addr{{font-family:Corm;font-weight:500;font-size:8.6pt;color:{MUTED}}}
.lb .close{{font-size:8.8pt;line-height:1.35;width:104mm;margin:3mm auto 0;font-style:italic}}
.tm{{font-size:6.2pt;letter-spacing:.3em;margin-top:2.8mm;padding-left:.3em}}
.turut{{list-style:none;columns:2;column-gap:4mm;width:124mm;margin:1.4mm auto 0;text-align:left;
  font-family:Corm;font-weight:500;font-size:7.3pt;line-height:1.17}}
.turut li{{break-inside:avoid;padding-left:2.4mm;text-indent:-2.4mm}}
.turut li::before{{content:"·";color:{GOLD};margin-right:1.2mm}}
.fam{{font-family:Corm;font-weight:500;font-size:8.4pt;line-height:1.35;margin-top:1.2mm}}
.evrow{{display:grid;grid-template-columns:1fr auto;gap:5mm;align-items:center;width:108mm;margin:.4mm auto 0}}
.fam .sep{{font-size:4pt;vertical-align:.5mm;margin:0 2.2mm;opacity:.7}}
.web{{display:flex;align-items:center;justify-content:center;gap:2.6mm;margin-top:2.6mm}}
.qr{{width:13mm;height:13mm;padding:1mm;border-radius:1.2mm;background:{IVORY}}}
.qr svg{{display:block;width:100%;height:100%}}
.web .tx{{text-align:left;font-family:Corm;font-weight:500;font-size:8pt;line-height:1.3}}
.web .tx b{{font-family:Jost;font-weight:500;font-size:6.6pt;letter-spacing:.06em;color:{GOLD}}}
"""

def lengkung():
    cx = PW / 2
    # ---------- front
    wx, wy, ww, wh = cx - 36, B + 31, 72, 92
    front = l_frame() + photo_window(wx, wy, ww, wh, GOLD, PW, PH) + seal(cx, wy + wh, 17, NIGHT) + f"""
<div class="c eye" style="top:{B+18.5}mm;font-size:6.6pt;letter-spacing:.42em;padding-left:.42em">The Wedding of</div>
<div class="c script names" style="top:{wy+wh+12}mm">Raja<span class="amp">&amp;</span>Febri</div>
<div class="c date" style="top:{wy+wh+30.5}mm">SABTU · 02 · 01 · 2027</div>
<div class="c loc" style="top:{wy+wh+36}mm">Rumah Pak Muri · Kp. Peusar, Binong, Curug</div>
<div class="c" style="top:{B+LH-38}mm">
  <div class="rule" style="margin-top:0;width:40mm"><b></b></div>
  <div class="kepada" style="margin-top:3.6mm">Kepada Yth. Bapak/Ibu/Saudara/i</div>
  <div class="dots"></div><div class="dots" style="width:62mm;margin-top:6mm"></div>
  <div class="ditempat">di Tempat</div>
</div>"""
    # ---------- back
    back = l_frame() + f"""
<div class="c" style="top:{B+20}mm">
  {ORN}
  <div class="eye salam">Assalamu'alaikum Warahmatullahi Wabarakatuh</div>
  <p class="intro">Dengan memohon rahmat dan ridho Allah SWT, kami bermaksud menyelenggarakan pernikahan putra-putri kami:</p>
  <div class="pair">
    <div><div class="script nm">Raja</div><div class="full">Muhamad Raja Ardiansyah</div><div class="par">Putra kedua dari<br>Bapak Muriyadi &amp; Ibu Nuraeni</div></div>
    <div class="and">&amp;</div>
    <div><div class="script nm">Febri</div><div class="full">Febri Yanti</div><div class="par">Putri keenam dari<br>Bapak Marda &amp; Ibu Nurhati</div></div>
  </div>
  <div class="rule"><b></b></div>
  <div class="ev">
    <div class="eye t">Resepsi</div>
    <div class="evrow">
      <div style="text-align:left">
        <div class="day">Sabtu, 2 Januari 2027</div>
        <div class="hj">24 RAJAB 1448 H</div>
        <div class="jam">Pukul 07.00 WIB – selesai</div>
        <div class="rumah">RUMAH PAK MURI</div>
        <div class="at">Kp. Peusar RT 002 / RW 001</div>
        <div class="addr">Kel. Binong, Kec. Curug, Kab. Tangerang, Banten 15810</div>
      </div>
      <div class="web" style="flex-direction:column;gap:1.2mm;margin:0"><div class="qr" style="width:17mm;height:17mm">{QR}</div>
        <div class="tx" style="text-align:center;font-size:7pt;line-height:1.15">Scan untuk<br>peta lokasi</div></div>
    </div>
  </div>
  <p class="close">Merupakan suatu kehormatan dan kebahagiaan bagi kami apabila Bapak/Ibu/Saudara/i berkenan hadir dan memberikan doa restu.</p>
  <div class="eye tm">Turut Mengundang</div>
  <ul class="turut">{turut_list()}</ul>
  <div class="eye tm">Kami yang Berbahagia</div>
  <div class="fam">Keluarga Bapak Muriyadi &amp; Ibu Nuraeni<span class="sep">◆</span>Keluarga Bapak Marda &amp; Ibu Nurhati</div>
</div>"""
    # ---------- die line (for the printer)
    die = f"""<svg class="ov" viewBox="0 0 {PW} {PH}">
<rect x="0" y="0" width="{PW}" height="{PH}" fill="#fff"/>
<path d="{arch_path(B - B, B - B, LW + 2*B, LH + 2*B)}" fill="none" stroke="#9aa" stroke-width=".2" stroke-dasharray="1 1"/>
<path d="{arch_path(B, B, LW, LH)}" fill="none" stroke="#ec008c" stroke-width=".35"/>
<path d="{arch_path(B, B, LW, LH, 5)}" fill="none" stroke="#00a0e0" stroke-width=".2" stroke-dasharray="2 1"/>
</svg>
<div class="c" style="top:{B+70}mm;font-family:Jost;font-size:8pt;line-height:1.6;color:#333">
<b style="font-size:10pt">GARIS POTONG (DIE-CUT)</b><br>
Ukuran jadi {LW} × {LH} mm, atas lengkung setengah lingkaran (jari-jari {LW//2} mm)<br>
<span style="color:#ec008c">━ magenta</span> = garis potong &nbsp; · &nbsp; <span style="color:#889">┅ abu-abu</span> = batas bleed 3 mm<br>
<span style="color:#00a0e0">┅ biru</span> = batas aman teks 5 mm<br><br>
Halaman 1 = depan, halaman 2 = belakang (bolak-balik)<br>
Halaman ini jangan ikut dicetak.
</div>"""
    pages = [page(PW, PH, front, "dark lf"), page(PW, PH, back, "dark lb"), page(PW, PH, die, "")]
    return doc("Undangan Raja & Febri, lengkung", PW, PH, L_CSS, pages), (PW, PH)


# ===================================================================== KOTAK (rectangle, ivory paper)
KW, KH = 148, 210
QW, QH = KW + 2*B, KH + 2*B
INK = "#1e3529"; KGOLD = "#a9844a"; ROSE = "#b0756a"; PAPER = "#f6f0e5"; SOFT = "#5d6a61"

def k_frame():
    out = ""
    for i, k in enumerate((6.5, 8.0)):
        out += (f'<rect x="{B+k}" y="{B+k}" width="{KW-2*k}" height="{KH-2*k}" fill="none" stroke="{KGOLD}" '
                f'stroke-width="{0.3 if i == 0 else 0.18}" stroke-opacity="{1 if i == 0 else .6}"/>')
    # corner diamonds where the two rules meet
    for x, y in ((B+7.25, B+7.25), (B+KW-7.25, B+7.25), (B+7.25, B+KH-7.25), (B+KW-7.25, B+KH-7.25)):
        out += f'<rect x="{x-1.3}" y="{y-1.3}" width="2.6" height="2.6" fill="{PAPER}" stroke="{KGOLD}" stroke-width=".25" transform="rotate(45 {x} {y})"/>'
    return f'<svg class="ov" viewBox="0 0 {QW} {QH}">{out}</svg>'

def corner_sprigs():
    """Leaf sprays in two opposite corners, drawn with the same leaf shape as the online ornament."""
    leaf = lambda x, y, a, s: (f'<path transform="translate({x} {y}) rotate({a}) scale({s})" '
                               f'd="M0 0 q-3.5 -5 -8.5 -4.5 q2 5 8.5 4.5z"/>')
    g = "".join([
        '<path d="M0 0 Q14 2 26 12" fill="none"/>',
        leaf(6, 1.0, -18, .9), leaf(12, 2.9, -12, .85), leaf(17.5, 5.6, -6, .78), leaf(22, 8.6, 0, .7),
    ])
    st = f'fill="none" stroke="{KGOLD}" stroke-width=".28" stroke-linecap="round"'
    return (f'<svg class="ov" viewBox="0 0 {QW} {QH}">'
            f'<g {st} transform="translate({B+11} {B+11})">{g}</g>'
            f'<g {st} transform="translate({B+KW-11} {B+KH-11}) rotate(180)">{g}</g></svg>')

K_CSS = f"""
.ivory{{background:radial-gradient(ellipse 80% 65% at 50% 40%,#fbf7ef 0%,{PAPER} 60%,#eee5d5 100%);color:{INK}}}
.ivory .eye{{color:{ROSE}}}
.ivory .muted{{color:{SOFT}}}
.kf .names{{font-size:42pt;color:{INK}}}
.kf .names .amp{{color:{KGOLD};font-size:31pt;margin:0 1.2mm}}
.kf .date{{font-family:Jost;font-weight:500;font-size:8pt;letter-spacing:.42em;color:{KGOLD};padding-left:.42em}}
.kf .loc{{font-family:Corm;font-style:italic;font-weight:500;font-size:9.5pt;color:{SOFT}}}
.kf .kepada{{color:{ROSE}}}
.kf .dots{{border-bottom-color:rgba(169,132,74,.8)}}
.kf .ditempat{{color:{SOFT}}}
.kb .orn{{width:30mm;color:{KGOLD}}}
.kb .pair{{margin-top:2.4mm}}
.kb .rule{{margin-top:2.6mm}}
.kb .ev .t{{margin-top:2mm}}
.kb .tm{{margin-top:2.4mm}}
.kb p{{font-family:Corm;font-weight:500}}
.kb .salam{{font-size:6.3pt;letter-spacing:.2em;line-height:1.7;margin-top:2.4mm;color:{ROSE}}}
.kb .intro{{font-size:9.6pt;line-height:1.35;width:104mm;margin:1.6mm auto 0}}
.kb .pair .nm{{color:{KGOLD}}}
.kb .pair .par{{color:{SOFT}}}
.kb .pair .and{{color:{KGOLD}}}
.kb .rule{{color:{KGOLD}}}
.verse{{font-family:Corm;font-style:italic;font-weight:500;font-size:8.6pt;line-height:1.34;width:112mm;margin:2.4mm auto 0;color:{SOFT}}}
.verse cite{{display:block;font-style:normal;font-family:Jost;font-weight:500;font-size:6pt;letter-spacing:.24em;color:{KGOLD};margin-top:1mm}}
.kb .ev .hj{{color:{KGOLD}}}
.kb .ev .addr{{color:{SOFT}}}
.kb .qr{{background:transparent;border:.25mm solid rgba(169,132,74,.7)}}
.kb .web .tx b{{color:{KGOLD}}}
.kb .close{{font-size:9pt;line-height:1.35;width:112mm;margin:2.8mm auto 0;font-style:italic}}
.kb .turut li::before{{color:{KGOLD}}}
.kb .turut{{width:124mm;font-size:7.3pt;line-height:1.12}}
"""

def kotak():
    cx = QW / 2
    wx, wy, ww, wh = cx - 35, B + 30, 70, 90
    front = k_frame() + corner_sprigs() + photo_window(wx, wy, ww, wh, KGOLD, QW, QH) + seal(cx, wy + wh, 17, "#17201b") + f"""
<div class="c eye" style="top:{B+18}mm;font-size:6.6pt;letter-spacing:.42em;padding-left:.42em">The Wedding of</div>
<div class="c script names" style="top:{wy+wh+12}mm">Raja<span class="amp">&amp;</span>Febri</div>
<div class="c date" style="top:{wy+wh+30.5}mm">SABTU · 02 · 01 · 2027</div>
<div class="c loc" style="top:{wy+wh+36}mm">Rumah Pak Muri · Kp. Peusar, Binong, Curug</div>
<div class="c" style="top:{B+KH-39}mm">
  <div class="rule" style="margin-top:0;width:40mm;color:{KGOLD}"><b></b></div>
  <div class="kepada" style="margin-top:3.6mm">Kepada Yth. Bapak/Ibu/Saudara/i</div>
  <div class="dots"></div><div class="dots" style="width:62mm;margin-top:6mm"></div>
  <div class="ditempat">di Tempat</div>
</div>"""
    back = k_frame() + f"""
<div class="c" style="top:{B+10.5}mm">
  {ORN}
  <div class="eye salam">Assalamu'alaikum Warahmatullahi Wabarakatuh</div>
  <p class="intro">Dengan memohon rahmat dan ridho Allah SWT, kami bermaksud menyelenggarakan pernikahan putra-putri kami:</p>
  <div class="pair">
    <div><div class="script nm">Raja</div><div class="full">Muhamad Raja Ardiansyah</div><div class="par">Putra kedua dari<br>Bapak Muriyadi &amp; Ibu Nuraeni</div></div>
    <div class="and">&amp;</div>
    <div><div class="script nm">Febri</div><div class="full">Febri Yanti</div><div class="par">Putri keenam dari<br>Bapak Marda &amp; Ibu Nurhati</div></div>
  </div>
  <p class="verse">“Dan di antara tanda-tanda kekuasaan-Nya diciptakan-Nya untukmu pasangan hidup dari jenismu sendiri supaya kamu dapat ketenangan hati dan dijadikannya kasih sayang di antara kamu.”<cite>QS. AR-RUM : 21</cite></p>
  <div class="rule"><b></b></div>
  <div class="ev">
    <div class="eye t">Resepsi</div>
    <div class="evrow">
      <div style="text-align:left">
        <div class="day">Sabtu, 2 Januari 2027</div>
        <div class="hj">24 RAJAB 1448 H</div>
        <div class="jam">Pukul 07.00 WIB – selesai</div>
        <div class="rumah">RUMAH PAK MURI</div>
        <div class="at">Kp. Peusar RT 002 / RW 001</div>
        <div class="addr">Kel. Binong, Kec. Curug, Kab. Tangerang, Banten 15810</div>
      </div>
      <div class="web" style="flex-direction:column;gap:1.2mm;margin:0"><div class="qr" style="width:17mm;height:17mm">{QR}</div>
        <div class="tx" style="text-align:center;font-size:7pt;line-height:1.15">Scan untuk<br>peta lokasi</div></div>
    </div>
  </div>
  <p class="close">Merupakan suatu kehormatan dan kebahagiaan bagi kami apabila Bapak/Ibu/Saudara/i berkenan hadir dan memberikan doa restu.</p>
  <div class="eye tm">Turut Mengundang</div>
  <ul class="turut">{turut_list()}</ul>
  <div class="eye tm">Kami yang Berbahagia</div>
  <div class="fam">Keluarga Bapak Muriyadi &amp; Ibu Nuraeni<span class="sep">◆</span>Keluarga Bapak Marda &amp; Ibu Nurhati</div>
</div>"""
    pages = [page(QW, QH, front, "ivory kf"), page(QW, QH, back, "ivory kb")]
    return doc("Undangan Raja & Febri, kotak", QW, QH, L_CSS + K_CSS, pages), (QW, QH)


if __name__ == "__main__":
    for name, fn in (("lengkung", lengkung), ("kotak", kotak)):
        h, size = fn()
        (HERE / f"{name}.html").write_text(h)
        print(name, size)
