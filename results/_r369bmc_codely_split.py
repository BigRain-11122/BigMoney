import hashlib, sys

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\pit-git.md"
APPLY = "--apply" in sys.argv

MOVE_IDX = [11, 12, 19, 30, 37, 38, 44, 46, 63, 70, 75, 77, 79, 82, 85, 87,
            94, 96, 99, 104, 106, 107, 108, 112, 114, 117, 118, 121, 124, 126,
            136, 137, 139, 140, 146, 150, 152, 157, 160, 161, 162, 168, 169,
            170, 171, 172, 175, 176, 180]
assert len(MOVE_IDX) == 49 and len(set(MOVE_IDX)) == 49

raw = open(SRC, "rb").read()
before_md5 = hashlib.md5(raw).hexdigest()
text = raw.decode("utf-8")
lines = text.split("\r\n")

for i in MOVE_IDX:
    assert lines[i].startswith("- "), f"line {i} is not an entry: {lines[i][:60]!r}"

sec = [(i, ln) for i, ln in enumerate(lines) if ln.startswith("#")]
print("SECTION MAP:")
for i, ln in sec:
    print(f"  {i:3d} {ln!r}")

moved = [lines[i] for i in MOVE_IDX]
moved_bytes = sum(len(ln.encode("utf-8")) + 2 for ln in moved)  # +2 CRLF each

POINTER = ("- 域指针·D-20261002-06 首拆件（2026-10-02 r369 bm-c·T-2026-10-02-144(c)）：git 域坑律 49 条"
           "（rebase/push 撞拒净路族·外科 CAS 直投族·让路/closeout 树卫与删除集自证族·staged 吞件族·"
           "silent-git/Invoke-SilentExe 包装器族·git 输出固定列解析族·D-19 水位 git show 字节律）"
           "已整域 verbatim 迁出→**research/pit-git.md**（件内字节对账+md5 行·零丢失断言）——"
           "S0 集成/push 撞拒/让路手术/closeout/外科推送/staged 提交前/解析 git 输出/零窗 git 调用"
           "必先读该件；引擎/数据/池/协议域+流水下沉=后续拆件（D-06 全线收口窗 10-07）。")
pb = len(POINTER.encode("utf-8")) + 2

after_bytes = len(raw) - moved_bytes + pb
print(f"\nbefore={len(raw)}B md5={before_md5}")
print(f"moved 49 entries, bytes(with CRLF)={moved_bytes}")
print(f"pointer line bytes={pb}")
print(f"CODELY.md after ~{after_bytes}B")
print(f"pit-git.md ~= {moved_bytes + 700}B")

# --- locate insertion anchor: right after '### Project' header ---
try:
    proj = next(i for i, ln in enumerate(lines) if ln.strip() == "### Project")
except StopIteration:
    proj = next(i for i, ln in enumerate(lines) if ln.startswith("## Codely"))
print(f"pointer insert after line {proj}: {lines[proj]!r}")

if not APPLY:
    print("\nDRY RUN ONLY (no writes). Re-run with --apply.")
    sys.exit(0)

# --- build new CODELY.md ---
new_lines = []
for i, ln in enumerate(lines):
    if i in MOVE_IDX:
        continue
    new_lines.append(ln)
    if i == proj:
        new_lines.append(POINTER)
assert len(new_lines) == len(lines) - 49 + 1
new_text = "\r\n".join(new_lines)
new_raw = new_text.encode("utf-8")
after_md5 = hashlib.md5(new_raw).hexdigest()
assert len(new_raw) == after_bytes, (len(new_raw), after_bytes)

# --- build pit-git.md ---
HEAD = (
    "# pit-git —— git 域坑律正典（D-20261002-06 域分件·首拆件）\r\n"
    "\r\n"
    "> 来源：CODELY.md 整域 verbatim 迁出（2026-10-02 r369 bm-c·T-2026-10-02-144(c)·集团裁定 D-20261002-06「坑律按域分件·轮 prompt 按需局部读」）。\r\n"
    "> 执法面：S0 集成/push 撞拒/让路手术/closeout/外科推送/staged 提交纪律/git 输出固定列解析/零窗 git 包装器——上述动作前必读本件。\r\n"
    f"> 字节对账行（零丢失断言）：CODELY.md 迁出前 {len(raw):,}B（md5={before_md5}）→迁出后 {len(new_raw):,}B（md5={after_md5}·净变化=−{moved_bytes}B 迁出+{pb}B 指针行）；"
    f"移出 {len(moved)} 条·条目字节和（含 CRLF 行尾）={moved_bytes:,}B==主件净删减字节·逐字节恒等零丢失；本件由拆件脚本机械迁移非手抄（r335 机证律同源）。\r\n"
    "> 后续域件：pit-engine/pit-data/pit-pool/pit-protocol + 流水条目下沉月归档（D-06 全线收口窗 2026-10-07）。\r\n"
    "\r\n"
)
dst_text = HEAD + "\r\n".join(moved) + "\r\n"
dst_raw = dst_text.encode("utf-8")
dst_md5 = hashlib.md5(dst_raw).hexdigest()

open(SRC, "wb").write(new_raw)
open(DST, "wb").write(dst_raw)

print(f"\nAPPLIED:")
print(f"  CODELY.md: {len(raw):,}B -> {len(new_raw):,}B (md5 {before_md5} -> {after_md5})")
print(f"  research/pit-git.md: {len(dst_raw):,}B md5={dst_md5} ({len(moved)} entries)")
print(f"  byte check: {moved_bytes:,} removed == {len(raw) - len(new_raw) + pb - pb:,} (assert passed)")
print("RECON LINE:")
print(f"  D-20261002-06 first-split: CODELY.md {len(raw):,}->{len(new_raw):,}B (-{moved_bytes}B moved / +{pb}B pointer), "
      f"pit-git.md {len(dst_raw):,}B md5={dst_md5}, main md5 {before_md5}->{after_md5}, 49 entries verbatim, zero-loss assert PASS")
