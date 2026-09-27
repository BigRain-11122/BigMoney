# r341 bm-a SECOND collision resolve (16 UU vs bm-b r336) + CODELY renumber-26th fold
# Laws: r176 (renumber later-arriver) / R208/R216 (snapshot take-new) / r327 (entry-level bidir verify)
#       / r140/r322 (autofill) / r188 (compute_audit union) / r329 (twin coupling) / O-20260927-0230 (<=10KB)
import subprocess, json, io, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def bl(stage, path):
    return subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True).stdout

def take_ours_verbatim(path, note):
    open(path, 'wb').write(bl(2, path))
    return 'take-ours-verbatim: %s (%s)' % (path, note)

report = []

# ---- 1) snapshot family: ours (bm-b r336) newer in ALL probes -> take ours verbatim ----
for path, note in [
    ('docs/daily_report/REPORT-2026-09-27.json', 'generated_at 17:53:33 > 17:51:35'),
    ('docs/daily_report/REPORT-2026-09-27.md', 'twin md from same newer side (r329)'),
    ('results/regime_state.json', 'updated 17:52:07 > 17:50:43'),
    ('results/dashboard_status.json', 'generated_at 17:53:36 > 17:51:37'),
    ('results/dashboard_status.js', 'js wrapper from same newer side'),
    ('results/fundamental_b_layer_filter.json', 'updated 17:52:37 > 17:51:28'),
    ('results/futures_update_status.json', 'ts 17:52:22 > 17:51:07'),
    ('results/heat_update_status.json', 'updated 17:52:22 > 17:51:07'),
    ('results/lhb_update_status.json', 'updated 17:52:21 > 17:51:06'),
    ('results/scorecard_v1.json', 'generated 17:52:53 > 17:50:55'),
    ('results/strategy_scorecard.json', 'generated 17:53:08 > 17:51:01'),
    ('results/token_usage.json', 'generated 17:53:39 > 17:51:37'),
    ('results/update_status.json', 'updated 17:52:05 > 17:50:42'),
]:
    report.append(take_ours_verbatim(path, note))

# ---- 2) autofill_state.json : launches union + last_tick inner-ts take-new ----
p_af = 'results/autofill_state.json'
af_o = json.loads(bl(2, p_af).decode('utf-8')); af_t = json.loads(bl(3, p_af).decode('utf-8'))
def ckey(e):
    return tuple(e.get(k) for k in ('ts', 'machine', 'pid', 'runner_sha256', 'entry', 'shard'))
merged, seen, conflicts = [], {}, []
for e in af_o['launches'] + af_t['launches']:
    k = ckey(e)
    if k in seen:
        if seen[k] == e:
            continue
        if all(seen[k].get(f) == e.get(f) for f in set(seen[k]) & set(e)):
            m = dict(seen[k]); m.update(e); merged[merged.index(seen[k])] = m; seen[k] = m
        else:
            conflicts.append(k)
    else:
        merged.append(e); seen[k] = e
assert not conflicts, 'launch true-conflicts %s' % conflicts
merged.sort(key=lambda e: e.get('ts') or '')
merged = merged[-50:] if len(merged) > 50 else merged
lt_o = af_o['last_tick']; lt_t = af_t['last_tick']
lt_new = lt_t if lt_t.get('ts', '') >= lt_o.get('ts', '') else lt_o   # mine 17:50:02 > 17:50:01
assert isinstance(lt_new, dict)
raw = json.dumps({'launches': merged, 'last_tick': lt_new}, ensure_ascii=False, indent=1).encode('utf-8')
json.loads(raw.decode('utf-8'))
open(p_af, 'wb').write(raw)
report.append('autofill_state: launches union %d+%d->%d + last_tick take-new %s'
              % (len(af_o['launches']), len(af_t['launches']), len(merged), lt_new['ts']))

# ---- 3) compute_audit.json : full ts-key union both sides + ours newer latest ----
p_ca = 'results/compute_audit.json'
ca_o = json.loads(bl(2, p_ca).decode('utf-8')); ca_t = json.loads(bl(3, p_ca).decode('utf-8'))
by = {}
for e in ca_t['history']:
    by[e['ts']] = e          # mine (228-union from first resolve) first
