# _r386bma_resolve.py -- R386 bm-a rebase-conflict resolver (canon: bigmoney-conflict-resolve skill)
# Faces: CODELY.md (memory-union, BOTH-SIDES-ARCHIVED variant), archive 202609.md (batch-31
# number-collision yield), daily_report twin (ts-diffpick + md byte-copy),
# fundamental_b_layer_filter (snapshot deep-ts take-new).
# Laws: r327 entry-coverage rebuild / r328 dual-annotation pointer / r139 cover-face re-stitch /
#       r329 twin coupling / R350 staged-blob deep-ts probe / r161/r176 number-collision yield.
import subprocess, json, sys, io

def blob(stage, path):
    return subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True).stdout

report = []

# ---------- 1) archive 202609.md: batch-31 number collision, ours yields (content-subset) ----------
P_ARCH = 'research/memory-archive/202609.md'
b1, b2, b3 = blob(1, P_ARCH), blob(2, P_ARCH), blob(3, P_ARCH)
assert b2.startswith(b1) and b3.startswith(b1), 'archive: both sides must be pure appends on base'
so, sm = b2[len(b1):], b3[len(b1):]
# extract our three migrated entries (verbatim) and verify each is inside origin's batch-31 section
ours_entries = [ln + '\n' for ln in sm.decode('utf-8').splitlines()
                if ln.startswith('- [2026-09-28 05:') and '坑律' in ln]
origin_txt = so.decode('utf-8')
for e in ours_entries:
    assert e.strip() in origin_txt, 'YIELD ABORT: our migrated entry not covered by origin batch-31'
yield_note = ('\n> 让路注记（r386 bm-a·r161/r176 撞号让号先例·commit 时间序 bm-b r363 三十一批先落 origin=正典节）：'
              'bm-a R386 同窗独立整编同批号（同三条 r361/r384/r362 逐条恒等且⊂ r363 五条节），bm-a 侧节让路丢弃=零内容损失；'
              'bm-a 新坑律（hermetic-fixture 面）已并入 CODELY 热层，指针行双批注见热层（r328 律）。\n')
new_arch = b2.rstrip(b'\n') + b'\n' + yield_note.encode('utf-8')
open(P_ARCH, 'wb').write(new_arch)
report.append(f'archive: yielded batch-31 (3 entries verbatim-covered by origin 5-entry section), '
              f'{len(b1)}+{len(so)}+note -> {len(new_arch)}B')

# ---------- 2) CODELY.md: entry-coverage rebuild (both sides archived; union keeps both new pit-laws) ----------
P_C = 'CODELY.md'
c1, c2, c3 = blob(1, P_C), blob(2, P_C), blob(3, P_C)
BOM = b'\xef\xbb\xbf'
def core(b): return b[3:] if b[:3] == BOM else b
o_txt, m_txt = core(c2).decode('utf-8'), core(c3).decode('utf-8')
# our new pit-law entry (the only entry ours has that origin lacks), identified by r386 marker
ours_new = [ln for ln in m_txt.splitlines() if ln.startswith('- [2026-09-28 06:3x r386 bm-a]')]
assert len(ours_new) == 1, 'expected exactly one r386 bm-a new pit-law entry'
entry = ours_new[0]
assert entry not in o_txt, 'r386 entry already on origin side?'
assert entry in m_txt
# dual-annotation note appended after origin's batch-31 pointer line (r328)
pointer_anchor = '三十一批'
idx = o_txt.rfind(pointer_anchor)
assert idx >= 0
line_end = o_txt.find('\n', idx)
dual = ('（r386 bm-a 同窗独立整编同批号撞号：bm-a 侧三条 r361/r384/r362 恒等⊂本批五条、bm-a 节让路=archive 让路注记；'
        'bm-a 新坑律一条并入热层——r328 双批注并含）')
new_c_txt = o_txt[:line_end] + dual + o_txt[line_end:]
# append our new entry at the end (entry-zone)
new_c_txt = new_c_txt.rstrip('\n') + '\n\n' + entry + '\n'
new_c_bytes = BOM + new_c_txt.encode('utf-8')
open(P_C, 'wb').write(new_c_bytes)
assert len(new_c_bytes) <= 10240, f'CODELY over 10KB line: {len(new_c_bytes)}'
# coverage check: every entry line on either side must be in new CODELY or in archive-new
arch_txt = new_arch.decode('utf-8', errors='replace')
def entries(t): return {ln.strip() for ln in t.splitlines() if ln.strip().startswith('- [2026-09-28') and '坑律' in ln}
eo, em = entries(o_txt), entries(m_txt)
en = entries(new_c_txt)
missing = [e for e in (eo | em) if e not in en and e not in arch_txt]
assert not missing, f'coverage FAIL: {len(missing)} entries lost: {missing[:2]}'
report.append(f'CODELY: entry-coverage rebuild ok (origin {len(eo)} + ours {len(em)} -> new {len(en)} hot + rest archived), '
              f'{len(new_c_bytes)}B <=10KB')

# ---------- 3) daily_report twin: json deep-ts pick, md byte-copy from SAME side ----------
P_J, P_M = 'docs/daily_report/REPORT-2026-09-28.json', 'docs/daily_report/REPORT-2026-09-28.md'
j2, j3 = blob(2, P_J), blob(3, P_J)
m2, m3 = blob(2, P_M), blob(3, P_M)
def deep_ts(b):
    d = json.loads(b.decode('utf-8-sig'))
    cands = []
    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and len(v) >= 19 and v[:2] == '20' and ('T' in v or ':' in v[10:13]):
                    cands.append(v)
                walk(v, path + (k,))
        elif isinstance(o, list):
            for i, v in enumerate(o): walk(v, path + (i,))
    walk(d, ())
    return max(cands) if cands else ''
t2, t3 = deep_ts(j2), deep_ts(j3)
side = 2 if t2 >= t3 else 3   # same-second tie -> HEAD/origin side (r140)
jb = j2 if side == 2 else j3
mb = m2 if side == 2 else m3
json.loads(jb.decode('utf-8-sig'))  # parse gate
open(P_J, 'wb').write(jb)
open(P_M, 'wb').write(mb)
report.append(f'daily_report twin: deep-ts pick side={":2:origin" if side==2 else ":3:ours"} ({t2} vs {t3}), md byte-copied same side')

# ---------- 4) fundamental_b_layer_filter: snapshot deep-ts take-new (R350 staged-blob probe) ----------
P_F = 'results/fundamental_b_layer_filter.json'
f2, f3 = blob(2, P_F), blob(3, P_F)
t2, t3 = deep_ts(f2), deep_ts(f3)
fb = f2 if t2 >= t3 else f3
json.loads(fb.decode('utf-8-sig'))
open(P_F, 'wb').write(fb)
report.append(f'fundamental_b_layer_filter: deep-ts take side={":2:" if t2>=t3 else ":3:"} ({t2} vs {t3})')

# ---------- final: conflict-marker gate ----------
for p in [P_ARCH, P_C, P_J, P_M, P_F]:
    raw = open(p, 'rb').read()
    assert b'<<<<<<<' not in raw and b'>>>>>>>' not in raw, f'conflict markers left in {p}'

print('R386 RESOLVER OK')
for r in report:
    print(' -', r)
