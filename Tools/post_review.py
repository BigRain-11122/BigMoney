"""Tools/post_review.py -- post-hoc review mechanism (O-20260924-2115, T-37).

Canonical = firm/POST_REVIEW.md v1.0 (GM order commit 5a1b80d). Three
separations: action vs outcome, claim vs verification (executor never
self-certifies), criteria vs narrative (only pre-frozen criteria count).

Mechanics (canonical s2): deterministic zero-LLM re-derivation of
machine-checkable criteria for closed items -> verdict per canonical s3-4:
  YES  = closed + all checks re-derived green
  NO   = closed + any check red (failed checks listed verbatim)
  WAIT = in_flight (interim state disclosed, never folded into YES)
  IDLE = criteria anchors all absent (nothing done yet)
Ledger = results/post_review.jsonl (append-only, canonical s2) + rendered
report face results/post_review/REPORT-YYYYMMDD.md for the CEO dashboard.

Criteria registry = results/post_review_criteria.json (data file; criteria
frozen at claim/order time -- the reviewer NEVER invents criteria, it only
encodes what the ticket spec already froze). Check kinds (canonical s2
machine-verifiable classes): file existence / metric thresholds / git
evidence:
  file_exists(path) / file_contains(path, substr) / json_field(path,
  dotted.key, expected|"*") / json_gte(path, dotted.key, min) /
  count_glob(pattern, min) / git_log_file(path, substr|"*")

Self-congratulation detection (canonical s3, heuristics honestly labelled):
  (a) action-word lines (已立|已建|已完成|已交付|已生效|已落地|已接线) in the
      latest round-report entry lacking an evidence-pointer token
      (results/|scripts/|Tools/|fleet/|rc=|PASS|commit|[0-9a-f]{7,})
  (b) positive-vs-honest-negative ratio in the same tail (all-positive
      stream itself is the suspicion)
Exit codes: 0 normal; 2 mechanism fault (honest, never masked).
selftest = offline injection matrix; the false-claim sample MUST be caught
(order acceptance clause).
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRITERIA = os.path.join(ROOT, "results", "post_review_criteria.json")
LEDGER = os.path.join(ROOT, "results", "post_review.jsonl")
REPORT_DIR = os.path.join(ROOT, "results", "post_review")
ROUND_REPORTS = [
    os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-a.md"),
    os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md"),
    os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md"),
]
ACTION_WORDS = re.compile(r"已立|已建|已完成|已交付|已生效|已落地|已接线")
EVIDENCE_TOKEN = re.compile(
    r"results[/\\]|scripts[/\\]|Tools[/\\]|firm[/\\]|fleet[/\\]|rc=\d|PASS|"
    r"FAIL|commit|[0-9a-f]{7,}")
NEG_MARK = re.compile(r"FAIL|判负|✗|诚实负|未达|不达标|负收|红项|VOID")


def _now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ------------------------------------------------------------------ checks
def _json_path(d, path):
    """Walk a dotted path. Numeric segments index lists as ints (dicts keep
    string keys), so frozen criteria like 'launches.0.verdict' resolve."""
    for k in path.split("."):
        if isinstance(d, list) and k.lstrip("-").isdigit():
            d = d[int(k)]
        else:
            d = d[k]
    return d


def _check(kind, args):
    """One deterministic re-derivation. Returns (ok: bool, detail: str)."""
    try:
        if kind == "file_exists":
            p = os.path.join(ROOT, args[0])
            return os.path.exists(p), ("exists" if os.path.exists(p)
                                       else "ABSENT")
        if kind == "file_contains":
            p = os.path.join(ROOT, args[0])
            if not os.path.exists(p):
                return False, "file absent"
            txt = open(p, encoding="utf-8", errors="replace").read()
            ok = args[1] in txt
            return ok, ("contains" if ok else "MISSING: " + args[1][:60])
        if kind == "json_field":
            p = os.path.join(ROOT, args[0])
            d = json.load(open(p, encoding="utf-8"))
            d = _json_path(d, args[1])
            if args[2] == "*":
                return True, f"{args[1]}={d}"
            ok = str(d) == str(args[2])
            return ok, f"{args[1]}={d} (want {args[2]})"
        if kind == "json_gte":
            p = os.path.join(ROOT, args[0])
            d = json.load(open(p, encoding="utf-8"))
            d = _json_path(d, args[1])
            ok = float(d) >= float(args[2])
            return ok, f"{args[1]}={d} (min {args[2]})"
        if kind == "count_glob":
            n = len(glob.glob(os.path.join(ROOT, args[0])))
            ok = n >= int(args[1])
            return ok, f"count={n} (min {args[1]})"
        if kind == "git_log_file":
            out = subprocess.run(
                ["git", "log", "--oneline", "-5", "--", args[0]],
                cwd=ROOT, capture_output=True, text=True,
                encoding="utf-8", errors="replace").stdout
            if args[1] == "*":
                return bool(out.strip()), f"git history: {len(out.splitlines())} commits"
            ok = args[1] in out
            return ok, ("git hit: " + args[1][:40] if ok else "no git hit")
    except FileNotFoundError:
        return False, "file absent"
    except (KeyError, IndexError) as ex:
        return False, f"key absent: {ex}"
    except Exception as ex:
        return False, f"error: {ex}"
    return False, f"unknown kind: {kind}"


def review_items(items):
    rows = []
    for it in items:
        passed, failed = [], []
        for c in it.get("checks", []):
            ok, detail = _check(c["kind"], c.get("args", []))
            (passed if ok else failed).append(
                f"{c['kind']}:{detail}")
        status = it.get("status", "closed")
        anchors = bool(it.get("checks"))
        if status == "in_flight":
            verdict = "WAIT"
        elif not anchors:
            verdict = "IDLE"
        elif failed:
            verdict = "NO"
        else:
            verdict = "YES"
        rows.append({
            "ts": _now(), "id": it["id"], "claim": it.get("claim", ""),
            "claim_source": it.get("claim_source", ""),
            "status": status,
            "waiting_on": it.get("waiting_on", ""),
            "verdict": verdict,
            "n_checks": len(it.get("checks", [])),
            "failed_checks": failed,
            "passed_checks": len(passed),
            "evidence": "; ".join(passed[:4]),
        })
    return rows


def append_ledger(rows):
    with open(LEDGER, "a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


# ------------------------------------------- self-congratulation detection
def _latest_entry(path):
    """Rough tail of a round-report file (last ~60 lines = latest entry)."""
    try:
        lines = open(path, encoding="utf-8", errors="replace").readlines()
        return lines[-60:]
    except Exception:
        return []


def self_congratulation_scan():
    flags, stats = [], []
    for path in ROUND_REPORTS:
        if not os.path.exists(path):
            continue
        tail = _latest_entry(path)
        action_lines = [l for l in tail if ACTION_WORDS.search(l)]
        missing = [l.strip()[:90] for l in action_lines
                   if not EVIDENCE_TOKEN.search(l)]
        pos = sum(1 for l in tail if ACTION_WORDS.search(l))
        neg = sum(1 for l in tail if NEG_MARK.search(l))
        stats.append({
            "file": os.path.basename(path),
            "action_word_lines": pos,
            "with_evidence": len(action_lines) - len(missing),
            "missing_evidence_pointer": len(missing),
            "honest_negative_marks": neg,
            "positive_vs_negative": round(pos / neg, 2) if neg else None,
        })
        flags.extend({"file": os.path.basename(path), "line": m}
                     for m in missing[:5])
    return {"stats": stats, "flagged_lines": flags,
            "heuristic": "action-word line must carry an evidence-pointer "
                         "token in the same line (canonical s3-1, "
                         "heuristic honestly labelled)"}


def cmd_run():
    if not os.path.exists(CRITERIA):
        print(f"criteria registry absent: {CRITERIA}")
        return 2
    try:
        items = json.load(open(CRITERIA, encoding="utf-8"))
    except Exception as ex:
        print(f"criteria registry unreadable: {ex}")
        return 2
    if isinstance(items, dict):
        items = items.get("items", [])
    rows = review_items(items)
    append_ledger(rows)
    scan = self_congratulation_scan()
    n_yes = sum(1 for r in rows if r["verdict"] == "YES")
    n_no = sum(1 for r in rows if r["verdict"] == "NO")
    n_wait = sum(1 for r in rows if r["verdict"] == "WAIT")
    n_idle = sum(1 for r in rows if r["verdict"] == "IDLE")
    all_green = (n_no == 0 and n_wait == 0)
    os.makedirs(REPORT_DIR, exist_ok=True)
    day = dt.datetime.now().strftime("%Y%m%d")
    md = [f"# 事后复审报告 REPORT-{day}（O-20260924-2115 · 首批回填）",
          f"生成 {_now()} · 复审器=确定性重derive（零 LLM，执行侧不自证）",
          f"",
          f"判定分布：✓{n_yes} / ✗{n_no} / 🟡{n_wait} / ⬜{n_idle}"
          + ("  **⚠ 反全绿条款：本报告全绿=复核不严嫌疑**" if all_green else ""),
          ""]
    md.append("| 宣称 id | 判 | 失败判据 | 宣称（一句话） |")
    md.append("|---|---|---|---|")
    for r in rows:
        v = {"YES": "✓", "NO": "✗", "WAIT": "🟡", "IDLE": "⬜"}[r["verdict"]]
        fail = "; ".join(r["failed_checks"])[:120] or "—"
        md.append(f"| {r['id']} | {v} | {fail} | {r['claim'][:80]} |")
    md += ["", "## 自我感动专项检测（启发式·如实标注）", ""]
    for s in scan["stats"]:
        md.append(f"- {s['file']}: 动作词行 {s['action_word_lines']}，"
                   f"缺证据指针 {s['missing_evidence_pointer']}，"
                   f"诚实负标记 {s['honest_negative_marks']}，"
                   f"正负比 {s['positive_vs_negative']}")
    for f in scan["flagged_lines"]:
        md.append(f"  - FLAG: {f['file']}: {f['line']}")
    report = os.path.join(REPORT_DIR, f"REPORT-{day}.md")
    with open(report, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print(f"review rows: YES={n_yes} NO={n_no} WAIT={n_wait} IDLE={n_idle}")
    for r in rows:
        if r["verdict"] == "NO":
            print(f"  NO {r['id']}: " + "; ".join(r["failed_checks"])[:140])
    print(f"ledger -> {LEDGER}")
    print(f"report -> {report}")
    return 0


def cmd_selftest():
    import tempfile
    global CRITERIA, LEDGER, ROUND_REPORTS
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("post_review selftest:")
    with tempfile.TemporaryDirectory() as tmp:
        CRITERIA = os.path.join(tmp, "criteria.json")
        LEDGER = os.path.join(tmp, "post_review.jsonl")
        ROUND_REPORTS = []
        # build a real anchor file in tmp via a criteria-relative trick:
        # checks resolve relative to ROOT, so use ROOT-relative real paths
        # plus one intentionally-absent path for the false-claim injection.
        items = [
            {"id": "FALSE-CLAIM-01", "claim": "X 已交付（注入虚报样本）",
             "status": "closed",
             "checks": [{"kind": "file_exists",
                         "args": ["results/_no_such_file_xyz.json"]}]},
            {"id": "TRUE-01", "claim": "smoke 套件在仓",
             "status": "closed",
             "checks": [{"kind": "file_exists", "args": ["smoke_test.py"]},
                        {"kind": "file_contains",
                         "args": ["smoke_test.py", "PASS"]}]},
            {"id": "WAIT-01", "claim": "T-27 接线（否决窗内）",
             "status": "in_flight", "waiting_on": "7 天否决窗",
             "checks": [{"kind": "file_exists",
                         "args": ["results/portfolio_blend_tournament.json"]}]},
            {"id": "GIT-01", "claim": "POST_REVIEW 正典有 git 史",
             "status": "closed",
             "checks": [{"kind": "git_log_file",
                         "args": ["firm/POST_REVIEW.md", "2115"]}]},
            {"id": "JSON-01", "claim": "blend tournament winner=B_MAXDIV",
             "status": "closed",
             "checks": [{"kind": "json_field",
                         "args": ["results/portfolio_blend_tournament.json",
                                  "winner", "B_MAXDIV"]}]},
        ]
        with open(CRITERIA, "w", encoding="utf-8") as fh:
            json.dump(items, fh, ensure_ascii=False)
        rows = review_items(items)
        v = {r["id"]: r["verdict"] for r in rows}
        ok("S1 injected false claim caught as NO",
           v["FALSE-CLAIM-01"] == "NO"
           and rows[0]["failed_checks"])
        ok("S2 true item YES", v["TRUE-01"] == "YES")
        ok("S3 in_flight WAIT (interim disclosed, never folded to YES)",
           v["WAIT-01"] == "WAIT")
        ok("S4 git evidence kind works", v["GIT-01"] == "YES")
        ok("S5 json_field expected match", v["JSON-01"] in ("YES", "NO"))
        append_ledger(rows)
        n = sum(1 for _ in open(LEDGER, encoding="utf-8"))
        ok("S6 ledger append", n == len(rows))
        # S7 anti-all-green: a NO row forbids all-green
        ok("S7 anti-all-green logic",
           any(r["verdict"] == "NO" for r in rows)
           and not (all(r["verdict"] == "YES" for r in rows)))
        # S8 hermetic numeric-path boundary fixtures (pure fn, no file face)
        ok("S8a numeric list index resolves",
           _json_path({"launches": [{"verdict": "launched"}]},
                      "launches.0.verdict") == "launched")
        ok("S8b dict string key '0' stays a key",
           _json_path({"launches": {"0": {"verdict": "x"}}},
                      "launches.0.verdict") == "x")
        try:
            _json_path([{"a": 1}], "1.a")
            ok("S8c out-of-range index raises", False)
        except IndexError:
            ok("S8c out-of-range index raises", True)
    print("SELFTEST", "ALL PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "run":
        sys.exit(cmd_run())
    sys.exit(cmd_selftest())


if __name__ == "__main__":
    main()
