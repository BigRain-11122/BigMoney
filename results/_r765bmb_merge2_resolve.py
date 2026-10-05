# r765 bm-b merge loop-2 resolver: 8 non-CLI faces per bm-c r600 receipt recipes
# (regen twin ts-newer-wins, r756 normalized compare). CLI-supported faces
# (compute_audit/regime_state/update_status/lhb/futures/token_usage) are resolved
# separately by scripts/merge_lane_views.py resolve (single-source canonical).
# This script: stages 2/3 probe -> ts-normalized take-newer -> write -> parse-verify -> git add.
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
    # r756 law: space -> T before compare
    return s.replace(" ", "T", 1) if isinstance(s, str) else ""

receipt = {"round": 765, "machine": "bm-b", "window": "merge loop-2 absorb bm-c r600 (behind-5)", "faces": {}, "asserts": []}

FACES = [
    # (path, ts keys)
    ("results/_attrition_guard_scan.json", ("ts", "updated")),
    ("results/fundamental_b_layer_filter.json", ("updated", "ts")),
    ("docs/daily_report/REPORT-2026-10-06.json", ("generated_at", "generated")),
    ("docs/daily_report/REPORT-2026-10-06.md", None),  # md twin, bound to json side
    ("docs/live_usage/LIVE-2026-10-06.json", ("generated",)),
    ("docs/live_usage/LIVE-2026-10-06.md", None),
    ("docs/live_usage/LIVE-latest.json", ("generated",)),
    ("docs/live_usage/LIVE-latest.md", None),
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

# close probe + marker scan over all 14 loop-2 UU faces
ALL14 = [p for p, _ in FACES] + [
    "results/compute_audit.json", "results/regime_state.json", "results/update_status.json",
    "results/lhb_update_status.json", "results/futures_update_status.json", "results/token_usage.json",
]
bad = [p for p in ALL14 if (lambda b: b"<<<<<<<" in b or b">>>>>>>" in b)(stage(0, p))]
uu = [l for l in git("ls-files", "-u").decode("utf-8", "replace").splitlines() if l.strip()]
# note: CLI faces may not be added yet when this runs -> stage-0 read fails; scan worktree instead for them
wt_bad = [p for p in ALL14 if p not in [f for f, _ in FACES] and (lambda raw: b"<<<<<<<" in raw or b">>>>>>>" in raw)(open(p, "rb").read())]
receipt["asserts"].append({"marker_scan_index": bad, "marker_scan_worktree_cli_faces": wt_bad})
receipt["uu_after_own_adds"] = uu
receipt["clean"] = not bad and not wt_bad
json.dump(receipt, open("results/_r765bmb_merge2_resolve.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in receipt["faces"].items():
    print(k.split("/")[-1], "->", v.get("side"), "(ours", v.get("ours_ts"), "theirs", v.get("theirs_ts"), ")")
print("own-face marker scan clean:", receipt["clean"], "| remaining UU (CLI faces pending):", len(uu))
