# r766 bm-b merge resolver: 9 non-CLI faces per bm-c r600/r765 receipt recipes
# (regen twin ts-newer-wins, r756 normalized compare: space->T + dict-lex compare
# via strptime-equivalent normalized string; md twins bound to json side).
# CLI-supported faces (compute_audit/regime_state/update_status/lhb/futures/token_usage)
# already resolved via scripts/merge_lane_views.py resolve (single-source canonical).
# This script: stage 2/3 probe -> ts-normalized take-newer -> write -> parse-verify -> git add.
import subprocess, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (a[0], r.returncode, r.stderr.decode("utf-8", "replace")[:200]))
    return r.stdout

def stage(n, path):
    return git("show", ":%d:%s" % (n, path))

def norm(s):
    # r756 law: space -> T before compare (mixed separator dict-order poison)
    return s.replace(" ", "T", 1) if isinstance(s, str) else ""

receipt = {"round": 766, "machine": "bm-b", "window": "merge behind-5 absorb (bm-c r601/r602 + bm-a r761 W149 ignition)", "faces": {}, "asserts": []}

FACES = [
    # (path, ts keys)  -- None keys = md twin bound to json side
    ("docs/daily_report/REPORT-2026-10-06.json", ("generated_at", "generated")),
    ("docs/daily_report/REPORT-2026-10-06.md", None),
    ("docs/live_usage/LIVE-2026-10-06.json", ("generated",)),
    ("docs/live_usage/LIVE-2026-10-06.md", None),
    ("docs/live_usage/LIVE-latest.json", ("generated",)),
    ("docs/live_usage/LIVE-latest.md", None),
    ("results/fundamental_b_layer_filter.json", ("updated", "ts")),
    ("results/scorecard_v1.json", ("generated",)),
    ("results/strategy_scorecard.json", ("generated",)),
]
bound = {}
for path, keys in FACES:
    if keys is None:
        json_twin = path[:-3] + ".json"
        side, ob, tb = bound[json_twin]
        b = stage(2 if side == "ours" else 3, path)
        open(path, "wb").write(b)
        git("add", "--", path)
        receipt["faces"][path] = {"recipe": "regen twin ts-newer-wins (r756), md same-side bound", "side": side}
        continue
    od, td = json.loads(stage(2, path)), json.loads(stage(3, path))
    o = max(norm(od.get(k) or "") for k in keys)
    t = max(norm(td.get(k) or "") for k in keys)
    side = "ours" if o >= t else "theirs"
    b = stage(2 if side == "ours" else 3, path)
    open(path, "wb").write(b)
    if path.endswith(".json"):
        json.loads(b.decode("utf-8", "replace"))  # parse-verify before add (r185 law)
    git("add", "--", path)
    if path.endswith(".json"):
        bound[path] = (side, o, t)
    receipt["faces"][path] = {"recipe": "regen twin ts-newer-wins (r756 normalized)", "side": side,
                              "ours_ts": o, "theirs_ts": t}

# close probe + marker scan over all 15 UU faces
ALL15 = [p for p, _ in FACES] + [
    "results/compute_audit.json", "results/regime_state.json", "results/update_status.json",
    "results/lhb_update_status.json", "results/futures_update_status.json", "results/token_usage.json",
]
bad = [p for p in ALL15 if (lambda b: b"<<<<<<<" in b or b">>>>>>>" in b)(open(p, "rb").read())]
uu = [l for l in git("ls-files", "-u").decode("utf-8", "replace").splitlines() if l.strip()]
receipt["asserts"].append({"marker_scan_15faces_worktree": bad})
receipt["uu_after_all_adds"] = uu
receipt["clean"] = (not bad) and (not uu)
json.dump(receipt, open("results/_r766bmb_merge_resolve.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in receipt["faces"].items():
    print(k.split("/")[-1], "->", v.get("side"), "(ours", v.get("ours_ts"), "theirs", v.get("theirs_ts"), ")")
print("marker scan clean:", receipt["clean"], "| remaining UU:", len(uu))
