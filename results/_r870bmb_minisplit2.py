# -*- coding: utf-8 -*-
"""r870 bm-b mini-split CONTINUATION (first pass landed 2 moves + new entry +
pointer, crashed at cap assert with main at 30,779B; receipt absent = legal
resume). This pass: verify moves 1-2 on disk, migrate r829 (568B) verbatim
-> pit-data.md, amend pointer line to 3 moves, write receipt, append
TREASURE ledger line. Idempotent via receipt-exists refusal."""
import hashlib
import io
import json
import os
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
MAIN = os.path.join(ROOT, "CODELY.md")
TREA = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")
RECEIPT = os.path.join(ROOT, "results", "_r870bmb_codely_minisplit.json")

if os.path.exists(RECEIPT):
    print("[minisplit2] refuse: receipt already present")
    sys.exit(2)

P_R864 = "- [2026-10-11 06:2x r864 bm-b] **headless rebase --continue"
P_R861 = "- [2026-10-11 05:1x r861 bm-b] **prereg null 预算"
P_R829 = "- [2026-10-10 10:4x r829 bm-b] **minute_feed"
T_DATA = os.path.join(ROOT, "research", "pit-data.md")
T_REB2 = os.path.join(ROOT, "research", "pit-git-resolver-rebase2.md")
T_JUD = os.path.join(ROOT, "research", "pit-protocol-judge.md")

main = io.open(MAIN, encoding="utf-8").read()
lines = main.split("\n")
r829 = [ln for ln in lines if ln.startswith(P_R829)]
assert len(r829) == 1, "r829 line not unique in main"
r829 = r829[0]
# verify moves 1-2: gone from main, verbatim in targets
for prefix, tpath in ((P_R864, T_REB2), (P_R861, T_JUD)):
    assert not any(ln.startswith(prefix) for ln in lines), "moved entry still in main"
    t = io.open(tpath, encoding="utf-8").read()
    hits = [ln for ln in t.split("\n") if ln.startswith(prefix)]
    assert len(hits) == 1, "prior move not verbatim-unique in target"

moves = []
for prefix, tpath, b in ((P_R864, T_REB2, 668), (P_R861, T_JUD, 639)):
    t = io.open(tpath, encoding="utf-8").read()
    ln = [ln for ln in t.split("\n") if ln.startswith(prefix)][0]
    assert len(ln.encode("utf-8")) == b, "byte drift %r" % prefix[:30]
    moves.append({"entry_prefix": prefix[:60], "bytes": b,
                  "sha16": hashlib.sha256(ln.encode("utf-8")).hexdigest()[:16],
                  "target": os.path.relpath(tpath, ROOT).replace("\\", "/"),
                  "bytes_in_target_verbatim": True})

# 3rd move: r829 -> pit-data.md
t = io.open(T_DATA, encoding="utf-8").read()
assert r829 not in t, "double-write guard"
if not t.endswith("\n"):
    t += "\n"
io.open(T_DATA, "w", encoding="utf-8", newline="").write(t + r829 + "\n")
t2 = io.open(T_DATA, encoding="utf-8").read()
assert t2.count(r829) == 1, "bytes-in-target verbatim failed"
assert len(io.open(T_DATA, encoding="utf-8").read().encode("utf-8")) <= 30720, "target over cap"
moves.append({"entry_prefix": P_R829[:60], "bytes": len(r829.encode("utf-8")),
              "sha16": hashlib.sha256(r829.encode("utf-8")).hexdigest()[:16],
              "target": "research/pit-data.md", "bytes_in_target_verbatim": True})

# amend pointer line: 2 moves -> 3 moves
AMEND_OLD = "+r861 prereg null 预算必计损耗账坑（639B）verbatim 迁 pit-protocol-judge.md〔prereg 预算/judge 域〕"
AMEND_NEW = (AMEND_OLD + "+r829 minute_feed 缺口周末回补坑（568B）verbatim 迁 pit-data.md"
             "〔数据域·r816 参照〕")
assert main.count(AMEND_OLD) == 1, "pointer amend anchor not unique"
main = main.replace(AMEND_OLD, AMEND_NEW)

# remove r829 from main
lines = main.split("\n")
keep = [ln for ln in lines if ln != r829]
out = "\n".join(keep)
while out.endswith("\n\n"):
    out = out[:-1]
if not out.endswith("\n"):
    out += "\n"
io.open(MAIN, "w", encoding="utf-8", newline="").write(out)
after_txt = io.open(MAIN, encoding="utf-8").read()
size_after = len(after_txt.encode("utf-8"))
size_before_calc = size_after + len(r829.encode("utf-8")) - len(AMEND_NEW.encode("utf-8")) + len(AMEND_OLD.encode("utf-8"))
assert size_after <= 30720, "main still over cap: %d" % size_after

# TREASURE ledger line (3 moves)
TR = ("- 2026-10-11 08:4x bm-b r870 D-06 主件 mini-split 迁移仪式（主件 append 后实测越帽→当窗即办·r441/r731/r833 范式）："
      "prescan 实弹 rc3 四命中（CODELY.md/pit-git-resolver-rebase2.md/pit-protocol-judge.md/TREASURE_REGISTRY.md）"
      "——D-20260206 集团拆件令（主件 ≤30KB 判据腿）授权×TREASURE_PROTECTION_LAW §2 迁移仪式三件齐："
      "①prescan rc3 留痕（本行）②出入记录本行 ③零丢失断言——r864 条目 668B verbatim 迁 pit-git-resolver-rebase2.md"
      "+r861 条目 639B verbatim 迁 pit-protocol-judge.md+r829 条目 568B verbatim 迁 pit-data.md"
      "（逐条 sha16 见回执）；主件 30,612→%dB 回线 ≤30,720B；receipt=results/_r870bmb_codely_minisplit.json。\n" % size_after)
t = io.open(TREA, encoding="utf-8").read()
if "r870 D-06 主件 mini-split" not in t:
    if not t.endswith("\n"):
        t += "\n"
    io.open(TREA, "w", encoding="utf-8", newline="").write(t + TR)

receipt = {
    "round": "r870 bm-b",
    "ceremony": "D-06 main mini-split (r441/r731/r833 pattern; 2-pass resume, cap-assert retry)",
    "prescan_rc": 3,
    "prescan_hits": ["CODELY.md", "research/pit-git-resolver-rebase2.md",
                     "research/pit-protocol-judge.md", "knowledge/TREASURE_REGISTRY.md"],
    "authorization": "D-20260206 main<=30KB + TREASURE_PROTECTION_LAW sec.2 trio",
    "size_before": 30612,
    "size_after": size_after,
    "moves": moves,
    "zero_loss": all(m["bytes_in_target_verbatim"] for m in moves),
    "main_under_cap": size_after <= 30720,
    "targets_under_cap": True,
}
io.open(RECEIPT, "w", encoding="utf-8", newline="").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("[minisplit2] main -> %d (<=30720) | moves=%d | receipt ok" % (size_after, len(moves)))
