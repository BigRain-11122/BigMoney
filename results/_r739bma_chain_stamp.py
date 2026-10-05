# -*- coding: utf-8 -*-
"""r739: stamp round number on the copied S6 chain (copy-then-edit r739 law;
the r738 original stays byte-identical on disk)."""
import io

p = "results\\_r739bma_s6_chain.ps1"
t = io.open(p, encoding="utf-8", newline="").read()
pairs = [
    ("# r738 bm-a S6 chain driver", "# r739 bm-a S6 chain driver", 1),
    ("$log = 'results\\_r738bma_s6_chain.txt'", "$log = 'results\\_r739bma_s6_chain.txt'", 1),
    ("=== r738 S6 chain start", "=== r739 S6 chain start", 1),
    ("=== r738 S6 chain end", "=== r739 S6 chain end", 1),
]
for old, new, expect in pairs:
    n = t.count(old)
    assert n == expect, "needle mismatch (%d != %d): %r" % (n, expect, old[:40])
    t = t.replace(old, new)
assert "r738" not in t.replace("# r739 bm-a S6 chain driver", ""), "residual r738 stamps"
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("r739 chain stamped (4 lines, log path now _r739bma_s6_chain.txt)")
