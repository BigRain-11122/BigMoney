# -*- coding: utf-8 -*-
# r380 bm-c T-144(c) data-domain split: 5 entries verbatim -> research/pit-data.md
# Laws: r530 bytes-in/bytes-out; r509 text-level surgical edit; D-06 byte-recon mandatory;
# new-pit-law same-window append (O-20260927-0230: new pits enter CODELY.md first).
import hashlib, os

CWD = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = os.path.join(CWD, "CODELY.md")
PIT = os.path.join(CWD, "research", "pit-data.md")

raw = open(CODELY, "rb").read()
size_before = len(raw)
md5_before = hashlib.md5(raw).hexdigest()
assert b"\r\n" in raw, "working tree expected CRLF"
lines = raw.split(b"\r\n")

ANCHORS = [
    "- [2026-10-01 07:0x r496 bm-b] astock panel complete 活锁两-pass".encode("utf-8"),
    "- [2026-10-01 12:2x r503 bm-b] S6 日刷数据面".encode("utf-8"),
    "- [2026-10-01 20:4x r334 bm-c] lane-pin 数据面".encode("utf-8"),
    "- [2026-10-01 23:5x r340 bm-c] 采集器挂死面".encode("utf-8"),
    "- [2026-10-02 15:3x r371 bm-c] 采集器网关".encode("utf-8"),
]
idx = {}
for a in ANCHORS:
    hits = [i for i, l in enumerate(lines) if l.startswith(a)]
    assert len(hits) == 1, f"anchor not unique: {a[:40]!r} hits={hits}"
    idx[a] = hits[0]

moved = [lines[idx[a]] for a in ANCHORS]
moved_bytes = sum(len(l) + 2 for l in moved)

PTR = (
    "- 域指针·D-20261002-06 数据域拆件（2026-10-02 r380 bm-c·T-2026-10-02-144(c)）：数据域坑律 5 条"
    "（采集器挂死诊断与网关 pid 复用自愈族·数据面板 complete 活锁两-pass+冻结探针时序族·prereg 数据文件 hash 钉日刷轮换族·lane-pin 数据面 selftest 两态律）"
    "已整域 verbatim 迁出→**research/pit-data.md**（件内字节对账+md5 行·零丢失断言）——"
    "数据面板停泊诊断/采集器活性判定与网关自愈/prereg 数据钉法/lane-pin 数据面红腿定性前必读该件；"
    "余域=协议+流水下沉（D-06 全线收口窗 10-07）。"
).encode("utf-8")

NEWLAW = (
    "- [2026-10-02 19:1x r380 bm-c] python 解析 git status --porcelain 的 stdout.strip() 剥首行前导空格坑"
    "（S0 纯 FF 分面 checkout 实弹·git 固定列输出解析族 r366/r572 第三例）：r.stdout.strip() 把首行 ' M docs/...' 的行首空格剥成 'M docs/...'"
    "——后续 line[3:] 切片从 'd' 变 'o'（'docs/'→'ocs/' 幽灵路径），批量 checkout 首锚 pathspec 不匹配 rc=1"
    "（git 对其余 pathspec 部分执行=其余件已恢复、首件残留旧版的半完成态）；两轮独立解析同错（第二轮回首行换 .md 件再牺牲一件）靠 repr 逐行诊断定谳。"
    "正法=porcelain 解析禁对整输出 strip（空行过滤逐行 l.strip() 判 bool 即可）或改用 -z NUL 分隔面；"
    "诊断签名=pathspec 报错文件名=真实文件名截头 2 字符。"
    "How to apply：一切固定列 git 输出解析脚本按行原样入列表、仅对单行判空，勿对整输出 strip；"
    "遇「pathspec 'Xocs/...' did not match」首查整段 strip 面勿疑 git。"
).encode("utf-8")

first_pos = min(idx.values())
drop = set(idx.values())
out = []
for i, l in enumerate(lines):
    if i in drop:
        if i == first_pos:
            out.append(PTR)
        continue
    out.append(l)
ref_at = next(i for i, l in enumerate(out) if l.startswith(b"### Reference"))
out.insert(ref_at, NEWLAW)
new_raw = b"\r\n".join(out)
size_after = len(new_raw)
md5_after = hashlib.md5(new_raw).hexdigest()

expected = size_before - moved_bytes + len(PTR) + 2 + len(NEWLAW) + 2
assert size_after == expected, f"size recon mismatch: {size_after} != {expected}"

hdr = [
    "# pit-data —— 数据域坑律正典（D-20261002-06 域分件·第四拆件）",
    "",
    "> 来源：CODELY.md 整域 verbatim 迁出（2026-10-02 r380 bm-c·T-2026-10-02-144(c)·集团裁定 D-20261002-06「坑律按域分件·轮 prompt 按需局部读」）。",
    "> 执法面：数据面板 complete 停泊诊断（attempts/settled 双-pass 法）/采集器活性判定（三面活性+双龄停滞自愈）/"
    "prereg 冻结面钉数据文件 hash（日刷轮换面语义钉）/lane-pin 数据面 selftest 红腿定性/隔离员 heal 时序——上述数据链动作前必读本件。",
    None,  # byte-recon line, filled below
    "> 已拆域件：pit-git.md（r369·49 条）；pit-pool.md（r373·16 条）；pit-engine.md（r585·33 条）；pit-data.md（r380·5 条）；"
    "余域=协议+流水下沉（D-06 全线收口窗 2026-10-07）。",
    "",
]
recon = (
    f"> 字节对账行（零丢失断言）：CODELY.md 迁出前 {size_before:,}B（md5={md5_before}）→迁出后 {size_after:,}B"
    f"（md5={md5_after}·同窗新坑律追加 1 条 {len(NEWLAW)+2:,}B）；移出 5 条·条目字节和（含 CRLF 行尾）={moved_bytes:,}B"
    "==主件净删减字节·逐字节恒等零丢失；本件由拆件脚本机械迁移非手抄（r335 机证律同源）。"
)
hdr[4] = recon
hdr_bytes = [h.encode("utf-8") if isinstance(h, str) else h for h in hdr]
pit_raw = b"\r\n".join(hdr_bytes + moved) + b"\r\n"

open(PIT, "wb").write(pit_raw)
open(CODELY, "wb").write(new_raw)

v_pit = open(PIT, "rb").read()
v_c = open(CODELY, "rb").read()
pit_lines = v_pit.split(b"\r\n")
c_lines = v_c.split(b"\r\n")
for l in moved:
    assert l in pit_lines, f"moved entry missing in pit: {l[:40]!r}"
    assert l not in c_lines, f"moved entry still in CODELY: {l[:40]!r}"
assert PTR in c_lines, "pointer line missing"
assert NEWLAW in c_lines, "new-law line missing"
assert hashlib.md5(v_c).hexdigest() == md5_after
print(f"before={size_before:,}B md5={md5_before}")
print(f"after={size_after:,}B md5={md5_after}")
print(f"moved 5 entries = {moved_bytes:,}B (CRLF tree space)")
print(f"pit-data.md = {len(pit_raw):,}B entries verbatim zero-loss PASS")
print(f"PTR={len(PTR)+2:,}B NEWLAW={len(NEWLAW)+2:,}B")
print("SPLIT OK")
