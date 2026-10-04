# r695 bm-a: da44b8b11 mask (UTF-16 blob) decoded -> rerun failing cell (exact-match hunt)
import io, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import refine_bench_rev_census as RC
import rev_osc_stock_p1 as RV

for rev in ("da44b8b11347", "f1bb63fea77e", "a728ba9b4301"):
    raw = subprocess.run(["git", "show", "%s:data/fundamental/b_layer_mask.csv" % rev],
                         capture_output=True, cwd=ROOT).stdout
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        txt = raw.decode("utf-16")
        enc = "utf-16 blob -> decoded"
    else:
        txt = raw.decode("utf-8", "replace")
        enc = "utf-8 blob"
    tmp = os.path.join(ROOT, "results", "_r695bma_mask_try2.csv")
    open(tmp, "w", encoding="utf-8", newline="").write(txt)
    RV.MASK = tmp
    RC._init_worker()
    cell = [c for c in RC.census_cells() if c["name"] == "D-15|raw|base|time|h20"][0]
    row = RC._cell_job(cell)
    hit = (row["sharpe_full"], row["ann_ret"]) == (1.1551, 0.091023)
    print("%s [%s]: sharpe=%r ann=%r entries=%r %s"
          % (rev[:10], enc, row["sharpe_full"], row["ann_ret"], row["entries"],
             "*** STAGE-A EXACT MATCH ***" if hit else ""))
    if hit:
        break
os.remove(os.path.join(ROOT, "results", "_r695bma_mask_try2.csv"))
print("PROBE_OK")
