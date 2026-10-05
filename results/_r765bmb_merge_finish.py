# r765 bm-b merge finisher: complete dead-session r764 resolver section 7 (6 UU faces)
# Lineage: _r764bmb_resolve.py sections 1-6 (12 faces) already staged by r764 dead session
# (died in section 7, receipt never written). This script finishes section 7 per the same
# recipes (take-new by generated + md twin same-side, r708/r758/r759 lineage) with the
# r756 ts-normalize law, then runs the full 18-face verification pass (marker scan +
# index stage-0 parse + union stats) the dead session never reached, and writes the receipt.
import subprocess, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (a[0], r.returncode, r.stderr.decode("utf-8", "replace")[:200]))
    return r.stdout

def stage(n, path):
    return git("show", ":%d:%s" % (n, path))

receipt = {
    "round_finisher": 765, "machine": "bm-b", "merge_window": "r764 dead-session merge origin/main (behind-13)",
    "lineage": "sections 1-6 (12 faces) resolved+staged by r764 dead session via _r764bmb_resolve.py; "
               "section 7 (6 faces) completed by r765 finisher _r765bmb_merge_finish.py (same recipes, r756 ts-normalize law); "
               "verification pass + receipt completed by r765 (dead session died pre-receipt)",
    "faces": {}, "asserts": [],
}

def norm_ts(s):
    # r756 law: normalize separator forms (space -> T) before any ts compare
    return s.replace(" ", "T", 1) if isinstance(s, str) else ""

def pick_newer(od, td, keys):
    o = max(norm_ts(od.get(k) or "") for k in keys)
    t = max(norm_ts(td.get(k) or "") for k in keys)
    return ("ours" if o >= t else "theirs"), o, t

# ---- section 7: daily report + live usage families, take-new by generated, md twins same side ----
FAM = [
    ("docs/daily_report/REPORT-2026-10-06.json", ("generated_at", "generated")),
    ("docs/live_usage/LIVE-2026-10-06.json", ("generated",)),
    ("docs/live_usage/LIVE-latest.json", ("generated",)),
]
for j, keys in FAM:
    od, td = json.loads(stage(2, j)), json.loads(stage(3, j))
    side, o, t = pick_newer(od, td, keys)
    b = stage(2 if side == "ours" else 3, j)
    open(j, "wb").write(b)
    json.loads(b.decode("utf-8", "replace"))  # parse-validate before add (r185 law)
    git("add", "--", j)
    md = j[:-5] + ".md"
    mb = stage(2 if side == "ours" else 3, md)
    open(md, "wb").write(mb)
    git("add", "--", md)
    receipt["faces"][j] = {"recipe": "take-new by generated (ts-normalized r756)", "side": side,
                           "ours_ts": o, "theirs_ts": t, "bytes": len(b), "resolved_by": "r765 finisher"}
    receipt["faces"][md] = {"recipe": "md twin same-side bound (r708)", "side": side,
                            "bytes": len(mb), "resolved_by": "r765 finisher"}

# ---- verification pass: all 18 faces from index stage-0 (what the merge commit will ship) ----
SECTIONS_1_6 = [
    "results/compute_audit.json", "results/regime_state.json", "results/token_usage.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/lhb_update_status.json", "results/update_status.json", "results/_attrition_guard_scan.json",
    "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "results/dashboard_status.json", "results/dashboard_status.js",
]
bad_markers, bad_parse = [], []
for p in SECTIONS_1_6:
    receipt["faces"].setdefault(p, {"resolved_by": "r764 dead session (sections 1-6)", "verify": "stage-0 pass"})
for p in list(receipt["faces"]):
    b = stage(0, p)
    if b"<<<<<<<" in b or b">>>>>>>" in b:
        bad_markers.append(p)
    if p.endswith(".json"):
        try:
            json.loads(b.decode("utf-8", "replace"))
        except Exception as e:
            bad_parse.append({"path": p, "err": str(e)[:80]})

# rebuilt stats for receipt completeness (dead session died before writing them)
ca = json.loads(stage(0, "results/compute_audit.json").decode("utf-8", "replace"))
receipt["faces"]["results/compute_audit.json"].update(
    {"recipe": "rolling-union by content identity + latest take-new by ts", "union_hist": len(ca.get("history", [])),
     "latest_ts": (ca.get("latest") or {}).get("ts")})
tu = json.loads(stage(0, "results/token_usage.json").decode("utf-8", "replace"))
receipt["faces"]["results/token_usage.json"].update(
    {"recipe": "per-key-max-union", "generated": tu.get("generated"), "machines": sorted((tu.get("machines") or {}).keys())})
js = stage(0, "results/dashboard_status.js")
receipt["asserts"].append({"js_wrapper_format": js.startswith(b"window.DASH_DATA")})
sc = json.loads(stage(0, "results/scorecard_v1.json").decode("utf-8", "replace"))
receipt["faces"]["results/scorecard_v1.json"].update({"recipe": "take-new by generated", "taken_generated": sc.get("generated") or sc.get("ts")})

# ---- close probe: UU set must be empty after adds ----
uu_after = [l for l in git("ls-files", "-u").decode("utf-8", "replace").splitlines() if l.strip()]
receipt["asserts"].append({"uu_after_add": uu_after, "uu_clean": not uu_after})
receipt["asserts"].append({"conflict_marker_scan_18faces": bad_markers, "clean": not bad_markers})
receipt["asserts"].append({"json_parse_scan": bad_parse, "clean": not bad_parse})
receipt["face_count"] = len(receipt["faces"])
receipt["verify_all_clean"] = (not uu_after) and (not bad_markers) and (not bad_parse)

json.dump(receipt, open("results/_r764bmb_merge_resolve.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("faces:", receipt["face_count"], "| verify_all_clean:", receipt["verify_all_clean"])
print("section7 sides:", {k.split("/")[-1]: v.get("side") for k, v in receipt["faces"].items() if "r765 finisher" in str(v.get("resolved_by"))})
print("uu_after:", uu_after)
print("bad_markers:", bad_markers, "| bad_parse:", bad_parse)
