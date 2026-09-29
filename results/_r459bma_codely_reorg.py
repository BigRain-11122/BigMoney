# -*- coding: utf-8 -*-
"""_r459bma_codely_reorg.py -- hot-cold reorg: CODELY.md 10,357B > 10,240B
hard line, same-window mandatory (moved 1 (r458) / lost 0). Idempotence
guard per r457 law: target-section tag in-file probe first."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202609.md")
TAG = "## 热冷整编 2026-09-30 r459 bm-a 窗批"
PREFIX = "- [2026-09-30 04:4x r458 bm-a]"
POINTER = ("- 冷层指针：r458 泊位族选双面核验坑（zoo 行状态面滞后于 results 判决面）"
           "全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r459 bm-a 窗批』节"
           "（法面=防重核双面序：rg results 判决面先行·zoo/登记行只作线索）。")

with io.open(CODELY, encoding="utf-8") as fh:
    codely = fh.read()
with io.open(ARCHIVE, encoding="utf-8") as fh:
    arch = fh.read()

if TAG in arch:
    print("idempotent: archive section already present -- verify-only pass")
else:
    lines = codely.splitlines()
    hits = [i for i, ln in enumerate(lines) if ln.startswith(PREFIX)]
    assert len(hits) == 1, f"entry hits {len(hits)} != 1"
    entry = lines[hits[0]]
    assert "How to apply" in entry, "entry tail missing (swallow check)"
    sect = (TAG + "\n\n（CODELY.md 10,357B>10,240B 硬线当窗即办·"
            "moved 1 (r458)/lost 0·行级零丢失校验。）\n\n" + entry + "\n")
    arch = arch.rstrip("\n") + "\n\n" + sect
    with io.open(ARCHIVE + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(arch)
    os.replace(ARCHIVE + ".tmp", ARCHIVE)
    lines[hits[0]] = POINTER
    codely2 = "\n".join(lines) + "\n"
    assert codely.count(PREFIX) == 1 and POINTER in codely2
    assert len(codely2.splitlines()) == len(codely.splitlines()), "line count drift"
    assert entry not in codely2, "verbatim still in hot layer"
    assert entry in arch, "verbatim not in archive (lost!)"
    with io.open(CODELY + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(codely2)
    os.replace(CODELY + ".tmp", CODELY)

print("codely bytes:", os.path.getsize(CODELY))
print("archive bytes:", os.path.getsize(ARCHIVE))
assert os.path.getsize(CODELY) < 10240, "still over hard line"
print("REORG OK: moved 1 / lost 0, under 10240 line")
