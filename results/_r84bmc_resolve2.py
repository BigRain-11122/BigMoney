# -*- coding: utf-8 -*-
"""r84 bm-c resolver2: 7-UU replay batch (d9316621 onto ef92ff78, S7 push-collision).

ours = ef92ff78 (bm-a r326), theirs = d9316621 (bm-c r84), base = dd34727b.
Canon: r322 composite-key field-union; r140 same-sec tie->HEAD; r188/R208 ledger
union zero-loss; D-20260927-09 deep-scan ts probes; memory-union direct-concat;
CODELY <=10KB water-line -> 15th-batch hot-cold archival IN-WINDOW (group order
O-20260927-0230); seat-opinion dual-filing yield per commit-priority (bm-a F-02
stands, bm-c draft withdrawn -> yield receipt F-04).
"""
import io, json, subprocess, datetime

def stage(n, path):
    return subprocess.run(['git', 'show', f':{n}:{path}'],
                          capture_output=True, check=True).stdout

def blob(ref, path):
    if ref.startswith(':'):
        return stage(ref[1:-1] if ref.endswith(':') else ref[1:], path)
    return subprocess.run(['git', 'show', f'{ref}:{path}'],
                          capture_output=True, check=True).stdout

TS = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
HMS = TS[11:16].replace(':', '')

# ---------- 1) autofill_state: launches identical (zero-loss trivial) +
# last_tick take-NEW by inner ts (r140: compare ts then assign whole dict;
# r84 live: in-round bm-c watchdog tick 14:00:01 > bm-b 13:40:02)
o = json.loads(blob(':2:', 'results/autofill_state.json'))
t = json.loads(blob(':3:', 'results/autofill_state.json'))
K = lambda r: (r.get('ts'), r.get('machine'), r.get('pid'),
               r.get('runner_sha256'), r.get('entry'), r.get('shard'))
ok = {K(r): r for r in o['launches']}
tk = {K(r): r for r in t['launches']}
assert set(ok) == set(tk) and len(ok) == len(o['launches']) == 44
bad = [k for k in ok if ok[k] != tk[k]]
assert not bad, f'same-key divergence {bad[:2]}'
assert t['last_tick']['ts'] > o['last_tick']['ts'], 'theirs not newer'
tb_raw = blob(':3:', 'results/autofill_state.json')
open('results/autofill_state.json', 'wb').write(tb_raw)
json.loads(io.open('results/autofill_state.json', encoding='utf-8').read())
print(f"1 autofill_state: launches 44 keysets identical zero-loss; last_tick "
      f"take-new {t['last_tick']['ts']}/{t['last_tick']['machine']} (theirs bytes)")

# ---------- 2) prospect summary: snapshot take-new (generated only-diff)
o = json.loads(blob(':2:', 'results/prospect_paper/_summary.json'))
t = json.loads(blob(':3:', 'results/prospect_paper/_summary.json'))
diff = {k for k in set(o) | set(t) if o.get(k) != t.get(k)}
assert diff == {'generated'}, diff
assert t['generated'] > o['generated']
open('results/prospect_paper/_summary.json', 'wb').write(blob(':3:', 'results/prospect_paper/_summary.json'))
print(f"2 prospect _summary: take-new generated {t['generated']} (only-diff verified)")

# ---------- 3) regime_state: snapshot take-new (updated only-diff)
o = json.loads(blob(':2:', 'results/regime_state.json'))
t = json.loads(blob(':3:', 'results/regime_state.json'))
diff = {k for k in set(o) | set(t) if o.get(k) != t.get(k)}
assert diff == {'updated'}, diff
assert t['updated'] > o['updated']
open('results/regime_state.json', 'wb').write(blob(':3:', 'results/regime_state.json'))
print(f"3 regime_state: take-new updated {t['updated']} (state={t['state']})")

