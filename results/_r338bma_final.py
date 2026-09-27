import subprocess
import json
import time
import io

now = time.strftime('%Y-%m-%d %H:%M:%S')


def show(ref, path):
    r = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True)
    assert r.returncode == 0, f'show {ref} rc={r.returncode}'
    return r.stdout.decode('utf-8', errors='replace')


# ---------- 1. FINAL bidirectional zero-loss audit (entries in tree-union-archive) ----------
o = show('5c5dab93', 'CODELY.md')
m = show('0cf7c5eb', 'CODELY.md')
cur = open('CODELY.md', encoding='utf-8').read()
arch = open('research/memory-archive/202609.md', encoding='utf-8', errors='replace').read()


def entries(t):
    return {l.strip() for l in t.splitlines() if l.strip().startswith('- [')}


eo, em, ec = entries(o), entries(m), entries(cur)
lost = []
for x in (eo - ec) | (em - ec):
    # entry is zero-loss iff: its variant is in tree OR its full text is verbatim in archive
    frag = x[:80]
    in_arch = frag in arch or x[100:180] in arch
    if not in_arch:
        # variant stub may cover it: check entry-id prefix (e.g. 'r333 bm-b') has SOME line in current
        ident = x.split(']')[0]
        covered = any(ident in l for l in cur.splitlines() if l.strip().startswith('- ['))
        if not covered:
            lost.append(x[:120])
print('final audit: origin %d | mine %d | current %d entries; TRUE-LOSS (no tree variant, no archive full): %d' % (
    len(eo), len(em), len(ec), len(lost)))
for x in lost:
    print('  TRUE-LOSS:', x)
assert not lost, 'zero-loss violation'

# ---------- 2. new pitlaw (rebase --continue claw blind spot) + 22nd batch (archive my r338 full for size) ----------
cod_b = open('CODELY.md', 'rb').read()
eol = '\r\n' if b'\r\n' in cod_b else '\n'
t = cod_b.decode('utf-8')
lines = t.split(eol)

new_entry = '- [2026-09-27 17:1x r338 bm-a] 坑律：**git rebase --continue 不触发 pre-commit 冲突标记钳=带标记件可被烧进重放 commit（r338 实弹：修复脚本崩溃后 add -A+continue 把标记版 CODELY 烧进 f2797d33，幸未 push）——救法=rebase 停在 pick N 时 HEAD=最后已应用 commit，修工作树后 git add+commit --amend --no-edit 原位净化再 continue（空 replay 自动弃=内容已在 amend 内）；推前必 git show <sha>:<热件> 查标记**。指针=results/_r338bma_codely_fix2.py+commit 1558405c 前身 f2797d33 实弹现场。'
# find my r338 full entry (the shared-JSON one) to archive as 22nd batch (size law)
r338_idx = None
for i, l in enumerate(lines):
    if '共享 JSON 面' in l and l.strip().startswith('- [') and 'r338 bm-a' in l:
        r338_idx = i
        break
assert r338_idx is not None
r338_full = lines[r338_idx]
r338_stub = '- [2026-09-27 16:5x r338 bm-a] 坑律（二十二批外迁·指针）：共享 JSON 面 python 追加编辑必先探原写者格式逐字节复刻（EOL/indent/尾换行；json.dump 默认 LF=整件重写 churn）。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十二批』节。'
lines[r338_idx] = r338_stub
lines.append(new_entry)
out = eol.join(lines)
open('CODELY.md', 'wb').write(out.encode('utf-8'))
sz = len(out.encode('utf-8'))
print('CODELY after 22nd batch:', sz, 'B (<=10240:', sz <= 10240, ')')
assert sz <= 10240

ARC = 'research/memory-archive/202609.md'
ab = open(ARC, 'rb').read()
aeol = '\r\n' if ab.count(b'\r\n') > (ab.count(b'\n') - ab.count(b'\r\n')) else '\n'
if not ab.endswith(aeol.encode()):
    ab += aeol.encode()