diff_content = []
for e in ca_o['history']:
    if e['ts'] in by:
        if by[e['ts']] != e:
            diff_content.append(e['ts'])   # same ts different payload = real divergence, flag
    else:
        by[e['ts']] = e        # theirs-only rows (their r336 new samples)
assert not diff_content, 'same-ts payload divergence: %s' % diff_content[:3]
union = [by[t] for t in sorted(by)]
assert len(union) == len(by), 'audit union loss'
ltc = ca_o['latest'] if ca_o['latest']['ts'] >= ca_t['latest']['ts'] else ca_t['latest']
raw = json.dumps({'latest': ltc, 'history': union}, ensure_ascii=False, indent=1).encode('utf-8')
json.loads(raw.decode('utf-8'))
open(p_ca, 'wb').write(raw)
report.append('compute_audit: history full union %d+%d->%d (same-ts content-equal assert pass) + latest take-new %s'
              % (len(ca_o['history']), len(ca_t['history']), len(union), ltc['ts']))

# ---- 4) CODELY.md : entry-level union keep-set + fold to renumbered 26th-batch section ----
p_cm = 'CODELY.md'
o_txt = bl(2, p_cm).decode('utf-8'); t_txt = bl(3, p_cm).decode('utf-8')
o_lines = o_txt.split('\n'); t_lines = t_txt.split('\n')

# ours (bm-b r336) indexes of rows to KEEP (23rd/24th/25th pointers + law variant)
keep_o = {31, 32, 33, 36, 37, 35}   # r91bmc23/r339bma23/r340bma24/r334bmb23/r335bmb25/10KB-law
keep_o_content = {8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 34}  # fold these
fold = [o_lines[i] for i in sorted(keep_o_content) if o_lines[i].strip()]
# my side: keep 3 pointers (renumbered) + drop my old-25th pointers/idx (regenerated below)
my_ptrs_idx = [i for i, l in enumerate(t_lines) if l.startswith('- [2026-09-27 17:3x r334') or l.startswith('- [2026-09-27 17:5x r335') or l.startswith('- [2026-09-27 17:5x r341')]
my_law_old = [l for l in t_lines if l.startswith('- 坑律正典全量归档（2026-09-27 集团令')]
fold += my_law_old  # my law variant folds (bm-b's O35 variant kept live)

new_ptrs = [
    '- [2026-09-27 17:3x r334 bm-b] 坑律（二十六批外迁·指针）：rolling-ledger union 的 dedup 键族必含面实时间键（asof 键件 ts-only 全 None 塌缩 2+2→1 丢行实弹；正典=逐面键探+union 数对账+写回前三方 blob 复验）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十六批』节。',
    '- [2026-09-27 17:5x r335 bm-b] 坑律（二十六批外迁·指针）：tick git 集成的 add/stash 腿不受 r201 mid-rebase 护栏管辖（护栏只闸 commit/push 腿）——rebase UU 停点窗内 tick 照打 blind-add 标记件入 index+stash-pop 造新 UU+毁 :2:/:3: stage——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十六批』节。',
    '- [2026-09-27 17:5x r341 bm-a] 坑律（二十六批外迁·指针）：池批 stale-takeover 须「心跳停滞+git 零活动」双证并取（bm-b 71min stale 但 16:56 commit 在+W2-A 燃烧在途=忙非死；单凭 stale 接管=同 checkpoint 双写毁在飞批；O-1730 律防误伤补丁）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十六批』节。',
]
idx_row = ('- 二十六批外迁（r341 bm-a·2026-09-27·二次撞头当窗整编·行级零丢失）：bm-b r336 与本机 r341 同窗双整编，r176 让号律=本机 25 批节自重编为 26 批；'
           'bm-b 侧保留行 %d 条+本机律行变体 1 条外迁=archive 202609.md『坑律归档 2026-09-27 二十六批』节；保留=法行 2+23/24/25 批指针 5+新指针 3。'
           % len(fold))

