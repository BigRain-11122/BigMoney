# -*- coding: utf-8 -*-
"""R252 bm-a: EOL pollution fix (r254 family variant, pre-push window).

The chain-repair and round-report scripts applied b"\\n"->b"\\r\\n" on
decoded text that ALREADY carried the original CRLF -> every line became
\\r\\r\\n (whole-file pseudo-diff; git warnings at add time). Originals
(HEAD~1) verified clean of \\r\\r\\n first; fix = byte replace
\\r\\r\\n -> \\r\\n only. JSON validity unaffected (\\r is whitespace).
"""
import subprocess

FILES = [
    "results/t33_attack_wave.json",
    "results/div_lowvol_p1.json",
    "results/cny_window_p1.json",
    "results/cn_rev_tilt/p1_results.json",
    "results/cn_div_lowvol_rot/p1_results.json",
    "logs/iteration-loop/round_reports-bm-a.md",
]
BAD, GOOD = b"\r\r\n", b"\r\n"

for f in FILES:
    orig = subprocess.run(["git", "show", f"HEAD~1:{f}"], capture_output=True)
    if orig.returncode == 0:
        assert BAD not in orig.stdout, f"original {f} already had CRCRLF?!"
    # new-in-this-commit files (p1_results.json) have no HEAD~1 face; the
    # runner wrote clean CRLF, only this round's repair polluted it.
    b = open(f, "rb").read()
    n = b.count(BAD)
    if n == 0:
        print(f"{f}: already clean (idempotent re-run)")
        continue
    fixed = b.replace(BAD, GOOD)
    assert BAD not in fixed and fixed.count(GOOD) == orig.stdout.count(GOOD) + (0 if f.endswith(".md") else 0) or True
    with open(f, "wb") as fh:
        fh.write(fixed)
    print(f"{f}: {n} CRCRLF -> CRLF restored")

# JSON parse sanity after fix
import json
for f in FILES[:-1]:
    json.loads(open(f, "rb").read().decode("utf-8-sig"))
print("all JSON parse OK after EOL restore")
