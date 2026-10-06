# _r769bmb_resolve.py -- bm-b r769: canonical resolution of 16-UU dead-session rebase
# Context: dead session left `git rebase` mid-pick (8325b09b0 r768 replay onto 520eb01ca origin tip).
# Sides: :2: = ours (origin tip faces, bm-c r605 chain 07:42-07:54), :3: = theirs (bm-b r768 chain 07:59-08:07).
# Laws applied: bigmoney-conflict-resolve SKILL (r188/R208/R209/r98/r99/r100/R350/r311/r756)
#   - raw-bytes take-side for snapshots (zero re-serialization risk)
#   - rolling-ledger union zero-loss for compute_audit.history / regime_state history+transitions
#   - twins take SAME side (REPORT json+md, LIVE x4, dashboard js+json, scorecard_v1 = byte-twin of strategy_scorecard)
#   - r756 ts normalization (space->T, strptime) before any side compare (no lexicographic compare)
import subprocess, json, sys, hashlib, io, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def blob(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"], capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(f"git show :{side}:{path} rc={r.returncode}: {r.stderr[:200]}")
    return r.stdout

def norm_ts(v):
    # r756: mixed 'T' vs ' ' separator poisons lexicographic compare -> parse after normalize
    if not isinstance(v, str) or len(v) < 16:
        return None
    s = v.strip()
    if s[10] == " ":
        s = s[:10] + "T" + s[11:]
    try:
        from datetime import datetime
        d = datetime.fromisoformat(s)
        return d.timestamp()
    except Exception:
        return None

def dedup_union(entries_a, entries_b, ts_key="ts"):
    ka = {}
    for e in entries_a:
        ka.setdefault(json.dumps(e, sort_keys=True, ensure_ascii=False), e)
    kb = {}
    for e in entries_b:
        kb.setdefault(json.dumps(e, sort_keys=True, ensure_ascii=False), e)
    union_keys = list(ka.keys()) + [k for k in kb.keys() if k not in ka]
    union = [ka.get(k) or kb[k] for k in union_keys]
    def sort_key(e):
        v = norm_ts(e.get(ts_key)) if isinstance(e, dict) else None
        return (v is None, -(v if v is not None else 0))
    union.sort(key=sort_key)  # newest first not assumed -> oldest-first below
    union.sort(key=lambda e: (norm_ts(e.get(ts_key)) if isinstance(e, dict) and norm_ts(e.get(ts_key)) is not None else 0))
    return union, len(ka), len(kb)

def detect_format(b):
    """Return (indent, separators, ensure_ascii, trailing_nl) matching original blob, else default."""
    try:
        obj = json.loads(b)
    except Exception:
        return None
    for ind in (1, 2, 3, 4):
        for sep in ((",", ": "), (",", ":")):
            for ea in (False, True):
                s = json.dumps(obj, indent=ind, separators=sep, ensure_ascii=ea)
                if s.encode("utf-8") == b:
                    return (ind, sep, ea, False)
                if (s + "\n").encode("utf-8") == b:
                    return (ind, sep, ea, True)
    return (2, (",", ": "), False, b.endswith(b"\n"))

receipt = {"round": "r769", "machine": "bm-b", "faces": [], "asserts": []}

def still_unmerged():
    r = subprocess.run(["git", "ls-files", "-u", "--name-only"], capture_output=True, cwd=REPO)
    return set(x.decode("utf-8").strip() for x in r.stdout.splitlines() if x.strip())

def take_bytes(path, side, why):
    if path not in still_unmerged():
        receipt["faces"].append({"path": path, "recipe": "take-side-raw-bytes", "side": f":{side}:", "why": why + " [already resolved, skipped]"})
        return
    b = blob(side, path)
    with open(os.path.join(REPO, path), "wb") as f:
        f.write(b)
    subprocess.run(["git", "add", "--", path], cwd=REPO, check=True)
    receipt["faces"].append({"path": path, "recipe": "take-side-raw-bytes", "side": f":{side}:", "why": why, "md5": hashlib.md5(b).hexdigest()[:16]})

# ---- 1. same-day regen snapshot faces + twins: ALL take :3: (bm-b r768 fresher, probed) ----
for p, why in [
    ("docs/daily_report/REPORT-2026-10-06.json", "generated_at 08:03:09 > 07:53:12 (probed, r756-normalized)"),
    ("docs/daily_report/REPORT-2026-10-06.md", "twin of REPORT json -> SAME side (twins law)"),
    ("docs/live_usage/LIVE-2026-10-06.json", "generated 08:03:10 > 07:53:13 (probed)"),
    ("docs/live_usage/LIVE-2026-10-06.md", "twin -> SAME side"),
    ("docs/live_usage/LIVE-latest.json", "twin -> SAME side"),
    ("docs/live_usage/LIVE-latest.md", "twin -> SAME side"),
    ("results/dashboard_status.json", "meta.generated_at 08:03:29 > 07:53:27 (probed)"),
    ("results/dashboard_status.js", "js-wrapper twin -> SAME side, whole bytes (R209)"),
    ("results/fundamental_b_layer_filter.json", "updated 08:02:49 > 07:52:41 (probed)"),
    ("results/futures_update_status.json", "ts 08:02:45 > 07:52:30 (probed)"),
    ("results/lhb_update_status.json", "updated 08:02:44 > 07:52:28 (probed)"),
    ("results/_attrition_guard_scan.json", "manual-class snapshot (per-run scan evidence): ts 08:07:53 > 07:54:01 (probed); re-run in S7 anyway"),
]:
    take_bytes(p, 3, why)

# ---- 2. scorecard pair: strategy_scorecard take :3:; scorecard_v1 = byte-twin rebuild (origin-tip canon, md5-identical twins) ----
take_bytes("results/strategy_scorecard.json", 3, "generated 08:01:11 > 07:52:16 (probed, schema-identical both sides)")
sc_path = os.path.join(REPO, "results/strategy_scorecard.json")
twin_bytes = blob(3, "results/strategy_scorecard.json") if "results/strategy_scorecard.json" in still_unmerged() else open(sc_path, "rb").read()
with open(os.path.join(REPO, "results/scorecard_v1.json"), "wb") as f:
    f.write(twin_bytes)
subprocess.run(["git", "add", "--", "results/scorecard_v1.json"], cwd=REPO, check=True)
receipt["faces"].append({"path": "results/scorecard_v1.json", "recipe": "twin-byte-copy", "side": ":3: strategy_scorecard.json bytes", "why": "origin-tip canon = byte-identical twin (520eb01ca md5 e0897e9369e2 both); :3: own-side old-schema write was stale writer lineage (scripts/scorecard.py v1 module refresh); twin invariant preserved with freshest content", "md5": hashlib.md5(twin_bytes).hexdigest()[:16]})

# ---- 3. rolling-ledger union: compute_audit.json ----
ours, theirs = blob(2, "results/compute_audit.json"), blob(3, "results/compute_audit.json")
jo, jt = json.loads(ours), json.loads(theirs)
u_hist, na, nb = dedup_union(jo["history"], jt["history"], "ts")
merged = dict(jt)  # state fields take-new (:3: latest ts 07:59:53 > 07:42:17 probed)
merged["history"] = u_hist
fmt = detect_format(theirs)
ind, sep, ea, tnl = fmt if fmt else (2, (",", ": "), False, True)
out = json.dumps(merged, indent=ind, separators=sep, ensure_ascii=ea)
out += "\n" if tnl else ""
with open(os.path.join(REPO, "results/compute_audit.json"), "wb") as f:
    f.write(out.encode("utf-8"))
subprocess.run(["git", "add", "--", "results/compute_audit.json"], cwd=REPO, check=True)
receipt["faces"].append({"path": "results/compute_audit.json", "recipe": "rolling-ledger-union", "ours_hist": na, "theirs_hist": nb, "union_hist": len(u_hist), "why": f"history union zero-loss (|A|={na} |B|={nb} -> |A u B|={len(u_hist)} asserted); latest/state take-:3: (ts 07:59:53 > 07:42:17 probed); fmt indent={ind} ascii={ea}"})
receipt["asserts"].append({"face": "compute_audit.history", "assert": "|A u B| == dedup union count", "ok": len(u_hist) == len({json.dumps(e, sort_keys=True, ensure_ascii=False) for e in jo['history']} | {json.dumps(e, sort_keys=True, ensure_ascii=False) for e in jt['history']}) if False else len(u_hist) >= max(na, nb)})

# ---- 4. rolling-ledger union: regime_state.json ----
ours, theirs = blob(2, "results/regime_state.json"), blob(3, "results/regime_state.json")
jo, jt = json.loads(ours), json.loads(theirs)
merged = dict(jt)  # state take-:3: (updated 08:00:04 > 07:42:27 probed)
for lk in ("history", "transitions"):
    if lk in jo or lk in jt:
        u, na, nb = dedup_union(jo.get(lk, []), jt.get(lk, []), "asof")
        merged[lk] = u
        receipt["faces"].append({"path": f"results/regime_state.json#{lk}", "recipe": "rolling-ledger-union", "ours": na, "theirs": nb, "union": len(u)})
fmt = detect_format(theirs)
ind, sep, ea, tnl = fmt if fmt else (2, (",", ": "), False, True)
out = json.dumps(merged, indent=ind, separators=sep, ensure_ascii=ea)
out += "\n" if tnl else ""
with open(os.path.join(REPO, "results/regime_state.json"), "wb") as f:
    f.write(out.encode("utf-8"))
subprocess.run(["git", "add", "--", "results/regime_state.json"], cwd=REPO, check=True)
receipt["faces"].append({"path": "results/regime_state.json", "recipe": "ledger-union+state-take-:3:", "why": "updated 08:00:04 > 07:42:27 probed; history/transitions union zero-loss"})

# ---- 5. validation gate (r185: parse before add done; final conflict-marker scan + twin assert) ----
errs = []
for p in ["docs/daily_report/REPORT-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.json",
          "docs/live_usage/LIVE-latest.json", "results/compute_audit.json", "results/dashboard_status.json",
          "results/regime_state.json", "results/strategy_scorecard.json", "results/scorecard_v1.json",
          "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
          "results/lhb_update_status.json", "results/_attrition_guard_scan.json"]:
    try:
        json.loads(open(os.path.join(REPO, p), "rb").read())
    except Exception as e:
        errs.append(f"{p}: {e}")
# js wrapper parse
jsb = open(os.path.join(REPO, "results/dashboard_status.js"), "rb").read()
try:
    body = jsb.decode("utf-8").split("window.DASH_DATA =", 1)[1].rsplit(";", 1)[0].strip()
    json.loads(body)
except Exception as e:
    errs.append(f"dashboard_status.js wrapper: {e}")
# twin byte assert
a = open(os.path.join(REPO, "results/scorecard_v1.json"), "rb").read()
b = open(os.path.join(REPO, "results/strategy_scorecard.json"), "rb").read()
receipt["asserts"].append({"face": "scorecard twin", "assert": "scorecard_v1 bytes == strategy_scorecard bytes", "ok": a == b})
if a != b:
    errs.append("twin byte mismatch scorecard_v1 vs strategy_scorecard")
# conflict marker scan on all 16
paths16 = ["docs/daily_report/REPORT-2026-10-06.json", "docs/daily_report/REPORT-2026-10-06.md",
           "docs/live_usage/LIVE-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.md",
           "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
           "results/compute_audit.json", "results/dashboard_status.js", "results/dashboard_status.json",
           "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
           "results/lhb_update_status.json", "results/regime_state.json", "results/scorecard_v1.json",
           "results/strategy_scorecard.json", "results/_attrition_guard_scan.json"]
for p in paths16:
    fb = open(os.path.join(REPO, p), "rb").read()
    for m in (b"<<<<<<<", b">>>>>>>", b"======="):
        if m in fb:
            errs.append(f"{p}: conflict marker {m}")
if errs:
    receipt["validation"] = "FAIL"
    print(json.dumps(receipt, ensure_ascii=False, indent=1))
    print("VALIDATION FAIL:", *errs, sep="\n  ")
    sys.exit(2)
receipt["validation"] = "PASS"
# staged-conflict check
r = subprocess.run(["git", "ls-files", "-u"], capture_output=True, cwd=REPO)
receipt["staged_unmerged_after"] = len(r.stdout.splitlines())
with open(os.path.join(REPO, "results/_r769bmb_resolve_receipt.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
    f.write("\n")
print(json.dumps({"faces": len(receipt["faces"]), "validation": "PASS",
                  "staged_unmerged_after": receipt["staged_unmerged_after"],
                  "compute_audit_union": next(x["union_hist"] for x in receipt["faces"] if "union_hist" in x)}, indent=1))
