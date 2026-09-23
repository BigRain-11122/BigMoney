"""Traffic policy + pending-sync queue.

When network is HOTSPOT:
  - heavy pulls (>100MB) are deferred to pending_sync.json
  - only incremental updates (<5MB) allowed
  - worker result upload: metrics JSON only, no CSV

When LAN/WIFI:
  - normal sync, flush pending queue in FIFO order.
"""
import json
import os
from datetime import datetime, timezone

_ROOT = os.path.dirname(os.path.abspath(__file__))
PENDING_PATH = os.path.join(_ROOT, "logs", "pending_sync.json")
HEAVY_LIMIT_BYTES = 100 * 1024 * 1024       # 100 MB
LIGHT_LIMIT_BYTES = 5 * 1024 * 1024        # 5 MB

# reuse detector
from network_detector import read_status  # noqa: E402


def load_pending() -> list:
    if not os.path.exists(PENDING_PATH):
        return []
    with open(PENDING_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_pending(q: list):
    os.makedirs(os.path.dirname(PENDING_PATH), exist_ok=True)
    with open(PENDING_PATH, "w", encoding="utf-8") as f:
        json.dump(q, f, indent=2, ensure_ascii=False)


def defer(path: str, est_size_bytes: int, note: str = ""):
    q = load_pending()
    q.append({
        "path": path,
        "est_size_bytes": est_size_bytes,
        "queued_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": note,
    })
    save_pending(q)
    print(f"[traffic] deferred to pending queue: {path} "
          f"({est_size_bytes/1024/1024:.1f} MB)")


def can_run(task_name: str, est_size_bytes: int) -> bool:
    """Return True if task may run now."""
    st = read_status()
    if not st.get("hotspot", False):
        return True
    # on hotspot: only light tasks allowed
    if est_size_bytes <= LIGHT_LIMIT_BYTES:
        return True
    defer(f"task:{task_name}", est_size_bytes, "hotspot-deferred")
    return False


def check_traffic_allowed(task_name: str, estimated_size_mb: float) -> bool:
    """Public API matching the spec: size in MB."""
    return can_run(task_name, int(estimated_size_mb * 1024 * 1024))


def flush_pending() -> list:
    """Run all pending tasks when network recovers. Returns list of completed paths."""
    st = read_status()
    if st.get("hotspot", False):
        return []
    q = load_pending()
    done = []
    remaining = []
    for item in q:
        # In real deployment: call the actual sync/upload here.
        # We just record it as done and log.
        done.append(item["path"])
        print(f"[traffic] flushed pending: {item['path']}")
    if done:
        save_pending(remaining)
    return done


if __name__ == "__main__":
    # self-test
    st = read_status()
    print("current status:", st)
    print("can run 200MB pull?", can_run("daily_full_pull", 200 * 1024 * 1024))
    print("can run 2MB incremental?", can_run("incremental_today", 2 * 1024 * 1024))
    print("pending queue:", load_pending())
