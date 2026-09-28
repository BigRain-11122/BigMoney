// r414 bm-b town.html ETF-ops info-panel functional test:
// load D from dashboard_status.js, then eval the etfops BUILDS entry info fn with a minimal DOM-free harness.
const fs = require('fs');
const path = require('path');
const repo = path.resolve(__dirname, '..');
const js = fs.readFileSync(path.join(repo, 'results', 'dashboard_status.js'), 'utf-8');
const m = js.match(/\{[\s\S]*\}/);
const D = JSON.parse(m[0]);

const html = fs.readFileSync(path.join(repo, 'town.html'), 'utf-8');
// extract the etfops info arrow function source between "id:'etfops'" entry markers
const start = html.indexOf("{ id:'etfops'");
const end = html.indexOf("{ id:'dock'", start);
if (start < 0 || end < 0) { console.error('FAIL: etfops entry not found'); process.exit(1); }
const entry = html.slice(start, end);
const im = entry.match(/info:\s*\(\)\s*=>\s*\{([\s\S]*)\}\s*\},?\s*$/);
if (!im) { console.error('FAIL: info fn not extracted'); process.exit(1); }
const body = im[1];
// wrap into a function
const fn = new Function('D', 'return (() => {' + body + '})();');
const out = fn(D);
const text = out.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
console.log('INFO-PANEL-RENDER-OK length=' + out.length);
console.log('--- rendered text ---');
console.log(text);
// sanity assertions: real data rows present (not dim-only)
const checks = {
  has_taxonomy: out.includes('分类图谱 6 类'),
  has_system_v1_rows: out.includes('SYSTEM-V1') || out.includes('REV-OSC-STD'),
  has_kpi: out.includes('交易级胜率'),
  no_undefined: !out.includes('undefined'),
  no_null_str: !/\bnull\b/.test(out),
};
console.log('--- checks ---');
let fail = 0;
for (const [k, v] of Object.entries(checks)) {
  console.log(k + '=' + (v ? 'PASS' : 'FAIL'));
  if (!v) fail++;
}
process.exit(fail ? 1 : 0);
