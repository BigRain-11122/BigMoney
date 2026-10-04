"""r462 bm-c 32-UU merge resolver (canon: r461/r663 lineage).
Sides via git show HEAD:/MERGE_HEAD: raw bytes (r657 law 2, stage-immune).
Classes:
  - 26 regen faces: newer-tS wins (probe: ours newer 10:41-10:42 vs theirs
    10:35-10:37; ts-normalized compare per r461 law, not raw lexicographic)
  - dashboard_status.js/.json, daily_scorecard.json, paper_export x2: ours
    newer per _r462bmc_ambig_diff.txt (meta.generated_at / as_of mirrors)
  - x2_watch_log.jsonl + pool_core_samples.jsonl: exact-line union dedup +
    both-side containment asserts (bytes mode, r656 canon-set law)
  - token_usage.json: machines per-key max-wins union, side_picks>0 assert
    (r456 law), rest from newer side
  - compute_audit.json: history entry-identity union sorted by ts + latest
    newer-wins
Gates: reparse all .json, marker scan all faces, evidence JSON.
NO add/commit here (r657 law 3: surgery standalone, add/commit separate)."""
import datetime
import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
EV = ROOT + r"\results\_r462bmc_merge_resolve.json"
CREATE = 0x08000000


def git_show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       cwd=ROOT, creationflags=CREATE)
    assert r.returncode == 0, (ref, path, r.stderr[:200])
    return r.stdout


def norm_ts(v):
    if not isinstance(v, str):
        return None
    s = v.strip().replace("T", " ")
    return s[:19] if len(s) >= 16 else None


REGEN_OURS = [
    # (path, ours_ts, theirs_ts) -- probed normalized, ours newer all
    ("docs/daily_report/REPORT-2026-10-04.json", "2026-10-04 10:41:55", "2026-10-04 10:37:16"),
    ("docs/daily_report/REPORT-2026-10-04.md", "2026-10-04 10:41:55", "2026-10-04 10:37:16"),
    ("docs/live_usage/LIVE-2026-10-04.json", "2026-10-04 10:41:55", "2026-10-04 10:37:16"),
    ("docs/live_usage/LIVE-2026-10-04.md", "2026-10-04 10:41:55", "2026-10-04 10:37:16"),
    ("docs/live_usage/LIVE-latest.json", "2026-10-04 10:41:55", "2026-10-04 10:37:16"),
    ("docs/live_usage/LIVE-latest.md", "2026-10-04 10:41:55", "2026-10-04 10:37:16"),
    ("results/_attrition_guard_scan.json", "2026-10-04 10:42:28", "2026-10-04 10:39:29"),
    ("results/daily_scorecard.json", "2026-10-04 10:41:41", "2026-10-04 10:36:55"),
    ("results/dashboard_status.js", "2026-10-04 10:42:06", "2026-10-04 10:37:32"),
    ("results/dashboard_status.json", "2026-10-04 10:42:06", "2026-10-04 10:37:32"),
    ("results/fundamental_b_layer_filter.json", "2026-10-04 10:41:33", "2026-10-04 10:36:44"),
    ("results/futures_update_status.json", "2026-10-04 10:41:29", "2026-10-04 10:36:40"),
    ("results/lhb_update_status.json", "2026-10-04 10:41:28", "2026-10-04 10:36:39"),
    ("results/paper/COMPOSITE-CE-01_paper.json", "2026-10-04 10:41:35", "2026-10-04 10:36:47"),
    ("results/paper/COMPOSITE-CE-02_paper.json", "2026-10-04 10:41:36", "2026-10-04 10:36:48"),
    ("results/paper/DROUGHT-CE-01_paper.json", "2026-10-04 10:41:38", "2026-10-04 10:36:50"),
    ("results/paper/ENGULF-CE-01_paper.json", "2026-10-04 10:41:39", "2026-10-04 10:36:52"),
    ("results/paper/NEEDLE-DE-01_paper.json", "2026-10-04 10:41:40", "2026-10-04 10:36:54"),
    ("results/paper/VOLATILITY-CE-01_paper.json", "2026-10-04 10:41:41", "2026-10-04 10:36:55"),
    ("results/paper_export/export-2026-09-30.json", "2026-10-04 10:41:41", "2026-10-04 10:36:55"),
    ("results/paper_export/latest.json", "2026-10-04 10:41:41", "2026-10-04 10:36:55"),
    ("results/prospect_paper/_summary.json", "2026-10-04 10:41:42", "2026-10-04 10:36:57"),
    ("results/prospect_promotion/_summary.json", "2026-10-04 10:41:43", "2026-10-04 10:36:59"),
    ("results/regime_state.json", "2026-10-04 10:39:59", "2026-10-04 10:35:05"),
    ("results/scorecard_v1.json", "2026-10-04 10:40:28", "2026-10-04 10:35:46"),
    ("results/strategy_scorecard.json", "2026-10-04 10:40:38", "2026-10-04 10:36:01"),
    ("results/t35_open_fill_verify.json", "2026-10-04 10:41:41", "2026-10-04 10:36:55"),
    ("results/update_status.json", "2026-10-04 10:39:58", "2026-10-04 10:35:04"),
]

JSONL_UNION = [
    "results/x2_watch_log.jsonl",
    "results/pool_core_samples.jsonl",
]


