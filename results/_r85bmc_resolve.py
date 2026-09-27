# -*- coding: utf-8 -*-
"""r85 bm-c S0 re-land resolver: a7f66d3b (r84, backup origin/machine/bm-c-r84) onto
6a67f945 (bm-b r328). ours=:2:=HEAD(6a67f945), theirs=:3:=a7f66d3b, base=ef92ff78.
Canon: SKILL L1 exception (un-landed commit re-land, r84 pitlaw); r140 take-new by
inner ts; r188/R208 ledger union zero-loss; r319/D-09 probe-existence; memory-union
manual adjudication (prefix assertion failed = in-place edits both sides); dual
15th-batch numbering collision disambiguation (r176 yield spirit, archive kept
verbatim per 归档不删).
"""
import io, json, subprocess

def blob(n, path):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True)
    assert r.returncode == 0, f'blob :{n}:{path} rc={r.returncode}'
    return r.stdout

def put(path, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    with open(path, 'wb') as f:
        f.write(data)
    data.decode('utf-8')  # strict utf-8 verify

# ---------- A) 26 take-ours files (ours newer face per probe, byte-faithful) ----------
TAKE_OURS = [
    'docs/daily_report/REPORT-2026-09-27.json', 'docs/daily_report/REPORT-2026-09-27.md',
    'results/autofill_state.json', 'results/daily_scorecard.json',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/heat_update_status.json', 'results/lhb_update_status.json',
    'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-24.json', 'results/paper_export/latest.json',
    'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
    'results/regime_state.json', 'results/scorecard_v1.json',
    'results/strategy_scorecard.json', 'results/t35_open_fill_verify.json',
    'results/token_usage.json', 'results/update_status.json',
]
# per-file ours>theirs ts assertions (deep keys probed; r311/D-09 discipline)
def dig(d, path):
    for k in path.split('.'):
        d = d[int(k)] if k.isdigit() else d[k]
    return d
TSKEYS = {
    'docs/daily_report/REPORT-2026-09-27.json': 'generated_at',
    'results/autofill_state.json': 'last_tick.ts',
    'results/daily_scorecard.json': 'traders.0.forward_guard.as_of',
    'results/fundamental_b_layer_filter.json': 'updated',
    'results/futures_update_status.json': 'ts',
    'results/heat_update_status.json': 'updated',
    'results/lhb_update_status.json': 'updated',
    'results/paper/COMPOSITE-CE-01_paper.json': 'updated',
    'results/paper/COMPOSITE-CE-02_paper.json': 'updated',
    'results/paper/DROUGHT-CE-01_paper.json': 'updated',
    'results/paper/ENGULF-CE-01_paper.json': 'updated',
    'results/paper/NEEDLE-DE-01_paper.json': 'updated',
    'results/paper/VOLATILITY-CE-01_paper.json': 'updated',
    'results/paper_export/export-2026-09-24.json': 'generated_from_state_updated',
    'results/paper_export/latest.json': 'generated_from_state_updated',
    'results/prospect_paper/_summary.json': 'generated',
    'results/prospect_promotion/_summary.json': 'generated',
    'results/regime_state.json': 'updated',
    'results/scorecard_v1.json': 'generated',
    'results/strategy_scorecard.json': 'generated',
    'results/t35_open_fill_verify.json': 'ts',
    'results/token_usage.json': 'generated',
    'results/update_status.json': 'updated',
}
for f in TAKE_OURS:
    ob, tb = blob('2', f), blob('3', f)
    if f in TSKEYS:
        o, t = json.loads(ob), json.loads(tb)
        ov, tv = dig(o, TSKEYS[f]), dig(t, TSKEYS[f])
        assert ov > tv, f'{f}: ours {ov} NOT newer than theirs {tv}'
    if f.endswith(('.json', '.js')):
        txt = ob.decode('utf-8')
        if f.endswith('.js'):
            assert txt.lstrip().startswith('window.DASH_DATA'), f'{f}: wrapper stripped'
            json.loads(txt.strip()[len('window.DASH_DATA'):].strip().lstrip('=').rstrip(';'))
        else:
            json.loads(txt)
    put(f, ob)
# autofill extra assertions (r322 composite-key identity before byte-take)
o = json.loads(blob('2', 'results/autofill_state.json'))
t = json.loads(blob('3', 'results/autofill_state.json'))
K = lambda r: (r.get('ts'), r.get('machine'), r.get('pid'),
              r.get('runner_sha256'), r.get('entry'), r.get('shard'))
ok, tk = {K(r): r for r in o['launches']}, {K(r): r for r in t['launches']}
assert set(ok) == set(tk) and len(ok) == 44, f'launches keysets diverge {len(ok)}vs{len(tk)}'
bad = [k for k in ok if ok[k] != tk[k]]
assert not bad, f'same-key divergence (r322 flag-law): {bad[:2]}'
assert o['last_tick']['ts'] == '2026-09-27 14:00:02' and o['last_tick']['machine'] == 'bm-b'
print(f"A) take-ours x{len(TAKE_OURS)} byte-faithful (ts assertions {len(TSKEYS)}/26; "
      f"autofill 44-keyset identical + last_tick ours bm-b 14:00:02 > bm-c 14:00:01)")

# ---------- B) compute_audit: history composite-key union + latest take-new ----------
o = json.loads(blob('2', 'results/compute_audit.json'))
t = json.loads(blob('3', 'results/compute_audit.json'))
K = lambda e: (e.get('ts'), e.get('machine'))
ko = {K(e): e for e in o['history']}
kt = {K(e): e for e in t['history']}
assert len(ko) == len(o['history']) and len(kt) == len(t['history']), 'in-side dup keys'
bad = [k for k in set(ko) & set(kt) if ko[k] != kt[k]]
assert not bad, f'same-key content divergence (r322 flag-law) {bad[:2]}'
merged = dict(ko); merged.update(kt)
hist = sorted(merged.values(), key=lambda e: e['ts'])
assert 'ts' in o['latest'] and 'ts' in t['latest'], 'r319 probe-existence'
latest = dict(t['latest']) if t['latest']['ts'] > o['latest']['ts'] else dict(o['latest'])
out = dict(t); out['history'] = hist; out['latest'] = latest
ab = blob('1', 'results/compute_audit.json')
assert ab.count(b'\r\n') == 0, 'base face drifted to CRLF'
assert ab.split(b'\n')[1].startswith(b' "'), 'base indent-1 face expected'
# mirror base producer face (LF + indent=1, r223/r234: probe base, not sides)
io.open('results/compute_audit.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, ensure_ascii=False, indent=1) + '\n')
d = json.loads(io.open('results/compute_audit.json', encoding='utf-8').read())
assert len(d['history']) == len(merged) and d['latest']['ts'] == latest['ts']
print(f"B) compute_audit: history union {len(o['history'])}|{len(t['history'])}->"
      f"{len(hist)} zero-loss (overlap {len(set(ko) & set(kt))} identical), "
      f"latest take-new {latest['ts']}")

# ---------- C) x2_watch_log: line-level union zero-loss, stable ts order ----------
ol = blob('2', 'results/x2_watch_log.jsonl').decode('utf-8').splitlines()
tl = blob('3', 'results/x2_watch_log.jsonl').decode('utf-8').splitlines()
seen, union = set(), []
for line in ol + tl:
    if line.strip() and line not in seen:
        seen.add(line); union.append(line)
union.sort(key=lambda l: json.loads(l).get('ts', ''))
assert len(union) == len(set(ol) | set(tl)), 'union count mismatch'
n_o, n_t = len(set(ol) - set(tl)), len(set(tl) - set(ol))
io.open('results/x2_watch_log.jsonl', 'w', encoding='utf-8', newline='\n').write(
    '\n'.join(union) + '\n')
print(f"C) x2_watch_log: line union {len(set(ol))}|{len(set(tl))}->{len(union)} "
      f"(ours-only {n_o}, theirs-only {n_t}) zero-loss")

# ---------- D) memory-archive 202609.md: prefix-holds -> direct-concat suffixes ----------
b = blob('1', 'research/memory-archive/202609.md')
ob, tb = blob('2', 'research/memory-archive/202609.md'), blob('3', 'research/memory-archive/202609.md')
assert ob.startswith(b) and tb.startswith(b), 'archive prefix assertion (r212)'
a_suf, c_suf = ob[len(b):], tb[len(b):]
union = b + a_suf + c_suf
assert len(union) == len(b) + len(a_suf) + len(c_suf)
put('research/memory-archive/202609.md', union)
assert '十五批外迁（2026-09-27 r327 bm-a'.encode('utf-8') in union \
       and '十五批外迁（r84 bm-c'.encode('utf-8') in union, 'dual 15th-batch sections missing'
print(f"D) archive: concat {len(b)}+{len(a_suf)}(bm-a r327 fold)+{len(c_suf)}"
      f"(r84 entries)={len(union)}B; dual 15th-batch sections both present")

# ---------- E) CODELY.md: manual union (both sides in-place edited) ----------
ob, tb = blob('2', 'CODELY.md'), blob('3', 'CODELY.md')
assert ob.count(b'\r\n') == 0 and tb.count(b'\r\n') == 0
lines = ob.decode('utf-8').split('\n')
tl_lines = tb.decode('utf-8').split('\n')
# E1. remove r84-archived 4 entries (verbatim copies live in archive D union)
RM = ['- [2026-09-27 12:3x r321 bm-a] 坑律：', '- [2026-09-27 12:5x r323 bm-b] 坑律：',
      '- [2026-09-27 13:1x r82 bm-c] 坑律：', '- [2026-09-27 13:2x r325 bm-b] 坑律：']
removed = []
for m in RM:
    hits = [i for i, l in enumerate(lines) if l is not None and l.startswith(m)]
    assert len(hits) == 1, f'marker {m[:30]} hits {len(hits)}'
    removed.append(lines[hits[0]])
    lines[hits[0]] = None
arch_bytes = open('research/memory-archive/202609.md', 'rb').read()
for l in removed:
    assert l.encode('utf-8') in arch_bytes, f'archived entry missing verbatim: {l[:40]}'
lines = [l for l in lines if l is not None]
# E2. header line: append r84 15th-batch index sentence + numbering-collision note
hd = [i for i, l in enumerate(lines) if l.startswith('- 坑律正典全量归档')]
assert len(hd) == 1, f'header hits {len(hd)}'
sent = [l for l in tl_lines if l.startswith('十五批外迁（r84 bm-c')]
assert len(sent) == 1, f'r84 15th-batch line hits {len(sent)}'
note = ('（r85 勘注：两机同窗各编一批『十五批』——bm-a r327 面=四~十四批索引折叠归档、'
        'r84 bm-c 面=r321/r323/r82/r325 条目外迁，归档侧两『十五批』节并存零覆盖；'
        '后续新批自十六批起编。）')
lines[hd[0]] = lines[hd[0]] + sent[0] + note
# E3. insert r84 pitlaw entry after r328 bm-b entry (chronological tail)
r84 = [l for l in tl_lines if l.startswith('- [2026-09-27 14:1x r84 bm-c] 坑律：')]
assert len(r84) == 1, f'r84 entry hits {len(r84)}'
i328 = [i for i, l in enumerate(lines) if l.startswith('- [2026-09-27 14:1x r328 bm-b] 坑律：')]
assert len(i328) == 1, f'r328 entry hits {len(i328)}'
lines.insert(i328[0] + 1, r84[0])
new = '\n'.join(lines)
nb = new.encode('utf-8')
assert len(nb) < 10240, f'CODELY {len(nb)}B over 10KB water line'
put('CODELY.md', nb)
live = [l for l in lines if l.startswith('- [2026-09-27') and '坑律：**' in l]
print(f"E) CODELY: manual union {len(ob)}B -> {len(nb)}B (<10KB): -4 archived entries "
      f"(verbatim in archive), header + r84 十五批 index + numbering-collision note, "
      f"+r84 entry; live pitlaws = {len(live)}")

print('RESOLVE COMPLETE -- 30 UU: 26 take-ours + audit/x2 unions + archive concat + CODELY manual union')
