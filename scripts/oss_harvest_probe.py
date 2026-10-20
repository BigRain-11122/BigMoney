"""OSS 72h harvest probe -- BigMoney entity slice.

Mechanism: cph4/oss-harvest.md v1.0 (OSS 借力机制·每 72h 一轮滚动窗,
每实体每窗 >=1 次收获切片: 实搜面 >=1 处 + 候选五门评估, 或如实零发现).
Deadline face: D-20261020-12 routes the OSS over-window roster with a
10-21 24:00 deadline; bigmoney's last filing was 2026-10-08.

This script mechanizes the machine-checkable half of the five gates so the
filing is evidence-backed instead of hand-typed:

  gate 2 反重复   -- candidate name/url collides with an already-adopted
                     tool in research/OSS_HARVEST_LEDGER.md or with an
                     in-repo dependency surface (requirements.txt /
                     imports under scripts+firm+live).
  gate 3 许可     -- GitHub license spdx_id: MIT/Apache-2.0/BSD-* = 直用;
                     NOASSERTION/other = 需逐件验原文; GPL/AGPL = 禁入
                     产品交付链 (hard reject).
  gate 4 健康     -- stars >= MIN_STARS and pushed within MAX_AGE_DAYS.
  gate 5 成本     -- python repo, size under MAX_MB (local-runnable
                     envelope), not archived.

Gate 1 (契合) is a keyword->business-line mapping table kept here so the
report carries a one-line "替谁省什么/补什么" claim per candidate; the
human still owns the final call (寻源闸: 有轮=直接用/适配).

Network: GitHub search API, anonymous, <=3 calls per run, 1.2s spacing.
Output: results/oss_harvest/OH-<YYYYMMDD>-bigmoney.json + a ready-to-file
markdown body (stdout + file) so the daily filings stay mechanical.

Usage:
  python scripts/oss_harvest_probe.py scan [--queries N] [--per-page N]
  python scripts/oss_harvest_probe.py selftest
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RES_DIR = os.path.join(_ROOT, "results", "oss_harvest")
LEDGER = os.path.join(_ROOT, "research", "OSS_HARVEST_LEDGER.md")

# -- frozen parameter face (changing these is a prereg-level act) ----------
QUERIES = [
    # (query, business-line keyword map)
    ("quantitative trading backtest", "研究/策略"),
    ("technical indicators python", "工程/数据"),
]
MIN_STARS = 1000
MAX_AGE_DAYS = 180
MAX_MB = 60.0
GPL_FAMILY = ("GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0")
DIRECT_OK = ("MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC",
             "CC0-1.0", "Unlicense")
# in-repo dependency surface (gate 2 collision face); generated from
# requirements.txt + grep'd imports, kept explicit so the report is stable.
IN_REPO_DEPS = (
    "akshare", "tushare", "numpy", "pandas", "scipy", "statsmodels",
    "sklearn", "matplotlib", "requests", "pyarrow", "madmom", "librosa",
    "soundfile", "whisperx", "torch", "optuna", "duckdb", "polars",
)


def _today():
    return _dt.date.today().strftime("%Y%m%d")


def _norm(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def known_adopted(ledger_text: str):
    """Tool names already recorded in the harvest ledger (any section)."""
    txt = ledger_text or ""
    names = set()
    for m in re.finditer(r"\|\s*(?:S|E|A)\d+\s*\|\s*\*{0,2}([A-Za-z0-9_.\- ]+)", txt):
        names.add(_norm(m.group(1)))
    for m in re.finditer(r"github\.com/[A-Za-z0-9_.\-]+/([A-Za-z0-9_.\-]+)", txt):
        names.add(_norm(m.group(1)))
    return {n for n in names if len(n) >= 3}


def gate_license(spdx):
    s = (spdx or "").upper()
    if not s or s in ("NOASSERTION", "NONE"):
        return "VERIFY_SOURCE"
    if any(g in s for g in GPL_FAMILY):
        return "REJECT_GPL"
    if any(d.upper() in s for d in DIRECT_OK):
        return "DIRECT_OK"
    return "VERIFY_SOURCE"


def gate_health(repo, now=None):
    now = now or _dt.datetime.now(_dt.timezone.utc)
    stars = int(repo.get("stargazers_count") or 0)
    pushed = repo.get("pushed_at") or ""
    age_days = None
    if pushed:
        try:
            ts = _dt.datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=_dt.timezone.utc)
            age_days = (now - ts).total_seconds() / 86400.0
        except Exception:
            age_days = None
    ok = stars >= MIN_STARS and age_days is not None and age_days <= MAX_AGE_DAYS \
        and not repo.get("archived")
    return {"stars": stars, "age_days": None if age_days is None else round(age_days, 1),
            "archived": bool(repo.get("archived")), "ok": ok}


def gate_cost(repo):
    lang = (repo.get("language") or "").lower()
    size_mb = round(int(repo.get("size") or 0) / 1024.0, 2)
    ok = lang == "python" and size_mb <= MAX_MB
    return {"language": lang or None, "size_mb": size_mb, "ok": ok}


def gate_dedupe(name, url):
    hay = _norm(name) + " " + _norm(url.split("/")[-1] if url else "")
    hits = [d for d in IN_REPO_DEPS if _norm(d) and _norm(d) in hay]
    return {"in_repo_dep_hits": hits, "ok": not hits}


def evaluate(repo, ledger_names, line):
    name = repo.get("name") or ""
    url = repo.get("html_url") or ""
    lic = gate_license((repo.get("license") or {}).get("spdx_id"))
    dedupe = gate_dedupe(name, url)
    health = gate_health(repo)
    cost = gate_cost(repo)
    known = _norm(name) in ledger_names
    if lic == "REJECT_GPL":
        verdict = "REJECT_GPL"
    elif known:
        verdict = "DUPLICATE_ADOPTED"
    elif dedupe["in_repo_dep_hits"]:
        verdict = "DUPLICATE_IN_REPO"
    elif lic == "VERIFY_SOURCE":
        verdict = "PARKED_VERIFY_LICENSE"
    elif not (health["ok"] and cost["ok"]):
        verdict = "PARKED_HEALTH_OR_COST"
    else:
        verdict = "ADOPT_CANDIDATE"
    return {
        "name": name, "repo": repo.get("full_name"), "url": url,
        "spdx": (repo.get("license") or {}).get("spdx_id"),
        "license_gate": lic, "dedupe": dedupe, "health": health,
        "cost": cost, "already_adopted": known,
        "business_line": line, "verdict": verdict,
        "desc": (repo.get("description") or "")[:200],
        "fit_claim": "",
    }


_FIT_CLAIMS = {
    "研究/策略": "替研究员省因子库自建与外源寻源工时；补研究链数据/回测基础设施",
    "工程/数据": "替工程席省指标/数据管道自写工时；补采集器与面板计算底座",
}


def fetch(query, per_page):
    import urllib.request
    import urllib.parse
    q = urllib.parse.quote(query)
    url = ("https://api.github.com/search/repositories?q=" + q +
           "&sort=stars&order=desc&per_page=%d" % int(per_page))
    req = urllib.request.Request(url, headers={"User-Agent": "bm-b-oss-probe"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def build_report(payloads, ledger_text, date_str=None):
    date_str = date_str or _today()
    names = known_adopted(ledger_text)
    out = []
    for (query, line), payload in zip(QUERIES, payloads):
        for repo in (payload.get("items") or []):
            rec = evaluate(repo, names, line)
            rec["fit_claim"] = _FIT_CLAIMS.get(line, "")
            rec["query"] = query
            out.append(rec)
    # dedupe within the run (same repo can answer two queries)
    seen, uniq = set(), []
    for rec in out:
        key = rec["repo"]
        if key in seen:
            continue
        seen.add(key)
        uniq.append(rec)
    counts = {}
    for rec in uniq:
        counts[rec["verdict"]] = counts.get(rec["verdict"], 0) + 1
    body = _markdown(uniq, counts, date_str)
    return {
        "schema": "oss_harvest_probe/v1",
        "generated": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "date": date_str,
        "queries": [q for q, _ in QUERIES],
        "params": {"min_stars": MIN_STARS, "max_age_days": MAX_AGE_DAYS,
                   "max_mb": MAX_MB},
        "counts": counts, "candidates": uniq,
        "oh_body": body,
    }


def _markdown(recs, counts, date_str):
    d = "%s-%s-%s" % (date_str[:4], date_str[4:6], date_str[6:])
    lines = [
        "# OH-%s-bigmoney" % date_str,
        "",
        "- 窗: %s（滚动窗；上一件 OH-20261008-bigmoney，超窗件按 D-20261020-12 补办）" % d,
        "- 实搜面: GitHub search API 匿名检索 %d 条查询（%s），取 star 头部样本" % (
            len(QUERIES), " / ".join(q for q, _ in QUERIES)),
        "- 候选: 见下表（名称·源URL·许可·契合点）",
        "- 采用→落点: 见 verdict=ADOPT_CANDIDATE 行；本次无生产采用时如实记 0",
        "- parked+理由: DUPLICATE_* / PARKED_* 行理由随表",
        "- 下窗指针: 下一滚动窗同一 P0（deadline 面已清）",
        "",
        "| 仓库 | star | 许可 | 判定 | 契合点 |",
        "|---|---|---|---|---|",
    ]
    for r in recs[:12]:
        lines.append("| %s | %s | %s | %s | %s |" % (
            r["repo"], r["health"]["stars"], r["spdx"] or "NONE",
            r["verdict"], r["business_line"]))
    lines += ["", "计数: " + json.dumps(counts, ensure_ascii=False)]
    return "\n".join(lines)


def cmd_scan(queries_n, per_page):
    ledger_text = ""
    if os.path.exists(LEDGER):
        with open(LEDGER, "r", encoding="utf-8", errors="replace") as f:
            ledger_text = f.read()
    payloads = []
    for i, (q, _line) in enumerate(QUERIES[:queries_n]):
        if i:
            time.sleep(1.2)
        payloads.append(fetch(q, per_page))
    report = build_report(payloads, ledger_text)
    os.makedirs(RES_DIR, exist_ok=True)
    path = os.path.join(RES_DIR, "OH-%s-bigmoney.json" % report["date"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({"ok": True, "path": os.path.relpath(path, _ROOT),
                      "counts": report["counts"]}, ensure_ascii=False))
    for r in report["candidates"]:
        if r["verdict"] == "ADOPT_CANDIDATE":
            print("ADOPT %s %s %s" % (r["repo"], r["health"]["stars"], r["spdx"]))
    return 0


# --------------------------------------------------------------- selftest
class _R(dict):
    pass


def _mk(name, stars=5000, spdx="MIT", pushed="2026-10-15T00:00:00Z",
        lang="python", size=5000, archived=False):
    return {"name": name, "full_name": "x/" + name, "html_url":
            "https://github.com/x/" + name, "stargazers_count": stars,
            "license": {"spdx_id": spdx} if spdx else None, "pushed_at": pushed,
            "language": lang, "size": size, "archived": archived,
            "description": "d"}


def cmd_selftest():
    fails = []
    now = _dt.datetime(2026, 10, 20, tzinfo=_dt.timezone.utc)

    # license gates
    if gate_license("MIT") != "DIRECT_OK":
        fails.append("mit")
    if gate_license("AGPL-3.0") != "REJECT_GPL":
        fails.append("agpl")
    if gate_license("GPL-3.0") != "REJECT_GPL":
        fails.append("gpl")
    if gate_license("NOASSERTION") != "VERIFY_SOURCE":
        fails.append("noassertion")
    if gate_license(None) != "VERIFY_SOURCE":
        fails.append("none-lic")

    # health gate
    if not gate_health(_mk("a"), now)["ok"]:
        fails.append("health-ok")
    if gate_health(_mk("a", stars=10), now)["ok"]:
        fails.append("health-stars")
    if gate_health(_mk("a", pushed="2020-01-01T00:00:00Z"), now)["ok"]:
        fails.append("health-stale")
    if gate_health(_mk("a", archived=True), now)["ok"]:
        fails.append("health-archived")

    # cost gate
    if not gate_cost(_mk("a"))["ok"]:
        fails.append("cost-ok")
    if gate_cost(_mk("a", lang="C++"))["ok"]:
        fails.append("cost-lang")
    if gate_cost(_mk("a", size=200000))["ok"]:
        fails.append("cost-size")

    # dedupe gate
    if gate_dedupe("akshare", "https://github.com/x/akshare")["ok"]:
        fails.append("dedupe-dep")
    if not gate_dedupe("brandnewtool", "https://github.com/x/brandnewtool")["ok"]:
        fails.append("dedupe-clean")

    # verdict precedence: GPL beats everything
    rec = evaluate(_mk("akshare", spdx="AGPL-3.0"), set(), "工程/数据")
    if rec["verdict"] != "REJECT_GPL":
        fails.append("prec-gpl")
    # already-adopted beats in-repo dedupe
    rec = evaluate(_mk("qlib"), {_norm("qlib")}, "研究/策略")
    if rec["verdict"] != "DUPLICATE_ADOPTED":
        fails.append("prec-known")
    # clean MIT healthy -> adopt candidate
    rec = evaluate(_mk("brandnewtool"), set(), "研究/策略")
    if rec["verdict"] != "ADOPT_CANDIDATE":
        fails.append("prec-adopt")

    # report shape + markdown body
    rep = build_report([{"items": [_mk("brandnewtool")]},
                        {"items": [_mk("othertool")]}], "", "20261020")
    if rep["counts"].get("ADOPT_CANDIDATE") != 2:
        fails.append("report-counts")
    if not rep["oh_body"].startswith("# OH-20261020-bigmoney"):
        fails.append("report-body")
    # cross-query dedupe
    rep2 = build_report([{"items": [_mk("brandnewtool")]},
                         {"items": [_mk("brandnewtool")]}], "", "20261020")
    if len(rep2["candidates"]) != 1:
        fails.append("report-dedupe")

    # ledger name extraction
    names = known_adopted("| S1 | **qlib** | github.com/microsoft/qlib | MIT |")
    if _norm("qlib") not in names:
        fails.append("ledger-parse")

    total = 20
    if fails:
        print(json.dumps({"selftest": "FAIL", "fails": fails}, ensure_ascii=False))
        return 1
    print(json.dumps({"selftest": "PASS", "legs": total}, ensure_ascii=False))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(prog="oss_harvest_probe")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("scan")
    s.add_argument("--queries", type=int, default=len(QUERIES))
    s.add_argument("--per-page", type=int, default=5)
    sub.add_parser("selftest")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return cmd_selftest()
    if args.cmd == "scan":
        return cmd_scan(args.queries, args.per_page)
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())