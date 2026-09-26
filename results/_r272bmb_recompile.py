"""r272 bm-b: repo-root CODELY.md hot-cold recompile, r272 batch (D-20260924-01 paradigm, R156 precedent).

Watermark discipline (D-20260925-01(4) + r271 next-pointer item4): CODELY.md at 50,172 bytes
(49.0KB, one pit-law append from crossing the 50KB line). This quiet-Saturday maintenance round
performs the recompile proactively: move ALL flow-type entries (执行记录 per the 冷层指针
definition: 轮报告定案/执行记录/让路裁定) verbatim into research/memory-archive/202609.md
under a dated section header (R156 format), zero line loss verified by exact line-multiset.

Byte-face law (R254/R255/R257): both files probed = UTF-8, no BOM, LF-only, trailing newline.
Writes mirror all faces. Idempotency: exit 2 if zero flow lines found (already moved).
"""
import sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOT = os.path.join(ROOT, "CODELY.md")
COLD = os.path.join(ROOT, "research", "memory-archive", "202609.md")
MARK = "] 执行记录（"  # flow-type entry marker (both "- [date] 执行记录（" and "[date] 执行记录（" writers)

def die(msg, code):
    print(msg)
    sys.exit(code)

def read_bytes_face(p):
    b = open(p, "rb").read()
    face = {
        "bom": b[:3] == b"\xef\xbb\xbf",
        "lf": b.count(b"\n"),
        "crlf": b.count(b"\r\n"),
        "trailing_nl": b.endswith(b"\n"),
    }
    return b, face

hot_b, hot_face = read_bytes_face(HOT)
cold_b, cold_face = read_bytes_face(COLD)
for name, face in (("CODELY.md", hot_face), ("archive", cold_face)):
    if face["bom"] or face["crlf"]:
        die(f"unexpected byte face on {name}: BOM={face['bom']} CRLF={face['crlf']}", 1)

hot_txt = hot_b.decode("utf-8")
hot_lines = hot_txt.split("\n")  # trailing '' preserved
moved = [L for L in hot_lines if MARK in L]
if not moved:
    die("zero flow-type lines found in CODELY.md (already recompiled?)", 2)
# guard: a flow line must carry a date bracket head (never match prose inside other entries)
for L in moved:
    if "2026-09" not in L[:24]:
        die(f"flow-marker line without date head, refusing: {L[:60]!r}", 1)

new_hot_lines = [L for L in hot_lines if MARK not in L]

# line-multiset zero-loss gate: original == kept + moved (exact multiset)
if sorted(hot_lines) != sorted(new_hot_lines + moved):
    die("multiset verification FAILED pre-write (kept+moved != original)", 1)

header_lines = [
    "## 冷层归档增量·第二批：repo 根 CODELY.md 热冷整编（D-20260924-01·bm-b r272·2026-09-26）",
    "水位前置整编（49.0KB 距 50KB 线一步·r271 轮指针④）：以下 "
    + str(len(moved))
    + " 行为流水型条目（执行记录），详情正主=logs/iteration-loop/round_reports*.md 对应行与 git 历史；"
    "自热层移入本冷层，零丢失（行级 multiset 校验 PASS，bm-b r272）。检索按行首日期段。",
]
cold_txt = cold_b.decode("utf-8")
block = "\n".join(header_lines + moved) + "\n"
if not cold_txt.endswith("\n"):
    die("archive lacks trailing newline before append -- face changed, abort", 1)
new_cold_txt = cold_txt + block

with open(HOT, "wb") as f:
    f.write("\n".join(new_hot_lines).encode("utf-8"))
with open(COLD, "wb") as f:
    f.write(new_cold_txt.encode("utf-8"))

# post-write verification: re-read from disk, all three gates
hot_b2, hot_face2 = read_bytes_face(HOT)
cold_b2, cold_face3 = read_bytes_face(COLD)
hot_lines2 = hot_b2.decode("utf-8").split("\n")
cold_lines2 = cold_b2.decode("utf-8").split("\n")
g1 = sorted(hot_lines) == sorted(hot_lines2 + moved)  # multiset zero loss
g2 = all(L in cold_lines2 for L in moved)  # moved lines verbatim in cold layer
g3 = (not hot_face2["bom"]) and hot_face2["crlf"] == 0 and hot_face2["trailing_nl"] == hot_face["trailing_nl"]
g4 = (not cold_face3["bom"]) and cold_face3["crlf"] == 0
if not (g1 and g2 and g3 and g4):
    die(f"POST-WRITE GATE FAILED g1={g1} g2={g2} g3={g3} g4={g4}", 1)

print(f"recompile PASS: moved {len(moved)} flow lines")
for L in moved:
    print("  -", L[:66] + "...")
print(f"CODELY.md {len(hot_b)} -> {len(hot_b2)} bytes ({round(len(hot_b2)/1024, 1)} KB)")
print(f"archive {len(cold_b)} -> {len(cold_b2)} bytes")
print(f"gates: multiset-zero-loss={g1} verbatim-in-cold={g2} hot-face={g3} cold-face={g4}")
