# -*- coding: utf-8 -*-
"""r1047 bm-a CODELY.md hot-cold migration (r983/r800 paradigm; TREASURE_PROTECTION_LAW s2 migration entry).

Paradigm: prescan rc3 redline recorded (registry hit CODELY.md) -> zero-loss verbatim
migration of 13 window-batch pit/flow rows to research/memory-archive/202610.md new
window-batch section -> header double-write dedup -> one compact pointer row ->
receipt with byte equation -> TREASURE_REGISTRY append.

All operations byte-domain; atomic writes (temp + os.replace); no delete (archive keeps all).
"""
import hashlib, json, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (results/ parent)
CODELY = os.path.join(ROOT, 'CODELY.md')
ARCHIVE = os.path.join(ROOT, 'research', 'memory-archive', '202610.md')
REGISTRY = os.path.join(ROOT, 'knowledge', 'TREASURE_REGISTRY.md')
RECEIPT = os.path.join(ROOT, 'results', '_r1047bma_codely_hotcold_receipt.json')

def atomic_write(path, data):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix='.hotcold_')
    with os.fdopen(fd, 'wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def sha(b):
    return hashlib.sha256(b).hexdigest()

# ---------- 0. load ----------
pre_codely = open(CODELY, 'rb').read()
pre_archive = open(ARCHIVE, 'rb').read()
lines = pre_codely.splitlines(keepends=True)
assert len(lines) == 42, 'line count drift: %d' % len(lines)

# ---------- 1. migration set (0-based indices) ----------
MIG = [26, 27, 28, 29, 31, 32, 33, 35, 36, 37, 39, 40, 41]
EXPECT_PREFIX = {
    26: '[2026-10-15 16:5x r983 bm-b]',
    27: '[2026-10-15 17:0x] bm-c r1031',
    28: '[2026-10-15 17:4x r985 bm-b]',
    29: '[2026-10-17 05:5x r1027 bm-a]',
    31: '[2026-10-17 07:5x r1028 bm-a]',
    32: '[2026-10-17 09:36 r987 bm-b]',
    33: '[2026-10-17 13:2x r1066 bm-c]',
    35: '[2026-10-17 14:xx r1032 bm-a]',
    36: '[2026-10-17 18:1x r1069 bm-c]',
    37: '[2026-10-18 02:4x r1044 bm-a]',
    39: '[2026-10-18 04:5x r1045 bm-a]',
    40: '[2026-10-18 05:3x r1046 bm-a]',
    41: '[2026-10-18 02:2x r998 bm-b]',
}
migrated = []
for idx in MIG:
    raw = lines[idx]
    txt = raw.decode('utf-8', errors='replace').lstrip('- ')
    assert txt.startswith(EXPECT_PREFIX[idx]), 'prefix mismatch at L%d: %r' % (idx + 1, txt[:60])
    migrated.append(raw)
mig_bytes = sum(len(m) for m in migrated)

# ---------- 2. header dedup (lines 1-6 -> 2 clean lines) ----------
assert lines[0].rstrip(b'\r\n') == b'## Codely Structured Memories### Project'
assert lines[1].rstrip(b'\r\n') == b'## Codely Structured Memories'
assert lines[3].rstrip(b'\r\n') == b'### User'
header_new = b'## Codely Structured Memories\r\n### User\r\n'
header_removed_bytes = sum(len(lines[i]) for i in range(6)) - len(header_new)

# ---------- 3. new pointer row (CRLF face) ----------
pointer_text = (
    "- 冷层指针（r1047 bm-a 热冷整编·r983-r1046 窗批·D-20260924-01 范式·prescan rc3 判红实录=CODELY.md 登记簿命中·"
    "迁移范式入口=TREASURE_PROTECTION_LAW §2+r800/r983 先例·CEO 记忆治理令 2026-10-18 00:2x 顺风窗）："
    "r983 双写腐坏判例/r1031 部分 stash push×daemon 活窗/r985 wb-open 先截断/r1027 MF 源封锁双差分+饿死律/"
    "r1028 watermark UU newer-wins/r987 sparse cone 重物化/r1066 estate 回执时滞/r1032 rebase-continue quit+cherry-pick/"
    "r1069 ORD 水位 d19 守卫单源/r1044 Taildrop Downloads 扫腿/r1045 子进程 stdout capture+relay/r1046 idle fast-path 解锁三件/"
    "r998 IndexTTS 登记 13 条行原行全文 verbatim=archive 202610.md『热冷整编 2026-10-18 r1047 bm-a 窗批』节"
    "（receipt=results/_r1047bma_codely_hotcold_receipt.json）——执行面法条仍活：watermark 探针面 UU 按 ts newer-wins（r1028 律）/"
    "嵌套仓 sparse 清仓后全量 checkout 重物化（r987 律）/rebase --continue 死循环=quit+cherry-pick 保 estate（r1032 律）/"
    "closeout 水位步一律 d19_watermark.py update --advance 禁字面（r1069 律）/Taildrop 取件验证必扫 Downloads（r1044 律）/"
    "spawn 子进程依赖输出必 capture_output+relay（r1045 律）/环 idle fast-path 死锁解锁=backlog 行+force-pull poke+wake（r1046 律）。"
    "新坑律仍先入本件后回扫（O-20260927-0230 律）。\r\n"
)
pointer_bytes = pointer_text.encode('utf-8')

# ---------- 4. build new CODELY ----------
keep = []
keep.append(header_new)
for i in range(6, 26):            # L07-L26: user meta row + section heads + domain pointers + pin rows + reference rows
    keep.append(lines[i])
keep.append(pointer_bytes)       # compact pointer replaces the 13 migrated rows
new_codely = b''.join(keep)
assert b'\x00' not in new_codely

# ---------- 5. archive append block ----------
block_head = (
    "\n## 热冷整编 2026-10-18 r1047 bm-a 窗批（CODELY.md 流水判例 13 条 verbatim 迁入·D-20260924-01/O-20260927-0230 范式·"
    "prescan rc3 判红实录·receipt=results/_r1047bma_codely_hotcold_receipt.json）\n\n"
).encode('utf-8')
block = block_head + b''.join(migrated)
if not block.endswith(b'\n'):
    block += b'\n'
post_archive = pre_archive + block

# ---------- 6. verbatim zero-loss assertions ----------
for m in migrated:
    assert m in post_archive, 'verbatim fail: %r' % m[:60]
dropped_blank_bytes = sum(len(lines[i]) for i in (30, 34, 38))  # L31/L35/L39 structural blanks inside migration span
eq_removed = len(pre_codely) - len(new_codely)
eq_expect = mig_bytes + header_removed_bytes + dropped_blank_bytes - len(pointer_bytes)
assert eq_removed == eq_expect, 'byte equation drift: %d vs %d' % (eq_removed, eq_expect)
assert len(post_archive) == len(pre_archive) + len(block)

# ---------- 7. atomic writes ----------
atomic_write(CODELY, new_codely)
atomic_write(ARCHIVE, post_archive)

# ---------- 8. registry append ----------
pre_reg = open(REGISTRY, 'rb').read()
row = (
    "- 2026-10-18 07:1x bm-a r1047 CODELY.md 热冷整编迁移范式（D-20260924-01/O-20260927-0230 ≤10KB 硬线追账·r800/r983 范式同窗·"
    "prescan 实弹 rc3 判红：CODELY.md+archive 202610.md 双登记簿命中·迁移范式入口=TREASURE_PROTECTION_LAW §2·"
    "CEO 记忆治理直令 2026-10-18 00:2x 顺风窗）：流水判例 13 条行（r983/r1031/r985/r1027/r1028/r987/r1066/r1032/r1069/r1044/r1045/r1046/r998）"
    "verbatim 迁 archive 202610.md『热冷整编 2026-10-18 r1047 bm-a 窗批』节+双写头 6 行去重（r983 归一恒等范式）+紧凑指针行回填·"
    "零丢失对账=removed %dB == migrated %dB + dedup %dB - pointer %dB·archive +%dB·逐行 verbatim 断言 13/13 PASS·"
    "receipt=results/_r1047bma_codely_hotcold_receipt.json\n"
).encode('utf-8')
post_reg = pre_reg + (b'\n' if not pre_reg.endswith(b'\n') else b'') + row
atomic_write(REGISTRY, post_reg)

# ---------- 9. receipt ----------
receipt = {
    'ts': '2026-10-18T07:1x+08:00',
    'machine': 'bm-a', 'round': 'r1047',
    'action': 'CODELY.md hot-cold migration (13 flow/pit rows verbatim -> archive 202610.md window-batch)',
    'paradigm': 'D-20260924-01 / O-20260927-0230 / TREASURE_PROTECTION_LAW s2 migration entry; precedents r800 bm-a / r983 bm-b',
    'prescan': 'rc3 redline recorded (registry hit CODELY.md) — expected first leg of migration paradigm',
    'authorization_chain': 'O-20260927-0230 (<=10KB hard line, same-window obligation) + CEO memory-governance direct order 2026-10-18 00:2x (orders L1188) + O-20261015-1230/1235 lineage',
    'codely': {
        'pre_bytes': len(pre_codely), 'post_bytes': len(new_codely),
        'pre_sha256': sha(pre_codely), 'post_sha256': sha(new_codely),
        'rows_migrated': len(migrated), 'migrated_bytes': mig_bytes,
        'header_dedup_removed_bytes': header_removed_bytes,
        'dropped_blank_bytes': dropped_blank_bytes,
        'pointer_row_bytes': len(pointer_bytes),
    },
    'archive': {
        'pre_bytes': len(pre_archive), 'post_bytes': len(post_archive),
        'pre_sha256': sha(pre_archive), 'post_sha256': sha(post_archive),
        'appended_bytes': len(block),
    },
    'equation': {
        'removed_from_codely': eq_removed,
        'expected': eq_expect,
        'match': eq_removed == eq_expect,
    },
    'verbatim_assertions': '13/13 PASS (each migrated line byte-identical inside post_archive)',
    'registry_append_bytes': len(post_reg) - len(pre_reg),
}
atomic_write(RECEIPT, json.dumps(receipt, ensure_ascii=False, indent=1).encode('utf-8'))
print(json.dumps({k: receipt[k] for k in ('codely', 'archive', 'equation', 'verbatim_assertions')}, ensure_ascii=False))
print('HOTCOLD_OK')
