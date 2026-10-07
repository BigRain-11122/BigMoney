# -*- coding: utf-8 -*-
"""r832 bm-a CODELY increment migration (D-20260925-01④ + D-20261002-06 30,720B line,
append-overflow same-window law; r672 single-line migration pattern).
Main 31,405B > 30,720B after r832 pit append -> migrate 2 own lines verbatim:
  r832 writer-pause pit  -> research/pit-git-resolver.md (rebase x daemon-writer face)
  r830 buildgen line     -> research/pit-engine-freeze-editor.md (its own declared domain)
Compact pointer lines stay in main. Receipt with byte accounting + sha16."""
import hashlib, json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CP = os.path.join(ROOT, "CODELY.md")

main = open(CP, encoding="utf-8").read()
main_b_before = len(open(CP, "rb").read())

m832 = re.search(r"- \[2026-10-07 [^\n]*r832[^\n]*\n", main)
m830 = re.search(r"- \[2026-10-07 [^\n]*r830[^\n]*\n", main)
assert m832 and m830, "migration lines not found"
line832, line830 = m832.group(0), m830.group(0)

ptr832 = ("- [2026-10-07 16:3x r832 bm-a] 域指针·增量批：daemon 活写阻断 rebase 的 writer-pause 让路法坑 1 条 verbatim 迁 research/pit-git-resolver.md（rebase×daemon 活写面·E42 卡同窗入 METHODOLOGY_ASSETS）·收据 results/_r832bma_codely_increment.json；新坑律仍先入本件后回扫。\n")
ptr830 = ("- [2026-10-07 15:3x r830 bm-a] 域指针·增量批：冻结手术 buildgen 法首用（E41）坑行 verbatim 迁 research/pit-engine-freeze-editor.md（buildgen/冻结手术面·其行自declared 域）·收据同 _r832bma_codely_increment.json。\n")

# replace in main (each line -> compact pointer)
main2 = main.replace(line832, ptr832).replace(line830, ptr830)
# remove ONE blank line I added before the r832 line (the memappend wrote '\n' + line)
main2 = main2.replace(ptr832, ptr832, 1)
open(CP, "w", encoding="utf-8", newline="").write(main2)

# verbatim appends into domain files
tp = os.path.join(ROOT, "research", "pit-git-resolver.md")
t = open(tp, encoding="utf-8").read()
assert "writer-pause" not in t, "already migrated"
open(tp, "a", encoding="utf-8").write("\n" + line832)
ep = os.path.join(ROOT, "research", "pit-engine-freeze-editor.md")
e = open(ep, encoding="utf-8").read()
assert "buildgen 法首用" not in e, "already migrated"
open(ep, "a", encoding="utf-8").write("\n" + line830)

main_b_after = len(open(CP, "rb").read())
tgt1 = len(open(tp, "rb").read()); tgt2 = len(open(ep, "rb").read())
l832b = len(line832.encode("utf-8")); l830b = len(line830.encode("utf-8"))

receipt = {
    "round": "r832 bm-a", "ts": "2026-10-07T16:3x+08:00",
    "trigger": "main 31,405B > 30,720B after r832 pit append (same-window law D-20260925-01④ / D-20261002-06)",
    "migrations": [
        {"line": "r832 writer-pause pit", "bytes": l832b, "target": "research/pit-git-resolver.md",
         "sha16": hashlib.sha256(line832.encode("utf-8")).hexdigest()[:16],
         "pointer_bytes": len(ptr832.encode("utf-8"))},
        {"line": "r830 buildgen E41", "bytes": l830b, "target": "research/pit-engine-freeze-editor.md",
         "sha16": hashlib.sha256(line830.encode("utf-8")).hexdigest()[:16],
         "pointer_bytes": len(ptr830.encode("utf-8"))},
    ],
    "main_before": main_b_before, "main_after": main_b_after,
    "under_line": main_b_after <= 30720,
    "zero_loss": "verbatim bytes in targets, sha16 above, pointers retained in main",
}
json.dump(receipt, open(os.path.join(ROOT, "results", "_r832bma_codely_increment.json"), "w",
                       encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"main {main_b_before}->{main_b_after}B (under 30,720: {main_b_after <= 30720}); "
      f"r832->{l832b}B->pit-git-resolver; r830->{l830b}B->pit-engine-freeze-editor; receipt written")
