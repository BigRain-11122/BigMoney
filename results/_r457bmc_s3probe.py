"""r457 bm-c S3 standing checks: post_review re-derive + satengine status + pool hunger probe.
All child processes CREATE_NO_WINDOW; read-only."""
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(args, cwd=ROOT, timeout=300):
    r = subprocess.run(["python"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW, timeout=timeout)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, out, err


def main():
    rc, out, err = run(["Tools\\post_review.py"], timeout=600)
    print("== post_review rc=%d ==" % rc)
    print((out + err).strip()[-2000:])
    rc, out, err = run(["Tools\\saturation_engine.py", "status"], timeout=120)
    print("== satengine status rc=%d ==" % rc)
    print((out + err).strip()[-1500:])
    p = os.path.join(ROOT, "results", "runnable_pool.json")
    try:
        with open(p, encoding="utf-8-sig") as fh:
            pool = json.load(fh)
        items = pool if isinstance(pool, list) else pool.get("items", pool.get("queue", []))
        if isinstance(items, dict):
            items = list(items.values())
        print("== pool items %d ==" % len(items))
        for it in items[:20]:
            if isinstance(it, dict):
                print("  %s status=%s owner=%s lane=%s" % (
                    it.get("id", it.get("name", "?")),
                    it.get("status", "?"), it.get("owner", it.get("owner_since", "?")),
                    it.get("lane", "?")))
    except Exception as e:
        print("pool read error: %s" % e)


if __name__ == "__main__":
    main()
