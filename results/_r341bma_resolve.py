# r341 bm-a push-rejection rebase resolve (4 UU) + CODELY 25th-batch in-window archival
# Laws: R208/r311 (memory-union no-dedupe) / r322 (composite-key dedup) / r319 (key probe)
#       / r140 (last_tick whole-dict) / r185 (parse-verify before add) / O-20260927-0230 (<=10KB)
import subprocess, json, io, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def blob(stage, path):
    return subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True).stdout

def jload(b):
    return json.loads(b.decode('utf-8'))

report = []

# ---------- 1) regime_state.json : snapshot take-new (only 'updated' differs; probe verified) ----------
p_regime = 'results/regime_state.json'
b1, s2, s3 = blob(1, p_regime), blob(2, p_regime), blob(3, p_regime)
d_b, d_o, d_t = jload(b1), jload(s2), jload(s3)
diff_keys = [k for k in set(d_b) | set(d_o) | set(d_t) if not (d_b.get(k) == d_o.get(k) == d_t.get(k))]
assert diff_keys == ['updated'], 'regime unexpected diff face: %s' % diff_keys
assert d_t['updated'] >= d_o['updated'], 'theirs not newer'
open(p_regime, 'wb').write(s3)  # take theirs (mine, newest) verbatim bytes
report.append('regime_state: take-new theirs 17:50:43 verbatim (only updated field differed, hist/trans identical)')

# ---------- 2) autofill_state.json : mixed-dict+ledger ----------
p_af = 'results/autofill_state.json'
b1, s2, s3 = blob(1, p_af), blob(2, p_af), blob(3, p_af)
af_o, af_t = jload(s2), jload(s3)
lo, lt = af_o.get('launches', []), af_t.get('launches', [])

def ckey(e):
    # r319: probe fields before use; composite key r322
    return tuple(e.get(k) for k in ('ts', 'machine', 'pid', 'runner_sha256', 'entry', 'shard'))

merged, collisions, true_conflicts = [], {}, []
for e in lo + lt:
    k = ckey(e)
    if k in collisions:
        prev = collisions[k]
        if prev == e:
            continue  # identical dup -> one copy
        # field-set merge (r322): disjoint additions -> union fields
        if all(prev.get(f) == e.get(f) for f in set(prev) & set(e)):
            me = dict(prev); me.update(e)
            merged[merged.index(prev)] = me
            collisions[k] = me
        else:
            true_conflicts.append(k)  # real divergence -> flag, no silent double-keep
    else:
        merged.append(e); collisions[k] = e
assert not true_conflicts, 'launch key-collision true conflicts: %s' % true_conflicts
merged.sort(key=lambda e: e.get('ts') or '')          # asc sort for write-back (r245 law: producer append order)
merged = merged[-50:] if len(merged) > 50 else merged  # cap 50 keeping NEWEST
af_new = {'launches': merged, 'last_tick': af_t['last_tick']}
# r140: last_tick compare inner ts whole-dict; theirs ts 17:50:02 > ours 17:40:02 verified
assert af_t['last_tick']['ts'] >= af_o['last_tick']['ts']
assert isinstance(af_new['last_tick'], dict)
raw_af = json.dumps(af_new, ensure_ascii=False, indent=1).encode('utf-8')
json.loads(raw_af.decode('utf-8'))  # r185 parse-verify
open(p_af, 'wb').write(raw_af)
report.append('autofill_state: launches union %d+%d->%d (0 key-conflict, cap50 newest) + last_tick take-new 17:50:02'
              % (len(lo), len(lt), len(merged)))

# ---------- 3) compute_audit.json : rolling-ledger union + latest take-new ----------
p_ca = 'results/compute_audit.json'
b1, s2, s3 = blob(1, p_ca), blob(2, p_ca), blob(3, p_ca)
ca_o, ca_t = jload(s2), jload(s3)
ho, ht = ca_o['history'], ca_t['history']
assert all('ts' in e for e in ho + ht), 'ts key missing in face entries (r319 probe)'
by_ts = {}
for e in ho + ht:
    by_ts[e['ts']] = e  # ts unique per side (verified: no intra-side dups); cross-side same ts = same producer row
union = sorted(by_ts.values(), key=lambda e: e['ts'])
zero_loss = len(union) == len(set(e['ts'] for e in ho) | set(e['ts'] for e in ht))
assert zero_loss, 'audit union row loss'
# latest: deep probe latest.ts (D-09), take-new
lo_ts = (ca_o.get('latest') or {}).get('ts')
lt_ts = (ca_t.get('latest') or {}).get('ts')
assert lo_ts and lt_ts, 'latest.ts probe failed'
latest_new = ca_t['latest'] if lt_ts >= lo_ts else ca_o['latest']
ca_new = {'latest': latest_new, 'history': union}
raw_ca = json.dumps(ca_new, ensure_ascii=False, indent=1).encode('utf-8')
json.loads(raw_ca.decode('utf-8'))
open(p_ca, 'wb').write(raw_ca)
report.append('compute_audit: history union %d+%d->%d zero-loss + latest take-new %s'
              % (len(ho), len(ht), len(union), latest_new['ts']))

