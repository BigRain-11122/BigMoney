# r695 bm-a: full 10-cell RC parity sweep (in-process, census code verbatim)
import io, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import refine_bench_rev_census as RC
import contest_ytd_legs as CX   # for _pending_entrants + _rc_cells

cells = CX._rc_cells()
anchors = CX._census_anchor_rows()

RC._init_worker()  # panel load (census worker init verbatim)
print("panel loaded; sweeping %d RC cells (census _cell_job verbatim)" % len(cells))
t0 = time.time()
n_fail = 0
for c in cells:
    row = RC._cell_job(c)
    a = anchors[c["name"]]
    diffs = []
    for k in ("sharpe_full", "ann_ret", "max_dd", "n_days"):
        if row[k] != a[k]:
            diffs.append("%s %r!=%r" % (k, row[k], a[k]))
    for k in ("entries", "unfillable"):
        if row[k] != a[k]:
            diffs.append("%s %r!=%r" % (k, row[k], a[k]))
    if row["skips"] != a["skips"] or row["exits"] != a["exits"]:
        diffs.append("skips/exits")
    tag = "FAIL" if diffs else "pass"
    if diffs:
        n_fail += 1
    print("%s %-34s sharpe %r vs %r ann %r vs %r entries %r vs %r %s"
          % (tag, c["name"], row["sharpe_full"], a["sharpe_full"],
             row["ann_ret"], a["ann_ret"], row["entries"], a["entries"],
             "; ".join(diffs) if diffs else ""))
print("== sweep done %.1fs: %d/%d cells FAIL parity" % (time.time() - t0, n_fail, len(cells)))
print("PROBE_OK")
