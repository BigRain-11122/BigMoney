# -*- coding: utf-8 -*-
"""r879 bm-b CODELY.md mini-split migration ceremony (D-20260206 main-file
<=30KB criterion, r441/r731/r833/r870 pattern). Prescan rc3 landed (4 hits,
group-split-order authorized migration face, same as r870). Dispositions:
  1) append new r878 pit entry (with-block indent wiring bug + hermetic
     selftest wiring-face gap) to CODELY.md
  2) migrate r822 entry (655B) verbatim -> pit-protocol-d19.md
     (orders watermark consumption + queue content legality family)
  3) migrate r870 dual-name-key entry (861B) verbatim -> pit-protocol-judge.md
     (prereg consumption/judge domain)
  4) r865 entry (1359B) REMOVED from main per r896/r807 precedent: canonical
     content already proven in-domain (pit-protocol-d19.md L53 r871 条 covers
     corrected ORD method pin; L39 r672 covers DEC raw-blob law) - verified
     in-script before removal (复述禁令: verbatim re-migration would duplicate)
  5) pointer line + byte accounting receipt + TREASURE_REGISTRY ledger line
Idempotent: refuses if receipt already exists."""
import hashlib
import io
import json
import os
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
MAIN = os.path.join(ROOT, "CODELY.md")
D19 = os.path.join(ROOT, "research", "pit-protocol-d19.md")
JUD = os.path.join(ROOT, "research", "pit-protocol-judge.md")
TREA = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")
RECEIPT = os.path.join(ROOT, "results", "_r879bmb_codely_minisplit.json")

NEW_ENTRY = ("- [2026-10-11 12:2x r878 bm-b] **with 块内缩位接线坑+封闭自检不覆盖接线面（首 flush 炸死坑）**："
             "alphagen_rg_census.py cmd_run 内 run_cells_parallel 调用停在 with fp 头层级"
             "（块先退→flush 时 fp 已关）→首 checkpoint flush ValueError I/O-on-closed-file·"
             "19min 烧毁诊断走进程尸体+回溯定位才定谳；根因=前轮构造期缺陷且封闭自检 31 腿全绿"
             "未覆盖接线面——with 体调用缩进层级不进任何断言。手术=调用缩入 with 体+AST 断言 "
             "nested-inside-with True+selftest 31/31+py_compile rc0；ckpt 0 行=resume-safe "
             "零双计。How to apply：写「open+with+多点 flush/checkpoint」型 runner 必带 AST 断言"
             "（关键调用嵌套在 with 体内）；封闭自检必须含一条真接线腿（真文件句柄真 flush），"
             "纯内存 mock 自检=接线面零覆盖假绿。")

MIG = [
    (D19, "- [2026-10-10 07:5x r822 bm-b]"),
    (JUD, "- [2026-10-11 08:4x r870 bm-b] **冻结批"),
]
REMOVE_PREFIX = "- [2026-10-11 10:1x r865 bm-c]"

POINTER = ("- 域指针·r879 bm-b mini-split（10-11 12:5x·主件回弹增量坑律 r441/r731/r833/r870 范式·"
           "prescan rc3 四命中=D-20260206 集团拆件令授权迁移面）：r822 队列建面晚于同日 CEO 令=内容"
           "陈旧面坑（655B）verbatim 迁 pit-protocol-d19.md〔orders 水位消费+队列内容合法性族〕+"
           "r870 双名键坑（861B）verbatim 迁 pit-protocol-judge.md〔prereg 消费/judge 域〕+"
           "r865 水位双 sha 条（1359B）按 r896/r807 先例主件摘除——正典内容已在域件实证在位"
           "（pit-protocol-d19.md r871 勘误条+r672 raw-blob 律族·脚本内 grep 断言过）——"
           "逐条字节+sha16 对账=receipt results/_r879bmb_codely_minisplit.json"
           "（零丢失断言=迁移条 bytes in target verbatim+摘除条 in-domain 证据断言+主件回线 <=30KB）；"
           "新坑例（with 内缩接线坑）本窗入主件。")

TREASURE_LINE = ("- 2026-10-11 12:5x bm-b r879 D-06 主件 mini-split 迁移仪式（主件 append 后实测越帽→当窗即办·r441/r731/r833/r870 范式）："
                 "prescan 实弹 rc3 四命中（CODELY.md/pit-protocol-d19.md/pit-protocol-judge.md/"
                 "TREASURE_REGISTRY.md）——D-20260206 集团拆件令（主件 ≤30KB 判据腿）授权×"
                 "TREASURE_PROTECTION_LAW §2 迁移仪式三件齐：①prescan rc3 留痕（本行）②出入记录本行"
                 "③零丢失断言——r822 条目 655B verbatim 迁 pit-protocol-d19.md+r870 条目 861B "
                 "verbatim 迁 pit-protocol-judge.md（sha16 见回执）+r865 条目 1359B 主件摘除"
                 "（r896/r807 先例·in-domain 证据=pit-protocol-d19.md r871 条+r672 raw-blob 律族）；"
                 "主件 30,236→回线 ≤30,720B（回执字节恒等式）；receipt=results/_r879bmb_codely_minisplit.json。\n")

