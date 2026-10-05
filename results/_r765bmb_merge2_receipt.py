# r765 bm-b merge loop-2 receipt finisher (audit mode).
# The resolver script crashed at its final marker scan (stage-0 read on CLI faces
# before their git add); all 14 faces were already resolved+staged, UU=0. This
# finisher rebuilds the receipt post-hoc: side picked = hash-compare stage-0 blob
# vs ours-ref b884d4d16 (pre-merge main) and theirs-ref a30bbe0d0 (origin tip at
# merge time), then runs the full marker scan + close probe + receipt write.
import subprocess, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OURS_REF = "b884d4d16"   # merge #1 commit (pre loop-2 main tip)
THEIRS_REF = "a30bbe0d0"  # origin tip at loop-2 merge start

def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True)
    return r.stdout if r.returncode == 0 else None

def blob(ref, path):
    return git("show", "%s:%s" % (ref, path))

def sha1(b):
    import hashlib
    return hashlib.sha1(b).hexdigest() if b is not None else None

def norm(s):
    return s.replace(" ", "T", 1) if isinstance(s, str) else ""

FACES8 = [
    ("results/_attrition_guard_scan.json", ("ts", "updated")),
    ("results/fundamental_b_layer_filter.json", ("updated", "ts")),
    ("docs/daily_report/REPORT-2026-10-06.json", ("generated_at", "generated")),
    ("docs/daily_report/REPORT-2026-10-06.md", None),
    ("docs/live_usage/LIVE-2026-10-06.json", ("generated",)),
    ("docs/live_usage/LIVE-2026-10-06.md", None),
    ("docs/live_usage/LIVE-latest.json", ("generated",)),
    ("docs/live_usage/LIVE-latest.md", None),
]
CLI6 = ["results/compute_audit.json", "results/regime_state.json", "results/update_status.json",
        "results/lhb_update_status.json", "results/futures_update_status.json", "results/token_usage.json"]

receipt = {"round": 765, "machine": "bm-b", "window": "merge loop-2 absorb origin (behind-5: bm-c r600/r601 + bm-a r760)",
           "recipes_source": "bm-c r600 receipt family (_r600bmc_merge_resolve.json) + canonical CLI merge_lane_views resolve",
           "ours_ref": OURS_REF, "theirs_ref": THEIRS_REF, "faces": {}, "asserts": []}

for path, keys in FACES8:
    cur = git("show", ":0:%s" % path)
    o, t = blob(OURS_REF, path), blob(THEIRS_REF, path)
    side = "ours" if cur == o else ("theirs" if cur == t else "diverged")
    row = {"recipe": "regen twin ts-newer-wins (r756 normalized)" if keys else "md same-side bound",
           "side_picked": side, "bytes": len(cur or b"")}
    if keys:
        try:
            d = json.loads(cur.decode("utf-8", "replace"))
            row["chosen_ts"] = max(norm(d.get(k) or "") for k in keys)
        except Exception:
            row["chosen_ts"] = "?"
    receipt["faces"][path] = row

for path in CLI6:
    cur = git("show", ":0:%s" % path)
    o, t = blob(OURS_REF, path), blob(THEIRS_REF, path)
    side = "ours" if cur == o else ("theirs" if cur == t else "merged-union/other")
    receipt["faces"][path] = {"recipe": "canonical CLI merge_lane_views resolve (single-source)", "side_picked": side, "bytes": len(cur or b"")}

bad = [p for p in FACES8 + [(c, None) for c in CLI6] for p in [p[0]] if (lambda b: b"<<<<<<<" in b or b">>>>>>>" in b)(git("show", ":0:%s" % p) or b"")]
uu = [l for l in (git("ls-files", "-u") or b"").decode("utf-8", "replace").splitlines() if l.strip()]
receipt["asserts"].append({"marker_scan_14faces": bad, "clean": not bad})
receipt["asserts"].append({"uu_after_all_adds": uu, "uu_clean": not uu})
receipt["face_count"] = len(receipt["faces"])
receipt["verify_all_clean"] = not bad and not uu
json.dump(receipt, open("results/_r765bmb_merge2_resolve.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for p, r in receipt["faces"].items():
    print(p.split("/")[-1], "->", r["side_picked"], r.get("chosen_ts", ""))
print("marker scan clean:", not bad, "| UU:", len(uu))
