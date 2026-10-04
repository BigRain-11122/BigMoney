"""r506 bm-c: CODELY.md rebase-tail union (append-only both-sides-adds case,
outside the 31-face resolver classes). Keep upstream (origin) tail entries
AND our r506 entry, chronological order. UTF-8 + EOL-preserving (keepends)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "CODELY.md")

raw = io.open(P, "r", encoding="utf-8", newline="").read()
lines = raw.splitlines(keepends=True)
idx_open = [i for i, ln in enumerate(lines) if ln.startswith("<<<<<<< ")]
idx_base = [i for i, ln in enumerate(lines) if ln.startswith("||||||| ")]
idx_mid = [i for i, ln in enumerate(lines) if ln.rstrip("\r\n") == "======="]
idx_close = [i for i, ln in enumerate(lines) if ln.startswith(">>>>>>> ")]
assert len(idx_open) == len(idx_close) == len(idx_base) == len(idx_mid) == 1, \
    "marker counts %s %s %s %s" % (idx_open, idx_base, idx_mid, idx_close)
o, b, m, c = idx_open[0], idx_base[0], idx_mid[0], idx_close[0]
s1 = lines[o + 1:b]      # upstream (origin) side
s2 = lines[m + 1:c]      # our replayed side
out = lines[:o] + s1 + s2 + lines[c + 1:]
text = "".join(out)
assert "<<<<<<" not in text and ">>>>>>>" not in text and "|||||||" not in text, \
    "marker residue"
assert "[2026-10-05 01:2x r705 bm-a]" in text, "upstream r705 entry lost"
assert "[2026-10-05 01:3x r706 bm-a]" in text, "upstream r706 entry lost"
assert "[2026-10-05 01:3x r506 bm-c]" in text, "our r506 entry lost"
io.open(P, "w", encoding="utf-8", newline="").write(text)
print("CODELY union OK: kept %d upstream + %d ours, %d lines total"
      % (len(s1), len(s2), len(out)))
