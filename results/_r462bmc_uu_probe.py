"""r462 bm-c UU structural probe: for each conflicted face, extract ts-class
fields from BOTH sides (git show HEAD:/MERGE_HEAD: raw bytes, r657 law 2),
line counts for jsonl faces, per-key presence for machines-type faces.
File-out per r446 law. Zero console CJK print."""
import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = ROOT + r"\results\_r462bmc_uu_probe.json"

UU = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
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
    "results/pool_core_samples.jsonl",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/x2_watch_log.jsonl",
]

TS_KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "clock",
           "asof", "saved_at", "written_at", "written", "now", "time", "date")


def git_show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                        cwd=ROOT, creationflags=0x08000000)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def norm_ts(v):
    if not isinstance(v, str):
        return None
    s = v.strip()
    if len(s) < 10:
        return None
    return s.replace("T", " ")[:19]


def face_facts(blob):
    """Return dict of ts candidates + key hints for one side's bytes."""
    facts = {"bytes": len(blob)}
    txt = blob.decode("utf-8", "replace")
    if path.endswith((".jsonl",)) or path.endswith("x2_watch_log.jsonl") or path.endswith("pool_core_samples.jsonl"):
        lines = [ln for ln in txt.split("\n") if ln.strip()]
        facts["nonempty_lines"] = len(lines)
        # first/last line ts probe
        for tag, ln in (("first", lines[0] if lines else ""),
                        ("last", lines[-1] if lines else "")):
            try:
                j = json.loads(ln)
                tss = {k: norm_ts(j.get(k)) for k in TS_KEYS if isinstance(j.get(k), str)}
                if tss:
                    facts[tag + "_ts"] = tss
            except Exception:
                pass
        return facts
    if path.endswith(".js"):
        facts["head"] = txt[:200].replace("\n", " ")
        # generated ts probe in JS text
        import re
        m = re.search(r'(?:generated|updated|ts)["\x27]?\s*[:=]\s*["\x27](\d{4}-\d{2}-\d{2}[T ][\d:]+)', txt)
        if m:
            facts["ts_in_text"] = norm_ts(m.group(1))
        return facts
    try:
        j = json.loads(txt)
    except Exception as e:
        facts["parse_error"] = repr(e)[:120]
        facts["head"] = txt[:200].replace("\n", " ")
        return facts
    facts["top_keys"] = sorted(j.keys())[:20] if isinstance(j, dict) else None
    if isinstance(j, dict):
        tss = {}
        for k in TS_KEYS:
            if k in j:
                tss[k] = norm_ts(j[k])
        if tss:
            facts["top_ts"] = tss
        for sub in ("machines", "per_machine", "by_machine"):
            if isinstance(j.get(sub), dict):
                facts[sub + "_keys"] = sorted(j[sub].keys())
                per = {}
                for mk, mv in j[sub].items():
                    if isinstance(mv, dict):
                        for k in TS_KEYS:
                            if isinstance(mv.get(k), str):
                                per[mk] = {k: norm_ts(mv[k])}
                                break
                if per:
                    facts[sub + "_ts"] = per
    return facts


ev = {"ts": None, "faces": {}}
import datetime
ev["ts"] = datetime.datetime.now().isoformat(timespec="seconds")
for path in UU:
    entry = {}
    for side, ref in (("ours", "HEAD"), ("theirs", "MERGE_HEAD")):
        rc, blob, err = git_show(ref, path)
        if rc != 0:
            entry[side] = {"show_rc": rc, "err": err[:120]}
        else:
            entry[side] = face_facts(blob)
    ev["faces"][path] = entry
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("UU_PROBE_DONE faces=", len(UU))
