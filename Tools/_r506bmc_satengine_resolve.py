"""r506 bm-c: satengine lane-face UU resolve (rebase 4/4, two own-lane daemon
faces) via import of the v2 resolver's regen-newer logic; then CODELY.md
tail-union v2 (line-start-only residual assertions per r419 needle-furniture
law -- our own r506 entry quotes marker text mid-line as data)."""
import io
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import _r506bmc_rebase_resolve as R  # noqa: E402

for p in ("results/saturation_engine/face_bm-c.json",
          "results/saturation_engine_state.bm-c.json"):
    R.resolve_regen(p)
    print("resolved", p, "->", R.receipt["files"][p])
io.open(os.path.join(ROOT, "results", "_r506bmc_satengine_resolve.json"), "w",
        encoding="utf-8", newline="\n").write(
    io.open(os.path.join(ROOT, "results", "_r506bmc_rebase_resolve.json"),
            encoding="utf-8").read() if os.path.exists(
        os.path.join(ROOT, "results", "_r506bmc_rebase_resolve.json")) else "{}")

# --- CODELY.md union v2 (line-start marker parsing, no substring assertions)
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
s1 = lines[o + 1:b]      # upstream (origin) tail entries
s2 = lines[m + 1:c]      # our r506 entry
out = lines[:o] + s1 + s2 + lines[c + 1:]
text = "".join(out)
# line-start residual check ONLY (our entry quotes marker text mid-line)
assert not any(ln.startswith(("<<<<<<< ", "||||||| ", ">>>>>>> "))
               or ln.rstrip("\r\n") == "=======" for ln in out), "line-start marker residue"
assert "[2026-10-05 01:2x r705 bm-a]" in text, "upstream r705 entry lost"
assert "[2026-10-05 01:3x r706 bm-a]" in text, "upstream r706 entry lost"
assert "[2026-10-05 01:3x r506 bm-c]" in text, "our r506 entry lost"
io.open(P, "w", encoding="utf-8", newline="").write(text)
print("CODELY union v2 OK: %d upstream + %d ours kept, %d lines"
      % (len(s1), len(s2), len(out)))
