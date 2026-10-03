// r635 bm-a DOM-equivalent render probe: run dashboard.html's real
// fund_family render block against the live dashboard_status.json payload.
// Extracts esc/n2/fnum/chainRow + the ff block from dashboard.html source,
// evals it with D bound to the live payload, and asserts the rendered rows.
const fs = require("fs");
const path = require("path");
const root = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(root, "dashboard.html"), "utf8");
const payload = JSON.parse(
  fs.readFileSync(path.join(root, "results", "dashboard_status.json"), "utf8"));

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function n2(v, d) { return (v == null) ? "—" : v; }
function chainRow(name, val, st, stTxt) {
  return `<div class="chain-row"><span class="nm">${esc(name)}</span>
          <span class="val">${esc(val)}</span>
          <span class="st ${st}">${esc(stTxt)}</span></div>`;
}

// isolate the ff block: from 'const ff = D.data.fund_family;' to the
// closing '}' right before 'const fv = D.data.family_verdicts;'
const src = html;
const start = src.indexOf("const ff = D.data.fund_family;");
const end = src.indexOf("const fv = D.data.family_verdicts;");
if (start < 0 || end < 0 || end <= start) {
  console.error("[FAIL] render block not found in dashboard.html");
  process.exit(1);
}
let block = src.slice(start, end);
// neutralize the DOM sink: collect rows instead
block = block.replace("el.innerHTML = rows.join(\"\") || '<div class=\"empty\">链待产出</div>';", "");
const rows = [];
const D = { data: payload.data };
eval(block); // renders into `rows` via the patched chainRow closure

const joined = rows.join("\n");
const fail = [];
function check(name, cond, detail) {
  console.log((cond ? "[PASS] " : "[FAIL] ") + name + (detail ? " | " + detail : ""));
  if (!cond) fail.push(name);
}

check("campaign row rendered", joined.includes("基本面族战役"));
check("NULLS progress with /2000 target (VALUE)",
  /VALUE\[frozen\][^\n]*NULLS \d+\/2000/.test(joined));
check("gate row rendered", joined.includes("基本面族 · finalize 前置门"));
check("G-SEG blocker text (GM face)", joined.includes("G-SEG chop14&lt;50 待GM裁"));
check("passive crash blocker text (bm-b face)", joined.includes("passive崩 待bm-b修"));
check("gate row status warn/待裁", joined.includes('class="st warn">待裁/待修'));
console.log();
console.log("--- rendered rows ---");
console.log(joined);
console.log("--- end rows ---");
console.log("SUMMARY:", fail.length === 0 ? "ALL PASS" : `${fail.length} FAIL: ${fail}`);
process.exit(fail.length === 0 ? 0 : 1);
