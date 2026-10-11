# -*- coding: utf-8 -*-
"""r870 bm-b CODELY.md mini-split migration ceremony (D-20260206 main-file
<=30KB criterion, r441/r731/r833 pattern). Prescan rc3 landed (4 hits,
group-split-order authorized migration trio). Actions:
  1) append new r870 pit entry (dual-name key-face law) to CODELY.md
  2) migrate r864 entry (668B) verbatim -> pit-git-resolver-rebase2.md
  3) migrate r861 entry (639B) verbatim -> pit-protocol-judge.md
  4) replace migrated lines with one pointer line (batch)
  5) receipt with byte accounting + sha16 + zero-loss assertions
  6) TREASURE_REGISTRY migration ledger line
Idempotent: refuses if receipt already exists."""
import hashlib
import io
import json
import os
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
MAIN = os.path.join(ROOT, "CODELY.md")
REB2 = os.path.join(ROOT, "research", "pit-git-resolver-rebase2.md")
JUD = os.path.join(ROOT, "research", "pit-protocol-judge.md")
TREA = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")
RECEIPT = os.path.join(ROOT, "results", "_r870bmb_codely_minisplit.json")

NEW_ENTRY = ("- [2026-10-11 08:4x r870 bm-b] **冻结批存档次级面双名键坑（sh 正典键面律）**："
             "mp1_tsgate_p1.json five_member_oos 次级面含 bare+sh 双键且底层文件不同"
             "（510300 bare n_in=276 ≠ sh 418）——复核/对账/先验实读一律钉 sh 正典键面；"
             "r870 实弹：GATE-RECHECK-MP1 prereg §5.5 负员先验起草读 bare 键"
             "（510050=-0.0135/510300=-0.0101）与烧录消费 sh 键（-0.0087/-0.0072）键面错配——"
             "结构性结论（VOLUME 变体双负→RECHECK-FAIL）两键面一致成立零翻案，数值先验面不同源"
             "如实披露（§8 留痕）。How to apply：消费任何双名面板（data/daily 裸名+sh 前缀共存）的"
             "存档次级面前先钉键面；对账键面=正典 sh 键（A158-RECHECK 同律）；键面不一致的对账="
             "假漂移/假先验。正典=E55 卡（METHODOLOGY_ASSETS.md）+prereg §8。")

MIG = [
    (os.path.join(ROOT, "research", "pit-git-resolver-rebase2.md"),
     "- [2026-10-11 06:2x r864 bm-b] **headless rebase --continue"),
    (os.path.join(ROOT, "research", "pit-protocol-judge.md"),
     "- [2026-10-11 05:1x r861 bm-b] **prereg null 预算"),
]

POINTER = ("- 域指针·r870 bm-b mini-split（10-11 08:4x·主件回弹增量坑律 r441/r731/r833 范式·"
           "prescan rc3 四命中=D-20260206 集团拆件令授权迁移面）：r864 headless rebase --continue "
           "双拦坑（668B）verbatim 迁 pit-git-resolver-rebase2.md〔r787 姊妹域·rebase/sequencer "
           "child-2〕+r861 prereg null 预算必计损耗账坑（639B）verbatim 迁 pit-protocol-judge.md"
           "〔prereg 预算/judge 域〕——逐条字节+sha16 对账=receipt results/_r870bmb_codely_"
           "minisplit.json（零丢失断言=逐块 bytes in target verbatim+主件回线 <=30KB）；"
           "新坑例（双名键坑）本窗入主件。")

TREASURE_LINE = ("- 2026-10-11 08:4x bm-b r870 D-06 主件 mini-split 迁移仪式（主件 append 后实测越帽→当窗即办·r441/r731/r833 范式）："
                 "prescan 实弹 rc3 四命中（CODELY.md/pit-git-resolver-rebase2.md/pit-protocol-judge.md/"
                 "TREASURE_REGISTRY.md）——D-20260206 集团拆件令（主件 ≤30KB 判据腿）授权×"
                 "TREASURE_PROTECTION_LAW §2 迁移仪式三件齐：①prescan rc3 留痕（本行）②出入记录本行"
                 "③零丢失断言——r864 条目 668B verbatim 迁 pit-git-resolver-rebase2.md"
                 "（sha16 见回执）+r861 条目 639B verbatim 迁 pit-protocol-judge.md；"
                 "主件 30,612→回线 ≤30,720B（回执字节恒等式）；receipt=results/_r870bmb_codely_minisplit.json。\n")

