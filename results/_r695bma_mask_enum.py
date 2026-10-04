# r695 bm-a: enumerate ALL historical mask versions, find the exact stage-A reproducer
import io, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import refine_bench_rev_census as RC
import rev_osc_stock_p1 as RV

# all commits touching the mask, newest first
out = subprocess.run(["git", "log", "--format=%H %ci %h",
                      "--", "data/fundamental/b_layer_mask.csv"],
                     capture_output=True, cwd=ROOT)
revs = [l.split()[0:4:3] for l in out.stdout.decode().strip().splitlines()]
print("mask history:")
for r in revs[:10]:
    print("  %s %s" % (r[1], r[0][:12]))

CELL_NAME = "D-15|raw|base|time|h20"
target = (1.1551, 0.091023)
RC._init_worker()  # panel loaded once; we only patch MASK between runs? load_panel
# re-runs fully on RV.MASK change -> must reload panel each time. Cheaper: patch mask,
# reload, run cell (panel load ~7s each).
cell = [c for c in RC.census_cells() if c["name"] == CELL_NAME][0]

for r in revs[:8]:
    rev = r[0]
    mb = subprocess.run(["git", "show", "%s:data/fundamental/b_layer_mask.csv" % rev],
                        capture_output=True, cwd=ROOT).stdout
    tmp = os.path.join(ROOT, "results", "_r695bma_mask_try.csv")
    open(tmp, "wb").write(mb)
    RV.MASK = tmp
    RC._init_worker()
    row = RC._cell_job(cell)
    hit = (row["sharpe_full"], row["ann_ret"]) == target
    print("%s(%s): sharpe=%r ann=%r entries=%r  %s"
          % (rev[:10], r[1], row["sharpe_full"], row["ann_ret"],
             row["entries"], "*** STAGE-A EXACT MATCH ***" if hit else ""))
    if hit:
        break
os.remove(os.path.join(ROOT, "results", "_r695bma_mask_try.csv"))
print("PROBE_OK")
