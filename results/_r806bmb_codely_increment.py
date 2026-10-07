# r806 bm-b CODELY main-file increment migration (ritual r441/r703/r789 lineage; window per
# D-20261007-01(4) extended to 10-09). Trigger: S4 new-pit append on 30,428B main (292B headroom)
# would exceed 30,720B cap -> same-window mini-split mandated by water-level law.
# All six touched files probed pure-LF (0 CRLF) this window; split/join-by-LF is byte-safe here.
# New pit entry written as plain CJK source text, runtime .encode('utf-8') -- r666 byte-as-str law.
import hashlib, json, subprocess, sys, io, os

MAIN = 'CODELY.md'

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

def read_b(p):
    with open(p, 'rb') as f:
        return f.read()

def write_b(p, b):
    with open(p, 'wb') as f:
        f.write(b)

# --- step 0: prescan (treasure_guard, rc3 expected-hit logged per migration ritual) ---
prescan = subprocess.run([sys.executable, 'Tools/treasure_guard.py', 'prescan',
                          MAIN, 'research/pit-tooling.md', 'research/pit-git-resolver.md',
                          'research/pit-engine-freeze-editor.md', 'research/pit-protocol-d19.md'],
                         capture_output=True, text=True, encoding='utf-8', errors='replace')
prescan_rc = prescan.returncode

main_b = read_b(MAIN)
main_before = len(main_b)

# --- step 1: extract 4 foreign pointer rows by unique prefix, count==1 gate each ---
needles = {
    'r672_d19_ptr': ('域指针·r672 bm-c'.encode('utf-8'), 'research/pit-protocol-d19.md'),
    'r679_resolver_ptr': ('域指针·r679 bm-c'.encode('utf-8'), 'research/pit-git-resolver.md'),
    'r830_freeze_ptr': ('- [2026-10-07 15:3x r830 bm-a]'.encode('utf-8'), 'research/pit-engine-freeze-editor.md'),
    'r832_writerpause_ptr': ('- [2026-10-07 16:3x r832 bm-a]'.encode('utf-8'), 'research/pit-git-resolver.md'),
}
# needle must sit at a line start to avoid subline hits
lines = main_b.split(b'\n')
extracted = {}
new_lines = []
for ln in lines:
    matched = None
    for k, (needle, target) in needles.items():
        if ln.startswith(needle):
            assert matched is None, 'double-match line'
            matched = k
    if matched:
        assert matched not in extracted, 'needle matched twice: ' + matched
        extracted[matched] = ln
    else:
        new_lines.append(ln)
assert set(extracted.keys()) == set(needles.keys()), 'missing needles: ' + repr(sorted(set(needles) - set(extracted)))

main_stripped = b'\n'.join(new_lines)

# --- step 2: new pit entry (S4, four-question gate passed, one matter, <=1.5KB) ---
entry = ('- [2026-10-07 18:5x r806 bm-b] **会话死→claim keepalive 断供→合法接管→活双烧坑（r601 族复发·新律面=keepalive 责任体错位：bm-b daemon 无自推 claim 刷新 vs bm-a daemon r290 四连自推）**：r806 前会话死于轮中（~18:03）后 FUND-DIVLOWVOL-P1-NULLS claim keepalive 断供（末次 owner_since 刷新 17:58:08·末次 nulls 证据推 17:54）→claim 龄 25min>20min 门→bm-a autofill 18:19:52 合法接管+18:24:02 launch（pid 53000·launch 台账实证）→本机 burner（17:46:35 起·本地 1826/2000·26 行未提交）照烧=活双烧 ~10min（探测两证=origin nulls 1800 vs 本地 1826 差+共享面嵌套 shards[0].owner=bm-a@18:24:17——顶层 owner=None 是 r720 盲区勿单读）。处置=r601 正典：杀本机 6 进程（父+5 worker·先验 cmdline 归属）+partial 26 行移旁 results/_r806bmb_nulls_partial.jsonl（零丢失·不入共享面防与 bm-a 单写者撞）+nulls.jsonl checkout origin verbatim+池面让路零 kill-advice+S6 腿02 settle 冲镜像防 daemon 按陈旧自 claim（owner=bm-b@17:58）re-launch。How to apply：①会话轮中必查自家 in-flight claim 的 owner_since 距今龄>15min 即推 checkpoint commit；②daemon 侧 r290 self-commit keepalive 缺失=本机 daemon 版本漂移候修面（bm-a 有 bm-b 无）；③双烧探测读 origin refs 非工作树（r598 律）。')
entry_b = entry.encode('utf-8')
assert len(entry_b) <= 1600, 'entry over 1.5KB budget: %d' % len(entry_b)

