const fs = require('fs');
const t = fs.readFileSync('town.html', 'utf8');
const m = t.match(/<script>\r?\n([\s\S]*?)<\/script>/);
if (!m) { console.log('NO INLINE SCRIPT BLOCK'); process.exit(1); }
fs.writeFileSync(process.env.TEMP + '\\_r592bmb_town_inline.js', m[1]);
console.log('extracted', m[1].length, 'chars');
