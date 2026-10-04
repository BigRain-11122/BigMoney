"""r464 bm-c pre-merge inspection: crash_fuse + representative snapshot faces,
both sides (HEAD vs origin/main) ts fields, to drive per-face resolution."""
import json
import subprocess

C = 0x08000000


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       creationflags=C, cwd=".")
    return r.returncode, r.stdout


FACES = [
    "results/crash_fuse.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/regime_state.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/fundamental_b_layer_filter.json",
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
]


def peek(path):
    out = {}
    for ref in ("HEAD", "origin/main"):
        rc, b = show(ref, path)
        if rc != 0:
            out[ref] = "SHOW_FAIL"
            continue
        try:
            d = json.loads(b.decode("utf-8", "replace"))
        except Exception as e:  # noqa: BLE001
            out[ref] = "PARSE_FAIL " + str(e)[:60]
            continue
        keys = {}
        for k in ("ts", "updated", "updated_at", "clock", "clock_read",
                  "last_run", "generated", "generated_at", "asof", "cutoff"):
            if k in d:
                keys[k] = str(d[k])[:32]
        if not keys:
            keys["(top-keys)"] = ",".join(list(d.keys())[:12])[:120]
        out[ref] = keys
    return out


def main():
    for p in FACES:
        r = peek(p)
        print("==", p)
        for ref, v in r.items():
            print("  ", ref, v)
    # crash_fuse deep structure
    rc, b = show("HEAD", "results/crash_fuse.json")
    d = json.loads(b.decode("utf-8", "replace"))
    print("crash_fuse HEAD top keys:", list(d.keys()))
    rc, b = show("origin/main", "results/crash_fuse.json")
    d2 = json.loads(b.decode("utf-8", "replace"))
    print("crash_fuse ORIGIN top keys:", list(d2.keys()))
    for k in sorted(set(d.keys()) | set(d2.keys())):
        a, c = d.get(k), d2.get(k)
        if a != c:
            sa = json.dumps(a, ensure_ascii=False)[:150]
            sc = json.dumps(c, ensure_ascii=False)[:150]
            print(f"DIFFER {k}:\n   HEAD={sa}\n   ORIGIN={sc}")


if __name__ == "__main__":
    main()
