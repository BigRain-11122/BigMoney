# -*- coding: utf-8 -*-
"""r365 bm-a rebase-storm resolver (replay of b4c72760 onto origin/main 2c32dd96 = bm-c r117).
28 UU same-window S6 mirror storm. Stage sourcing: :2: = ours = origin (bm-c r117),
:3: = theirs = mine (bm-a R365). Adjudication pre-read by results/_r365bma_probe.py:
  - 22 snapshots + daily_report md twin + dashboard js twin: ALL take-MINE
    (my S6 chain 23:50:32-23:52:26 fresher than bm-c's 23:48:43-23:49:31 on every face;
     twins same-side coupling r327/r329/R209, js/md = byte-copy from MINE blob)
  - autofill_state: launches 47=47 fully-identical + last_tick ours 23:50:02 > mine 23:50:01
    -> take OURS whole (dict-ts compare, r140 family; strictly fresher not a tie)
  - regime_state: history 2+2 & transitions identical both sides, only 'updated' differs
    (mine 23:50:33 > ours 23:48:44) -> take MINE whole
  - compute_audit: history ts-key union 201+201 -> 202 distinct (only-ours 23:48:34 bm-c row
    + only-mine 23:50:30 my row), zero same-ts divergence, NO resolver cap (r360 law),
    state face take-MINE (freshest producer 23:50:30)
  - x2_watch_log: line-level union 1044+1044 -> 1050 (6 only-ours bm-c live.paper rows
    23:49:1x-2x + 6 only-mine rows 23:51:4x-50), ts-sorted append order, zero loss (r188)
NO auto-push: caller runs pre-continue marker scan then git -c core.editor=true rebase --continue."""
import io
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(*args, binary=False):
    p = subprocess.run(["git"] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={p.returncode}: {p.stderr[:300].decode('utf-8', 'replace')}")
    return p.stdout if binary else p.stdout.decode("utf-8", errors="replace")


def blob(stage, path):
    return git("show", f"{stage}:{path}", binary=True)


def write_bytes(path, data):
    io.open(path, "wb").write(data)


def take(stage, path, log, why):
    write_bytes(path, blob(stage, path))
    log.append(f"  {path}: take-{'OURS' if stage == ':2' else 'MINE'} ({why})")


def fmt_detect(b):
    crlf = b"\r\n" in b
    txt = b.decode("utf-8")
    indent = 1
    for line in txt.splitlines():
        if line.startswith('  "') or line.startswith("  {") or line.startswith("  ["):
            indent = 2
            break
        if line.startswith('   "'):
            indent = 3
            break
    non_ascii = any(ord(c) > 127 for c in txt)
    return crlf, indent, not non_ascii


def write_mirror(path, obj, mirror_bytes):
    crlf, indent, asc = fmt_detect(mirror_bytes)
    txt = json.dumps(obj, ensure_ascii=asc, indent=indent) + "\n"
    data = txt.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    write_bytes(path, data)


MINE_TAKE_SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def main():
    log = []
    # 1) snapshots: all take-MINE (probe 23:50-23:52 > 23:48-23:49)
    for p in MINE_TAKE_SNAPSHOTS:
        take(":3", p, log, "snapshot deep-probe MINE fresher (r100/R350 hardened)")
    # 2) twins same-side MINE (byte copies from MINE blob)
    take(":3", "docs/daily_report/REPORT-2026-09-27.md", log, "twin-coupled same-side MINE byte-copy (r329)")
    take(":3", "results/dashboard_status.js", log, "dash pair same-side MINE whole-bytes wrapper (R209)")
    # 3) autofill_state: launches identical + last_tick OURS strictly fresher -> take OURS whole
    take(":2", "results/autofill_state.json", log, "launches 47=47 identical + last_tick ours 23:50:02 > mine 23:50:01 (dict-ts compare)")
    # 4) regime_state: history/transitions identical both sides -> take MINE fresher 'updated'
    take(":3", "results/regime_state.json", log, "history 2+2 & transitions identical, updated 23:50:33 > 23:48:44")
    # 5) compute_audit: rolling-ledger ts-key union no-cap + state face take-MINE
    a = json.loads(blob(":2", "results/compute_audit.json").decode("utf-8"))
    b = json.loads(blob(":3", "results/compute_audit.json").decode("utf-8"))
    ha, hb = a.get("history", []), b.get("history", [])
    ka = {r.get("ts") for r in ha}
    kb = {r.get("ts") for r in hb}
    merged = {}
    div = []
    for r in ha:
        merged[r.get("ts")] = r
    for r in hb:
        t = r.get("ts")
        if t in merged:
            sa, sb = set(merged[t]), set(r)
            if merged[t] != r:
                if sb >= sa:
                    merged[t] = r  # mine field-superset of ours (r322)
                elif sa >= sb:
                    pass  # ours superset, keep ours
                else:
                    div.append(t)  # true divergence -> fail-closed
        else:
            merged[t] = r
    assert not div, f"compute_audit same-ts true-divergence rows, manual: {div}"
    assert set(merged.keys()) == (ka | kb), "union key loss"
    rows = sorted(merged.values(), key=lambda r: r.get("ts", ""))
    out = dict(b)  # state face take-MINE (freshest producer 23:50:30)
    out["history"] = rows
    write_mirror("results/compute_audit.json", out, blob(":3", "results/compute_audit.json"))
    log.append(f"  results/compute_audit.json: history union {len(ha)}+{len(hb)} -> {len(rows)} (distinct {len(ka | kb)}, no-cap zero-loss r360-law), state face MINE")
    # 6) x2_watch_log: line-level union zero-loss, ts-sorted
    xa = blob(":2", "results/x2_watch_log.jsonl").decode("utf-8").splitlines()
    xb = blob(":3", "results/x2_watch_log.jsonl").decode("utf-8").splitlines()
    union = sorted(set(xa) | set(xb), key=lambda ln: (json.loads(ln).get("ts", ""), ln))
    assert len(union) == len(set(xa) | set(xb)), "x2 union loss"
    data = ("\n".join(union) + "\n").encode("utf-8")
    if b"\r\n" in blob(":3", "results/x2_watch_log.jsonl"):
        data = data.replace(b"\n", b"\r\n")
    write_bytes("results/x2_watch_log.jsonl", data)
    log.append(f"  results/x2_watch_log.jsonl: line union {len(xa)}+{len(xb)} -> {len(union)} (only-ours 6 bm-c rows + only-mine 6 rows, ts-sorted, zero loss r188)")
    # parse-verify every resolved face (r185 law)
    verify = MINE_TAKE_SNAPSHOTS + [
        "docs/daily_report/REPORT-2026-09-27.md",
        "results/autofill_state.json",
        "results/compute_audit.json",
        "results/regime_state.json",
        "results/dashboard_status.js",
        "results/x2_watch_log.jsonl",
    ]
    for p in verify:
        raw = io.open(p, "rb").read()
        assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, f"markers left: {p}"
        if p.endswith(".js"):
            assert b"window.DASH_DATA" in raw and raw.rstrip().endswith(b"};"), f"js wrapper broken: {p}"
        elif p.endswith(".jsonl"):
            for i, ln in enumerate(raw.decode("utf-8").splitlines()):
                if ln.strip():
                    json.loads(ln)
        elif p.endswith(".json"):
            json.loads(raw.decode("utf-8"))
    # autofill last_tick dict-shape assertion (canon)
    af = json.loads(io.open("results/autofill_state.json", encoding="utf-8").read())
    assert isinstance(af.get("last_tick"), dict), "last_tick not dict"
    print(f"PARSE-VERIFY {len(verify)}/{len(verify)} OK (marker-clean + json/jsonl-valid + js-wrapper + last_tick dict)")
    for l in log:
        print(l)
    git("add", "--", *verify)
    rem = [p for p in git("diff", "--name-only", "--diff-filter=U").strip().splitlines() if p]
    assert rem == [], f"unexpected remaining UU set: {rem}"
    print("remaining UU: none -- rebase --continue ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())
