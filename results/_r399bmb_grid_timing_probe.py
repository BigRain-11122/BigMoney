import sys
import time

sys.path.insert(0, "scripts")
import grid_dualface_backtest as G  # noqa: E402

t0 = time.time()
shard, err = G.burn_member("510300")
dt = time.time() - t0
if shard is None:
    print("REFUSE:", err)
    sys.exit(2)
n_cells = len(shard["cells"])
rows = shard["face"]["rows"]
es = shard["eval_start_date"]
print(f"burn_member(510300) in-memory: {dt:.1f}s cells={n_cells} "
      f"face_rows={rows} eval_start={es}")
print(f"projected full batch (5 members): ~{dt * 5 / 60:.1f} min")
