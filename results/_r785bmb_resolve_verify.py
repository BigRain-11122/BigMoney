# r785 bm-b post-resolve verification: parse-verify all 13 faces before add (r185 law).
import subprocess, json, hashlib, re

FACES = {
 "results/lhb_update_status.json": "json",
 "results/regime_state.json": "json",
 "results/fundamental_b_layer_filter.json": "json",
 "results/futures_update_status.json": "json",
 "docs/daily_report/REPORT-2026-10-06.json": "json",
 "docs/daily_report/REPORT-2026-10-06.md": "text",
 "docs/live_usage/LIVE-2026-10-06.json": "json",
 "docs/live_usage/LIVE-2026-10-06.md": "text",
 "docs/live_usage/LIVE-latest.json": "json",
 "docs/live_usage/LIVE-latest.md": "text",
 "results/dashboard_status.json": "json",
 "results/dashboard_status.js": "js_origin_verbatim",
 "results/token_usage.json": "json",
}
MARK = re.compile(r"^(<{7}|={7}|>{7})", re.M)
report, fails = {}, []

for p, kind in FACES.items():
    raw = open(p, "rb").read()
    text = raw.decode("utf-8", "replace")
    entry = {"bytes": len(raw), "sha16": hashlib.sha256(raw).hexdigest()[:16],
             "conflict_markers": len(MARK.findall(text))}
    if entry["conflict_markers"]:
        fails.append((p, "conflict markers"))
    if kind == "json":
        try:
            json.loads(text)
        except Exception as e:
            fails.append((p, f"json parse: {e}"))
    elif kind == "js_origin_verbatim":
        h = subprocess.run(["git", "rev-parse", "-q", "--verify", ":3:" + p],
                           capture_output=True, text=True).stdout.strip()
        ob = subprocess.run(["git", "cat-file", "blob", h], capture_output=True).stdout
        entry["origin_blob_sha16"] = hashlib.sha256(ob).hexdigest()[:16]
        entry["byte_identical_to_stage3"] = (raw == ob)
        if not entry["byte_identical_to_stage3"]:
            fails.append((p, "js not byte-identical to origin stage3"))
        if not text.startswith("window.DASH_DATA") or "json.dumps" in "":
            pass
        if "window.DASH_DATA" not in text:
            fails.append((p, "js wrapper stripped"))
    report[p] = entry

# LIVE twins same-side byte assertion (r439): dated vs latest must be identical pairs
for a, b in [("docs/live_usage/LIVE-2026-10-06.json", "docs/live_usage/LIVE-latest.json"),
             ("docs/live_usage/LIVE-2026-10-06.md", "docs/live_usage/LIVE-latest.md")]:
    same = open(a, "rb").read() == open(b, "rb").read()
    report[f"twin_same::{a}=={b}"] = same
    if not same:
        fails.append((f"{a}!={b}", "twins differ"))

# regime zero-loss: history rows ours-staged >= theirs-staged and union superset
h2 = subprocess.run(["git", "rev-parse", "-q", "--verify", ":2:results/regime_state.json"],
                    capture_output=True, text=True).stdout.strip()
b2 = json.loads(subprocess.run(["git", "cat-file", "blob", h2], capture_output=True).stdout)
h3 = subprocess.run(["git", "rev-parse", "-q", "--verify", ":3:results/regime_state.json"],
                    capture_output=True, text=True).stdout.strip()
b3 = json.loads(subprocess.run(["git", "cat-file", "blob", h3], capture_output=True).stdout)
wt = json.loads(open("results/regime_state.json", encoding="utf-8").read())
for k in ("history", "transitions", "triggers"):
    so = {json.dumps(r, sort_keys=True) for r in (b2.get(k) or [])}
    st = {json.dumps(r, sort_keys=True) for r in (b3.get(k) or [])}
    sw = {json.dumps(r, sort_keys=True) for r in (wt.get(k) or [])}
    report[f"regime::{k}"] = {"ours": len(so), "theirs": len(st), "wt": len(sw),
                              "wt_superset_of_both": (so | st) <= sw}
    if not ((so | st) <= sw):
        fails.append((f"regime {k}", "zero-loss violated"))

with open("results/_r785bmb_resolve_verify.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump({"report": report, "fails": fails}, f, ensure_ascii=False, indent=1)
print("FAILS:", fails if fails else "NONE - all 13 faces verified")
