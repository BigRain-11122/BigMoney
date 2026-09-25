"""R212 resolver step-0: conflict shape census (R208 law: scan file shape BEFORE resolving).

For each UU file, extract side-2 (ours = base bm-b r221) and side-3 (theirs = my R212),
report structural keys + ts fields to classify snapshot vs rolling-ledger.
"""
import json, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")

UU = [
    "CODELY.md",
    "results/autofill_state.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def side(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def probe_json(b, label):
    try:
        j = json.loads(b.decode("utf-8-sig"))
    except Exception as e:
        print(f"  {label}: NON-JSON ({type(e).__name__}) first 60B: {b[:60]!r}")
        return None
    keys = list(j.keys()) if isinstance(j, dict) else f"<list len={len(j)}>"
    tsf = {}
    if isinstance(j, dict):
        for k in ("ts", "generated_at", "updated_at", "time", "date"):
            if k in j:
                tsf[k] = j[k]
        for k in ("history", "launches", "transitions", "rounds", "ledger"):
            if k in j:
                v = j[k]
                tsf[f"{k}_len"] = len(v) if isinstance(v, (list, dict)) else "?"
        if "last_tick" in j and isinstance(j["last_tick"], dict):
            tsf["last_tick.ts"] = j["last_tick"].get("ts")
    print(f"  {label}: keys={keys} ts_fields={tsf}")
    return j

for p in UU:
    print("==", p)
    b2, b3 = side(p, 2), side(p, 3)
    if p.endswith(".md"):
        l2 = b2.decode("utf-8", errors="replace").splitlines()
        l3 = b3.decode("utf-8", errors="replace").splitlines()
        print(f"  ours lines={len(l2)} tail={l2[-1][:80]!r}")
        print(f"  theirs lines={len(l3)} tail={l3[-1][:80]!r}")
        o2, o3 = set(l2), set(l3)
        print(f"  only-in-ours={len(l2)-len(o2&o3)} only-in-theirs={len(l3)-len(o2&o3)}")
    elif p.endswith(".js"):
        h2, h3 = b2[:80], b3[:80]
        import re
        t2 = re.search(rb"generated_at[\"':\s]+([\d\-T:. ]+)", b2)
        t3 = re.search(rb"generated_at[\"':\s]+([\d\-T:. ]+)", b3)
        print(f"  ours bytes={len(b2)} gen_at={t2.group(1) if t2 else '?'} head={h2[:50]!r}")
        print(f"  theirs bytes={len(b3)} gen_at={t3.group(1) if t3 else '?'} head={h3[:50]!r}")
    else:
        probe_json(b2, "ours")
        probe_json(b3, "theirs")
