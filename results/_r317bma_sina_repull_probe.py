"""r317 bm-a interim probe: sina_mf A1 deep repull pace + ETA (watch-face evidence, read-only)."""
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT / "data" / "sina_mf" / "_progress.json").read_text(encoding="utf-8"))
done = len(d["done"])
todo = 5228
now = time.time()
# repull lock mtime = process start face (11:04:12 local = lock file mtime)
lock = ROOT / "data" / "sina_mf" / "_refresh.lock"
start = lock.stat().st_mtime
elapsed_min = (now - start) / 60.0
pace = done / elapsed_min if elapsed_min > 0 else 0.0
eta_min = (todo - done) / pace if pace > 0 else float("nan")
out = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "probe": "sina_mf A1 deep repull interim (r317 bm-a)",
    "done": done,
    "todo": todo,
    "remaining": todo - done,
    "elapsed_min": round(elapsed_min, 1),
    "pace_per_min": round(pace, 1),
    "eta_min": round(eta_min, 1),
    "eta_abs": time.strftime("%H:%M", time.localtime(now + eta_min * 60)) if pace > 0 else None,
    "attempts_fail": len(d.get("attempts_fail") or []),
    "lock_alive": lock.exists(),
}
print(json.dumps(out, ensure_ascii=False))
(ROOT / "results" / "_r317bma_sina_repull_probe.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8"
)
