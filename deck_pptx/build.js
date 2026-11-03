// SaaS-Pulse deck in the editorial black/stone style of the reference deck. Numbers come from data.json.
const pptxgen = require("pptxgenjs");
const sharp = require("sharp");
const fs = require("fs");
const D = JSON.parse(fs.readFileSync(__dirname + "/data.json", "utf8"));
const { applyTheme } = require(process.env.SKILL + "/scripts/apply_theme.js");

const INK = "121110", INK2 = "2B2A28", CARDD = "1F1E1C", MUTED = "6F695D", MUTED_D = "A59E90",
  STONE = "EBE7DF", STONE2 = "DCD6CB", WHITE = "FFFFFF", ACC = "D2552F";
const THEME = {
  name: "SaaS-Pulse Editorial", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: INK, lt1: WHITE, dk2: INK2, lt2: STONE, accent1: ACC, accent2: MUTED, accent3: STONE2, accent4: "8C8579", accent5: "4A4741", accent6: "B9B2A5", hlink: ACC, folHlink: MUTED }
};
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "SaaS-Pulse"; pres.author = "Daksh Chauhan";
const C = pres.SchemeColor;
const TOTAL = 12;
const f2 = x => x.toFixed(2), f3 = x => x.toFixed(3), pc = (x, d = 0) => (100 * x).toFixed(d) + "%";
const NICE = { system_of_record: "System of record", data_gravity: "Data gravity", switching_costs_integrations: "Switching costs", compliance_security: "Compliance & security", network_effects_ecosystem: "Network effects", none_or_commodity: "None / commodity" };

pres.defineSlideMaster({ title: "DARK", background: { color: INK }, objects: [],
  slideNumber: undefined,
  placeholders: undefined });
pres.defineSlideMaster({ title: "LIGHT", background: { color: WHITE }, objects: [] });

