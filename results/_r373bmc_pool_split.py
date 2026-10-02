# -*- coding: utf-8 -*-
# _r373bmc_pool_split.py -- D-20261002-06 pool-domain split (piece 2, r373 bm-c).
# Mechanism verbatim from r369 first-split (_r369bmc_codely_split.py):
# byte-level read/write, CRLF-preserve, verbatim move, per-entry content-anchor
# asserts (index-drift guard), byte reconciliation + md5 lines, zero-loss assert.
import hashlib, sys

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\pit-pool.md"
APPLY = "--apply" in sys.argv

# (line_idx, must_contain_marker) -- pool domain: runnable_pool claims/harvest/
# ghost-ready/supply/governance/file-editing family.
MOVE = [
    (8,   "r289 bm-c"),        # 共享 JSON 整文件重写格式坑 (runnable_pool.json)
    (12,  "r508 bm-b"),        # 池批件 id 检索禁裸子串坑
    (37,  "r488 bm-b"),        # 烧录不翻池=幽灵 ready 面坑
    (39,  "r297 bm-c"),        # push 阻塞期池认领不可见坑
    (54,  "r497 bm-b"),        # burn runner claim 握手+park_note 盲区
    (59,  "r509 bm-a"),        # runnable_pool 外科=文本级定点编辑律
    (60,  "r309 bm-c"),        # 池 ghost 面死锁供给触发坑
    (62,  "载面 indent 漂移坑"),# r500 bm-b (r289 载面 indent)
    (63,  "收养×池面复活幽灵 ready 坑"),
    (64,  "r310 bm-c"),        # daemon harvest 翻面不含产物件坑
    (67,  "r513 bm-a"),        # WIP 阻断→池面三联症 stale-view
    (70,  "r514 bm-a"),        # 池登记 id 镜像 _entry_of 核验律
    (74,  "r316 bm-c"),        # host_gates 数据缺件过闸坑
    (78,  "r507 bm-b"),        # 供给写入面×池冲突基底选错坑
    (88,  "r526 bm-a"),        # shard.owner 停泊批红牌根治对象律
    (89,  "r527 bm-a"),        # 点火前必读 entry 层治理三字段坑
]
MOVE_IDX = [m[0] for m in MOVE]
assert len(MOVE_IDX) == 16 and len(set(MOVE_IDX)) == 16

raw = open(SRC, "rb").read()
before_md5 = hashlib.md5(raw).hexdigest()
text = raw.decode("utf-8")
lines = text.split("\r\n")

for i, marker in MOVE:
    assert lines[i].startswith("- "), f"line {i} not an entry: {lines[i][:60]!r}"
    assert marker in lines[i], f"line {i} missing anchor {marker!r}: {lines[i][:80]!r}"

# pointer insert point: right after the first-split git pointer line
anchor_idx = next(i for i, ln in enumerate(lines) if "域指针·D-20261002-06 首拆件" in ln)
assert anchor_idx == 5, f"git pointer not at 5: {anchor_idx}"

moved = [lines[i] for i in MOVE_IDX]
moved_bytes = sum(len(ln.encode("utf-8")) + 2 for ln in moved)

POINTER = ("- 域指针·D-20261002-06 池域拆件（2026-10-02 r373 bm-c·T-2026-10-02-144(c)）：池域坑律 16 条"
           "（幽灵 ready/双层翻面族·claim 握手与认领可见性族·harvest/供给停摆族·池文件字节编辑律·entry 层治理面）"
           "已整域 verbatim 迁出→**research/pit-pool.md**（件内字节对账+md5 行·零丢失断言）——"
           "池认领/翻面/harvest/供给判定/池面冲突解/WM 红牌定性/池文件编辑前必读该件；"
           "余域=引擎/数据/协议+流水下沉（D-06 全线收口窗 10-07）。")
pb = len(POINTER.encode("utf-8")) + 2

after_bytes = len(raw) - moved_bytes + pb
print(f"before={len(raw):,}B md5={before_md5}")
print(f"moved 16 entries, bytes(with CRLF)={moved_bytes:,}")
print(f"pointer line bytes={pb}")
print(f"CODELY.md after ~{after_bytes:,}B")
print(f"pit-pool.md ~= {moved_bytes + 800:,}B")

if not APPLY:
    print("\nDRY RUN ONLY (no writes). Re-run with --apply.")
    sys.exit(0)

new_lines = []
for i, ln in enumerate(lines):
    if i in MOVE_IDX:
        continue
    new_lines.append(ln)
    if i == anchor_idx:
        new_lines.append(POINTER)
assert len(new_lines) == len(lines) - 16 + 1
new_text = "\r\n".join(new_lines)
new_raw = new_text.encode("utf-8")
after_md5 = hashlib.md5(new_raw).hexdigest()
assert len(new_raw) == after_bytes, (len(new_raw), after_bytes)
# zero-loss: every moved entry absent from new SRC, present verbatim in DST
for ln in moved:
    assert ln not in new_text, "moved entry still in main file!"

HEAD = (
    "# pit-pool —— 池域坑律正典（D-20261002-06 域分件·第二拆件）\r\n"
    "\r\n"
    "> 来源：CODELY.md 整域 verbatim 迁出（2026-10-02 r373 bm-c·T-2026-10-02-144(c)·集团裁定 D-20261002-06「坑律按域分件·轮 prompt 按需局部读」）。\r\n"
    "> 执法面：池认领/翻面（烧+翻原子·entry+shard 双层）/harvest 对账/供给与饥饿判定/池面冲突解基底/WM 红牌定性/池文件（runnable_pool.json）字节级编辑——上述动作前必读本件。\r\n"
    f"> 字节对账行（零丢失断言）：CODELY.md 迁出前 {len(raw):,}B（md5={before_md5}）→迁出后 {len(new_raw):,}B（md5={after_md5}·净变化=−{moved_bytes:,}B 迁出+{pb}B 指针行）；"
    f"移出 {len(moved)} 条·条目字节和（含 CRLF 行尾）={moved_bytes:,}B==主件净删减字节·逐字节恒等零丢失；本件由拆件脚本机械迁移非手抄（r335 机证律同源）。\r\n"
    "> 已拆域件：pit-git.md（r369·49 条）；余域=引擎/数据/协议+流水下沉（D-06 全线收口窗 2026-10-07）。\r\n"
    "\r\n"
)
dst_text = HEAD + "\r\n".join(moved) + "\r\n"
dst_raw = dst_text.encode("utf-8")
dst_md5 = hashlib.md5(dst_raw).hexdigest()
for ln in moved:
    assert ln in dst_text, "moved entry missing from DST!"

open(SRC, "wb").write(new_raw)
open(DST, "wb").write(dst_raw)

print(f"\nAPPLIED:")
print(f"  CODELY.md: {len(raw):,}B -> {len(new_raw):,}B (md5 {before_md5} -> {after_md5})")
print(f"  research/pit-pool.md: {len(dst_raw):,}B md5={dst_md5} ({len(moved)} entries)")
print("RECON LINE:")
print(f"  D-20261002-06 pool-split: CODELY.md {len(raw):,}->{len(new_raw):,}B (-{moved_bytes:,}B moved / +{pb}B pointer), "
      f"pit-pool.md {len(dst_raw):,}B md5={dst_md5}, main md5 {before_md5}->{after_md5}, 16 entries verbatim, zero-loss assert PASS")
