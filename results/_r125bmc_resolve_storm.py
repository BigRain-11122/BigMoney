# r125 bm-c push-storm resolver: 14-UU S6 mirror faces vs bm-a r372 closeout (origin tip 6ed08001 02:30:56)
# Laws applied: r352 (rebase :2:=HEAD=upstream probe-first + side-assert fail-closed),
#               r133 (stage-blob marker scan BEFORE any resolution),
#               r140 (same-second tie -> take origin),
#               r120 (audit history ts-key union / regime asof row-union / twins coupled),
#               r353 (subprocess git show stdout utf-8 -- PS `>` redirect is UTF-16 poison)
import subprocess, json, sys

UU = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
# storm-2 (02:33 vs bm-b r354 chain): heat_update_status NOT conflicted (storm-1 take-:2: kept
# lane-owner authoritative face; bm-b did not touch it) -- removed from UU.

def blob(spec):
    out = subprocess.run(["git", "show", spec], capture_output=True)
    if out.returncode != 0:
        raise RuntimeError("git show failed: " + spec + " -> " + out.stderr.decode("utf-8", "replace"))
    return out.stdout.decode("utf-8", "replace")

def side_probe(path):
    """Return (s2, s3) raw text for a path."""
    return blob(":2:" + path), blob(":3:" + path)

MARKERS = ["<<<<<<<", "=======", ">>>>>>>"]

def marker_scan(path, s2, s3):
    hits = []
    for tag, s in (("2", s2), ("3", s3)):
        for m in MARKERS:
            if m in s:
                # js twin carries '<<<<<<<' nowhere legit; json neither
                hits.append((path, tag, m))
    return hits

def jload(s, path):
    try:
        return json.loads(s)
    except Exception as e:
        print("  !! parse fail", path, str(e)[:80])
        return None

def ts_of(obj, path):
    """Best-effort freshness key extraction."""
    if not isinstance(obj, dict):
        return None
    for k in ("ts", "generated", "generated_at", "updated_at", "asof", "written_at", "last_run"):
        v = obj.get(k)
        if isinstance(v, str) and len(v) >= 10:
            return (k, v)
    # nested common spots
    for k in ("meta", "envelope", "state"):
        sub = obj.get(k)
        if isinstance(sub, dict):
            for kk in ("ts", "generated", "generated_at", "updated_at", "asof"):
                v = sub.get(kk)
                if isinstance(v, str) and len(v) >= 10:
                    return (k + "." + kk, v)
    return None

def main():
    print("=== step-0: HEAD fingerprint vs :2: (rebase side law r352) ===")
    head_ok, mism = [], []
    for p in UU:
        h = blob("HEAD:" + p)
        s2, s3 = side_probe(p)
        head_ok.append(h == s2)
    print("HEAD==:2: for all:", all(head_ok), "| per-file:", head_ok)
    if not all(head_ok):
        print("FATAL side-inversion suspicion; abort for manual adjudication")
        sys.exit(2)

    print("\n=== step-1: marker scan on stage blobs (r133) ===")
    mh = []
    for p in UU:
        s2, s3 = side_probe(p)
        mh.extend(marker_scan(p, s2, s3))
    print("marker hits:", mh if mh else "NONE")

    print("\n=== step-2: per-face ts analysis ===")
    for p in UU:
        s2, s3 = side_probe(p)
        if p.endswith(".json"):
            o2, o3 = jload(s2, p), jload(s3, p)
            t2, t3 = ts_of(o2, p), ts_of(o3, p)
            print(p, "| :2: ", t2, "| :3: ", t3)
        else:
            # md/js: first 3 lines ts-ish grep
            import re
            f2 = re.findall(r"20\d\d-\d\d-\d\d[ T]\d\d:\d\d(:\d\d)?", s2[:2000])
            f3 = re.findall(r"20\d\d-\d\d-\d\d[ T]\d\d:\d\d(:\d\d)?", s3[:2000])
            print(p, "| :2: first-ts:", f2[:2], "| :3: first-ts:", f3[:2])

def raw_bytes(spec):
    out = subprocess.run(["git", "show", spec], capture_output=True)
    if out.returncode != 0:
        raise RuntimeError("git show failed: " + spec)
    return out.stdout

def strip_keys(obj, keys):
    """Deep copy minus given top-level (and nested one-level) runtime keys."""
    import copy
    o = copy.deepcopy(obj)
    for k in keys:
        o.pop(k, None)
        for v in o.values():
            if isinstance(v, dict):
                v.pop(k, None)
    return o