main_new = main_stripped
if not main_new.endswith(b'\n'):
    main_new += b'\n'
main_new += entry_b + b'\n'

# byte equation (constructor == equation, r669 dual-derive gate)
out_bytes = sum(len(v) + 1 for v in extracted.values())  # each row + its LF
constructor = main_before - out_bytes + len(entry_b) + 1
assert len(main_new) == constructor, 'byte equation failed: %d vs %d' % (len(main_new), constructor)

# --- step 3: append extracted rows verbatim to domain tails (all faces probed LF) ---
results_entries = {}
for k, (needle, target) in needles.items():
    tb = read_b(target)
    row = extracted[k]
    tb_new = tb
    if tb_new and not tb_new.endswith(b'\n'):
        tb_new += b'\n'
    tb_new += row + b'\n'
    write_b(target, tb_new)
    results_entries[k] = {'target': target, 'bytes': len(row), 'sha16': sha16(row),
                          'target_bytes_after': len(tb_new)}

write_b(MAIN, main_new)

# --- step 4: post-write verification ---
main_after_b = read_b(MAIN)
assert main_after_b == main_new, 'main write-back mismatch'
for k, (needle, target) in needles.items():
    assert main_after_b.count(extracted[k]) == 0, 'extracted row still in main: ' + k
    assert read_b(target).count(extracted[k]) == 1, 'row not exactly-once in target: ' + k
assert main_after_b.count(entry_b) == 1
assert len(main_after_b) <= 30720, 'main over cap: %d' % len(main_after_b)

over = []
for f in os.listdir('research'):
    if f.startswith('pit-') and f.endswith('.md'):
        sz = os.path.getsize(os.path.join('research', f))
        if sz > 30720:
            over.append((f, sz))
assert not over, 'domain file over cap: ' + repr(over)

# --- step 5: registry line (append-only, TREASURE_REGISTRY in/out record) ---
reg = 'knowledge/TREASURE_REGISTRY.md'
reg_b = read_b(reg)
reg_line = ('- 2026-10-07 18:5x bm-b r806 D-06 主件增量批迁移仪式（触发=S4 新坑 append 于 30,428B 余量 292B 主件→当窗即办·r441/r703/r789 仪式同款·D-20261007-01④ 顺延窗 10-09）：prescan rc3 留痕（CODELY.md+research/ 全族+TREASURE_REGISTRY 登记册类 fail-closed 面具）——出入记录本行①零丢失断言②：CODELY.md 主件 30,428B→%dB（4 条外机指针行 verbatim 迁移非删除：r672→pit-protocol-d19.md/%dB·r679→pit-git-resolver.md/%dB·r830→pit-engine-freeze-editor.md/%dB·r832→pit-git-resolver.md/%dB）+r806 新坑（会话死→keepalive 断供→合法接管→活双烧）%dB 入主件；字节方程式双 derive 恒等门过；全域件 ≤30,720B；receipt=results/_r806bmb_codely_increment.json。' % (
    len(main_after_b), results_entries['r672_d19_ptr']['bytes'], results_entries['r679_resolver_ptr']['bytes'],
    results_entries['r830_freeze_ptr']['bytes'], results_entries['r832_writerpause_ptr']['bytes'], len(entry_b)))
reg_new = reg_b
if reg_new and not reg_new.endswith(b'\n'):
    reg_new += b'\n'
reg_new += reg_line.encode('utf-8')
write_b(reg, reg_new)

receipt = {
 'ritual': 'r441/r703/r789 migration ritual (r806 bm-b, prescan rc3 logged, window D-20261007-01(4) ext 10-09)',
 'prescan_rc': prescan_rc,
 'entries': results_entries,
 'new_pit': {'id': 'r806_session_death_claim_stale_double_burn', 'bytes': len(entry_b), 'sha16': sha16(entry_b), 'placement': 'main tail'},
 'asserts': [
   'main %d -> %d B (<=30720)' % (main_before, len(main_after_b)),
   'byte equation exact (4 rows + LFs out, 1 entry + LF in)',
   'each extracted row verbatim x1 in target, x0 in main, sha16-anchored',
   'all pit-*.md <= 30720B',
   'registry in/out line appended',
 ],
 'sizes': {'main_before': main_before, 'main_after': len(main_after_b)},
 'pit_files': len([f for f in os.listdir('research') if f.startswith('pit-') and f.endswith('.md')]),
 'registry_line_appended': True,
}
with io.open('results/_r806bmb_codely_increment.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(json.dumps({'prescan_rc': prescan_rc, 'main_before': main_before, 'main_after': len(main_after_b),
                  'moved': {k: v['bytes'] for k, v in results_entries.items()}, 'new_pit_bytes': len(entry_b)}))
