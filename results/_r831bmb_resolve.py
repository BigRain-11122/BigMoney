"""r831 bm-b rebase-resolver: origin advanced (bm-a r952 T20 done) while dead
bm-b r831 attempt did same fix -> later-comer yields (fleet README S4).

Files & recipes (classify_conflicts.py + manual UNKNOWN adjudication):
- scripts/update_futures.py : take OURS (origin, bm-a lane-owner fix); verify
  fix markers present (it.get("p") + 11/11 selftest leg)
- state/queue/tech.md        : take OURS (bm-a done row; drop bm-b false
  yield-narrative row)
- results/compute_audit.json / regime_state.json : rolling-ledger = union
  list-valued keys (zero row loss), scalar fields take newer-ts side
- results/update_status.json / queue_head_collision_probe.json : snapshot
  take-new by doc ts
- results/scorecard_v1.json / strategy_scorecard.json : take OURS (host=bm-a
  single-writer guard faces)
Validation: json.loads every resolved json before writeback. Exit 0 ok / 2 fault.
"""
import json
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"


def blob(stage, path):
    r = subprocess.run(["git", "-C", ROOT, "show", ":%s:%s" % (stage, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git show :%s:%s rc=%s" % (stage, path, r.returncode))
    return r.stdout


def doc_ts(d):
    for k in ("ts", "generated", "asof", "generated_at", "updated", "probe_ts"):
        v = d.get(k) if isinstance(d, dict) else None
        if isinstance(v, str) and v:
            return k, v
    return None, None


def newer(d_ours, d_theirs):
    """True -> ours is newer (or tie -> ours per r140 same-second tie law)."""
    k1, t1 = doc_ts(d_ours)
    k2, t2 = doc_ts(d_theirs)
    if t1 and t2:
        return t1 >= t2
    if t1:
        return True
    return not t2


def union_ledgers(d_ours, d_theirs):
    out = {}
    for k in d_ours:
        ov, tv = d_ours.get(k), d_theirs.get(k)
        if isinstance(ov, list) and isinstance(tv, list):
            seen = {json.dumps(x, ensure_ascii=True, sort_keys=True) for x in ov}
            merged = list(ov)
            added = 0
            for x in tv:
                key = json.dumps(x, ensure_ascii=True, sort_keys=True)
                if key not in seen:
                    merged.append(x)
                    added += 1
            out[k] = merged
            print("  ledger %s: |ours|=%d +theirs_new=%d -> %d" %
                  (k, len(ov), added, len(merged)))
        else:
            out[k] = ov if newer(d_ours, d_theirs) else tv
    for k in d_theirs:
        if k not in out:
            out[k] = d_theirs[k]
    return out


def main():
    log = []
    # --- code + queue row: take OURS with marker verification
    ours_fut = blob(2, "scripts/update_futures.py")
    ok_fix = b'it.get("p")' in ours_fut or b'it["p"]' in ours_fut
    ok_test = b"11/11" in ours_fut
    print("update_futures.py OURS fix-marker=%s selftest11=%s" % (ok_fix, ok_test))
    if not (ok_fix and ok_test):
        print("FATAL: origin-side fix incomplete -> manual adjudication needed")
        return 2
    open(ROOT + r"\scripts\update_futures.py", "wb").write(ours_fut)
    ours_tech = blob(2, "state/queue/tech.md")
    if b"| done |" not in ours_tech or b"T20" not in ours_tech:
        print("FATAL: origin tech.md T20 done row missing")
        return 2
    open(ROOT + r"\state\queue\tech.md", "wb").write(ours_tech)
    log.append("take-ours: scripts/update_futures.py, state/queue/tech.md")

    # --- single-writer guard faces: take OURS (host=bm-a)
    for p in ("results/scorecard_v1.json", "results/strategy_scorecard.json"):
        b = blob(2, p)
        json.loads(b.decode("utf-8"))  # validate before writeback (r185)
        open(ROOT + "\\" + p.replace("/", "\\"), "wb").write(b)
        log.append("take-ours(guard host=bm-a): " + p)

    # --- rolling-ledger union faces
    for p in ("results/compute_audit.json", "results/regime_state.json"):
        o = json.loads(blob(2, p).decode("utf-8"))
        t = json.loads(blob(3, p).decode("utf-8"))
        merged = union_ledgers(o, t)
        json.loads(json.dumps(merged))  # roundtrip validation
        open(ROOT + "\\" + p.replace("/", "\\"), "w",
             encoding="utf-8", newline="").write(
            json.dumps(merged, ensure_ascii=True, indent=1) + "\n")
        log.append("union-ledger: " + p)

    # --- snapshot take-new by ts
    for p in ("results/update_status.json", "results/queue_head_collision_probe.json"):
        o = json.loads(blob(2, p).decode("utf-8"))
        t = json.loads(blob(3, p).decode("utf-8"))
        side, pick = ("ours", o) if newer(o, t) else ("theirs", t)
        open(ROOT + "\\" + p.replace("/", "\\"), "w",
             encoding="utf-8", newline="").write(
            json.dumps(pick, ensure_ascii=True, indent=1) + "\n")
        k1, t1 = doc_ts(o)
        k2, t2 = doc_ts(t)
        print("%s take-new=%s (ours %s=%s / theirs %s=%s)" % (p, side, k1, t1, k2, t2))
        log.append("take-new(%s): %s" % (side, p))

    json.dump({"round": "r831", "log": log}, open(
        ROOT + r"\results\_r831bmb_resolve_receipt.json", "w",
        encoding="utf-8"), ensure_ascii=True, indent=1)
    print("RESOLVED: %d entries" % len(log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
