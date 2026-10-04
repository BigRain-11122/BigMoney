# r695 bm-a: stale-mask hypothesis -- burn census-era mask version, re-run failing cell
# bm-a was 23 commits behind origin at census time (r512 report); if the 09-30 mask
# commit (bd4da77b6, bm-b) was among the unmerged, stage-A burned on the 09-29 mask.
import io, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

def mask_bytes(rev):
    out = subprocess.run(["git", "show", "%s:data/fundamental/b_layer_mask.csv" % rev],
                         capture_output=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr[:200]
    return out.stdout

cur = open(os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv"), "rb").read()
old = mask_bytes("30564da6a")     # 09-29 11:06 version (pre-bd4da77b6)
mid = mask_bytes("bd4da77b6")    # 09-30 11:33 version (current committed state)
print("current==bd4da77b6:", cur == mid)
print("current==30564da6a(09-29):", cur == old)
print("old size=%d cur size=%d" % (len(old), len(cur)))
# line-level diff count
old_l = old.decode("utf-8", "replace").splitlines()
cur_l = cur.decode("utf-8", "replace").splitlines()
diffn = sum(1 for a, b in zip(old_l, cur_l) if a != b)
print("differing lines (09-29 vs now):", diffn, "of", len(cur_l))

if cur == old:
    print("MASK IDENTICAL -- stale-mask hypothesis DEAD")
    sys.exit(0)

# burn old mask to a temp file and run the failing cell against it
import refine_bench_rev_census as RC
import rev_osc_stock_p1 as RV
tmp_mask = os.path.join(ROOT, "results", "_r695bma_mask_0929.csv")
open(tmp_mask, "wb").write(old)
RV.MASK = tmp_mask                      # in-process override (load_panel reads RV.MASK)
RC._init_worker()                       # load panel with OLD mask
cell = [c for c in RC.census_cells() if c["name"] == "D-15|raw|base|time|h20"][0]
row = RC._cell_job(cell)
print("OLD-MASK rerun: sharpe_full=%r ann_ret=%r entries=%r skips=%r"
      % (row["sharpe_full"], row["ann_ret"], row["entries"], row["skips"]))
print("stage-A anchor:   sharpe_full=1.1551 ann_ret=0.091023 entries=4457")
print("today new-mask:   sharpe_full=1.1622 ann_ret=0.092307 entries=4457")
match = (row["sharpe_full"] == 1.1551 and row["ann_ret"] == 0.091023)
print("OLD-MASK REPRODUCES STAGE-A:", match)
print("PROBE_OK")
