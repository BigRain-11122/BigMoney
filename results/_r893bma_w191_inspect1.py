# -*- coding: utf-8 -*-
"""r893 adoption helper: locate seat-archive wording across the four W190 face dumps."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for f in ("pf_block", "n1_entry", "n1_mat", "n1_claim"):
    t = io.open(r"results/_r893bma_w191_probe_%s.txt" % f,
                encoding="utf-8", newline="").read()
    hits = [m for m in re.finditer(r"archive[^\"\\]{0,120}", t)]
    print("===", f, len(t), "bytes,", len(hits), "archive hits")
    for m in hits[:5]:
        print("   ", repr(m.group()[:135]))
    # also find seat-related context lines
    for m in re.finditer(r"[^\r\n]{0,80}self-ack[^\r\n]{0,110}", t):
        print("  SA:", repr(m.group()[:190]))
