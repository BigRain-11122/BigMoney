"""Terminal monitor: scan results dir and print progress."""
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS, all_combinations


def snapshot() -> dict:
    total = len(all_combinations())
    files = glob.glob(os.path.join(PATHS.results_dir, "*.json"))
    done = 0
    ok = 0
    err = 0
    for f in files:
        try:
            with open(f) as fh:
                r = json.load(fh)
            done += 1
            if r.get("status") == "ok":
                ok += 1
            else:
                err += 1
        except Exception:
            continue
    return {
        "total": total,
        "done": done,
        "ok": ok,
        "error": err,
        "pct": round(done / total * 100, 1) if total else 0,
    }


def render(s: dict):
    bar_w = 40
    filled = int(bar_w * s["pct"] / 100)
    bar = "#" * filled + "-" * (bar_w - filled)
    print(f"\r[{bar}] {s['pct']:.1f}%  "
          f"done={s['done']}/{s['total']}  "
          f"ok={s['ok']} err={s['error']}", end="")


def watch(interval: float = 5.0):
    try:
        while True:
            render(snapshot())
            time.sleep(interval)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    watch()
