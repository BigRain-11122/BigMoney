"""r504 bm-c: double-burn guard probe -- any live bm-c python child burning
N2-W15 screen shard-2 (pid/cmdline), + daemon face snapshot (satengine state)."""
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    cmd = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
           "Where-Object {$_.CommandLine -notmatch 'Get-CimInstance'} | "
           "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress")
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    raw = (r.stdout or b"").decode("gbk", "replace").strip()
    print("PY-PROCS-RAW-LEN", len(raw))
    if not raw:
        print("NO-LIVE-PYTHON")
        return
    try:
        procs = json.loads(raw)
        if isinstance(procs, dict):
            procs = [procs]
    except Exception:
        print("JSON-PARSE-FAIL; raw head:", raw[:400])
        procs = []
    for p in procs:
        cl = (p.get("CommandLine") or "")
        pid = p.get("ProcessId")
        short = cl.replace(ROOT, ".")[:200]
        print("PID", pid, short)
    # daemon face snapshot
    for f in ("results/saturation_engine_state.bm-c.json",
              "results/saturation_engine/face_bm-c.json"):
        try:
            with open(os.path.join(ROOT, f), encoding="utf-8-sig") as fh:
                d = json.load(fh)
            keys = [k for k in d.keys()]
            print("FACE", f, "keys:", keys[:20])
            for k in ("current", "queue", "wave", "burning", "running",
                      "last_tick", "pid", "entries"):
                if k in d:
                    print("  ", k, "=", str(d[k])[:300])
        except Exception as e:
            print("FACE", f, "err", repr(e))


if __name__ == "__main__":
    main()
