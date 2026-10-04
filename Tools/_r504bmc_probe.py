"""r504 bm-c S3 pre-board probe: fleet task board scan + W3 judge custody
(pid alive / product landed) + pool N2-W15 face. Zero-window subprocess."""
import glob
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def probe_pid(pid):
    # self-match guard: probe via -File exact-path style is not applicable;
    # use Get-CimInstance but exclude self by checking CommandLine content.
    cmd = ("Get-CimInstance Win32_Process -Filter 'ProcessId=%d' | "
           "Select-Object -ExpandProperty CommandLine" % pid)
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command", cmd],
        capture_output=True, creationflags=CREATE_NO_WINDOW)
    out = (r.stdout or b"").decode("gbk", "replace").strip()
    return out if out else None


def main():
    # 1) board scan
    stats = {}
    flagged = []
    for f in sorted(glob.glob(os.path.join(ROOT, "fleet", "tasks", "*.json"))):
        try:
            with open(f, encoding="utf-8-sig") as fh:
                d = json.load(fh)
        except Exception:
            continue
        s = d.get("status", "?")
        stats[s] = stats.get(s, 0) + 1
        blob = json.dumps(d)
        if s == "open":
            flagged.append((os.path.basename(f), "OPEN"))
        if "immediate" in blob and s != "done":
            flagged.append((os.path.basename(f), s + "/IMMEDIATE"))
    print("BOARD", stats)
    for x in flagged:
        print("BOARD-ATTN", x)

    # 2) W3 judge custody
    cl = probe_pid(26052)
    print("W3-PID-26052:", "ALIVE" if cl else "DEAD", (cl or "")[:120])
    for p in (glob.glob(os.path.join(ROOT, "results", "*w3*judge*"))
              + glob.glob(os.path.join(ROOT, "results", "**", "w3_judge*.json"),
                          recursive=True)
              + glob.glob(os.path.join(ROOT, "results", "*w3*.json"))):
        print("W3-FACE", os.path.relpath(p, ROOT), os.path.getmtime(p))

    # 3) pool N2-W15 face
    try:
        with open(os.path.join(ROOT, "results", "runnable_pool.json"),
                  encoding="utf-8-sig") as fh:
            d = json.load(fh)
        s = json.dumps(d)
        idx = s.find("N2-W15")
        if idx >= 0:
            print("POOL-N2W15:", s[max(0, idx - 150):idx + 700])
        else:
            print("POOL-N2W15: NOT-FOUND (may have flipped to done)")
    except Exception as e:
        print("POOL err", repr(e))


if __name__ == "__main__":
    main()