async function png(svg, w, h) {
  const buf = await sharp(Buffer.from(svg), { density: 300 }).resize(Math.round(w * 220), Math.round(h * 220)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}
const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const FONT = `font-family="Arial, Liberation Sans, Helvetica, sans-serif"`;

function frame(s, i, section, dark) {
  const fg = dark ? MUTED_D : MUTED;
  const n = String(i).padStart(2, "0");
  s.addText(`${n} / ${String(TOTAL - 1).padStart(2, "0")}`, { x: 0.7, y: 0.35, w: 2, h: 0.3, fontSize: 11, color: fg, charSpacing: 2, margin: 0, isTextBox: true, objectName: "page" });
  s.addText(section.toUpperCase(), { x: 7.6, y: 0.35, w: 5.03, h: 0.3, fontSize: 11, color: fg, align: "right", charSpacing: 3, margin: 0, isTextBox: true, objectName: "section" });
  s.addText(`SECTION ${n} — SAAS-PULSE`, { x: 0.7, y: 6.95, w: 5, h: 0.3, fontSize: 10, color: fg, charSpacing: 3, margin: 0, isTextBox: true, objectName: "footer" });
}
function title(s, text, dark, w = 5.8) {
  s.addText(text.toUpperCase(), { x: 0.7, y: 0.95, w, h: 1.55, fontFace: "Arial", bold: true, fontSize: 38, color: dark ? WHITE : INK, valign: "top", margin: 0, lineSpacingMultiple: 0.95, isTextBox: true, objectName: "title" });
}
function lead(s, text, dark, y = 2.6, w = 5.6) {
  s.addText(text, { x: 0.7, y, w, h: 0.9, fontSize: 17, color: dark ? "E6E1D8" : INK2, valign: "top", margin: 0, isTextBox: true, objectName: "lead" });
}
function points(s, items, dark, y = 3.65, w = 5.6, gap = 0.82) {
  items.forEach(([lab, txt], k) => {
    s.addText([
      { text: lab.toUpperCase(), options: { fontSize: 11, bold: true, charSpacing: 2, color: dark ? WHITE : INK, breakLine: true } },
      { text: txt, options: { fontSize: 15, color: dark ? "C9C3B8" : INK2 } }
    ], { x: 0.7, y: y + k * gap, w, h: gap - 0.06, valign: "top", margin: 0, paraSpaceAfter: 3, isTextBox: true, objectName: "point" + k });
  });
}
function kicker(s, text, dark) {
  s.addText(text, { x: 0.7, y: 6.4, w: 6.2, h: 0.4, fontSize: 14, italic: true, color: dark ? MUTED_D : MUTED, margin: 0, isTextBox: true, objectName: "kicker" });
}
function rows(s, list, dark, x = 7.0, y = 1.2, w = 5.63, h = 0.72, gap = 0.18) {
  list.forEach(([lab, txt, hi], k) => {
    const yy = y + k * (h + gap);
    const fill = hi ? (dark ? WHITE : INK) : (dark ? CARDD : STONE);
    const fg = hi ? (dark ? INK : WHITE) : (dark ? WHITE : INK);
    s.addShape(pres.shapes.RECTANGLE, { x, y: yy, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, objectName: "row" + k });
    s.addText(lab.toUpperCase(), { x: x + 0.25, y: yy, w: 1.7, h, fontSize: 10.5, bold: true, charSpacing: 2, color: hi ? fg : (dark ? MUTED_D : MUTED), valign: "middle", margin: 0, isTextBox: true });
    s.addText(txt, { x: x + 2.0, y: yy, w: w - 2.2, h, fontSize: 15, color: fg, valign: "middle", margin: 0, isTextBox: true });
  });
}

// ---------- SVG art ----------
function venn(labels, center, dark, W = 600, H = 560) {
  const st = dark ? "#EDE8DF" : "#2B2A28", fill = dark ? "#EDE8DF" : "#121110";
  const c = [[230, 210], [370, 210], [300, 335]], r = 150;
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" ${FONT}>`;
  c.forEach(([x, y]) => s += `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" fill-opacity="${dark ? 0.04 : 0.03}" stroke="${st}" stroke-width="2"/>`);
  const pos = [[160, 175], [440, 175], [300, 425]];
  labels.forEach((L, k) => L.split("\n").forEach((t, j) => s += `<text x="${pos[k][0]}" y="${pos[k][1] + j * 24}" text-anchor="middle" font-size="19" font-weight="700" letter-spacing="2" fill="${st}">${esc(t)}</text>`));
  if (center) s += `<text x="300" y="262" text-anchor="middle" font-size="18" font-weight="700" letter-spacing="2" fill="#D2552F">${esc(center)}</text>`;
  return s + "</svg>";
}
function rings() {
  const W = 620, H = 560, cx = 310, cy = 280;
  const R = [[250, "THIN UI · CRUD · DASHBOARDS", "exposed to AI-built internal tools"], [185, "WORKFLOW · INTEGRATIONS", "switching costs"], [120, "DATA · NETWORK EFFECTS", ""], [60, "SYSTEM OF\nRECORD ·\nCOMPLIANCE", ""]];
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" ${FONT}>`;
  const fills = ["#F4F1EC", "#EBE7DF", "#DCD6CB", "#121110"];
  R.forEach(([r], k) => s += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fills[k]}" stroke="#2B2A28" stroke-width="${k === 0 ? 2.5 : 1.5}" ${k === 0 ? 'stroke-dasharray="7 6"' : ""}/>`);
  s += `<text x="${cx}" y="${cy - 212}" text-anchor="middle" font-size="16" font-weight="700" letter-spacing="2" fill="#D2552F">THIN UI · CRUD · DASHBOARDS</text>`;
  s += `<text x="${cx}" y="${cy - 192}" text-anchor="middle" font-size="14" fill="#6F695D">most exposed to AI-built tools</text>`;
  s += `<text x="${cx}" y="${cy - 152}" text-anchor="middle" font-size="15" font-weight="700" letter-spacing="2" fill="#2B2A28">WORKFLOW · INTEGRATIONS</text>`;
  s += `<text x="${cx}" y="${cy - 88}" text-anchor="middle" font-size="15" font-weight="700" letter-spacing="2" fill="#2B2A28">DATA · NETWORK EFFECTS</text>`;
  ["SYSTEM OF", "RECORD ·", "COMPLIANCE"].forEach((t, j) => s += `<text x="${cx}" y="${cy - 14 + j * 20}" text-anchor="middle" font-size="14" font-weight="700" letter-spacing="1.5" fill="#FFFFFF">${t}</text>`);
  s += `<text x="${cx}" y="${H - 6}" text-anchor="middle" font-size="14" fill="#6F695D">hypothesis: the deeper the ring, the harder to replace</text>`;
  return s + "</svg>";
}
function pipeline() {
  const W = 620, H = 560;
  const src = [["SEC 10-K", `${(D.n.par / 1000).toFixed(0)}k paragraphs`], ["SEC XBRL", `${D.n.rev} revenue rows`], ["HACKER NEWS", `${D.n.hn.toLocaleString()} items`], ["PRICING PAGES", `${D.n.price} records`], ["MARKET DATA", `${D.n.stk} tickers vs IGV`]];
  const out = [["RQ1", "moat classifier"], ["RQ2", "build vs buy"], ["RQ3", "moat vs market"]];
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" ${FONT}>`;
  const cx = 330, cy = 280;
  src.forEach(([a, b], k) => { const y = 50 + k * 110; s += `<path d="M 200 ${y + 25} C 260 ${y + 25}, 260 ${cy}, ${cx - 62} ${cy}" fill="none" stroke="#B9B2A5" stroke-width="1.6"/><rect x="0" y="${y}" width="200" height="54" rx="4" fill="#EBE7DF"/><text x="16" y="${y + 23}" font-size="13" font-weight="700" letter-spacing="1.5" fill="#121110">${a}</text><text x="16" y="${y + 43}" font-size="14" fill="#4A4741">${esc(b)}</text>`; });
  out.forEach(([a, b], k) => { const y = 135 + k * 105; s += `<path d="M ${cx + 62} ${cy} C 450 ${cy}, 440 ${y + 27}, 470 ${y + 27}" fill="none" stroke="#2B2A28" stroke-width="1.8"/><rect x="470" y="${y}" width="150" height="54" rx="4" fill="#121110"/><text x="486" y="${y + 23}" font-size="13" font-weight="700" letter-spacing="1.5" fill="#D2552F">${a}</text><text x="486" y="${y + 43}" font-size="14" fill="#FFFFFF">${b}</text>`; });
  s += `<circle cx="${cx}" cy="${cy}" r="62" fill="#FFFFFF" stroke="#121110" stroke-width="2.5"/><text x="${cx}" y="${cy - 4}" text-anchor="middle" font-size="13" font-weight="700" letter-spacing="1.5" fill="#121110">FROZEN</text><text x="${cx}" y="${cy + 16}" text-anchor="middle" font-size="13" font-weight="700" letter-spacing="1.5" fill="#121110">DATASET</text>`;
  return s + "</svg>";
}
function funnel() {
  const W = 620, H = 540;
  const st = [[`${D.n.par.toLocaleString()}`, "10-K paragraphs"], ["200", "gold candidates (keyword buckets)"]];
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" ${FONT}>`;
  const box = (x, y, w, h, big, small, hi) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${hi ? "#FFFFFF" : "#1F1E1C"}"/><text x="${x + 18}" y="${y + 38}" font-size="28" font-weight="900" fill="${hi ? "#121110" : "#FFFFFF"}">${big}</text><text x="${x + 18}" y="${y + 62}" font-size="14" fill="${hi ? "#4A4741" : "#A59E90"}">${esc(small)}</text>`;
  s += box(0, 0, 620, 80, st[0][0], st[0][1]);
  s += `<line x1="310" y1="80" x2="310" y2="110" stroke="#6F695D" stroke-width="2"/>`;
  s += box(0, 110, 620, 80, st[1][0], st[1][1]);
  s += `<path d="M 155 190 L 155 225 M 465 190 L 465 225" stroke="#6F695D" stroke-width="2"/>`;
  s += box(0, 225, 300, 92, String(D.n.train), "train · keyword-rule labels");
  s += box(320, 225, 300, 92, "60", "val + test · LLM-reviewed, author-approved");
  s += `<path d="M 470 317 L 470 352" stroke="#6F695D" stroke-width="2"/>`;
  s += box(320, 352, 300, 92, String(D.n.test), `test kept · ${D.n.excl} unusable rows excluded`, true);
  s += `<text x="0" y="370" font-size="15" font-weight="700" letter-spacing="2" fill="#D2552F">RULE vs REVIEW</text><text x="0" y="410" font-size="40" font-weight="900" fill="#FFFFFF">κ = ${f2(D.n.kappa)}</text><text x="0" y="440" font-size="15" fill="#A59E90">${pc(D.n.agree)} agreement on ${D.n.rev_eval} rows</text>`;
  s += `<text x="0" y="${H - 16}" font-size="14" fill="#A59E90">The reviewer saw the rule's suggestion, so test labels may lean toward the rule.</text>`;
  return s + "</svg>";
}
function scoring() {
  const W = 620, H = 300; const L = ["System of record", "Data gravity", "Switching costs", "Compliance & security", "Network effects", "None / commodity"];
  const v = [0.22, 0.08, 0.14, 0.12, 0.38, 0.06];
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" ${FONT}>`;
  s += `<rect x="0" y="95" width="130" height="80" fill="#EBE7DF"/><text x="65" y="130" text-anchor="middle" font-size="13" font-weight="700" letter-spacing="1.5" fill="#121110">10-K</text><text x="65" y="150" text-anchor="middle" font-size="13" font-weight="700" letter-spacing="1.5" fill="#121110">PARAGRAPH</text>`;
  s += `<line x1="130" y1="135" x2="180" y2="135" stroke="#2B2A28" stroke-width="2"/><rect x="180" y="95" width="120" height="80" fill="#121110"/><text x="240" y="130" text-anchor="middle" font-size="13" font-weight="700" letter-spacing="1.5" fill="#FFFFFF">QWEN</text><text x="240" y="150" text-anchor="middle" font-size="13" font-weight="700" letter-spacing="1.5" fill="#FFFFFF">1.5B</text><line x1="300" y1="135" x2="330" y2="135" stroke="#2B2A28" stroke-width="2"/>`;
  L.forEach((l, k) => { const y = 18 + k * 44, w = v[k] * 520; s += `<text x="340" y="${y + 17}" font-size="15" fill="#2B2A28">${esc(l)}</text><rect x="340" y="${y + 23}" width="${Math.min(w, 270)}" height="12" fill="${k === 4 ? "#D2552F" : "#B9B2A5"}"/>`; });
  s += `<text x="340" y="${H - 2}" font-size="12" fill="#6F695D">illustration: each label string is scored; the highest wins</text>`;
  return s + "</svg>";
}
function f1bars() {
  const W = 640, H = 470, L = 170, R = 600, top = 20, rowH = 66;
  const sx = v => L + v * (R - L);
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" ${FONT}>`;
  [0, 0.25, 0.5, 0.75, 1].forEach(g => s += `<line x1="${sx(g)}" y1="${top}" x2="${sx(g)}" y2="${top + rowH * 6}" stroke="#E3DED5" stroke-width="1.2"/><text x="${sx(g)}" y="${top + rowH * 6 + 24}" text-anchor="middle" font-size="14" fill="#6F695D">${g.toFixed(2)}</text>`);
  s += `<defs><pattern id="h" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="#EBE7DF"/><line x1="0" y1="0" x2="0" y2="8" stroke="#B9B2A5" stroke-width="4"/></pattern></defs>`;
  D.methods.forEach((m, k) => {
    const y = top + k * rowH + 14, h = 36;
    const fill = m.k === "lora" ? "#D2552F" : m.k === "keyword_rule_baseline" ? "url(#h)" : m.k.includes("baseline") ? "#DCD6CB" : "#4A4741";
    s += `<text x="${L - 12}" y="${y + 24}" text-anchor="end" font-size="15" ${m.k === "lora" ? 'font-weight="700"' : ""} fill="#121110">${esc(m.name)}</text>`;
    s += `<rect x="${L}" y="${y}" width="${sx(m.f1) - L}" height="${h}" fill="${fill}"/>`;
    const a = sx(m.fci[0]), b = sx(m.fci[1]), cy = y + h / 2;
    s += `<line x1="${a}" y1="${cy}" x2="${b}" y2="${cy}" stroke="#121110" stroke-width="1.6"/><line x1="${a}" y1="${cy - 8}" x2="${a}" y2="${cy + 8}" stroke="#121110" stroke-width="1.6"/><line x1="${b}" y1="${cy - 8}" x2="${b}" y2="${cy + 8}" stroke="#121110" stroke-width="1.6"/>`;
    s += `<text x="${Math.max(b, sx(m.f1)) + 10}" y="${y + 24}" font-size="16" font-weight="700" fill="#121110">${f2(m.f1)}</text>`;
  });
  s += `<text x="${(L + R) / 2}" y="${H - 8}" text-anchor="middle" font-size="14" fill="#6F695D">Macro-F1 on ${D.n.test} test paragraphs · whiskers = 95% bootstrap CI</text>`;
  return s + "</svg>";
}
function perclass() {
  const order = Object.keys(NICE); const W = 640, H = 450, L = 200, R = 560;
  const sx = v => L + v * (R - L);
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" ${FONT}>`;
  [0, 0.5, 1].forEach(g => s += `<line x1="${sx(g)}" y1="10" x2="${sx(g)}" y2="400" stroke="#2B2A28" stroke-width="1.2"/><text x="${sx(g)}" y="424" text-anchor="middle" font-size="14" fill="#A59E90">${g.toFixed(1)}</text>`);
  order.forEach((k, i) => {
    const p = D.perclass[k], y = 20 + i * 64;
    s += `<text x="${L - 12}" y="${y + 20}" text-anchor="end" font-size="15" fill="#FFFFFF">${esc(NICE[k])}</text><text x="${L - 12}" y="${y + 40}" text-anchor="end" font-size="12" fill="#A59E90">n = ${p.support}</text>`;
    s += `<rect x="${L}" y="${y + 4}" width="${sx(p.f1_score) - L}" height="30" fill="${k === "none_or_commodity" ? "#D2552F" : "#EDE8DF"}"/><text x="${sx(p.f1_score) + 10}" y="${y + 25}" font-size="16" font-weight="700" fill="#FFFFFF">${f2(p.f1_score)}</text>`;
  });
  s += `<text x="${(L + R) / 2}" y="${H - 4}" text-anchor="middle" font-size="14" fill="#A59E90">LoRA F1 per class (test set)</text>`;
  return s + "</svg>";
}
function hnchart() {
  const W = 620, H = 470; const ord = ["build_internal", "buy_saas", "hybrid_or_neutral"], col = { build_internal: "#EDE8DF", buy_saas: "#8C8579", hybrid_or_neutral: "#D2552F" };
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" ${FONT}>`;
  s += `<text x="0" y="22" font-size="14" font-weight="700" letter-spacing="2" fill="#A59E90">WHAT THE MODEL PREDICTED vs. THE TRUE MIX (60 comments)</text>`;
  const rowsD = [["True labels", { build_internal: 20, buy_saas: 20, hybrid_or_neutral: 20 }], ["Zero-shot", D.hn.zd], ["Few-shot", D.hn.fd]];
  rowsD.forEach(([lab, d], k) => {
    const y = 55 + k * 95; let x = 140; s += `<text x="0" y="${y + 33}" font-size="16" fill="#FFFFFF" font-weight="${k === 0 ? 700 : 400}">${lab}</text>`;
    ord.forEach(o => { const w = (d[o] || 0) / 60 * 470; if (w > 0) { s += `<rect x="${x}" y="${y}" width="${w}" height="52" fill="${col[o]}"/>`; if (w > 34) s += `<text x="${x + w / 2}" y="${y + 33}" text-anchor="middle" font-size="16" font-weight="700" fill="${o === "build_internal" ? "#121110" : "#FFFFFF"}">${d[o]}</text>`; } x += w; });
  });
  const ly = 345; ord.forEach((o, k) => s += `<rect x="${140 + k * 160}" y="${ly}" width="16" height="16" fill="${col[o]}"/><text x="${162 + k * 160}" y="${ly + 13}" font-size="16" fill="#C9C3B8">${o.replace(/_/g, " ")}</text>`);
  s += `<text x="0" y="410" font-size="36" font-weight="900" fill="#FFFFFF">${pc(D.hn.z, 1)}</text><text x="190" y="398" font-size="16" fill="#A59E90">accuracy, both methods</text><text x="190" y="422" font-size="16" fill="#A59E90">chance = 33.3% · 95% CI ${pc(D.hn.zci[0])}–${pc(D.hn.zci[1])}</text>`;
  return s + "</svg>";
}
function scatter() {
  const W = 460, H = 440, P = 50, S = 370;
  const sx = v => P + v * S, sy = v => P - 30 + (1 - v) * S;
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" ${FONT}>`;
  s += `<rect x="${P}" y="${P - 30}" width="${S}" height="${S}" fill="#F4F1EC"/>`;
  [0, 0.5, 1].forEach(g => s += `<line x1="${sx(g)}" y1="${sy(0)}" x2="${sx(g)}" y2="${sy(1)}" stroke="#DCD6CB" stroke-width="1.2"/><line x1="${sx(0)}" y1="${sy(g)}" x2="${sx(1)}" y2="${sy(g)}" stroke="#DCD6CB" stroke-width="1.2"/><text x="${sx(g)}" y="${sy(0) + 20}" text-anchor="middle" font-size="13" fill="#6F695D">${g * 100}</text><text x="${P - 8}" y="${sy(g) + 5}" text-anchor="end" font-size="13" fill="#6F695D">${g * 100}</text>`);
  D.pts.forEach(p => s += `<circle cx="${sx(p.rx)}" cy="${sy(p.ry)}" r="5" fill="#121110" fill-opacity="0.72"/>`);
  s += `<text x="${P + S / 2}" y="${H - 8}" text-anchor="middle" font-size="13" fill="#2B2A28">moat-score percentile</text><text x="14" y="${P - 30 + S / 2}" text-anchor="middle" font-size="13" fill="#2B2A28" transform="rotate(-90 14 ${P - 30 + S / 2})">excess-return percentile</text>`;
  return s + "</svg>";
}
function sectors() {
  const W = 470, H = 430, Z = 250, sc = 1.25;
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" ${FONT}>`;
  s += `<text x="0" y="18" font-size="13" font-weight="700" letter-spacing="2" fill="#6F695D">MEDIAN EXCESS RETURN vs IGV, BY SECTOR</text>`;
  s += `<line x1="${Z}" y1="36" x2="${Z}" y2="${40 + D.sec.length * 58}" stroke="#121110" stroke-width="1.5"/>`;
  D.sec.forEach((r, k) => {
    const y = 44 + k * 58, w = Math.abs(r.exc) * sc, pos = r.exc >= 0;
    s += `<rect x="${pos ? Z : Z - w}" y="${y}" width="${w}" height="34" fill="${pos ? "#D2552F" : "#4A4741"}"/>`;
    s += `<text x="${pos ? Z - 10 : Z + 10}" y="${y + 23}" text-anchor="${pos ? "end" : "start"}" font-size="15" fill="#121110">${esc(r.category)} (${r.n})</text>`;
    s += `<text x="${pos ? Z + w + 8 : Z - w - 8}" y="${y + 23}" text-anchor="${pos ? "start" : "end"}" font-size="15" font-weight="700" fill="#121110">${r.exc > 0 ? "+" : ""}${r.exc.toFixed(0)}%</text>`;
  });
  return s + "</svg>";
}

(async () => {
  // 00 title
  let s = pres.addSlide({ masterName: "DARK" }); frame(s, 0, "AI × SaaS defensibility", true);
  s.addText("SAAS-PULSE", { x: 0.7, y: 1.0, w: 6.3, h: 0.5, fontSize: 14, bold: true, charSpacing: 4, color: ACC, margin: 0, isTextBox: true });
  s.addText("WHICH SAAS MOATS HOLD AGAINST AI?", { x: 0.7, y: 1.5, w: 6.3, h: 2.1, fontFace: "Arial", bold: true, fontSize: 40, color: WHITE, valign: "top", margin: 0, lineSpacingMultiple: 0.95, isTextBox: true, objectName: "title" });
  lead(s, "An original dataset of 10-K filings, developer discussion and market data, read by a fine-tuned GenAI moat classifier.", true, 3.75, 5.9);
  [[D.n.co, "companies"], [(D.n.par / 1000).toFixed(0) + "k", "10-K paragraphs"], [D.n.hn.toLocaleString(), "HN items"]].forEach(([b, l], k) => {
    s.addText([{ text: String(b), options: { fontFace: "Arial Black", fontSize: 28, color: WHITE, breakLine: true } }, { text: l.toUpperCase(), options: { fontSize: 10, charSpacing: 2, color: MUTED_D } }], { x: 0.7 + k * 2.0, y: 4.85, w: 1.9, h: 0.95, margin: 0, valign: "top", isTextBox: true });
  });
  s.addText("Daksh Chauhan · Semester VII · Adani University", { x: 0.7, y: 6.4, w: 6, h: 0.35, fontSize: 14, color: "E6E1D8", margin: 0, isTextBox: true });
  s.addImage({ data: await png(venn(["10-K\nTEXT", "DEVELOPERS", "MARKET"], "MOAT?", true), 6, 5.6), x: 6.9, y: 0.95, w: 6.0, h: 5.6, altText: "Three overlapping circles: 10-K text, developers, market, meeting at 'moat?'" });
  s.addNotes("I built an original dataset to ask: as AI makes software cheaper to build, which protections do SaaS companies claim, and do those claims line up with what the market did? The GenAI part is a model that reads 10-K text and labels the type of moat.");

  // 01 why
  s = pres.addSlide({ masterName: "LIGHT" }); frame(s, 1, "The pressure", false); title(s, "Why this question", false);
  lead(s, "AI coding tools make simple internal software much cheaper to build. Not every SaaS product is equally easy to replace.", false);
  points(s, [["The pressure", "CRUD apps, dashboards and trackers can now be built in-house in days."], ["The counter-argument", "Systems of record, compliance and data platforms are hard to replace whatever the build cost."], ["What we test", "Can we measure claimed moats in 10-Ks, and do they match outcomes?"]], false);
  kicker(s, "This is the hypothesis. The rest of the deck tests it.", false);
  s.addImage({ data: await png(rings(), 6.2, 5.6), x: 6.75, y: 1.0, w: 6.2, h: 5.6, altText: "Concentric rings from exposed thin UI to deep system-of-record moats" });
  s.addNotes("This is the hypothesis, not a finding. If building software gets cheaper, the products at risk are the ones with no structural protection.");

  // 02 RQs
  s = pres.addSlide({ masterName: "DARK" }); frame(s, 2, "Research design", true); title(s, "Three questions", true);
  lead(s, "One GenAI task at the core, one developer view, one market check.", true);
  points(s, [["Core task", "A 1.5B open LLM labels the moat type in each 10-K paragraph."], ["Comparison", "Zero-shot vs few-shot vs LoRA fine-tuning, against simple baselines."], ["Outcome link", "Model output is aggregated per company and tested against returns."]], true);
  rows(s, [["RQ1 · Classify", "Can a small LLM label moat types, and does fine-tuning beat prompting?", true], ["RQ2 · Developers", "Do Hacker News developers argue for building internal tools or buying SaaS?"], ["RQ3 · Market", "Do companies with more moat language show better excess returns since 2023?"]], true, 7.0, 1.6, 5.63, 1.15, 0.3);
  kicker(s, "First, the data.", true);
  s.addNotes("Three questions. RQ1 is the core GenAI task. RQ2 is the developer side. RQ3 connects the model's output to financial outcomes.");

  // 03 dataset
  s = pres.addSlide({ masterName: "LIGHT" }); frame(s, 3, "Dataset", false); title(s, "Our own dataset", false);
  lead(s, "Collected and prepared for this project from five public sources, then frozen so every run reads the same files.", false);
  points(s, [["Scale", `${D.n.fil} filings · ${D.n.par.toLocaleString()} paragraphs · ${D.n.co} companies`], ["Market", `${D.n.stk} tickers, Jan 2023 → Oct 2026, vs IGV (${D.n.igv > 0 ? "+" : ""}${D.n.igv.toFixed(1)}%)`], ["Ethics", "Declared user agent, rate limits, robots.txt, no login walls. Datasheet + SHA-256 manifest."]], false);
  kicker(s, "Pricing pages proved too patchy; they are used descriptively only.", false);
  s.addImage({ data: await png(pipeline(), 6.2, 5.6), x: 6.75, y: 1.0, w: 6.2, h: 5.6, altText: "Five sources feed a frozen dataset that serves three research questions" });
  s.addNotes("Everything was collected for this project from public sources. Pricing pages turned out too patchy: enterprise vendors often have no public pricing.");

  // 04 labels
  s = pres.addSlide({ masterName: "DARK" }); frame(s, 4, "Labels", true); title(s, "An honest gold set", true);
  lead(s, "Six moat classes. Training labels come from keyword rules; test labels were reviewed.", true);
  points(s, [["Classes", "System of record · data gravity · switching costs · compliance · network effects · none"], ["Train", `${D.n.train} paragraphs, keyword-rule labels (noisy by design)`], ["Test", `${D.n.test} paragraphs reviewed by an independent LLM (Claude Opus 5.5), approved by the author`]], true);
  kicker(s, "The rules were right about two times in three.", true);
  s.addImage({ data: await png(funnel(), 6.2, 5.4), x: 6.75, y: 1.05, w: 6.0, h: 5.23, altText: "Funnel from all paragraphs to the 35-row reviewed test set; kappa between rule and review" });
  s.addNotes(`Training labels come from keyword rules. Validation and test were reviewed by a different, stronger LLM and approved by me. Rule and review agreed ${pc(D.n.agree)} of the time, kappa ${f2(D.n.kappa)}. The reviewer could see the rule's suggestion, which can bias the test labels toward the rule.`);

  // 05 method
  s = pres.addSlide({ masterName: "LIGHT" }); frame(s, 5, "GenAI method", false); title(s, "One model, three regimes", false);
  lead(s, "Qwen2.5-1.5B-Instruct on a Kaggle T4. Every method is scored the same way.", false);
  points(s, [["Fair scoring", "No free text: the model scores each of the six labels and the most likely wins."], ["Baselines", "Majority class, random, and the keyword rule itself."]], false, 3.65, 5.6, 0.95);
  rows(s, [["Zero-shot", "Taxonomy definitions + paragraph → label"], ["Few-shot", "Plus 6 training examples, one per class"], ["LoRA", `4-bit base, r = 8, α = 16, loss on label only, ${D.epochs} epochs, ${D.n.train} examples`, true]], false, 7.0, 1.0, 5.63, 0.78, 0.18);
  s.addImage({ data: await png(scoring(), 6.2, 3.0), x: 6.85, y: 3.85, w: 5.8, h: 2.81, altText: "Illustration of constrained label scoring" });
  kicker(s, "Constrained scoring removed the parse failures of the first run.", false);
  s.addNotes("All three methods use the same 1.5 billion parameter model. Constrained scoring means the model never writes free text; it ranks the six labels. That makes the comparison fair.");

  // 06 RQ1
  const lo = D.methods.find(m => m.k === "lora"), fs_ = D.methods.find(m => m.k === "few_shot_cot");
  s = pres.addSlide({ masterName: "LIGHT" }); frame(s, 6, "RQ1 · Results", false); title(s, "Fine-tuning beats prompting", false, 5.6);
  s.addText([{ text: f2(lo.f1), options: { fontFace: "Arial Black", fontSize: 54, color: ACC } }, { text: `  vs  ${f2(fs_.f1)}`, options: { fontFace: "Arial Black", fontSize: 30, color: INK2 } }], { x: 0.7, y: 2.55, w: 5.6, h: 0.95, margin: 0, isTextBox: true });
  s.addText("macro-F1, LoRA vs few-shot prompting", { x: 0.7, y: 3.45, w: 5.6, h: 0.35, fontSize: 13, color: MUTED, margin: 0, isTextBox: true });
  points(s, [["Significance", `McNemar vs few-shot p = ${f3(D.mcn.few_shot_vs_lora)}; vs zero-shot p = ${f3(D.mcn.zero_shot_vs_lora)}. n = ${D.n.test}, so intervals are wide.`], ["* Keyword rule", `Highest score but not a fair rival: ${D.n.rule_kept} of ${D.n.test} test labels are the rule's own label, kept on review.`]], false, 4.05, 5.6, 1.05);
  s.addImage({ data: await png(f1bars(), 6.4, 4.7), x: 6.6, y: 1.1, w: 6.3, h: 4.63, altText: "Macro-F1 by method with confidence intervals" });
  kicker(s, "The fair comparison is between the GenAI methods.", false);
  s.addNotes(`Prompting gives about ${f2(fs_.f1)} macro-F1; LoRA lifts it to ${f2(lo.f1)}, significant against few-shot at p = ${f3(D.mcn.few_shot_vs_lora)}, with wide intervals on ${D.n.test} paragraphs. The keyword rule looks best because the test labels started from it.`);

  // 07 per class
  const none = D.perclass.none_or_commodity;
  s = pres.addSlide({ masterName: "DARK" }); frame(s, 7, "RQ1 · Errors", true); title(s, "Where it goes wrong", true);
  lead(s, "The model over-claims: plain business descriptions get labelled as moats.", true);
  points(s, [["Strongest", "Network effects and systems of record: distinctive vocabulary."], ["Weakest", `None / commodity recall ${f2(none.recall)}: the biggest class (${none.support} of ${D.n.test}).`], ["Caveat", "2 to 6 test examples per class: read these as rough."]], true);
  kicker(s, "More reviewed 'none' examples would help most.", true);
  s.addImage({ data: await png(perclass(), 6.4, 4.5), x: 6.6, y: 1.25, w: 6.3, h: 4.43, altText: "LoRA F1 per moat class" });
  s.addNotes("Per class, the model is strongest on network effects and systems of record. Its main error is over-claiming, so recall on the none class is low.");

  // 08 examples
  s = pres.addSlide({ masterName: "LIGHT" }); frame(s, 8, "RQ1 · Evidence", false); title(s, "Real test paragraphs", false, 11);
  const cw = 3.75;
  D.ex.forEach((e, k) => {
    const x = 0.7 + k * (cw + 0.2), ok = e.l === e.g;
    const txt = e.text.length > 230 ? e.text.slice(0, 230).replace(/\s+\S*$/, "") + " …" : e.text;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 2.0, w: cw, h: 4.3, fill: { color: STONE }, line: { color: STONE, width: 0 }, objectName: "excard" + k });
    s.addText(`${e.t} · FY${e.fy}`, { x: x + 0.25, y: 2.15, w: cw - 0.5, h: 0.35, fontSize: 11, bold: true, charSpacing: 2, color: MUTED, margin: 0, isTextBox: true });
    s.addText(`“${txt}”`, { x: x + 0.25, y: 2.55, w: cw - 0.5, h: 2.45, fontSize: 13.5, italic: true, color: INK2, valign: "top", margin: 0, isTextBox: true });
    s.addText([{ text: "GOLD  ", options: { fontSize: 10, bold: true, charSpacing: 2, color: MUTED } }, { text: NICE[e.g], options: { fontSize: 14, bold: true, color: INK, breakLine: true } },
    { text: "LORA  ", options: { fontSize: 10, bold: true, charSpacing: 2, color: MUTED } }, { text: NICE[e.l] + (ok ? "  ✓" : "  ✗"), options: { fontSize: 14, bold: true, color: ok ? "2E6B3F" : ACC, breakLine: true } },
    { text: "FEW-SHOT  ", options: { fontSize: 10, bold: true, charSpacing: 2, color: MUTED } }, { text: NICE[e.f] || e.f, options: { fontSize: 14, color: INK2 } }], { x: x + 0.25, y: 5.1, w: cw - 0.5, h: 1.1, margin: 0, valign: "top", paraSpaceAfter: 2, isTextBox: true });
  });
  s.addText("Quoted verbatim from the test set (truncated): two cases LoRA gets right where few-shot fails, and one LoRA error.", { x: 0.7, y: 6.4, w: 11.9, h: 0.4, fontSize: 14, italic: true, color: MUTED, margin: 0, isTextBox: true });
  s.addNotes("These are real paragraphs from the test set. Two show where fine-tuning helped, and one shows a typical over-claiming error.");

  // 09 HN
  s = pres.addSlide({ masterName: "DARK" }); frame(s, 9, "RQ2 · Developers", true); title(s, "A negative result", true);
  lead(s, "On Hacker News stance, both prompting methods are barely above chance.", true);
  points(s, [["Result", `${pc(D.hn.z, 1)} accuracy for zero-shot and few-shot; the 95% interval includes chance.`], ["Failure mode", "The model almost never predicts “hybrid”, though it is a third of the benchmark."], ["Decision", "No corpus-wide build-vs-buy percentage is reported: it would turn bias into a fake trend."]], true);
  kicker(s, "Benchmark labels here are rule-generated, not reviewed.", true);
  s.addImage({ data: await png(hnchart(), 6.2, 4.7), x: 6.75, y: 1.15, w: 6.0, h: 4.55, altText: "Predicted vs true stance mix for 60 HN comments" });
  s.addNotes("This one did not work, and I report it. Developer comments are sarcastic and nuanced, and a 1.5B model without fine-tuning is barely above chance. I deliberately do not turn its predictions into a percentage.");

  // 10 RQ3
  s = pres.addSlide({ masterName: "LIGHT" }); frame(s, 10, "RQ3 · Market", false); title(s, "No moat premium", false, 4.0);
  s.addText([{ text: `ρ = ${f2(D.rho.rho)}`, options: { fontFace: "Arial Black", fontSize: 40, color: INK, breakLine: true } }, { text: `p = ${f3(D.rho.p)} · 95% CI [${f2(D.rho.ci_lo)}, ${f2(D.rho.ci_hi)}] · n = ${D.rho.n}`, options: { fontSize: 13, color: MUTED } }], { x: 0.7, y: 2.6, w: 4.2, h: 1.1, margin: 0, valign: "top", isTextBox: true });
  points(s, [["Moat vs return", "Weakly positive, not significant. Revenue growth: ρ = " + f2(D.rhog.rho) + "."], ["Sector matters more", "Descriptive only; we do not claim what caused it."], ["Noise", "Moat scores come from a 60%-accurate model, which weakens any correlation."]], false, 3.9, 4.2, 0.82);
  s.addImage({ data: await png(scatter(), 4.6, 4.4), x: 4.85, y: 1.2, w: 3.9, h: 3.73, altText: "Rank scatter of moat score vs excess return for 92 companies" });
  s.addImage({ data: await png(sectors(), 4.7, 4.3), x: 8.85, y: 1.2, w: 3.95, h: 3.61, altText: "Median excess return vs IGV by sector" });
  s.addText("Each dot = one company (percentile ranks, as Spearman uses).", { x: 4.85, y: 5.05, w: 3.9, h: 0.5, fontSize: 12, color: MUTED, margin: 0, isTextBox: true });
  kicker(s, "“No link found” is not “moats don’t matter”.", false);
  s.addNotes(`The correlation between moat share and excess return is ${f2(D.rho.rho)}, p = ${f3(D.rho.p)}: not significant. Sector differences are much larger, and they are descriptive.`);

  // 11 conclusions
  s = pres.addSlide({ masterName: "DARK" }); frame(s, 11, "The big picture", true); title(s, "Three takeaways", true);
  points(s, [["1 · GenAI works here", `LoRA on ${D.n.train} weak labels: ${f2(lo.f1)} macro-F1, about double prompting.`], ["2 · Stance is hard", "Developer build-vs-buy stance stayed near chance."], ["3 · Market link not shown", "Moat language did not significantly predict 2023–26 excess returns."], ["Limitations", `Rule-based training labels, anchoring risk, n = ${D.n.test}, self-reported 10-K claims, survivorship, no causal claims.`], ["Next", "Blind human labels, a larger test set, a bigger model for HN."]], true, 2.6, 5.9, 0.78);
  s.addImage({ data: await png(venn(["LoRA >\nPROMPTING", "HN ≈\nCHANCE", "NO MOAT\nPREMIUM"], "", true), 6, 5.6), x: 6.9, y: 0.95, w: 6.0, h: 5.6, altText: "Three circles summarising the three findings" });
  s.addNotes("Fine-tuning clearly helps a small model learn this taxonomy, developer stance was a negative result, and the market link was not significant. The main improvement would be blind human labels and a bigger test set. Thank you.");

  await pres.writeFile({ fileName: __dirname + "/SaaS_Pulse_Deck.pptx" });
  await applyTheme(__dirname + "/SaaS_Pulse_Deck.pptx", THEME);
  console.log("written");
})();
