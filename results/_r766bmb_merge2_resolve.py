# r766 bm-b merge loop-2 resolver: 7 non-CLI faces (bm-c r602 + bm-a r762 wave)
# bloodline: _r766bmb_merge_resolve.py loop-1 (r765 receipt family recipes)
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

receipt = {"round": 766, "machine": "bm-b", "window": "merge loop-2 absorb (bm-c r602 + bm-a r762 W149 finalize + W150 seat, phantom-deletion claw trigger per r759)", "faces": {}, "asserts": []}

FACES = [
    ("docs/daily_report/REPORT-2026-10-06.json", ("generated_at", "generated")),
    ("docs/daily_report/REPORT-2026-10-06.md", None),
    ("docs/live_usage/LIVE-2026-10-06.json", ("generated",)),
    ("docs/live_usage/LIVE-2026-10-06.md", None),
    ("docs/live_usage/LIVE-latest.json", ("generated",)),
    ("docs/live_usage/LIVE-latest.md", None),
    ("results/fundamental_b_layer_filter.json", ("updated", "ts")),
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

ALL13 = [p for p, _ in FACES] + [
    "results/compute_audit.json", "results/regime_state.json", "results/update_status.json",
    "results/lhb_update_status.json", "results/futures_update_status.json", "results/token_usage.json",
]
bad = [p for p in ALL13 if (lambda b: b"<<<<<<<" in b or b">>>>>>>" in b)(open(p, "rb").read())]
uu = [l for l in git("ls-files", "-u").decode("utf-8", "replace").splitlines() if l.strip()]
receipt["asserts"].append({"marker_scan_13faces_worktree": bad})
receipt["uu_after_all_adds"] = uu
receipt["clean"] = (not bad) and (not uu)
json.dump(receipt, open("results/_r766bmb_merge2_resolve.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in receipt["faces"].items():
    print(k.split("/")[-1], "->", v.get("side"), "(ours", v.get("ours_ts"), "theirs", v.get("theirs_ts"), ")")
print("marker scan clean:", receipt["clean"], "| remaining UU:", len(uu))