# ---------- 4) compute_audit: history composite-key union + latest take-new
o = json.loads(blob(':2:', 'results/compute_audit.json'))
t = json.loads(blob(':3:', 'results/compute_audit.json'))
K = lambda e: (e.get('ts'), e.get('machine'))
ko = {K(e): e for e in o['history']}
kt = {K(e): e for e in t['history']}
assert len(ko) == len(o['history']) and len(kt) == len(t['history']), 'in-side dup keys'
bad = [k for k in set(ko) & set(kt) if ko[k] != kt[k]]
assert not bad, f'same-key content divergence {bad[:2]} (r322 flag-law)'
merged = dict(ko)
merged.update(kt)
assert len(merged) == len(ko) + len(set(kt) - set(ko)) == 206, len(merged)
hist = sorted(merged.values(), key=lambda e: e['ts'])
assert 'ts' in o['latest'] and 'ts' in t['latest'], 'r319 probe-existence'
latest = dict(t['latest']) if t['latest']['ts'] > o['latest']['ts'] else dict(o['latest'])
assert latest['ts'] == '2026-09-27 14:04:27'
out = dict(t)
out['history'] = hist
out['latest'] = latest
io.open('results/compute_audit.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, ensure_ascii=False, indent=1) + '\n')
d = json.loads(io.open('results/compute_audit.json', encoding='utf-8').read())
assert len(d['history']) == 206 and d['latest']['ts'] == '2026-09-27 14:04:27'
print(f"4 compute_audit: history union {len(o['history'])}+{len(t['history'])}->"
      f"{len(hist)} zero-loss (overlap {len(set(ko) & set(kt))} content-identical), "
      f"latest take-new 14:04:27")

# ---------- 5) x2_watch_log: line-level union zero-loss, stable ts order
ol = blob(':2:', 'results/x2_watch_log.jsonl').decode('utf-8').splitlines()
tl = blob(':3:', 'results/x2_watch_log.jsonl').decode('utf-8').splitlines()
seen, union = set(), []
for line in ol + tl:
    if line.strip() and line not in seen:
        seen.add(line)
        union.append(line)
union.sort(key=lambda l: (json.loads(l).get('ts', '') if l.strip() else ''))
assert len(union) == len(set(ol) | set(tl)), 'union count mismatch'
n_o, n_t = len(set(ol) - set(tl)), len(set(tl) - set(ol))
io.open('results/x2_watch_log.jsonl', 'w', encoding='utf-8', newline='\n').write(
    '\n'.join(union) + '\n')
print(f"5 x2_watch_log: line union {len(set(ol))}|{len(set(tl))}->{len(union)} "
      f"(ours-only {n_o}, theirs-only {n_t}) zero-loss")

# ---------- 6) CODELY.md: memory-union direct-concat + 15th-batch water-line archival
b = blob(':1:', 'CODELY.md')
ob, tb = blob(':2:', 'CODELY.md'), blob(':3:', 'CODELY.md')
assert ob.startswith(b) and tb.startswith(b), 'memory-union prefix assertion (r212)'
a_suf, c_suf = ob[len(b):], tb[len(b):]
union = b + a_suf + c_suf
assert len(union) == len(b) + len(a_suf) + len(c_suf)
union.decode('utf-8')
txt = union.decode('utf-8')
# 15th-batch: move 4 oldest pitlaw entries to research/memory-archive/202609.md
MARKS = ['- [2026-09-27 12:3x r321 bm-a] 坑律：',
         '- [2026-09-27 12:5x r323 bm-b] 坑律：',
         '- [2026-09-27 13:1x r82 bm-c] 坑律：',
         '- [2026-09-27 13:2x r325 bm-b] 坑律：']
lines = txt.split('\n')          # CODELY blobs are pure LF (measured: crlf=0)
moved = []
for m in MARKS:
    hits = [i for i, l in enumerate(lines) if l is not None and l.startswith(m)]
    assert len(hits) == 1, f'marker {m[:28]} hits {len(hits)}'
    moved.append(lines[hits[0]])
    lines[hits[0]] = None
kept = [l for l in lines if l is not None]
# index clause line right after the 十四批 line
idx = next(i for i, l in enumerate(kept) if l.startswith('十四批外迁'))
kept.insert(idx + 1, '十五批外迁（r84 bm-c·S7 重放窗水位律当窗整编）：r321 skill 双副本同步断链/'
            'r323 bm-b GBK 污染全量扫/r82 bm-c S0.5 决策台账 origin 直读/r325 bm-b '
            'universal-newlines=归档十五批节·行级零丢失。')
new_txt = '\n'.join(kept)
assert len(moved) == 4
nb = new_txt.encode('utf-8')
assert len(nb) < 10240, f'CODELY post-archival {len(nb)}B still over 10KB line'
io.open('CODELY.md', 'wb').write(nb)
nb.decode('utf-8')
# archive side: verbatim moves, line-level zero loss
arch_path = 'research/memory-archive/202609.md'
ab = open(arch_path, 'rb').read()
arch_eol = '\r\n' if ab.count(b'\r\n') * 2 > ab.count(b'\n') else '\n'
sec = (f"{arch_eol}## 十五批外迁（r84 bm-c·2026-09-27 {HMS}·S7 重放窗水位律当窗整编）"
       f"{arch_eol}（自根 CODELY.md 行级外迁·原行逐字保全·检索按『指针=』字段）{arch_eol}"
       + arch_eol.join(moved) + arch_eol)
with open(arch_path, 'ab') as f:
    f.write(sec.encode('utf-8'))
ab2 = open(arch_path, 'rb').read()
ab2.decode('utf-8')
for l in moved:
    assert l.encode('utf-8') in ab2, 'archived line missing verbatim'
print(f"6 CODELY: memory-union concat {len(b)}+{len(a_suf)}+{len(c_suf)}"
      f"={len(union)}B -> 15th-batch archival x4 lines -> {len(nb)}B (<10KB OK); "
      f"archive +{len(sec.encode('utf-8'))}B verbatim-zero-loss")

# ---------- 7) HQ-FEEDBACK: append-union + seat-opinion YIELD surgery
b = blob(':1:', 'HQ-FEEDBACK.md')
ob, tb = blob(':2:', 'HQ-FEEDBACK.md'), blob(':3:', 'HQ-FEEDBACK.md')
assert ob.startswith(b) and tb.startswith(b)
a_suf = ob[len(b):]
c_lines = tb[len(b):].decode('utf-8').split('\r\n')
c_lines = [l for l in c_lines if l.strip()]
assert len(c_lines) == 2 and c_lines[0].startswith('- F-20260927-02') \
       and c_lines[1].startswith('- F-20260927-03'), c_lines[0][:40]
f04 = (f"- F-20260927-04 [bm-c r84 2026-09-27 {HMS}·委员会席位意见双头让路回执] "
       f"**C-20260927-01 席3（财务资源席）意见双头撞车按 commit 时间序裁定：bm-a ef92ff78"
       f"（r326·13:47 先落 origin）=其 F-20260927-02 单件为准；bm-c r84 同窗独立稿"
       f"（本地 commit 未及推）后到让路撤稿**。独立先行纪律正向实证=两稿未互阅而立场收敛"
       f"（③均选 A ¥29.9 入门档+防自蚕食功能隔离护栏同构；差异面=bm-a 增 N3 同批/N8 合规后置"
       f"/¥99 年付与连续性负债条款、bm-c 增 4 周预注册回访三指标——均为加性补充零冲突）。"
       f"席位意见唯一载体=F-20260927-02（bm-a）；本行=让路回执+收敛证据留痕，非第二意见。"
       f"状态=closed（双头收口·意见窗内）。")
out = b + a_suf + (c_lines[1] + '\r\n').encode('utf-8') + (f04 + '\r\n').encode('utf-8')
open('HQ-FEEDBACK.md', 'wb').write(out)
out.decode('utf-8')
assert out.startswith(b + a_suf)
print(f"7 HQ-FEEDBACK: union {len(b)}+{len(a_suf)}(bm-a F-02 kept)+F-03 receipt kept"
      f"+F-04 yield receipt added; bm-c F-02 draft withdrawn (commit-priority yield)")

# ---------- 8) state note fix (single-writer mine)
st = json.loads(io.open('state-bm-c.json', encoding='utf-8').read())
assert st['round_no'] == 84
st['note'] = ("r84: S0 poison-commit re-land (r322 field-union, 6 cc restored) + council "
              "seat-3 wired; C-20260927-01 opinion dual-filing YIELDED to bm-a "
              "ef92ff78 F-20260927-02 (commit-priority, first-landed; bm-c concurrent "
              "draft withdrawn, stance converged both-A + anti-cannibalization guard; "
              "yield receipt F-20260927-04) + D-20260927-09 receipt F-20260927-03 "
              "closed + 7-UU replay batch canon-resolved (memory-union + CODELY 15th-"
              "batch water-line archival x4 + audit/regime/x2 ledger unions) + MSG bm-b "
              "cc-strip self-audit + S6 32/32 rc=0 + smoke 25/25.")
st['last_round_ts'] = TS
io.open('state-bm-c.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(st, ensure_ascii=False, indent=1) + '\n')
json.loads(io.open('state-bm-c.json', encoding='utf-8').read())
print('8 state-bm-c.json: note fixed for yield (round_no=84 kept)')

# ---------- 9) round report ADDENDUM (append-only ledger, r83 precedent)
add = (f"{TS}｜R84 bm-c ADDENDUM (S7 push-collision receipt per canon) | first push "
       f"(d9316621) rejected vs bm-a ef92ff78 (r326 13:47 same-window: T-86 W2-A pool "
       f"register + seat-3 opinion F-20260927-02 + S6 32/32) -> pull --rebase "
       f"two-commit replay: 1/2 autofill content-identical tie->ours; 2/2 = 7-UU batch "
       f"canon-resolved: CODELY memory-union direct-concat + <=10KB water-line 15th-"
       f"batch in-window archival (r321/r323/r82/r325 x4 -> 202609.md 十五批节, final "
       f"CODELY <10KB) + HQ-FEEDBACK append-union with SEAT-OPINION YIELD (bm-a F-02 "
       f"stands first-landed per commit-priority; bm-c concurrent draft withdrawn, "
       f"stance converged both-A 29.9+anti-cannibalization, yield receipt F-20260927-"
       f"04, D-09 receipt kept F-03) + compute_audit history union 206 zero-loss + "
       f"latest take-new 14:04:27 + regime/prospect snapshot take-new + x2 line union "
       f"zero-loss + state note fixed + commit message amended pre-push | zero abort "
       f"zero force-push; evidence=results/_r84bmc_probe2.py+results/_r84bmc_resolve2.py "
       f"[via bm-c]")
p = 'logs/iteration-loop/round_reports-bm-c.md'
bb = open(p, 'rb').read()
with open(p, 'ab') as f:
    f.write((add + '\n').encode('utf-8'))
b2 = open(p, 'rb').read()
assert b2 == bb + (add + '\n').encode('utf-8')
b2.decode('utf-8')
print('9 round report: R84 ADDENDUM appended (push-collision receipt + yield)')

print('RESOLVE2 COMPLETE -- all 7 UU + surgeries done, parse-verified')