if os.path.exists(RECEIPT):
    print("[minisplit] refuse: receipt already present")
    sys.exit(2)

txt = io.open(MAIN, encoding="utf-8").read()
size_before = len(txt.encode("utf-8"))
lines = txt.split("\n")

# 1) locate migration lines (verbatim, unique prefix)
found = {}
for path, prefix in MIG:
    hits = [ln for ln in lines if ln.startswith(prefix)]
    assert len(hits) == 1, "prefix not unique/missing: %r -> %d hits" % (prefix[:40], len(hits))
    found[prefix] = hits[0]
for prefix, ln in found.items():
    assert ln in txt and txt.count(ln) == 1, "line not verbatim-unique in main"

# 2) append verbatim to domain files (newline discipline: target ends with \n)
#    idempotent: a target that already carries the verbatim line (prior crashed
#    run append) counts as moved-in, not a double-write.
receipt_moves = []
for path, prefix in MIG:
    t = io.open(path, encoding="utf-8").read()
    ln = found[prefix]
    if ln not in t:
        if not t.endswith("\n"):
            t += "\n"
        io.open(path, "w", encoding="utf-8", newline="").write(t + ln + "\n")
    t2 = io.open(path, encoding="utf-8").read()
    assert ln in t2, "bytes-in-target verbatim failed"
    assert t2.count(ln) == 1, "double-write detected in target"
    receipt_moves.append({
        "entry_prefix": prefix[:60],
        "bytes": len(ln.encode("utf-8")),
        "sha16": hashlib.sha256(ln.encode("utf-8")).hexdigest()[:16],
        "target": os.path.relpath(path, ROOT).replace("\\", "/"),
        "bytes_in_target_verbatim": True,
    })

# 3) remove migrated lines from main, append new entry + pointer line
mig_lines = set(found[prefix] for _, prefix in MIG)
keep = [ln for ln in lines if ln not in mig_lines]
# drop one trailing empty line left by removal (structure identity r783 law)
out = "\n".join(keep)
while out.endswith("\n\n"):
    out = out[:-1]
if not out.endswith("\n"):
    out += "\n"
if NEW_ENTRY[:40] not in out:
    out += NEW_ENTRY + "\n"
out += POINTER + "\n"
io.open(MAIN, "w", encoding="utf-8", newline="").write(out)
after = io.open(MAIN, encoding="utf-8").read()
size_after = len(after.encode("utf-8"))
assert size_after <= 30720, "main still over cap: %d" % size_after

# 4) TREASURE ledger line
t = io.open(TREA, encoding="utf-8").read()
if "r870 D-06 主件 mini-split" not in t:
    if not t.endswith("\n"):
        t += "\n"
    io.open(TREA, "w", encoding="utf-8", newline="").write(t + TREASURE_LINE)

# 5) receipt
receipt = {
    "round": "r870 bm-b",
    "ceremony": "D-06 main mini-split (r441/r731/r833 pattern)",
    "prescan_rc": 3,
    "prescan_hits": ["CODELY.md", "research/pit-git-resolver-rebase2.md",
                     "research/pit-protocol-judge.md", "knowledge/TREASURE_REGISTRY.md"],
    "authorization": "D-20260206 main<=30KB + TREASURE_PROTECTION_LAW sec.2 trio",
    "size_before": size_before,
    "size_after": size_after,
    "new_entry_bytes": len(NEW_ENTRY.encode("utf-8")),
    "pointer_line_bytes": len(POINTER.encode("utf-8")),
    "moves": receipt_moves,
    "zero_loss": all(m["bytes_in_target_verbatim"] for m in receipt_moves),
    "main_under_cap": size_after <= 30720,
}
io.open(RECEIPT, "w", encoding="utf-8", newline="").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("[minisplit] main %d -> %d (<=30720) | moved %d entries | new entry %dB | receipt ok"
      % (size_before, size_after, len(receipt_moves), len(NEW_ENTRY.encode("utf-8"))))
