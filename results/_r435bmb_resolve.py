# -*- coding: utf-8 -*-
"""r435 bm-b rebase conflict resolver (skill: bigmoney-conflict-resolve).

CODELY.md (memory-union recipe R208/r212): HEAD carries bm-c's same-window
waterline reorg (their new LHB entry + three entries my commit archived).
Mine carries the 探针 r431 entry (identical on both sides) + lesson 116.
Union = drop the three archived entries (my pointer already covers them),
dedupe the identical r431 line, keep bm-c's new entry verbatim + my 116.

research/memory-archive/202609.md (UNKNOWN class -> manual = append-log-md
union, both appended sections verbatim, commit-time order bm-c first [I am
the later committer per fleet/README sec.4]): same-window double-archive of
batches 113/114 disclosed honestly; both hot pointers stay true.

Zero-loss verification + parse guards before write-back (r185 law)."""
import io
import sys

RES = []


def fail(msg):
    print("RESOLVE-FAIL:", msg)
    sys.exit(2)


def split_conflict(lines, path):
    i = 0
    out = []
    while i < len(lines):
        if lines[i].startswith("<<<<<<<"):
            j = lines.index("=======", i)
            k = next(x for x in range(j + 1, len(lines))
                     if lines[x].startswith(">>>>>>>"))
            out.append(("c", lines[i + 1:j], lines[j + 1:k]))
            i = k + 1
        else:
            out.append(("p", lines[i]))
            i += 1
    return out


# ---------- CODELY.md ----------
P = "CODELY.md"
lines = io.open(P, encoding="utf-8").read().splitlines()
parts = split_conflict(lines, P)
if sum(1 for p in parts if p[0] == "c") != 1:
    fail(f"{P}: expected exactly 1 conflict region")
resolved = []
for p in parts:
    if p[0] == "p":
        resolved.append(p[1])
        continue
    head, mine = p[1], p[2]
    # identical-line dedupe proof (r431 probe entry byte-equal both sides)
    r431 = [l for l in head if l.startswith("- [2026-09-29 15:5x r431 bm-b]")]
    if len(r431) != 1 or r431[0] not in mine:
        fail(f"{P}: r431 line not byte-identical across sides")
    archived_prefixes = (
        "- [2026-09-29 15:1x r434 bm-a] 坑律一百一十二批",
        "- [2026-09-29 15:5x r435 bm-a] 坑律一一三批",
        "- [2026-09-29 16:4x r437 bm-a] 坑律一百一十五批",
    )
    for pref in archived_prefixes:
        if not any(l.startswith(pref) for l in head):
            fail(f"{P}: HEAD side missing archived entry {pref[:40]}")
        if any(l.startswith(pref) for l in mine):
            fail(f"{P}: MY side still carries {pref[:40]}")
    lhb = [l for l in head if l.startswith("- [2026-09-29 17:2x r229 bm-c]")]
    if len(lhb) != 1:
        fail(f"{P}: bm-c LHB entry count != 1")
    e116 = [l for l in mine if l.startswith("- [2026-09-29 17:5x r435 bm-b]")]
    if len(e116) != 1:
        fail(f"{P}: lesson-116 line count != 1")
    # union order: r431 probe, bm-c LHB (HEAD placement), lesson 116 (mine)
    resolved.extend([r431[0], lhb[0], e116[0]])
new = "\n".join(resolved) + "\n"
io.open(P, "w", encoding="utf-8", newline="").write(new)
RES.append(f"CODELY.md: union kept r431(x1 deduped byte-equal) + "
           f"bm-c LHB r229 + lesson 116; 3 archived entries dropped "
           f"(pointer-covered); markers=0")

# ---------- archive 202609.md ----------
P2 = "research/memory-archive/202609.md"
lines2 = io.open(P2, encoding="utf-8").read().splitlines()
parts2 = split_conflict(lines2, P2)
if sum(1 for p in parts2 if p[0] == "c") != 1:
    fail(f"{P2}: expected exactly 1 conflict region")
resolved2 = []
for p in parts2:
    if p[0] == "p":
        resolved2.append(p[1])
        continue
    head, mine = p[1], p[2]
    # commit-time order: bm-c section (HEAD, landed first) then mine
    resolved2.extend(head)
    resolved2.extend(mine)
new2 = "\n".join(resolved2) + "\n"
io.open(P2, "w", encoding="utf-8", newline="").write(new2)
RES.append("archive: both sections kept verbatim in commit-time order "
           "(bm-c r229 first, r435 bm-b second); same-window double-archive "
           "of batches 113/114 disclosed (both pointers stay true)")

# ---------- zero-loss verification (line-anchored markers per lesson-85
# law: archive verbatim quotations may CONTAIN markers in-block; probe must
# anchor ^) ----------
hot = io.open("CODELY.md", encoding="utf-8").read()
arc = io.open(P2, encoding="utf-8").read()


def real_markers(text):
    return [l[:20] for l in text.splitlines()
            if l.startswith(("<<<<<<<", "=======", ">>>>>>>"))]


for nm, txt in (("CODELY.md", hot), ("archive", arc)):
    if real_markers(txt):
        fail(f"line-anchored marker still present in {nm}: "
             f"{real_markers(txt)[:2]}")
for pref in archived_prefixes + (
        "- [2026-09-29 15:4x r223 bm-c] 坑律一百一十三批",
        "- [2026-09-29 16:2x r225 bm-c] 坑律一百一十四批"):
    if any(l.startswith(pref) for l in hot.splitlines()):
        fail(f"hot still carries archived {pref[:40]}")
    if not any(l.startswith(pref) for l in arc.splitlines()):
        fail(f"archive lost {pref[:40]}")
# five entries verbatim in MY archive section (batch 112/113/113b/114/115)
for pref in archived_prefixes + (
        "- [2026-09-29 15:4x r223 bm-c] 坑律一百一十三批",
        "- [2026-09-29 16:2x r225 bm-c] 坑律一百一十四批"):
    if sum(1 for l in arc.splitlines() if l.startswith(pref)) < 1:
        fail(f"archive missing {pref[:40]}")
if "坑律一百一十六批" not in hot or "坑律归档 2026-09-29 r229 bm-c 窗批" not in arc \
        or "坑律归档 2026-09-29 r435 bm-b 窗批" not in arc \
        or "LHB 源改史实录" not in hot:
    fail("content loss detected in hot/archive")
for r in RES:
    print("RESOLVED:", r)
print("ZERO-LOSS VERIFIED: hot", len(hot.encode('utf-8')), "B; archive",
      len(arc.encode('utf-8')), "B")
