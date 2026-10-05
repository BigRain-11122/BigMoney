# r764 bm-b merge resolver: 18 UU faces per canonical recipes (skill + r758/r759 lineage)
# recipes: rolling-ledger union (compute_audit/regime_state), snapshot take-new by ts,
# js-wrapper take-side whole bytes + twins same-side bound (r708), token per-key union.
import subprocess, json, io, sys

def stage(n, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("stage read fail %s: %s" % (path, r.stderr.decode()[:100]))
    return r.stdout

def jload(b):
    return json.loads(b.decode("utf-8", "replace"))

receipt = {"round": 764, "machine": "bm-b", "faces": {}, "asserts": []}

def take_side(path, side, note):
    """whole-bytes take-side + add"""
    b = stage(2 if side == "ours" else 3, path)
    open(path, "wb").write(b)
    subprocess.run(["git", "add", "--", path], check=True)
    receipt["faces"][path] = {"recipe": "take-side", "side": side, "note": note, "bytes": len(b)}

def resolve_json(path, builder, note):
    o, t = stage(2, path), stage(3, path)
    od, td = jload(o), jload(t)
    merged = builder(od, td)
    blob = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
    open(path, "wb").write(blob)
    json.loads(open(path, encoding="utf-8").read())  # parse-validate before add (r185 law)
    subprocess.run(["git", "add", "--", path], check=True)
    receipt["faces"][path] = {"recipe": "json-merge", "note": note}

# ---- 1. compute_audit.json: history union by content identity + latest take-new by ts ----
def build_compute_audit(od, td):
    seen, hist = set(), []
    for row in td["history"] + od["history"]:
        k = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            hist.append(row)
    hist.sort(key=lambda r: r.get("ts", ""))
    latest = od["latest"] if od["latest"].get("ts", "") >= td["latest"].get("ts", "") else td["latest"]
    receipt["faces"]["results/compute_audit.json"] = {"recipe": "rolling-union",
        "ours_hist": len(od["history"]), "theirs_hist": len(td["history"]),
        "union_hist": len(hist), "latest_side": "ours" if latest is od["latest"] else "theirs",
        "latest_ts": latest.get("ts")}
    return {"latest": latest, "history": hist}
resolve_json("results/compute_audit.json", build_compute_audit, "r188/R208 rolling union")

# ---- 2. regime_state.json: transitions union + take-new state fields by updated ----
def build_regime(od, td):
    seen, tr = set(), []
    for row in td["transitions"] + od["transitions"]:
        k = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            tr.append(row)
    tr.sort(key=lambda r: r.get("asof", ""))
    base = od if od.get("updated", "") >= td.get("updated", "") else td
    out = dict(base)
    out["transitions"] = tr
    receipt["faces"]["results/regime_state.json"] = {"recipe": "rolling-union",
        "base_side": "ours" if base is od else "theirs", "updated": base.get("updated"),
        "ours_tr": len(od["transitions"]), "theirs_tr": len(td["transitions"]), "union_tr": len(tr)}
    return out
resolve_json("results/regime_state.json", build_regime, "r188/R208 rolling union")

# ---- 3. token_usage.json: top-level from newer generated + machines per-key union ----
def build_token(od, td):
    base = od if od.get("generated", "") >= td.get("generated", "") else td
    other = td if base is od else od
    out = dict(base)
    mm = {}
    for k in set(base.get("machines", {})) | set(other.get("machines", {})):
        b, o = base.get("machines", {}).get(k), other.get("machines", {}).get(k)
        if b is None:
            mm[k] = o
        elif o is None:
            mm[k] = b
        else:
            # per-key max-union: keep side with larger cumulative bytes-ish value (r759 receipt precedent)
            def val(x):
                if isinstance(x, dict):
                    for kk in ("total_bytes", "bytes", "est_tokens", "tokens", "value"):
                        if kk in x:
                            return x[kk]
                    return sum(v for v in x.values() if isinstance(v, (int, float)))
                return x if isinstance(x, (int, float)) else 0
            mm[k] = b if val(b) >= val(o) else o
    out["machines"] = mm
    receipt["faces"]["results/token_usage.json"]["machines_pick"] = {k: ("base" if mm[k] in base.get("machines", {}).values() else "other") for k in mm}
    return out
receipt["faces"]["results/token_usage.json"] = {"recipe": "per-key-max-union",
    "ours_generated": "2026-10-06 06:04:29", "theirs_generated": "2026-10-06 05:53:42", "base_side": "ours"}
resolve_json("results/token_usage.json", build_token, "r759 per-key max-union")

# ---- 4. pure snapshots: take-new by embedded ts ----
def newer_side(od, td, *keys):
    def mx(d):
        return max((d.get(k) or "") for k in keys)
    return "ours" if mx(od) >= mx(td) else "theirs"

SNAP = [
    ("results/fundamental_b_layer_filter.json", ("updated",), "R216 take-new by updated"),
    ("results/futures_update_status.json", ("ts",), "R208 take-new by ts"),
    ("results/lhb_update_status.json", ("updated",), "R208 take-new by updated"),
    ("results/update_status.json", ("updated",), "R208 take-new by updated"),
    ("results/_attrition_guard_scan.json", ("ts",), "latest-scan take-new by ts"),
]
for path, keys, note in SNAP:
    od, td = jload(stage(2, path)), jload(stage(3, path))
    take_side(path, newer_side(od, td, *keys), note + " (ts ours=%s theirs=%s)" % (
        max((od.get(k) or "") for k in keys), max((td.get(k) or "") for k in keys)))

# ---- 5. scorecard pair: THEIRS newer (05:44 > 05:41/05:42) same-side bound ----
for path in ("results/scorecard_v1.json", "results/strategy_scorecard.json"):
    od, td = jload(stage(2, path)), jload(stage(3, path))
    side = newer_side(od, td, "generated", "ts", "updated")
    take_side(path, side, "take-new by generated (ours 05:41:47/05:42:02 theirs 05:44:38/05:44:44) same-side pair")

# ---- 6. dashboard_status.json: no top-level ts -> probe inner ts; js twin same side whole bytes ----
od, td = jload(stage(2, "results/dashboard_status.json")), jload(stage(3, "results/dashboard_status.json"))
def deep_ts(d):
    best = ""
    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("ts", "generated", "updated", "asof", "generated_at") and isinstance(v, str):
                    best = max(best, v)
                walk(v)
        elif isinstance(x, list):
            for v in x[:50]:
                walk(v)
    walk(d)
    return best
ots, tts = deep_ts(od), deep_ts(td)
dside = "ours" if ots >= tts else "theirs"
take_side("results/dashboard_status.json", dside, "deep-ts take-new (ours=%s theirs=%s)" % (ots or "?", tts or "?"))
take_side("results/dashboard_status.js", dside, "js-wrapper take-side whole bytes, same side as .json twin (R209/r708)")
ojs = stage(2 if dside == "ours" else 3, "results/dashboard_status.js")
receipt["asserts"].append({"js_wrapper_format": ojs.startswith(b"window.DASH_DATA")})

# ---- 7. daily report + live usage families: take-new by generated + md twins same side ----
for j, keys in (("docs/daily_report/REPORT-2026-10-06.json", ("generated_at", "generated")),
                ("docs/live_usage/LIVE-2026-10-06.json", ("generated",)),
                ("docs/live_usage/LIVE-latest.json", ("generated",))):
    od, td = jload(stage(2, j)), jload(stage(3, j))
    side = newer_side(od, td, *keys)
    take_side(j, side, "take-new by generated + twins same-side")
    md = j[:-5] + ".md" if j.endswith(".json") else None
    if md:
        take_side(md, side, "md twin same-side bound (r708)")

# ---- 8. REPORT-2026-10-06.md twin (json already handled above) ----
# handled by pair loop above

# ---- final asserts: zero conflict markers across resolved faces ----
bad = []
for p in receipt["faces"]:
    b = open(p, "rb").read()
    if b"<<<<<<<" in b or b">>>>>>>" in b:
        bad.append(p)
receipt["asserts"].append({"conflict_marker_scan": bad, "clean": not bad})
receipt["face_count"] = len(receipt["faces"])
json.dump(receipt, open("results/_r764bmb_merge_resolve.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("resolved faces:", len(receipt["faces"]))
print("compute_audit:", json.dumps(receipt["faces"]["results/compute_audit.json"], ensure_ascii=False))
print("regime:", json.dumps(receipt["faces"]["results/regime_state.json"], ensure_ascii=False))
print("scorecard side:", receipt["faces"]["results/scorecard_v1.json"]["side"], "| dashboard side:", dside, "(ours=%s theirs=%s)" % (ots or "?", tts or "?"))
print("marker scan clean:", not bad)
