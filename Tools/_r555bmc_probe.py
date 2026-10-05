"""r555 bm-c S2/S3 compact board probe (r536/r539 lineage).
Fleet tasks board + runnable pool counts + watermark verdict read.
Read-only. No mutations."""
import glob
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    with io.open(p, encoding="utf-8-sig") as fh:
        return json.load(fh)


def main():
    ts = glob.glob(os.path.join(ROOT, "fleet", "tasks", "*.json"))
    stat = {}
    open_ids = []
    for p in ts:
        d = load(p)
        s = d.get("status", "?")
        stat[s] = stat.get(s, 0) + 1
        if s == "open":
            open_ids.append(d.get("id", os.path.basename(p)))
    print("TASKS total=%d stat=%s" % (len(ts), stat))
    print("OPEN: %s" % (open_ids if open_ids else "none"))
    pool = os.path.join(ROOT, "results", "runnable_pool.json")
    d = load(pool)
    e = d.get("entries", d if isinstance(d, list) else [])
    c = {}
    ready = []
    waiting = []
    for x in e:
        s = x.get("status", "?")
        c[s] = c.get(s, 0) + 1
        if s == "ready":
            ready.append(x.get("id"))
        if s == "waiting":
            waiting.append(x.get("id"))
    print("POOL total=%d stat=%s" % (len(e), c))
    print("READY: %s" % (ready if ready else "none"))
    print("WAITING: %s" % (waiting if waiting else "none"))
    wm = os.path.join(ROOT, "results", "watermark_red.json")
    if os.path.exists(wm):
        w = load(wm)
        print("WM red=%s lane=%s next_pick=%s" % (
            w.get("red"), w.get("lane", w.get("reason", ""))[:80],
            (w.get("next_pick") or "none")))
    else:
        print("WM watermark_red.json absent")
    wl = os.path.join(ROOT, "results", "watermark.jsonl")
    if os.path.exists(wl):
        lines = [l for l in io.open(wl, encoding="utf-8-sig").read().splitlines() if l.strip()]
        if lines:
            last = json.loads(lines[-1])
            print("WM-LAST verdict=%s ts=%s" % (
                last.get("verdict"), last.get("ts", last.get("generated", ""))))


if __name__ == "__main__":
    main()
