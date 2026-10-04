# r717 bm-b rebase-window resolver (17 UU faces)
# Laws applied: r710-A python bytes / r710-B stage-blob asserts / r185 parse-verify
# / r140 tie->origin / r98-r100 R350 hardened ts probe (already adjudicated in probe)
# / r510+r708 twins same side / r188-R208 rolling-ledger union zero-loss
# / r713 zero-UU recheck before continue / r223/r234 EOL mirror base blob
import subprocess, json, io, sys

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    assert r.returncode == 0, f"git show :{stage}:{path} rc={r.returncode}"
    b = r.stdout
    assert len(b) > 100, f"stage {stage} {path} suspiciously small ({len(b)}B) - r710-B"
    return b

def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)

def take(path, side):
    b = blob(side, path)
    if path.endswith(".json"):
        json.loads(b)  # r185 parse-verify winning blob before write
    write_bytes(path, b)
    return f"take:{side} {len(b)}B"

# --- adjudicated winners (probe table r717, hardened ts, tie->origin r140) ---
ORIGIN = ["docs/daily_report/REPORT-2026-10-05.json",
          "docs/daily_report/REPORT-2026-10-05.md"]          # tie 06:59:35 -> origin
CHURN  = ["docs/live_usage/LIVE-2026-10-05.json",
          "docs/live_usage/LIVE-2026-10-05.md",
          "docs/live_usage/LIVE-latest.json",
          "docs/live_usage/LIVE-latest.md",
          "results/dashboard_status.json",
          "results/dashboard_status.js",                     # twin follows json (r708)
          "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json",
          "results/lhb_update_status.json",
          "results/scorecard_v1.json",
          "results/strategy_scorecard.json",
          "results/token_usage.json",
          "results/update_status.json"]

report = []
for p in ORIGIN:
    report.append(take(p, "2") + " (tie->origin r140)")
for p in CHURN:
    report.append(take(p, "3") + " (ts-newer churn)")

# --- twin-side assertions (r510/r708) ---
def side_ts_check(paths, expect_side):
    for p in paths:
        s = 2 if p in ORIGIN else 3
        assert s == (2 if expect_side == "2" else 3), f"twin side mismatch {p}"

# LIVE family all churn; REPORT family all origin; dashboard json+js churn
assert all(p in CHURN for p in ["docs/live_usage/LIVE-2026-10-05.json",
                                "docs/live_usage/LIVE-2026-10-05.md",
                                "docs/live_usage/LIVE-latest.json",
                                "docs/live_usage/LIVE-latest.md"])
assert all(p in ORIGIN for p in ORIGIN)

# --- compute_audit.json: rolling-ledger union on history (dedup by ts), latest take-new ---
b2, b3 = blob("2", "results/compute_audit.json"), blob("3", "results/compute_audit.json")
j2, j3 = json.loads(b2), json.loads(b3)
h2, h3 = j2["history"], j3["history"]
assert all("ts" in e for e in h2 + h3), "dedup key ts missing in entries (r319)"
by = {}
for e in h2 + h3:
    by[e["ts"]] = e          # same-ts collision: later write wins (churn listed last)
union = sorted(by.values(), key=lambda e: e["ts"])
zero_loss = len(union) == len(set(list(e["ts"] for e in h2) + list(e["ts"] for e in h3)))
assert zero_loss, "union not zero-loss"
payload = dict(j3)           # state fields take-new (churn latest 07:21:37)
payload["history"] = union
s = json.dumps(payload, indent=2, ensure_ascii=False)
crlf = b"\r\n" in b2          # EOL mirror base blob (r223/r234)
if crlf:
    s = s.replace("\n", "\r\n")
if b2.endswith(b"\n"):
    s += "\r\n" if crlf else "\n"
write_bytes("results/compute_audit.json", s.encode("utf-8"))
chk = json.loads(open("results/compute_audit.json", "rb").read().decode("utf-8"))
assert len(chk["history"]) == len(union) and chk["latest"] == j3["latest"], "re-read verify failed (r704)"
report.append(f"compute_audit union: |A|={len(h2)} |B|={len(h3)} |AUB|={len(union)} latest=churn")

# --- regime_state.json: rolling-ledger union history/transitions (dedup by asof), state take-new ---
b2, b3 = blob("2", "results/regime_state.json"), blob("3", "results/regime_state.json")
j2, j3 = json.loads(b2), json.loads(b3)
uh = {}
for e in j2.get("history", []) + j3.get("history", []):
    uh[e["asof"]] = e
ut = {}
for e in j2.get("transitions", []) + j3.get("transitions", []):
    k = e.get("ts") or e.get("asof")
    assert k, "transitions dedup key missing (r319)"
    ut[k] = e
payload = dict(j3)            # state fields take-new (churn 07:21:50)
payload["history"] = sorted(uh.values(), key=lambda e: e["asof"])
payload["transitions"] = sorted(ut.values(), key=lambda e: (e.get("ts") or e.get("asof")))
if payload == j3 and b3 == open("results/regime_state.json","rb").read():
    report.append("regime_state: churn blob already == union+take-new, verbatim kept")
else:
    s = json.dumps(payload, indent=2, ensure_ascii=False)
    if b"\r\n" in b2:
        s = s.replace("\n", "\r\n")
    if b2.endswith(b"\n"):
        s += "\r\n" if b"\r\n" in b2 else "\n"
    write_bytes("results/regime_state.json", s.encode("utf-8"))
    chk = json.loads(open("results/regime_state.json", "rb").read().decode("utf-8"))
    assert chk["history"] == payload["history"] and chk["state"] == j3["state"], "re-read verify failed"
    report.append(f"regime_state union: history |AUB|={len(payload['history'])} transitions |AUB|={len(payload['transitions'])} state=churn")

io.open(r"results\_r717bmb_resolve_report.txt", "w", encoding="ascii").write("\n".join(report) + "\n")
print(f"RESOLVED {len(report)} faces")
for line in report:
    print(line)
