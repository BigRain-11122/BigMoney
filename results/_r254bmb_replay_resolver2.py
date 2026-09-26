"""_r254bmb_replay_resolver2 -- fix-up legs after resolver1 (bm-b r254 replay).

resolver1 gaps (self-caught, r242 probe-first law):
  1. dashboard pair: top-level ts absent (real key = meta.generated_at) ->
     resolver1 None-tie defaulted to ours = FORBIDDEN silent-side pattern.
     Field-probe verdict: ours 14:15:18 vs theirs 14:20:23 -> THEIRS (bm-b mine)
     newer -> take side-3 whole-byte for BOTH .json and .js (wrapper asserted).
  2. compute_audit.json: structure = {latest, history}; resolver1 top-level
     probe missed latest.ts -> merged.latest stayed ours (bm-a 14:14:10 stale)
     while my audit 14:19:32 is newer -> latest take-new by latest.ts (mine),
     history union (202 rows) preserved untouched.
"""
import json
import subprocess
import sys

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"


def blob(side, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (side, path)],
                       capture_output=True, cwd=ROOT)
    return r.stdout if r.returncode == 0 else None


def put(path, data):
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(data)


def jload(b):
    try:
        return json.loads(b.decode("utf-8-sig"))
    except Exception:
        return None


def jload_wrapped(b):
    """js-wrapper face: `window.DASH_DATA = {...};` -> strip wrapper then parse."""
    if b is None:
        return None
    s = b.decode("utf-8-sig", errors="replace").strip()
    pre = "window.DASH_DATA"
    if not s.startswith(pre):
        return None
    s = s[s.index("=") + 1:].strip().rstrip(";").strip()
    try:
        return json.loads(s)
    except Exception:
        return None


def main():
    log = []
    # 1. dashboard pair -> side 3 (mine, meta.generated_at newer), whole bytes
    for p in ("results/dashboard_status.json", "results/dashboard_status.js"):
        loader = jload if p.endswith(".json") else jload_wrapped
        a = loader(blob(2, p))
        t = loader(blob(3, p))
        va = str(((a or {}).get("meta") or {}).get("generated_at") or "")
        vt = str(((t or {}).get("meta") or {}).get("generated_at") or "")
        assert va and vt, "meta.generated_at absent on a side -- fail-closed"
        win = 3 if vt > va else 2
        data = blob(win, p)
        if p.endswith(".js"):
            assert data.strip().startswith(b"window.DASH_DATA"), "R209 wrapper"
        else:
            assert jload(data) is not None
        put(p, data)
        log.append("  %s: meta.generated_at ours=%s vs theirs=%s -> side %d whole-byte"
                   % (p, va, vt, win))
    # 2. compute_audit latest take-new (history union on disk untouched)
    p = "results/compute_audit.json"
    cur = jload(open(ROOT + "\\results\\compute_audit.json", "rb").read()) or {}
    la = jload(blob(2, p)) or {}
    lt = jload(blob(3, p)) or {}
    tsa = str((la.get("latest") or {}).get("ts") or "")
    tst = str((lt.get("latest") or {}).get("ts") or "")
    assert tsa and tst, "latest.ts absent -- fail-closed"
    cur["latest"] = lt["latest"] if tst > tsa else la["latest"]
    out = json.dumps(cur, ensure_ascii=False, indent=1).encode("utf-8")
    put(p, out)
    assert jload(out) is not None and len(cur.get("history") or []) == 202
    log.append("  %s: latest.ts ours=%s vs theirs=%s -> %s; history union 202 preserved"
               % (p, tsa, tst, "theirs(mine)" if tst > tsa else "ours"))
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
