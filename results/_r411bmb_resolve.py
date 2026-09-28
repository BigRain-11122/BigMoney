# -*- coding: utf-8 -*-
"""r411 bm-b rebase-conflict resolver (skill: bigmoney-conflict-resolve).

Conflict face: my mid-round commit (T-105 v1.3 slice + S6 partial products)
replaying on top of origin 8df049dc3 (bm-c round-199 S6 completion, same-day
page regens + shared compute_audit write).

Classifier verdicts:
  - docs/daily_report/REPORT-2026-09-29.{md,json}  snapshot  -> take-new by
    generated ts, twins same side (r98/r99/r100)
  - docs/live_usage/LIVE-2026-09-29.{md,json}      UNKNOWN -> manual class:
    same-day idempotent regen dated page (same family as daily report
    snapshot) -> same recipe, twins same side
  - results/compute_audit.json                    rolling-ledger -> union
    history zero-loss + newest snapshot fields take-new (deep ts probe,
    r188/R208/r311)

Post-resolution: rerun ceo_live_usage.py + daily_report.py (v1.3 code) to
regenerate today's pages deterministically -> final content authoritative.
"""
import json
import subprocess
import sys

ROOT = r"E:\Fluxgroup\FluxGroup\quant\bigmoney"


def blob(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"], cwd=ROOT,
                         capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"git show :{stage}:{path} rc={out.returncode}")
    return out.stdout.decode("utf-8-sig")


def jload(stage, path):
    return json.loads(blob(stage, path))


def write(path, text):
    with open(path.replace("/", "\\"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(text)


def resolve_pages():
    """Take-new by generated ts; twins same side; SAME side for md+json
    decided by the json ts (single probe point)."""
    decisions = []
    for base in ("docs/live_usage/LIVE-2026-09-29",
                 "docs/daily_report/REPORT-2026-09-29"):
        pjson = base + ".json"
        pmd = base + ".md"
        s2, s3 = jload(2, pjson), jload(3, pjson)
        t2 = s2.get("generated") or s2.get("generated_at")
        t3 = s3.get("generated") or s3.get("generated_at")
        side = 3 if str(t3) >= str(t2) else 2   # same-second tie -> HEAD-side
        # rebase inversion: stage3 = my replayed commit (HEAD of replay)
        src = blob(side, pjson)
        srcmd = blob(side, pmd)
        write(pjson, src)
        write(pmd, srcmd)
        decisions.append({"path": base, "ts_s2": str(t2), "ts_s3": str(t3),
                          "took_stage": side})
    return decisions


def resolve_audit():
    """rolling-ledger: union history rows (dedupe by identity of full row
    ts+machine), newest latest by deep ts probe; deep-scan compare path."""
    s2, s3 = jload(2, "results/compute_audit.json"), \
        jload(3, "results/compute_audit.json")
    h2 = s2.get("history") or []
    h3 = s3.get("history") or []
    seen = {}
    for row in h2 + h3:
        key = (str(row.get("ts")), str(row.get("machine")),
               json.dumps(row.get("flags"), sort_keys=True))
        seen.setdefault(key, row)
    merged = sorted(seen.values(), key=lambda r: str(r.get("ts")))
    cap = s3.get("history_cap") or s2.get("history_cap") or 200
    merged = merged[-int(cap):] if cap else merged
    # newest snapshot fields: deep ts probe on nested latest.ts
    def deepts(d):
        lat = d.get("latest") or {}
        return str(lat.get("ts") or d.get("ts") or "")
    base = s3 if deepts(s3) >= deepts(s2) else s2   # tie -> replay side
    out = dict(base)
    out["history"] = merged
    n2, n3 = len(h2), len(h3)
    assert len(merged) >= max(n2, n3), "union zero-loss violated"
    text = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    write("results/compute_audit.json", text)
    return {"history_s2": n2, "history_s3": n3, "history_merged":
            len(merged), "latest_from": "s3" if base is s3 else "s2",
            "deepts_s2": deepts(s2), "deepts_s3": deepts(s3)}


def main():
    pages = resolve_pages()
    audit = resolve_audit()
    # parse-validate every written json (r185 law)
    for p in ("docs/live_usage/LIVE-2026-09-29.json",
              "docs/daily_report/REPORT-2026-09-29.json",
              "results/compute_audit.json"):
        with open(p.replace("/", "\\"), encoding="utf-8") as fh:
            json.load(fh)
    print(json.dumps({"pages": pages, "audit": audit},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