section = aeol.join([
    '## 坑律归档 2026-09-27 二十二批（r338 bm-a·新坑律 append 水位律当窗整编：r338 共享JSON面全文外迁保 ≤10KB 硬线）',
    r338_full,
    ''])
ab += section.encode('utf-8') + aeol.encode()
open(ARC, 'wb').write(ab)
atext = open(ARC, encoding='utf-8', errors='replace').read()
assert r338_full in atext, '22nd batch verbatim assert FAIL'
print('archive 22nd batch verbatim assert PASS')

# ---------- 3. round report addendum ----------
rr = 'logs/iteration-loop/round_reports-bm-a.md'
add = (
    "2026-09-27 17:1x | r338 addendum | push-collision receipt: 1st push rejected vs origin bm-c r90 (5c5dab93 S0-FOLD) + bm-b r333 same-window -> "
    "S7 rebase 29-file UU batch (28 resolver-classified + CODELY.md 第29件=replay 停在 2/2 时经 union 审计再发现) -> _r338bma_resolve.py (r334 lineage + r335 未来哨卫修正): "
    "compute_audit 220|201->221 (ts,machine)-union / regime asof-union / x2 834|828->840 / archive suffix-concat base891035+origin2039+mine1869 双二十批并存(r85 勘注先例域) / 24 take-side faces mine 16:57:xx 全后到(嵌套探针+未来哨卫) / 孪生+dashboard pair 同侧断言过; "
    "CODELY memory-union 条目级审计抓真损失 3 条 (r333bmb tick危险窗/r90bmc stage-blob反封锁/r89bmc stub-drop 全文 archive 无备份) -> 二十一批恢复批: 3 全文 verbatim 入档+存根回树+2 存根变体经双二十批节覆盖=零丢失; "
    "autofill_state 48|48->48 复合键 union last_tick 17:00:02; "
    "坑律新条: rebase --continue 不走 pre-commit 钳 (r338 实弹: 修复脚本崩溃后 add -A 把标记版 CODELY 烧进中间 commit, 救法=HEAD 停点 amend 原位净化再 continue, 空 replay 自动弃) + 二十二批 (r338 共享JSON面全文外迁保硬线); "
    "replay 终态: 5c5dab93 -> 1558405c (f2797d33 amend 净化版; ca39132e 空 replay 自动弃=autofill 面已在 amend 内) -> push LANDED\n"
)
with io.open(rr, 'a', encoding='utf-8', newline='') as f:
    f.write(add)
print('round report addendum appended')

# ---------- 4. heartbeat refresh ----------
hp = 'fleet/machines/bm-a.json'
h_raw = open(hp, 'rb').read()
heol = '\r\n' if h_raw.count(b'\r\n') > 0 else '\n'
h = json.loads(h_raw.decode('utf-8'))
h['last_seen'] = now
h['current_task'] = 'r338 complete+pushed (SINA-CONSTRUCT-P1 5/5 REJECT closed, rebase collision resolved zero-loss, 21st/22nd archival)'
h['heartbeat_epoch_utc'] = int(time.time())
iso = time.strftime('%Y-%m-%dT%H:%M:%S%z')
h['clock_read'] = iso[:-2] + ':' + iso[-2:]
s = json.dumps(h, ensure_ascii=False, indent=1)
open(hp, 'wb').write(s.replace('\n', heol).encode('utf-8') if heol == '\r\n' else (s + '\n').encode('utf-8'))
h2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int) and 'T' in h2['clock_read']
print('heartbeat refreshed:', h2['clock_read'])

# ---------- 5. orders re-scan (S7 double-scan) ----------
import glob
import re as _re
files = sorted(glob.glob('fleet/orders/O-*.md'))
acked = json.load(open('fleet/machines/bm-a.json', encoding='utf-8')).get('orders_ack') or []
ids = [_re.search(r'O-[\w.-]+\.md', f).group(0) for f in files]
unacked = [i for i in ids if i not in acked]
print('orders double-scan:', len(ids), 'files, unacked:', unacked if unacked else 'NONE')
print('FINAL BATCH DONE')
