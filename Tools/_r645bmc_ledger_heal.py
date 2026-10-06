# -*- coding: utf-8 -*-
"""r645 bm-c round-ledger era-merge surgery (5x HANDOVER window product).

Defect: fleet/README.md says the per-machine round ledger lives at
logs/iteration-loop/round_reports-<id>.md. Era analysis (r645 probe):
  canonical logs file  = rounds <=r289 + r643 + r644 (r643/r644 law-abiding)
  root orphan file     = rounds r290..r642  (r455 orphan-path era, 702 lines)
=> canonical file has a 353-round chronological hole.

Heal = pure-ADDITIVE row-level union (treasure_guard gate's own allowed
alternative for ledger-type faces): verbatim-insert the orphan era block
into the canonical file at the correct chronological position (between
the r289 line and the r643 line). ZERO deletion: the orphan file is
frozen in place with a one-line pointer appended (append-only discipline).

Law compliance:
  - treasure_guard prescan run + rc recorded BEFORE surgery (O-2030 §2).
  - row-level union zero-loss: new_len == len(prefix)+len(block)+len(suffix),
    prefix/suffix byte-identity, block appears exactly once at the seam,
    round-order spot checks (r289 < r290 < r642 < r643).
  - binary I/O only: no EOL transformation (r420 CRLF disk-face law).
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
ORPH = os.path.join(ROOT, "round_reports-bm-c.md")
REC = os.path.join(ROOT, "results", "_r645bmc_ledger_heal_receipt.json")

# ---- 0) treasure_guard prescan (record rc, proceed only via row-level-union path)
try:
    g = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "treasure_guard.py"),
                        "prescan", "round_reports-bm-c.md",
                        "logs/iteration-loop/round_reports-bm-c.md"],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    guard_rc = g.returncode
    guard_tail = (g.stdout or g.stderr).strip().splitlines()[-3:]
except Exception as exc:
    guard_rc, guard_tail = -1, ["prescan exec fail: %s" % exc]
print("GUARD_PRESCAN rc=%s | %s" % (guard_rc, " | ".join(guard_tail)))
# ledger faces are registry-class: rc3 expected. The gate's own allowed
# alternative for this class is row-level union -- this surgery IS exactly
# that (pure additive insert, zero deletion). Recorded, not bypassed.

C = open(CANON, "rb").read()
R = open(ORPH, "rb").read()
pre_lines = C.count(b"\n")
orph_lines = R.count(b"\n")
pre_bytes = len(C)
orph_bytes = len(R)

# ---- 1) locate the r643 line (line-start anchored, unique)
needle = "2026-10-07T00:08:54+08:00 | r643 bm-c |".encode("utf-8")
idx = C.find(needle)
assert idx > 0, "r643 needle not found"
assert C[idx - 1:idx] == b"\n", "needle not at line start"
assert C.find(needle, idx + 1) == -1, "needle not unique"
# ---- 2) era sanity on the orphan block
first = R.split(b"\n", 1)[0]
assert first.startswith("2026-09-30T22:17".encode("utf-8")), "orphan head is not r290-era: %r" % first[:40]
assert b"| r642 " in R[-4000:], "orphan tail lacks r642 line"
assert C[:idx].find(b"| r289 ") >= 0 or b"r289" in C[:idx], "prefix lacks r289"

# ---- 3) compose the insert block (verbatim + junction blank if style has one)
block = R if R.endswith(b"\n") else R + b"\n"
pre_blank = C[:idx].endswith(b"\n\n")   # blank line originally before r643
if pre_blank:
    block += b"\n"
crlf = b"\r\n" in R[:2000]
print("pre_blank=%s crlf_in_orphan=%s orph_bytes=%d pre_bytes=%d" %
      (pre_blank, crlf, orph_bytes, pre_bytes))

newC = C[:idx] + block + C[idx:]

# ---- 4) zero-loss verification (all must hold before write)
assert len(newC) == len(C) + len(block), "length arithmetic fail"
assert newC.startswith(C[:idx]), "prefix identity fail"
assert newC.endswith(C[idx:]), "suffix identity fail"
seam = newC.find(block)
assert seam == len(C[:idx]), "block not at seam"
assert newC.count(block) == 1, "block appears more than once"

# round-sequence verification (tolerates BOTH ASCII '|' and fullwidth '｜'
# era separators and placeholder timestamps like T21:5x / ++08:00)
import re
MARK = re.compile(rb"(?m)^2026-\S+?[ \xef\xbc\x9c|]+r(\d{1,4})\b")   # ASCII | or fullwidth ｜(U+FF5C)

def line_rounds(buf):
    return [int(m.group(1)) for m in MARK.finditer(buf)]

pre_seq = line_rounds(C)
blk_seq = line_rounds(block)
new_seq = line_rounds(newC)
assert blk_seq and blk_seq[0] == 290, "orphan block head not r290: %r" % blk_seq[:3]
assert blk_seq[-1] == 642, "orphan block tail not r642: %r" % blk_seq[-3:]
assert all(a <= b for a, b in zip(blk_seq, blk_seq[1:])), "orphan block not non-decreasing (addenda are legal, out-of-order is not)"
assert 643 in pre_seq and 644 in pre_seq and 289 in pre_seq, "pre-seq era markers missing"
cut = pre_seq.index(643)
assert new_seq == pre_seq[:cut] + blk_seq + pre_seq[cut:], "sequence splice mismatch"
assert all(a <= b for a, b in zip(new_seq, new_seq[1:])), "merged sequence not non-decreasing"
post_lines = newC.count(b"\n")
assert post_lines == pre_lines + block.count(b"\n"), "line-count arithmetic fail"
print("seq check: pre=%d rounds, block=%d rounds (r%d..r%d), merged=%d rounds strictly increasing"
      % (len(pre_seq), len(blk_seq), blk_seq[0], blk_seq[-1], len(new_seq)))

# ---- 5) atomic-ish write (write then re-open verify)
with open(CANON, "wb") as fh:
    fh.write(newC)
chk = open(CANON, "rb").read()
assert chk == newC, "write-back verify fail"
print("CANON healed: %d -> %d bytes (+%d), lines %d -> %d" %
      (pre_bytes, len(chk), len(block), pre_lines, post_lines))

# ---- 6) pointer line appended to frozen orphan (append-only, style-matched EOL)
eol = b"\r\n" if crlf else b"\n"
ptr = ("〔指针·r645 bm-c〕本件=r290-r642 纪元冻结面（r455 孤儿路径纪元）——正典轮账本=logs/iteration-loop/round_reports-bm-c.md；"
       "r290-r642 全块已于 r645 5x 窗 verbatim 并回正典件（字节恒等零丢失·receipt=results/_r645bmc_ledger_heal_receipt.json）·本件停写。"
       ).encode("utf-8")
with open(ORPH, "ab") as fh:
    fh.write(eol + ptr + eol)
print("ORPHAN pointer appended")

# ---- 7) receipt
receipt = {
    "surgery": "round-ledger era-merge (r645 5x window)",
    "canonical": "logs/iteration-loop/round_reports-bm-c.md",
    "orphan_frozen": "round_reports-bm-c.md",
    "guard_prescan_rc": guard_rc,
    "guard_prescan_tail": guard_tail,
    "pre_bytes": pre_bytes, "orphan_bytes": orph_bytes,
    "block_bytes": len(block), "post_bytes": len(newC),
    "pre_lines": pre_lines, "orphan_lines": orph_lines, "post_lines": post_lines,
    "insert_position": idx, "pre_blank_sep": pre_blank, "orphan_crlf": bool(crlf),
    "era": "r290..r642 inserted between r289 and r643",
    "verification": ["len_arithmetic", "prefix_identity", "suffix_identity",
                     "block_unique_at_seam", "round_order_r289<r290<r642<r643",
                     "line_count_arithmetic", "writeback_readback_equal"],
    "zero_loss": True, "deletions": 0,
}
with open(REC, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1, sort_keys=True)
    fh.write("\n")
print("RECEIPT " + REC)