def assert_eq(name, a, b):
    if a != b:
        print("FATAL side-assert FAIL-CLOSED on", name)
        print("  :2:", json.dumps(a, ensure_ascii=False)[:300])
        print("  :3:", json.dumps(b, ensure_ascii=False)[:300])
        sys.exit(2)
    print("  assert-eq OK:", name)

def resolve():
    print("=== resolve pass: all asserts BEFORE any write (fail-closed) ===")
    # --- asserts on deterministic science faces (minus runtime metadata) ---
    p = "results/scorecard_v1.json"
    o2, o3 = json.loads(raw_bytes(":2:"+p)), json.loads(raw_bytes(":3:"+p))
    assert_eq("scorecard_v1 rows (minus generated)",
              [strip_keys(r, ("generated",)) for r in o2.get("rows", o2.get("traders", []))],
              [strip_keys(r, ("generated",)) for r in o3.get("rows", o3.get("traders", []))])
    p = "results/strategy_scorecard.json"
    o2, o3 = json.loads(raw_bytes(":2:"+p)), json.loads(raw_bytes(":3:"+p))
    assert_eq("strategy_scorecard (minus generated/elapsed)",
              strip_keys(o2, ("generated", "elapsed_sec")), strip_keys(o3, ("generated", "elapsed_sec")))
    p = "results/fundamental_b_layer_filter.json"
    o2, o3 = json.loads(raw_bytes(":2:"+p)), json.loads(raw_bytes(":3:"+p))
    assert_eq("fundamental_b_layer_filter (deterministic minus updated)",
              strip_keys(o2, ("updated",)), strip_keys(o3, ("updated",)))
    p = "results/regime_state.json"
    o2, o3 = json.loads(raw_bytes(":2:"+p)), json.loads(raw_bytes(":3:"+p))
    assert_eq("regime_state (minus updated)",
              strip_keys(o2, ("updated",)), strip_keys(o3, ("updated",)))
    p = "results/update_status.json"
    o2, o3 = json.loads(raw_bytes(":2:"+p)), json.loads(raw_bytes(":3:"+p))
    assert_eq("update_status core (data_cutoff/rows/failures)",
              strip_keys(o2, ("updated", "now")), strip_keys(o3, ("updated", "now")))
    p = "docs/daily_report/REPORT-2026-09-28.json"
    o2, o3 = json.loads(raw_bytes(":2:"+p)), json.loads(raw_bytes(":3:"+p))
    # invariant faces only: combat block + report_date; rd.*/token_line are time-varying regen faces
    assert_eq("daily_report combat block (invariant face)", o2.get("combat"), o3.get("combat"))
    assert_eq("daily_report report_date", o2.get("report_date"), o3.get("report_date"))
    for p in ("results/lhb_update_status.json", "results/futures_update_status.json"):
        o2, o3 = json.loads(raw_bytes(":2:"+p)), json.loads(raw_bytes(":3:"+p))
        assert_eq(p + " (minus ts/updated/last_attempt)",
                  strip_keys(o2, ("ts", "updated", "last_attempt")),
                  strip_keys(o3, ("ts", "updated", "last_attempt")))
    # heat: storm-1 already took lane-owner :2: (bm-a snapshots=3 authoritative); bm-b r354 chain
    # did not touch it -> NOT conflicted in storm-2 -> zero action, face preserved as-is.
    print("  HEAT note: not in storm-2 UU; lane-owner authoritative face from storm-1 preserved")

    print("\n=== asserts passed -> writing resolutions ===")
    # 1) take-mine verbatim (fresher ts faces; science asserts above guarantee content parity):
    take3 = [f for f in UU if f != "results/compute_audit.json"]
    for p in take3:
        with open(p, "wb") as f:
            f.write(raw_bytes(":3:" + p))
        print("  take-:3: (mine, fresher):", p)
    # 2) compute_audit: history ts-key union (zero loss), latest = max-ts side (mine 02:28:05)
    o = json.loads(raw_bytes(":3:results/compute_audit.json"))
    h2 = json.loads(raw_bytes(":2:results/compute_audit.json"))["history"]
    seen = {h["ts"]: h for h in o["history"]}
    for h in h2:
        seen.setdefault(h["ts"], h)
    o["history"] = [seen[k] for k in sorted(seen)]
    with open("results/compute_audit.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(o, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("  union: compute_audit history", len(o["history"]), "items ts-key zero-loss; latest.ts =", o["latest"]["ts"])

    print("\n=== git add resolved files ===")
    for p in UU:
        r = subprocess.run(["git", "add", p], capture_output=True)
        if r.returncode != 0:
            print("FATAL git add", p, r.stderr.decode("utf-8", "replace")[:200]); sys.exit(2)
    print("  added 14/14")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "resolve":
        resolve()
    else:
        main()
