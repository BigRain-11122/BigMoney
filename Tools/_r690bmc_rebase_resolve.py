"""r690 bm-c rebase-conflict resolver (17 UU faces, r688/r678 canon):
- 10 regen twins -> take THEIRS (origin/newer: REPORT-2026-10-07.json
  tie-break included, .md, LIVE-2026-10-07.{json,md}, LIVE-latest.{json,md},
  _attrition_guard_scan, dashboard_status.{js,json},
  fundamental_b_layer_filter) -- bm-a r833 chain ran later on these faces;
- 5 single-state faces -> take MINE (ts-duel newer-wins: lhb_update_status
  17:00:53, regime_state 16:59:56, scorecard_v1 17:00:38,
  strategy_scorecard 17:00:47, update_status 16:59:55);
- compute_audit.json -> append-history union (ts-keyed dedup, sort asc,
  latest = max-ts entry; mine 16:59:47 > theirs 16:59:24, r570/r806 law);
- token_usage.json -> per-key max-union (globals from newer side = mine
  17:01:42; machines = per-machine newer-wins union, zero loss, r456 law).
REBASE ours/theirs INVERSION: REBASE_HEAD blob = mine (r688 law).
Blob-exact byte restore for take-side faces; zero conflict markers + JSON
parse post-validated before exit."""
import json
import re
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

THEIRS = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
]
MINE = [
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
TS_RE = re.compile(r"2026-10-0\d[ T][0-9:]{8}")
MARKER_RE = re.compile(r"^(<<<<<<<|=======|>>>>>>>)", re.M)


def raw(rev, path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"blob read fail {rev}:{path}: {r.stderr[:200]}")
    return r.stdout


def write_bytes(path, b):
    with open(REPO + "\\" + path.replace("/", "\\"), "wb") as fh:
        fh.write(b)


def main():
    receipts = {"take_theirs": [], "take_mine": [], "union": []}

    # -- take-side faces: blob-exact byte restore --
    for p in THEIRS:
        b = raw("origin/main", p)
        assert not MARKER_RE.search(b.decode("utf-8", "replace")), "marker in blob " + p
        if p.endswith(".json"):
            json.loads(b)
        write_bytes(p, b)
        assert open(REPO + "\\" + p.replace("/", "\\"), "rb").read() == b
        receipts["take_theirs"].append(p)
    for p in MINE:
        b = raw("REBASE_HEAD", p)
        assert not MARKER_RE.search(b.decode("utf-8", "replace")), "marker in blob " + p
        if p.endswith(".json"):
            json.loads(b)
        write_bytes(p, b)
        assert open(REPO + "\\" + p.replace("/", "\\"), "rb").read() == b
        receipts["take_mine"].append(p)

    # -- compute_audit.json: history union --
    ca = "results/compute_audit.json"
    d_mine = json.loads(raw("REBASE_HEAD", ca))
    d_theirs = json.loads(raw("origin/main", ca))
    by_ts = {}
    for e in d_theirs.get("history", []):
        by_ts[e.get("ts")] = e
    for e in d_mine.get("history", []):
        by_ts[e.get("ts")] = e
    merged = sorted(by_ts.values(), key=lambda x: x.get("ts") or "")
    union_ca = {"latest": merged[-1], "history": merged}
    assert union_ca["latest"].get("ts") == "2026-10-07 16:59:47", \
        "compute_audit latest anchor: %s" % union_ca["latest"].get("ts")
    write_bytes(ca, (json.dumps(union_ca, ensure_ascii=False, indent=2)
                     + "\n").encode("utf-8"))
    receipts["union"].append(
        {"path": ca, "history_n": len(merged),
         "theirs_n": len(d_theirs["history"]), "mine_n": len(d_mine["history"]),
         "latest": union_ca["latest"]["ts"]})

    # -- token_usage.json: per-key max-union --
    tk = "results/token_usage.json"
    t_mine = json.loads(raw("REBASE_HEAD", tk))
    t_theirs = json.loads(raw("origin/main", tk))
    assert t_mine.get("generated", "") > t_theirs.get("generated", ""), \
        "token globals newer-side anchor"
    m_mine = t_mine.get("machines", {})
    m_theirs = t_theirs.get("machines", {})
    machines = {}
    for k in sorted(set(m_mine) | set(m_theirs)):
        a, b = m_mine.get(k), m_theirs.get(k)
        if a is None:
            machines[k] = b
        elif b is None:
            machines[k] = a
        else:
            sa = max(TS_RE.findall(json.dumps(a))) if TS_RE.search(json.dumps(a)) else ""
            sb = max(TS_RE.findall(json.dumps(b))) if TS_RE.search(json.dumps(b)) else ""
            machines[k] = a if sa >= sb else b
    union_tk = dict(t_theirs)
    union_tk.update(t_mine)          # globals from newer side (mine)
    union_tk["machines"] = machines  # per-machine zero-loss union
    write_bytes(tk, (json.dumps(union_tk, ensure_ascii=False, indent=2)
                     + "\n").encode("utf-8"))
    receipts["union"].append(
        {"path": tk, "machines": sorted(machines),
         "generated": union_tk.get("generated")})

    # -- post-validate: all 17 resolved files marker-free + JSON parses --
    all_faces = THEIRS + MINE + [ca, tk]
    for p in all_faces:
        txt = open(REPO + "\\" + p.replace("/", "\\"),
                   encoding="utf-8", errors="replace").read()
        assert not MARKER_RE.search(txt), "marker pollution: " + p
        if p.endswith(".json"):
            json.loads(txt)
    print("resolver done: theirs=%d mine=%d union=%d; "
          "compute_audit history=%d (t=%d,m=%d) latest=%s; token machines=%s"
          % (len(THEIRS), len(MINE), len(receipts["union"]),
             receipts["union"][0]["history_n"],
             receipts["union"][0]["theirs_n"], receipts["union"][0]["mine_n"],
             receipts["union"][0]["latest"], receipts["union"][1]["machines"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
