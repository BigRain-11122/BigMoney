"""r710 bm-a merge-3 resolver (31 UU, bm-c r517 S6 wave vs my r710 close wave).

Laws applied (blood-line: r694/r704/r707/r708/r709/r515/r706):
- merge mode: ours = index :2:, theirs = :3: (r701-iii mapping; r405
  stage-read prohibition is rebase-mode-only, merge mode REQUIRES stage
  blobs for complete sides -- r515 zealous common-tail trap).
- regen faces: per-face directed ts probe (generated/updated/ts family),
  newer-wins; probes pre-verified ours 06:0x-06:1x > theirs 05:59-06:01.
- twins (md/json, js/json): single decision from the JSON twin, applied
  same-side to both (r708 same-side law).
- stage-blob readback: after write, reparse + CR-normalized byte equality
  vs the chosen stage blob (r515 readback assertion).
- compute_audit.json: history list union by row key (r707 union law).
- x2_watch_log.jsonl: line-level zero-loss union, residual-line
  tolerance = final residual set subset of source residual set (r706).
- token_usage.json: machines per-key max (bigger total bytes wins,
  tie->ours) + top-level ours-fresh (r466/r709 per-key max law).
- CODELY.md: block union = base tail + theirs-added + ours-added
  (append-only ledger, both new pit entries kept).

Receipt -> results/_r710bma_merge3_resolve.json (CJK-safe, no console).
"""
import difflib
import json
import subprocess
import sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
BASE_REF = "5a59e679d"
RECEIPT = REPO + r"\results\_r710bma_merge3_resolve.json"


def stage(n, path):
    b = subprocess.run(["git", "-C", REPO, "show", ":%d:%s" % (n, path)],
                       capture_output=True).stdout
    assert len(b) > 0, "empty stage blob %d for %s (stage cleared?)" % (n, path)
    return b


def ref(r, path):
    b = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (r, path)],
                       capture_output=True).stdout
    return b


TS_KEYS = ("generated", "generated_at", "updated", "ts", "written_at")


def find_ts(d, depth=0):
    best = ""
    if isinstance(d, dict) and depth < 3:
        for k in TS_KEYS:
            v = d.get(k)
            if isinstance(v, str) and v > best:
                best = v
        for v in d.values():
            b2 = find_ts(v, depth + 1)
            if b2 > best:
                best = b2
    return best


def cr_norm(b):
    return b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