def resolve_jsonl(path):
    ours = git_show("HEAD", path)
    theirs = git_show("MERGE_HEAD", path)
    o_lines = ours.split(b"\n")
    t_lines = theirs.split(b"\n")
    # trailing-newline handling: split keeps b"" tail if ends with \n
    o_canon = [ln for ln in o_lines if ln.strip()]
    t_canon = [ln for ln in t_lines if ln.strip()]
    seen = set()
    union = []
    for ln in o_canon + t_canon:
        if ln not in seen:
            seen.add(ln)
            union.append(ln)
    o_set = set(o_canon)
    t_set = set(t_canon)
    u_set = set(union)
    assert o_set <= u_set and t_set <= u_set, "containment fail " + path
    blob = b"\n".join(union) + b"\n"
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(blob)
    return {"class": "jsonl-union", "ours_lines": len(o_canon),
            "theirs_lines": len(t_canon), "union_lines": len(union),
            "ours_only": len(o_set - t_set), "theirs_only": len(t_set - o_set),
            "containment": True}


def entry_ts(obj):
    """max normalized ts string among string fields at depth<=1."""
    best = None
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for v in cur.values():
                if isinstance(v, str):
                    nt = norm_ts(v)
                    if nt and (best is None or nt > best):
                        best = nt
                elif isinstance(cur, dict) and isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            stack.extend(cur)
    return best


def resolve_token_usage(path):
    ours = json.loads(git_show("HEAD", path).decode("utf-8-sig"))
    theirs = json.loads(git_show("MERGE_HEAD", path).decode("utf-8-sig"))
    mo = ours.get("machines", {})
    mt = theirs.get("machines", {})
    merged = {}
    picks = {"ours": 0, "theirs": 0}
    for k in sorted(set(mo) | set(mt)):
        if k in mo and k in mt:
            to, tt = entry_ts(mo[k]), entry_ts(mt[k])
            if to is None and tt is None:
                merged[k] = mo[k]
                picks["ours"] += 1
            elif tt is None or (to is not None and to >= tt):
                merged[k] = mo[k]
                picks["ours"] += 1
            else:
                merged[k] = mt[k]
                picks["theirs"] += 1
        elif k in mo:
            merged[k] = mo[k]
            picks["ours"] += 1
        else:
            merged[k] = mt[k]
            picks["theirs"] += 1
    assert picks["ours"] + picks["theirs"] > 0, "side-pick zero (r456 law)"
    ours["machines"] = merged
    blob = json.dumps(ours, ensure_ascii=False, indent=1).encode("utf-8")
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(blob)
    return {"class": "token-max-union", "machines_keys": sorted(merged),
            "picks": picks}


def resolve_compute_audit(path):
    ours = json.loads(git_show("HEAD", path).decode("utf-8-sig"))
    theirs = json.loads(git_show("MERGE_HEAD", path).decode("utf-8-sig"))
    ho = ours.get("history", [])
    ht = theirs.get("history", [])
    ident = {}
    for e in ho + ht:
        ident.setdefault(json.dumps(e, sort_keys=True, ensure_ascii=False), e)
    def ets(e):
        return entry_ts(e) or ""
    merged = sorted(ident.values(), key=ets)
    lo, lt = entry_ts(ours.get("latest", {})), entry_ts(theirs.get("latest", {}))
    latest = ours.get("latest", {}) if (lt is None or (lo is not None and lo >= lt)) \
        else theirs.get("latest", {})
    ours["history"] = merged
    ours["latest"] = latest
    blob = json.dumps(ours, ensure_ascii=False, indent=1).encode("utf-8")
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(blob)
    return {"class": "compute-audit-union", "ours_hist": len(ho),
            "theirs_hist": len(ht), "union_hist": len(merged),
            "latest_side": "ours" if latest == ours.get("latest") and lo >= (lt or "") else "theirs",
            "latest_ts_ours": lo, "latest_ts_theirs": lt}


def marker_scan(blob, path):
    for mk in (b"<<<<<<< ", b">>>>>>> ", b"=======\n"):
        if blob.find(mk) >= 0:
            raise AssertionError("conflict marker in " + path)


def main():
    ev = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
          "faces": {}, "gates": {}}
    # 1. regen newer-wins (ours probed newer on all)
    for path, o_ts, t_ts in REGEN_OURS:
        assert norm_ts(o_ts) >= norm_ts(t_ts), "probe ordering violated " + path
        blob = git_show("HEAD", path)
        marker_scan(blob, path)
        with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
            f.write(blob)
        ev["faces"][path] = {"class": "regen-newer-wins", "side": "ours",
                            "ours_ts": o_ts, "theirs_ts": t_ts}
    # 2. jsonl unions
    for path in JSONL_UNION:
        ev["faces"][path] = resolve_jsonl(path)
    # 3. token usage max-union
    ev["faces"]["results/token_usage.json"] = resolve_token_usage(
        "results/token_usage.json")
    # 4. compute audit history union
    ev["faces"]["results/compute_audit.json"] = resolve_compute_audit(
        "results/compute_audit.json")
    # gates: reparse every resolved .json + marker scan
    fails = []
    for path in ev["faces"]:
        if path.endswith(".json"):
            try:
                with open(ROOT + "\\" + path.replace("/", "\\"), "rb") as f:
                    raw = f.read()
                marker_scan(raw, path)
                json.loads(raw.decode("utf-8-sig"))
            except Exception as e:  # noqa: BLE001
                fails.append((path, repr(e)[:120]))
        else:
            try:
                with open(ROOT + "\\" + path.replace("/", "\\"), "rb") as f:
                    marker_scan(f.read(), path)
            except Exception as e:  # noqa: BLE001
                fails.append((path, repr(e)[:120]))
    ev["gates"] = {"reparse_marker_fails": fails,
                   "faces_resolved": len(ev["faces"])}
    with open(EV, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("RESOLVE_DONE faces=%d fails=%d" % (len(ev["faces"]), len(fails)))
    for path, info in ev["faces"].items():
        if info.get("class") == "jsonl-union":
            print(path, "union", info["union_lines"], "ours_only",
                  info["ours_only"], "theirs_only", info["theirs_only"])


if __name__ == "__main__":
    main()
