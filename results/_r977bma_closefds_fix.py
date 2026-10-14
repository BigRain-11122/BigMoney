# r977 bm-a: close_fds leak fix across the 7 detached-refresh gate spawners.
# Root cause (live-confirmed this round): Popen(close_fds=False) on Windows
# makes the detached refresh inherit EVERY inheritable handle of the gate --
# including the gate's own stdout/stderr = the S6 chain's capture pipes. The
# refresh then holds the pipe write-ends for its whole lifetime (moneyflow
# full-universe = ~3.6h), so the chain parent parks in communicate() far past
# its timeout (r976 chain pid 130152 parked at leg-14, live evidence).
# Fix: close_fds=True -- the child still keeps lf via explicit std-handle
# passing (Python 3.7+ Windows semantics); no other handles are inherited.
import io
import sys

FILES = [
    "scripts/ah_panel_puller.py",
    "scripts/update_astock_daily.py",   # bm-b lane host -- same family defect, mechanical one-word fix
    "scripts/update_fund_statements.py",
    "scripts/update_moneyflow.py",
    "scripts/update_options.py",
    "scripts/update_sina_mf.py",
    "scripts/update_ths_panel.py",
]
OLD = "close_fds=False)"
NEW = "close_fds=True)"
# moneyflow carries the one stale rationale comment -> update it with the fix note
MF_OLD = "# child inherits lf; parent keeps running (R20 backfill precedent)"
MF_NEW = ("# child keeps lf via std-handle passing; close_fds=True stops the gate's\n"
          "# own std pipes (e.g. a batch chain's capture pipes) leaking into the\n"
          "# detached refresh -- r977 chain-park root cause, E64 card")

for path in FILES:
    t = io.open(path, encoding="utf-8", newline="").read()
    n = t.count(OLD)
    assert n == 1, (path, n)
    t = t.replace(OLD, NEW)
    if "update_moneyflow" in path:
        m = t.count(MF_OLD)
        assert m == 1, (path, m)
        t = t.replace(MF_OLD, MF_NEW)
    io.open(path, "w", encoding="utf-8", newline="").write(t)
    print("FIXED", path)
print("ALL 7 FIXED")