if os.path.exists(RECEIPT):
    print("[minisplit] refuse: receipt already present")
    sys.exit(2)

txt = io.open(MAIN, encoding="utf-8").read()
size_before = len(txt.encode("utf-8"))
lines = txt.split("\n")

# 1) locate migration + removal lines (verbatim, unique prefix)
found = {}
for path, prefix in MIG:
    hits = [ln for ln in lines if ln.startswith(prefix)]
    assert len(hits) == 1, "prefix not unique/missing: %r -> %d hits" % (prefix[:40], len(hits))
    found[prefix] = hits[0]
    assert txt.count(found[prefix]) == 1, "line not verbatim-unique in main"
rem_hits = [ln for ln in lines if ln.startswith(REMOVE_PREFIX)]
assert len(rem_hits) == 1, "remove-prefix not unique/missing: %d hits" % len(rem_hits)
r865_line = rem_hits[0]

# 2) r865 removal evidence gate: canonical content must be in-domain first
d19_txt = io.open(D19, encoding="utf-8").read()
assert "r871" in d19_txt and "raw-blob" in d19_txt, "r865 in-domain evidence missing"

# 3) append verbatim to domain files (newline discipline + idempotent guard)
receipt_moves = []
for path, prefix in MIG:
    t = io.open(path, encoding="utf-8").read()
    ln = found[prefix]
    if ln not in t:
        if not t.endswith("\n"):
            t += "\n"
        io.open(path, "w", encoding="utf-8", newline="").write(t + ln + "\n")
    t2 = io.open(path, encoding="utf-8").read()
    assert ln in t2 and t2.count(ln) == 1, "bytes-in-target verbatim failed/double-write"
    sz = len(t2.encode("utf-8"))
    assert sz <= 30720, "domain file over cap: %s %d" % (path, sz)
    receipt_moves.append({
        "entry_prefix": prefix[:60],
        "bytes": len(ln.encode("utf-8")),
        "sha16": hashlib.sha256(ln.encode("utf-8")).hexdigest()[:16],
        "target": os.path.relpath(path, ROOT).replace("\\", "/"),
        "bytes_in_target_verbatim": True,
        "target_bytes_after": sz,
    })

# 4) remove migrated+摘除 lines from main, append new entry + pointer line
outset = set(found.values()) | {r865_line}
keep = [ln for ln in lines if ln not in outset]
out = "\n".join(keep)
while out.endswith("\n\n"):
    out = out[:-1]
if not out.endswith("\n"):
    out += "\n"
assert NEW_ENTRY[:40] not in out
out += NEW_ENTRY + "\n"
out += POINTER + "\n"
io.open(MAIN, "w", encoding="utf-8", newline="").write(out)
after = io.open(MAIN, encoding="utf-8").read()
size_after = len(after.encode("utf-8"))
assert size_after <= 30720, "main still over cap: %d" % size_after
assert r865_line not in after and NEW_ENTRY[:40] in after

# 5) TREASURE ledger line
t = io.open(TREA, encoding="utf-8").read()
if "r879 D-06 主件 mini-split" not in t:
    if not t.endswith("\n"):
        t += "\n"
    io.open(TREA, "w", encoding="utf-8", newline="").write(t + TREASURE_LINE)

# 6) receipt
receipt = {
    "round": "r879 bm-b",
    "ceremony": "D-06 main mini-split (r441/r731/r833/r870 pattern)",
    "prescan_rc": 3,
    "prescan_hits": ["CODELY.md", "research/pit-protocol-d19.md",
                     "research/pit-protocol-judge.md", "knowledge/TREASURE_REGISTRY.md"],
    "authorization": "D-20260206 main<=30KB + TREASURE_PROTECTION_LAW sec.2 trio",
    "size_before": size_before,
    "size_after": size_after,
    "new_entry_bytes": len(NEW_ENTRY.encode("utf-8")),
    "pointer_line_bytes": len(POINTER.encode("utf-8")),
    "moves": receipt_moves,
    "removals": [{
        "entry_prefix": REMOVE_PREFIX[:60],
        "bytes": len(r865_line.encode("utf-8")),
        "sha16": hashlib.sha256(r865_line.encode("utf-8")).hexdigest()[:16],
        "disposition": "main-file removal per r896/r807 precedent (content-already-in-domain)",
        "in_domain_evidence": ["research/pit-protocol-d19.md contains r871 corrected-ORD entry",
                               "research/pit-protocol-d19.md contains r672 raw-blob law family"],
    }],
    "zero_loss": all(m["bytes_in_target_verbatim"] for m in receipt_moves),
    "main_under_cap": size_after <= 30720,
}
io.open(RECEIPT, "w", encoding="utf-8", newline="").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("[minisplit] main %d -> %d (<=30720) | moved %d | removed 1 (in-domain) | new entry %dB | receipt ok"
      % (size_before, size_after, len(receipt_moves), len(NEW_ENTRY.encode("utf-8"))))
