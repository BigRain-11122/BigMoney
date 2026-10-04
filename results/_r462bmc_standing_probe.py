"""r462 bm-c S3 standing probe (compact, file-out per r446 law):
1. watermark_red.json -> red / next_pick (compact JSON-serialized, never array-stringify flood)
2. saturation_engine status -> rc + head fields only (full dump to side file for archive)
Zero console CJK print."""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r462bmc_standing_probe.json")
SAT_FULL = os.path.join(ROOT, "results", "_r462bmc_satengine_status.txt")


def main():
    ev = {}
    # 1. watermark red / next_pick
    try:
        with open(os.path.join(ROOT, "results", "watermark_red.json"),
                  encoding="utf-8-sig") as f:
            wr = json.load(f)
        red = wr.get("red")
        if isinstance(red, (list, dict)):
            ev["wm_red"] = {"type": type(red).__name__,
                            "len": len(red), "repr": json.dumps(red, ensure_ascii=False)[:400]}
        else:
            ev["wm_red"] = red
        ev["wm_verdict"] = wr.get("verdict")
        npk = wr.get("next_pick")
        ev["wm_next_pick"] = npk if not isinstance(npk, (list, dict)) else json.dumps(npk, ensure_ascii=False)[:200]
    except Exception as e:  # noqa: BLE001
        ev["wm_error"] = repr(e)[:200]
    # 2. saturation engine status (bm-c instance = Tools/saturation_engine.py)
    r = subprocess.run(["python", "Tools/saturation_engine.py", "status"],
                      capture_output=True, cwd=ROOT,
                      creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    ev["sat_rc"] = r.returncode
    txt = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    with open(SAT_FULL, "w", encoding="utf-8", newline="") as f:
        f.write(txt)
        if err:
            f.write("\n--- STDERR ---\n")
            f.write(err)
    # compact head fields: parse first 3000 chars for status keys
    head = txt[:3000]
    ev["sat_head_keys"] = sorted(set(
        k for k in ("alive", "engine", "queue", "tick", "ts", "state", "pid",
                    "waves", "status", "queue_len", "n1")
        if ('"%s"' % k) in head or ('%s' % k) in head.split("\n")[0][:200]
    ))
    first_lines = [ln for ln in head.splitlines() if ln.strip()][:12]
    ev["sat_first_lines"] = first_lines
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("PROBE_DONE sat_rc=", r.returncode)


if __name__ == "__main__":
    main()
