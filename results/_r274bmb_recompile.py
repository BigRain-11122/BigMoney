"""r274 bm-b: repo-root CODELY.md hot-cold recompile, r274 batch (D-20260924-01 paradigm, R156/r272 precedent).

Watermark trigger (D-20260925-01(4)): after the r274 pit-law append, CODELY.md = 51,439 bytes (50.2KB,
line crossed). Move ONE flow-type line verbatim (the Project-section 2026-09-26 20:46 order-execution
pointer entry: fully carried by journal + fleet/ack/O-20260926-2000-bm-a-inventory.md + round reports,
and its C:\\Fluxgroup target-root statement is superseded by canon v2.0 / journal actual E:\\Fluxgroup)
into research/memory-archive/202609.md under a dated batch header. Zero line loss via line-multiset.

Byte-face law (R254/R255/R257): both files probed = UTF-8, no BOM, LF-only, trailing newline.
Idempotency: exit 2 if the line is already gone.
"""
import sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOT = os.path.join(ROOT, "CODELY.md")
COLD = os.path.join(ROOT, "research", "memory-archive", "202609.md")

LINE_HEAD = "- [2026-09-26 20:46] O-20260926-2000-bm-c"  # unique flow-entry head (r274 batch)

def die(msg, code):
    print(msg)
    sys.exit(code)

def read_bytes_face(p):
    b = open(p, "rb").read()
    face = {"bom": b[:3] == b"\xef\xbb\xbf", "crlf": b.count(b"\r\n"), "trailing_nl": b.endswith(b"\n")}
    return b, face

hot_b, hot_face = read_bytes_face(HOT)
cold_b, cold_face = read_bytes_face(COLD)
for name, face in (("CODELY.md", hot_face), ("archive", cold_face)):
    if face["bom"] or face["crlf"]:
        die(f"unexpected byte face on {name}: BOM={face['bom']} CRLF={face['crlf']}", 1)

hot_txt = hot_b.decode("utf-8")
hot_lines = hot_txt.split("\n")
moved = [L for L in hot_lines if L.startswith(LINE_HEAD)]
if not moved:
    die("r274 flow line not found in CODELY.md (already recompiled?)", 2)
if len(moved) > 1:
    die(f"non-unique line head matched {len(moved)} lines, refusing", 1)

new_hot_lines = [L for L in hot_lines if not L.startswith(LINE_HEAD)]
if sorted(hot_lines) != sorted(new_hot_lines + moved):
    die("multiset verification FAILED pre-write", 1)

header_lines = [
    "## 冷层归档增量·第四批：repo 根 CODELY.md 热冷整编（D-20260924-01·bm-b r274·2026-09-26）",
    "水位触线整编（r274 坑律追加后 51,439B=50.2KB 越线）：以下 1 行为流水型条目（收令执行指针），"
    "详情正主=C:\\Users\\Administrator\\fluxgroup-migration-journal.log + fleet/ack/O-20260926-2000-bm-a-inventory.md"
    " 与轮报告对应行；其目标根陈述（C:\\Fluxgroup）已被 canon v2.0 与 journal 实况（E:\\Fluxgroup）超越，"
    "热层删除防误读；零丢失（行级 multiset 校验 PASS，bm-b r274）。",
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

hot_b2, hot_face2 = read_bytes_face(HOT)
cold_b2, cold_face3 = read_bytes_face(COLD)
hot_lines2 = hot_b2.decode("utf-8").split("\n")
cold_lines2 = cold_b2.decode("utf-8").split("\n")
g1 = sorted(hot_lines) == sorted(hot_lines2 + moved)
g2 = all(L in cold_lines2 for L in moved)
g3 = (not hot_face2["bom"]) and hot_face2["crlf"] == 0 and hot_face2["trailing_nl"] == hot_face["trailing_nl"]
g4 = (not cold_face3["bom"]) and cold_face3["crlf"] == 0
if not (g1 and g2 and g3 and g4):
    die(f"POST-WRITE GATE FAILED g1={g1} g2={g2} g3={g3} g4={g4}", 1)

print(f"recompile PASS: moved 1 flow line")
print("  -", moved[0][:66] + "...")
print(f"CODELY.md {len(hot_b)} -> {len(hot_b2)} bytes ({round(len(hot_b2)/1024, 1)} KB)")
print(f"archive {len(cold_b)} -> {len(cold_b2)} bytes")
print(f"gates: multiset-zero-loss={g1} verbatim-in-cold={g2} hot-face={g3} cold-face={g4}")