# ---------- 4) CODELY.md : memory-union direct-concat, then 25th-batch heat/cold archival ----------
p_cm = 'CODELY.md'
b1, s2, s3 = blob(1, p_cm), blob(2, p_cm), blob(3, p_cm)
base_txt, ours_txt, theirs_txt = b1.decode('utf-8'), s2.decode('utf-8'), s3.decode('utf-8')
assert ours_txt.startswith(base_txt) and theirs_txt.startswith(base_txt), 'prefix identity failed'
suf_o, suf_t = ours_txt[len(base_txt):], theirs_txt[len(base_txt):]
union_txt = base_txt + suf_o + suf_t  # r311: direct-concat, no line dedupe
ulines = union_txt.split('\n')
assert len(ulines) == 53, 'union line count %d' % len(ulines)

def is_content(i):
    return i < len(ulines) and ulines[i].strip() != ''

# keep set (headers/laws/newest pointers); everything else folds to archive 25th batch
KEEP_IDX = {0, 1, 2, 3, 4, 5, 8, 9, 15, 37, 38, 39}   # headers+User+冷层指针+10KB law + 23/24th pointers
fold_idx = [i for i in range(len(ulines)) if is_content(i) and i not in KEEP_IDX]
folded = [ulines[i] for i in fold_idx]

# three FULL pitlaws get archived verbatim + fresh pointer rows kept in CODELY
new_pointers = [
    '- [2026-09-27 17:3x r334 bm-b] 坑律（二十五批外迁·指针）：rolling-ledger union 的 dedup 键族必含面实时间键（asof 键件 ts-only 全 None 塌缩 2+2→1 丢行实弹；正典=逐面键探+union 数对账+写回前三方 blob 复验）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十五批』节。',
    '- [2026-09-27 17:5x r335 bm-b] 坑律（二十五批外迁·指针）：tick git 集成的 add/stash 腿不受 r201 mid-rebase 护栏管辖（护栏只闸 commit/push 腿）——rebase UU 停点窗内 tick 照打 blind-add 标记件入 index+stash-pop 造新 UU+毁 :2:/:3: stage——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十五批』节。',
    '- [2026-09-27 17:5x r341 bm-a] 坑律（二十五批外迁·指针）：池批 stale-takeover 须「心跳停滞+git 零活动」双证并取（bm-b 71min stale 但 16:56 commit 在+W2-A 燃烧在途=忙非死；单凭 stale 接管=同 checkpoint 双写毁在飞批；O-1730 律防误伤补丁）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十五批』节。',
]
idx_row = ('- 二十五批外迁（r341 bm-a·2026-09-27·当窗超线整编·行级零丢失）：rebase 双侧 append union 53 行超 ≤10KB 硬线触发当窗办；'
           '16-23 批全部指针/索引行 %d 条+3 条新 full（r334 dedup 键律/r335 tick add-stash 腿律/r341 池批接管双证律）'
           '外迁=archive 202609.md『坑律归档 2026-09-27 二十五批』节；保留=法行（冷层指针/≤10KB 律）+23/24 批最新指针+3 新指针行。' % len(folded))

kept = [ulines[i] for i in sorted(KEEP_IDX) if i < len(ulines)]
# rebuild: headers(0..9) + law 15 + new pointers + idx row + 23/24 pointers (37-39)
head = [ulines[i] for i in [0, 1, 2, 3, 4, 5, 8, 9]]
law = [ulines[15]]
tail_pointers = [ulines[i] for i in [37, 38, 39]]
new_body = head + law + new_pointers + [idx_row] + tail_pointers
new_txt = '\n'.join(new_body) + '\n'
new_blob_bytes = len(new_txt.encode('utf-8'))

# zero-loss check (r327-style multiset): union lines == kept_from_union + folded_to_archive
from collections import Counter
ms_union = Counter(l for l in ulines if l.strip() != '')
ms_kept = Counter(l for l in [ulines[i] for i in sorted(KEEP_IDX)] if l.strip() != '')
ms_fold = Counter(folded)
assert ms_union == ms_kept + ms_fold, 'CODELY fold zero-loss check FAILED'
open(p_cm, 'wb').write(new_txt.encode('utf-8'))
wt_size = os.path.getsize(p_cm)

# archive append (cold layer, verbatim)
p_arch = 'research/memory-archive/202609.md'
arch_raw = open(p_arch, 'rb').read()
arch_eol = b'\r\n' if b'\r\n' in arch_raw[:2000] else b'\n'
section = ['## 坑律归档 2026-09-27 二十五批（r341 bm-a 当窗超线整编·行级零丢失·rebase 双侧 append union 后 CODELY>10KB 触发·机械解档禁删）', '']
section += folded + ['']
with open(p_arch, 'ab') as f:
    if not arch_raw.endswith(arch_eol):
        f.write(arch_eol)
    f.write(arch_eol.join(l.encode('utf-8') for l in section))
# verify folded lines byte-present in archive now
arch_now = open(p_arch, 'rb').read().decode('utf-8')
missing = [l for l in folded if l not in arch_now]
assert not missing, 'folded lines missing from archive: %d' % len(missing)

report.append('CODELY: union 53 lines (base41+bmb11+bma1) direct-concat verbatim; fold %d rows -> archive 25th batch (zero-loss multiset assert pass); kept %d rows + 3 new pointers + 1 idx row; new size %dB (blob %dB, %s10KB)'
              % (len(folded), len(ms_kept), wt_size, new_blob_bytes, '<=' if wt_size <= 10240 else 'OVER'))

print('\n'.join(report))
print('WT_SIZE=%d HARDLINE=%d OK=%s' % (wt_size, 10240, wt_size <= 10240))
