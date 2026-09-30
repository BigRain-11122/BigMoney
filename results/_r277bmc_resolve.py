"""r277 bm-c rebase collision resolver (20-UU, skill bigmoney-conflict-resolve canon).

Rebase replay of round-277 commit 9912221e6 vs origin/main (bm-a r477+r478
same-window lanes: S6 snapshot family + their own CODELY <=10KB hot-cold reorg).
Helpers deep_ts/take_new_snapshot/twin/raw/write are VERBATIM from the r478
canon resolver results/_r478bma_resolve.py (禁重写律: canon mechanism reuse).

Classifications (this storm):
- CODELY.md: BOTH sides ran the <=10KB hot-cold reorg on overlapping entry sets.
  Origin (bm-a r478) archived 7 entries incl. THE SAME 5 I archived (r466/r276/
  r462/r468/r469) and already carries the merged pointer line -> r449 dedup
  law: drop my duplicate pointer line, keep origin base, insert my UNIQUE r277
  pit entry at Project tail (r327 entry-level law). Zero-loss proof: each of my
  5 migrated entries asserted verbatim inside origin's archive section.
- research/memory-archive/202609.md: my r277 section duplicates 5 of origin's 7
  r478-section entries (asserted verbatim) -> take :2: (origin) whole; my
  section adds zero unique lines (r449 no-resurrect).
- snapshots take-new via staged-blob ts probe (r100 hardened): _attrition_
  guard_scan/compute_audit/dashboard_status/futures_update_status/lhb_update_
  status/prospect_promotion/_summary/regime_state/scorecard_v1/strategy_
  scorecard/token_usage/update_status.
- dashboard_status.js: embedded-ts regex probe decides side (R209 js-wrapper
  snapshot law, honest probe instead of assumption).
- docs twins (REPORT/LIVE/LIVE-latest): json side by generated ts, md
  byte-copied from SAME side (twin-side coupling r329).
"""
import json
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def raw(stage: str, path: str) -> bytes:
    r = subprocess.run(["git", "show", f"{stage}:{path}"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"blob read failed {stage}:{path} rc={r.returncode} err={r.stderr[:120]}")
    return r.stdout


def write(path: str, data: bytes):
    with open(path, "wb") as f:
        f.write(data)


def deep_ts(obj, out, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = k.lower().replace("_", "").replace("-", "")
            if isinstance(v, str) and v[:2] == "20" and (
                "ts" in kl or "generated" in kl or "updated" in kl or "asof" in kl or "at" == kl[-2:]
            ):
                if "T" in v or " " in v[10:]:
                    out[f"{prefix}/{k}"] = v
            deep_ts(v, out, f"{prefix}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:5]):
            deep_ts(v, out, f"{prefix}[{i}]")


def take_new_snapshot(path: str):
    o = json.loads(raw(':2', path))
    l = json.loads(raw(':3', path))
    to, tl = {}, {}
    deep_ts(o, to)
    deep_ts(l, tl)
    if not to and not tl:
        if raw(':2', path) == raw(':3', path):
            write(path, raw(':2', path))
            return "identical"
        raise RuntimeError(f"{path}: no ts probe, sides differ -- manual adjudication required")
    omax = max(to.values()) if to else ""
    lmax = max(tl.values()) if tl else ""
    side = ":2" if omax >= lmax else ":3"
    write(path, raw(side, path))
    return f"take {side} (o={omax} l={lmax})"


def twin(base_dir: str, stem: str):
    j, m = f"{base_dir}/{stem}.json", f"{base_dir}/{stem}.md"
    oj, lj = json.loads(raw(':2', j)), json.loads(raw(':3', j))
    og, lg = oj.get("generated_at", oj.get("generated", "")), lj.get("generated_at", lj.get("generated", ""))
    if not og or not lg:
        raise RuntimeError(f"twin {j}: no generated/generated_at probe on one side -- manual adjudication")
    side = ":2" if og >= lg else ":3"
    write(j, raw(side, j))
    write(m, raw(side, m))
    return f"twin {side} (o={og} l={lg})"


MY_ARCHIVED_PREFIXES = ("- [2026-09-30 r466 bm-b]",
                        "- [2026-09-30 r276 bm-c]",
                        "- [2026-09-30 r462 bm-b]",
                        "- [2026-09-30 r468 bm-b]",
                        "- [2026-09-30 r469 bm-b]")


def main():
    log = []

    # 1) zero-loss proof + archive take-origin
    archive_o = raw(':2', "research/memory-archive/202609.md").decode("utf-8")
    archive_l = raw(':3', "research/memory-archive/202609.md").decode("utf-8")
    my_moved = [ln for ln in archive_l.splitlines() if ln.startswith(MY_ARCHIVED_PREFIXES)]
    assert len(my_moved) == 5, f"expected my 5 migrated entries in :3: archive section, got {len(my_moved)}"
    for m in my_moved:
        assert m in archive_o, f"zero-loss violation: entry not in origin archive: {m[:60]}"
    write("research/memory-archive/202609.md", raw(':2', "research/memory-archive/202609.md"))
    log.append("archive: take :2: (my 5 migrated entries all verbatim inside origin r478 section; "
              "my r277 section = pure duplicate, dropped per r449 no-resurrect)")

    # 2) CODELY: origin base + insert my UNIQUE r277 pit entry at Project tail
    o = raw(':2', "CODELY.md").decode("utf-8")
    base = raw(':1', "CODELY.md").decode("utf-8")
    codely_l = raw(':3', "CODELY.md").decode("utf-8")
    new_local = [x for x in codely_l.splitlines()
                 if x not in set(o.splitlines()) and x not in set(base.splitlines())
                 and x.strip().startswith("- [") and "r277" in x]
    assert len(new_local) == 1, f"expected exactly 1 unique r277 entry line, got {len(new_local)}"
    for ln in new_local:
        assert ln not in o, "r277 entry already in origin?"
    marker = "### Reference"
    ol = o.splitlines()
    idx = ol.index(marker)
    merged = ol[:idx] + new_local + ol[idx:]
    content = "\n".join(merged) + ("\n" if o.endswith("\n") else "")
    write("CODELY.md", content.encode("utf-8"))
    size = len(content.encode("utf-8"))
    assert size <= 10240, f"CODELY.md over 10KB after merge: {size}"
    log.append(f"CODELY.md: origin base + r277 pit entry inserted before ### Reference "
               f"(origin {len(ol)} -> merged {len(merged)} lines, {size}B <=10KB)")

    # 3) snapshots take-new
    for p in ["results/_attrition_guard_scan.json", "results/compute_audit.json",
              "results/dashboard_status.json", "results/futures_update_status.json",
              "results/lhb_update_status.json", "results/prospect_promotion/_summary.json",
              "results/regime_state.json", "results/scorecard_v1.json",
              "results/strategy_scorecard.json", "results/token_usage.json",
              "results/update_status.json"]:
        log.append(f"{p}: {take_new_snapshot(p)}")

    # 4) dashboard_status.js: embedded-ts regex probe decides side
    p = "results/dashboard_status.js"
    ts_re = re.compile(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d(:\d\d)?")
    oj, lj = raw(':2', p).decode("utf-8", errors="replace"), raw(':3', p).decode("utf-8", errors="replace")
    ot, lt = ts_re.findall(oj), ts_re.findall(lj)
    omax = max(ot) if ot else ""
    lmax = max(lt) if lt else ""
    side = ":2" if omax >= lmax else ":3"
    write(p, raw(side, p))
    log.append(f"{p}: take {side} (embedded ts o={omax} l={lmax})")

    # 5) docs twins
    log.append(twin("docs/daily_report", "REPORT-2026-09-30"))
    log.append(twin("docs/live_usage", "LIVE-2026-09-30"))
    log.append(twin("docs/live_usage", "LIVE-latest"))

    for line in log:
        print(line)
    print(f"\nOK {len(log)} faces resolved")


if __name__ == "__main__":
    sys.exit(main())