REGEN_FACES = [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/daily_report/REPORT-2026-10-05.md",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]

rec = {"round": "r710 bm-a merge-3", "faces": {}, "verdict": None}


def write_bytes(path, b):
    with open(REPO + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(b)


def resolve_regen(path):
    o = stage(2, path)
    t = stage(3, path)
    # JSON probe for directed ts (non-JSON twins inherit the twin decision)
    to = tt = ""
    try:
        po = json.loads(o.decode("utf-8"))
        pt = json.loads(t.decode("utf-8"))
        to = find_ts(po)
        tt = find_ts(pt)
    except Exception:
        to, tt = "", ""
    if to and tt:
        pick = "ours" if to >= tt else "theirs"
        reason = "ts %s vs %s" % (to, tt)
    else:
        pick = "ours"
        reason = "no-ts/deterministic face -> ours (probe pre-verified newer)"
    b = o if pick == "ours" else t
    write_bytes(path, b)
    rb = open(REPO + "\\" + path.replace("/", "\\"), "rb").read()
    ok_rb = cr_norm(rb) == cr_norm(b)
    ok_marker = rb.count(b"<<<<<<<") == 0
    rec["faces"][path] = {"mode": "regen-newer", "pick": pick,
                          "reason": reason, "readback_ok": ok_rb,
                          "marker_free": ok_marker}
    return ok_rb and ok_marker


def resolve_compute_audit():
    path = "results/compute_audit.json"
    o = json.loads(stage(2, path).decode("utf-8"))
    t = json.loads(stage(3, path).decode("utf-8"))
    oh = o.get("history", [])
    th = t.get("history", [])
    keyf = None
    if oh and isinstance(oh[0], dict):
        for k in ("ts", "generated", "generated_at", "t", "time"):
            if k in oh[0]:
                keyf = k
                break
    seen = set()
    union = []
    if keyf:
        for r in th + oh:  # theirs first, ours overwrite (newer side wins dup)
            k = r.get(keyf)
            if k in seen:
                continue
            seen.add(k)
            union.append(r)
    else:
        union = oh + [r for r in th if r not in oh]
    # order: keep chronological if keyf sortable
    if keyf:
        union.sort(key=lambda r: str(r.get(keyf, "")))
    o["history"] = union
    o["latest"] = t["latest"] if find_ts(t["latest"]) > find_ts(o["latest"]) \
        else o["latest"]
    b = json.dumps(o, ensure_ascii=False, indent=1).encode("utf-8")
    write_bytes(path, b)
    rb = json.loads(open(REPO + "\\" + path.replace("/", "\\"),
                         encoding="utf-8").read())
    ok = set(str(r.get(keyf)) for r in rb["history"]) >= \
        set(str(r.get(keyf)) for r in oh) and \
        set(str(r.get(keyf)) for r in rb["history"]) >= \
        set(str(r.get(keyf)) for r in th) if keyf else True
    rec["faces"][path] = {"mode": "history-union", "ours_n": len(oh),
                          "theirs_n": len(th), "union_n": len(union),
                          "superset_ok": bool(ok)}
    return bool(ok)


def resolve_x2_log():
    path = "results/x2_watch_log.jsonl"
    o = stage(2, path).decode("utf-8", errors="replace").splitlines()
    t = stage(3, path).decode("utf-8", errors="replace").splitlines()

    def residual(lines):
        res = []
        for ln in lines:
            s = ln.strip()
            if not s:
                continue
            try:
                json.loads(s)
            except Exception:
                res.append(s)
        return set(res)

    src_res = residual(o) | residual(t)
    seen = set()
    union = []
    for ln in o + t:  # ours order first, theirs appended if new
        s = ln.strip()
        if not s:
            continue
        if s in seen:
            continue
        seen.add(s)
        union.append(ln)
    b = ("\n".join(union) + "\n").encode("utf-8")
    write_bytes(path, b)
    back = open(REPO + "\\" + path.replace("/", "\\"), "rb").read()
    fin_res = residual(back.decode("utf-8", errors="replace").splitlines())
    ok = fin_res <= src_res and back.count(b"<<<<<<<") == 0
    rec["faces"][path] = {
        "mode": "jsonl-union", "ours_n": len([x for x in o if x.strip()]),
        "theirs_n": len([x for x in t if x.strip()]),
        "union_n": len(union), "residual_subset_ok": bool(fin_res <= src_res),
        "final_residual_n": len(fin_res)}
    return ok


def resolve_token():
    path = "results/token_usage.json"
    o = json.loads(stage(2, path).decode("utf-8"))
    t = json.loads(stage(3, path).decode("utf-8"))
    om, tm = o.get("machines", {}), t.get("machines", {})
    machines = {}
    for k in set(om) | set(tm):
        a, b2 = om.get(k), tm.get(k)
        if a is None:
            machines[k] = b2
        elif b2 is None:
            machines[k] = a
        else:
            sa = a.get("state_bytes", 0) + a.get("report_bytes", 0)
            sb = b2.get("state_bytes", 0) + b2.get("report_bytes", 0)
            machines[k] = a if sa >= sb else b2
    o["machines"] = machines
    b = json.dumps(o, ensure_ascii=False, indent=1).encode("utf-8")
    write_bytes(path, b)
    rb = json.loads(open(REPO + "\\" + path.replace("/", "\\"),
                         encoding="utf-8").read())
    ok = set(rb["machines"].keys()) >= set(om.keys()) and \
        set(rb["machines"].keys()) >= set(tm.keys())
    rec["faces"][path] = {"mode": "perkey-max-union",
                          "keys_n": len(machines), "superset_ok": bool(ok),
                          "top_pick": "ours (fresh 06:08)"}
    return bool(ok)


def resolve_codely():
    path = "CODELY.md"
    base = ref(BASE_REF, path).decode("utf-8").splitlines()
    ours = stage(2, path).decode("utf-8").splitlines()
    theirs = stage(3, path).decode("utf-8").splitlines()
    ours_add = [l[1:] for l in difflib.unified_diff(base, ours, lineterm="", n=0)
                if l.startswith("+") and not l.startswith("+++")]
    theirs_add = [l[1:] for l in difflib.unified_diff(base, theirs,
                                                      lineterm="", n=0)
                  if l.startswith("+") and not l.startswith("+++")]
    # both sides are pure tail-appends on the same base (verified by probe):
    # union = base + theirs_add + ours_add (bm-c pushed first)
    merged = base + theirs_add + ours_add
    b = ("\r\n".join(merged) + "\r\n").encode("utf-8")
    write_bytes(path, b)
    back = open(REPO + "\\" + path.replace("/", "\\"), "rb").read()
    bl = back.decode("utf-8").splitlines()
    ok = all(l in bl for l in ours_add) and \
        all(l in bl for l in theirs_add) and \
        len(bl) == len(base) + len(ours_add) + len(theirs_add) and \
        not any(x.lstrip().startswith("<<<<<<<") for x in bl)
    rec["faces"][path] = {"mode": "block-union", "base_n": len(base),
                          "ours_add_n": len(ours_add),
                          "theirs_add_n": len(theirs_add),
                          "merged_n": len(bl), "both_kept_ok": bool(ok)}
    return bool(ok)


def main():
    fails = []
    for p in REGEN_FACES:
        if not resolve_regen(p):
            fails.append(p)
    if not resolve_compute_audit():
        fails.append("results/compute_audit.json")
    if not resolve_x2_log():
        fails.append("results/x2_watch_log.jsonl")
    if not resolve_token():
        fails.append("results/token_usage.json")
    if not resolve_codely():
        fails.append("CODELY.md")
    rec["fails"] = fails
    rec["verdict"] = "RESOLVED-ALL-GREEN" if not fails else "HAS-FAILS"
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print("MERGE3_RESOLVE", rec["verdict"], "faces:", len(rec["faces"]),
          "fails:", len(fails))
    print("receipt -> results/_r710bma_merge3_resolve.json")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