# rebuild final CODELY
head = [o_lines[i] for i in [0, 1, 2, 3, 4, 5, 6, 7]]              # headers + User + 冷层指针
kept_law = [o_lines[35]]                                           # 10KB law (bm-b variant)
kept_others = [o_lines[i] for i in [31, 32, 33, 36, 37]]           # 23/24/25 pointers
final = head + kept_law + new_ptrs + [idx_row] + kept_others
final_txt = '\n'.join(final) + '\n'

# zero-loss: every content row of both sides in (final tree) or (fold->archive)
from collections import Counter
ms_union = Counter(l for l in o_lines + t_lines if l.strip())
ms_keep = Counter(l for l in final if l.strip())
ms_fold = Counter(l for l in fold if l.strip())
# new_ptrs/idx_row are net-new replacements; coverage law (r327): every distinct union entry row ends in tree or archive-fold
old_replaced = [t_lines[i] for i in my_ptrs_idx] + [l for l in t_lines if l.startswith('- 二十五批外迁（r341 bm-a')]
fold += [l for l in old_replaced if l not in fold]
set_union = set(l for l in o_lines + t_lines if l.strip())
set_cover = set(l for l in final if l.strip()) | set(l for l in fold if l.strip())
uncovered = set_union - set_cover
# variant duplicates of kept rows (same law, different text per side) fold verbatim to archive (double-preservation)
if uncovered:
    print('variant rows folded to archive: %d' % len(uncovered))
    for u in sorted(uncovered):
        print('  VAR', u[:100])
    fold += sorted(uncovered)
    set_cover = set(l for l in final if l.strip()) | set(l for l in fold if l.strip())
    uncovered = set_union - set_cover
assert not uncovered, 'CODELY fold zero-loss FAILED, uncovered: %s' % [u[:80] for u in list(uncovered)[:5]]
open(p_cm, 'wb').write(final_txt.encode('utf-8'))
wt = os.path.getsize(p_cm)
assert wt <= 10240, 'CODELY %dB over hardline' % wt
report.append('CODELY: entry-level union keep-set 16 rows (laws+23/24/25 ptrs+3 new 26th ptrs) + fold %d rows -> archive 26th; final %dB<=10KB' % (len(fold), wt))

# ---- 5) archive: retitle my 25th->26th section + extend with folded rows ----
p_arch = 'research/memory-archive/202609.md'
arch_raw = open(p_arch, 'rb').read()
eol = b'\r\n' if b'\r\n' in arch_raw[:2000] else b'\n'
txt = arch_raw.decode('utf-8')
old_title = '## 坑律归档 2026-09-27 二十五批（r341 bm-a 当窗超线整编·行级零丢失·rebase 双侧 append union 后 CODELY>10KB 触发·机械解档禁删）'
new_title = '## 坑律归档 2026-09-27 二十六批（r341 bm-a 当窗超线整编·行级零丢失·rebase 双侧 append union 后 CODELY>10KB 触发·r176 让号律：bm-b r336 二十五批先落本节自二十五重编·机械解档禁删）'
assert old_title in txt, 'my 25th section title not found for renumber'
txt = txt.replace(old_title, new_title)
# append folded rows at end of that section (i.e., at file end, since my section is last)
lines_out = txt.split(eol.decode('utf-8'))
addition = [''] + ['## 二十六批续（r341 bm-a 二次撞头折面·行级零丢失）'] + fold + ['']
new_arch = eol.decode('utf-8').join(lines_out + addition)
open(p_arch, 'wb').write(new_arch.encode('utf-8'))
# verify folded lines present verbatim
arch_now = open(p_arch, 'rb').read().decode('utf-8')
missing = [l for l in fold if l not in arch_now]
assert not missing, '%d folded lines missing from archive' % len(missing)
report.append('archive: my section renumbered 25->26 (r176) + %d folded rows appended verbatim (in-archive assert pass)' % len(fold))

print('\n'.join(report))
print('ALL-RESOLVED OK; CODELY wt=%d' % wt)
