# r796 bm-b rebase c3 resolver (r794 canon recipe: per-face deep-ts newer-wins, tie->stage2 r140,
# compute_audit history values-union by ts; auto-detect winner per face at each rebase step)
import json, re, subprocess, sys

FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
]


def blob(stage, path):
    r = subprocess.run(["git", "show", ":%s:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("blob read fail %s %s: %s" % (stage, path, r.stderr.decode()[:200]))
    return r.stdout.decode("utf-8")


def jblob(stage, path):
    return json.loads(blob(stage, path))


def ts_of(path, text):
    d = json.loads(text)
    if path.endswith("compute_audit.json"):
        return d["latest"]["ts"]
    if path.endswith("regime_state.json"):
        return d["updated"]
    if path.endswith("_attrition_guard_scan.json"):
        return d["ts"]
    if path.endswith("dashboard_status.json"):
        return d["data"]["update"]["last_run"]
    if path.endswith("strategy_scorecard.json") or path.endswith("scorecard_v1.json"):
        return d["generated"]
    return ""


receipt = []
for path in FACES:
    if path.endswith("compute_audit.json"):
        s2, s3 = jblob(2, path), jblob(3, path)
        # history values-union by ts; on same-ts collision keep stage2 (origin-public side)
        by_ts = {}
        for row in s3["history"]:
            by_ts[row["ts"]] = row
        for row in s2["history"]:
            by_ts[row["ts"]] = row
        merged_hist = sorted(by_ts.values(), key=lambda r: r["ts"])
        newer = s2 if s2["latest"]["ts"] >= s3["latest"]["ts"] else s3
        merged = dict(newer)
        merged["history"] = merged_hist
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(merged, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        receipt.append("%s UNION latest=%s(hist s2=%d s3=%d -> %d)" %
                       (path, newer["latest"]["ts"], len(s2["history"]), len(s3["history"]), len(merged_hist)))
    elif path.endswith("dashboard_status.js"):
        # twin of dashboard_status.json (same generator run) -> follow the .json winner
        jtxt2, jtxt3 = blob(2, "results/dashboard_status.json"), blob(3, "results/dashboard_status.json")
        winner = 2 if ts_of("results/dashboard_status.json", jtxt2) >= ts_of("results/dashboard_status.json", jtxt3) else 3
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(blob(winner, path))
        receipt.append("%s TWIN->stage%d" % (path, winner))
    else:
        t2, t3 = ts_of(path, blob(2, path)), ts_of(path, blob(3, path))
        winner = 2 if t2 >= t3 else 3   # tie -> stage2 (r140 law)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(blob(winner, path))
        receipt.append("%s s2=%s s3=%s -> stage%d" % (path, t2, t3, winner))

print("C3 RESOLVER: " + " | ".join(receipt))
r = subprocess.run(["git", "add"] + FACES, capture_output=True)
if r.returncode != 0:
    raise SystemExit("git add fail: " + r.stderr.decode()[:300])
print("STAGED OK")
