# -*- coding: utf-8 -*-
"""r455 bm-c merge resolve: 14 UU faces per r450/r452/r453 recipes.
- 12 take-ours by honest ts (regen faces, ours 08:39-08:41 > theirs 08:35-08:37)
- lhb_update_status.json take-THEIRS (08:36:02 > ours 08:20:09)
- regime_state.json tie -> ours (r452 deterministic-tie precedent)
- token_usage.json take-ours (identical machine keyset, ours newer=union face)
- compute_audit.json: history union by ts identity + latest=newer(ours) +
  preserve theirs superset top keys (machines, ts)
Post-resolve guards: line-start marker scan + JSON reparse + union containment
assert, then git add. Merge commit itself in stage 4."""
import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TAKE_OURS = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TAKE_THEIRS = ["results/lhb_update_status.json"]
UNION_FACES = ["results/compute_audit.json"]
ALL_FACES = TAKE_OURS + TAKE_THEIRS + UNION_FACES


def run(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, cwd=ROOT, text=True,
        encoding="utf-8", errors="replace",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def run_raw(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, cwd=ROOT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def blob(side, path):
    return run_raw(["show", ":%s:%s" % (side, path)]).stdout


def main():
    # 1) take-ours / take-theirs via checkout (byte-precise from index)
    for f in TAKE_OURS:
        r = run(["checkout", "--ours", f])
        assert r.returncode == 0, "checkout --ours failed: " + f
    for f in TAKE_THEIRS:
        r = run(["checkout", "--theirs", f])
        assert r.returncode == 0, "checkout --theirs failed: " + f
    print("TAKE_SIDES done: %d ours / %d theirs" % (len(TAKE_OURS), len(TAKE_THEIRS)))

    # 2) compute_audit union
    ours = json.loads(blob("2", "results/compute_audit.json"))
    theirs = json.loads(blob("3", "results/compute_audit.json"))
    h_o = ours.get("history", [])
    h_t = theirs.get("history", [])
    seen = {}
    order = []
    for e in h_t + h_o:
        k = e.get("ts")
        if k in seen:
            # same ts: prefer ours (newer writer) -- dedup keep-last wins
            seen[k] = e
        else:
            seen[k] = e
            order.append(k)
    union = [seen[k] for k in sorted(order)]
    assert len(union) >= max(len(h_o), len(h_t)), "union shrank"
    assert set(e.get("ts") for e in h_o) <= set(k for k in seen), "ours history not contained"
    assert set(e.get("ts") for e in h_t) <= set(k for k in seen), "theirs history not contained"
    merged = dict(theirs)          # superset top keys (machines, ts)
    merged["history"] = union
    merged["latest"] = ours["latest"]   # ours ts 08:39:02 > theirs 08:35:20
    if "ts" in merged:
        merged["ts"] = ours["latest"].get("ts", theirs.get("ts"))
    out = json.dumps(merged, ensure_ascii=False, indent=1) + "\n"
    with open(ROOT + r"\results\compute_audit.json", "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(out)
    json.loads(open(ROOT + r"\results\compute_audit.json", encoding="utf-8").read())
    print("COMPUTE_AUDIT union: hist %d+%d -> %d, latest=%s" % (
        len(h_o), len(h_t), len(union), merged["latest"].get("ts")))

    # 3) marker scan (line-start, r453 law) + JSON reparse of resolved faces
    bad_markers = []
    for f in ALL_FACES:
        p = ROOT + "\\" + f.replace("/", "\\")
        with open(p, "rb") as fh:
            raw = fh.read()
        for ln in raw.split(b"\n"):
            if ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>") or \
               ln.startswith(b"=======") and ln.strip() == b"=======":
                bad_markers.append(f)
                break
        if f.endswith(".json"):
            try:
                json.loads(raw.decode("utf-8", "replace"))
            except Exception as e:
                bad_markers.append(f + " JSON-FAIL:" + str(e)[:60])
    assert not bad_markers, "markers/parse fails: %s" % bad_markers
    print("MARKER+JSON guards PASS (14 faces)")

    # 4) stage resolved faces
    r = run(["add"] + ALL_FACES)
    assert r.returncode == 0, "add failed: " + (r.stdout + r.stderr)[:200]
    r = run(["diff", "--name-only", "--diff-filter=U"])
    assert not r.stdout.strip(), "UU still present: " + r.stdout
    print("STAGED 14 faces, zero UU remaining")
    print("RESOLVE_DONE")


if __name__ == "__main__":
    main()
