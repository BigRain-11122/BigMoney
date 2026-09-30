"""r492 rebase-conflict resolver WAVE 2 (bm-a, third-wave replay tax r351 family).

ALL_FACES pre-resolved via merge_lane_views. This handles: CODELY memory-union
(r327 entry-level), snapshot/twin deep-ts take-new (fixed probe v[:2]=='20'),
js-wrapper byte take-side (R209), append-log line union (r188).
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"blob read fail: {spec}: {r.stderr.decode()[:200]}")
    return r.stdout


def deep_ts(obj, found):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) >= 16 and v[:2] == "20" and v[4] == "-":
                found.append(v)
            deep_ts(v, found)
    elif isinstance(obj, list):
        for v in obj:
            deep_ts(v, found)


def take_newer(path, prefer_replay_on_tie=True):
    o = json.loads(blob(":2:" + path).decode("utf-8"))
    t = json.loads(blob(":3:" + path).decode("utf-8"))
    fo, ft = [], []
    deep_ts(o, fo)
    deep_ts(t, ft)
    mo = max(fo) if fo else ""
    mt = max(ft) if ft else ""
    if mt >= mo:
        side = "replay"
    elif mo > mt:
        side = "origin"
    else:
        side = "replay" if prefer_replay_on_tie else "origin"
    with open(path, "wb") as f:
        f.write(blob(":" + ("3" if side == "replay" else "2") + ":" + path))
    print(f"[{path}] o={mo} r={mt} -> {side}")
    return side


def byte_side(path, side):
    st = "3" if side == "replay" else "2"
    with open(path, "wb") as f:
        f.write(blob(":" + st + ":" + path))
    print(f"[{path}] byte-copy {side}")


def union_lines(path):
    o = blob(":2:" + path).decode("utf-8").splitlines()
    t = blob(":3:" + path).decode("utf-8").splitlines()
    seen = set(o)
    out = o + [ln for ln in t if ln not in seen]
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(out) + ("\n" if out else ""))
    print(f"[{path}] union {len(o)}+{len(out)-len(o)} = {len(out)} lines")


def codely_union():
    base = blob(":1:CODELY.md").decode("utf-8")
    origin = blob(":2:CODELY.md").decode("utf-8")
    replay = blob(":3:CODELY.md").decode("utf-8")
    if origin.startswith(base) and replay.startswith(base):
        tree = origin + replay[len(base):]
    elif replay.startswith(base):
        # origin did in-place edits: entry-level coverage (r327)
        suffix = replay[len(base):]
        tree = origin + suffix
    else:
        # replay did in-place restructure (hot-cold reorg): tree = replay
        # + carry over origin entries with NO identity-match in replay (r327 law).
        tree = replay
        def ident(ln):
            i = ln.find("]")
            return ln[:i] if ln.startswith("- [") and i > 0 else ln[:40]
        have = {ident(ln) for ln in tree.splitlines() if ln.startswith("- [")}
        new_from_origin = []
        for ln in origin.splitlines():
            if ln.startswith("- [") and ident(ln) not in have:
                new_from_origin.append(ln)
        if new_from_origin:
            lines = tree.splitlines()
            # insert before the '### Reference' marker (Project-section tail) if present
            try:
                ridx = lines.index("### Reference")
            except ValueError:
                ridx = len(lines)
            for k, ln in enumerate(new_from_origin):
                lines.insert(ridx + k, ln)
            tree = "\n".join(lines) + ("\n" if replay.endswith("\n") else "")
            print(f"[CODELY.md] carried {len(new_from_origin)} new origin entr(ies)")
    for src, name in ((origin, "origin"), (replay, "replay")):
        for ln in src.splitlines():
            if ln.startswith("- [") and ln not in tree.splitlines():
                # origin fat entries whose pointer-line twins exist in tree are covered by identity;
                # only flag entries whose IDENTITY is absent from tree entirely
                i = ln.find("]")
                if i > 0 and any(t.startswith(ln[:i]) for t in tree.splitlines() if t.startswith("- [")):
                    continue
                raise SystemExit(f"entry-loss guard: {name}: {ln[:80]}")
    with open("CODELY.md", "w", encoding="utf-8", newline="") as f:
        f.write(tree)
    print(f"[CODELY.md] union tree {len(tree.encode())}B "
          f"(base {len(base.encode())} origin {len(origin.encode())} replay {len(replay.encode())})")


codely_union()
side = take_newer("docs/daily_report/REPORT-2026-09-30.json")
byte_side("docs/daily_report/REPORT-2026-09-30.md", side)
side = take_newer("docs/live_usage/LIVE-2026-09-30.json")
byte_side("docs/live_usage/LIVE-2026-09-30.md", side)
side = take_newer("docs/live_usage/LIVE-latest.json")
byte_side("docs/live_usage/LIVE-latest.md", side)
side = take_newer("results/dashboard_status.json")
byte_side("results/dashboard_status.js", side)
for p in ("results/daily_scorecard.json", "results/fundamental_b_layer_filter.json",
          "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
          "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
          "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
          "results/paper_export/export-2026-09-30.json", "results/paper_export/latest.json",
          "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
          "results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/t35_open_fill_verify.json"):
    take_newer(p)
union_lines("results/x2_watch_log.jsonl")
print("wave2 done; parse-verify json faces:")
for p in ("docs/daily_report/REPORT-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.json",
          "docs/live_usage/LIVE-latest.json", "results/dashboard_status.json",
          "results/daily_scorecard.json", "results/fundamental_b_layer_filter.json",
          "results/paper_export/latest.json", "results/prospect_paper/_summary.json",
          "results/strategy_scorecard.json", "results/t35_open_fill_verify.json",
          "results/token_usage.json"):
    json.load(open(p, encoding="utf-8"))
print("all parse-verified")
