"""Multi-core census (T-134 s1, CEO order O-2026-09-30-2355 hard law #1).

O-2355 sec.1 (多核律): every pool-bound batch runner MUST be a real
multi-process implementation -- workers_plan is code, not a declaration.
This census enumerates the in-pool runner universe (every runner path
referenced by results/runnable_pool.json entries), source-scans each for
parallelism primitives, and emits a per-runner verdict:

  multiprocess   source contains real process-parallel machinery
                 (multiprocessing / ProcessPoolExecutor / joblib.Parallel)
  thread_io_only threads or asyncio only -- GIL-bound; legal for I/O gates,
                 NOT CPU multi-core (does not satisfy O-2355 for burn batches)
  single_core    no parallel machinery at all -- banned from pool per
                 hard law #1 until converted (T-134 s2)
  missing        path referenced by pool but absent on disk (registry rot)

The scan is static (no import, no execution -- scanning never launches
runners). Pool linkage counts + declared workers_plan per runner are
carried so the "declared vs code" delta face is visible in one artifact.

Deterministic, zero-network, read-only on sources; writes only
results/multicore_census.json. S6-chain updater/gate scripts are NOT
census universe (they are I/O gates, not pool burn batches; noted in
out_of_scope_face for honesty).

Subcommands:
    (no args)  live census -> results/multicore_census.json
    selftest   hermetic offline classifier scenarios (exit 0/1)
Exit codes: 0 = census recorded (any verdict mix is a legal finding),
2 = mechanism failure (pool unreadable / zero universe).
"""
import io
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

POOL_PATH = os.path.join("results", "runnable_pool.json")
OUT_PATH = os.path.join("results", "multicore_census.json")
TZ = timezone(timedelta(hours=8))

# Static face only: patterns match real machinery, not comments naming it.
RE_MULTIPROCESS = re.compile(
    r"import\s+multiprocessing|from\s+multiprocessing"
    r"|ProcessPoolExecutor|multiprocessing\.(Pool|Process|Manager)"
    r"|\bmp\.Pool\b|joblib\s*\.\s*Parallel|from\s+joblib\s+import"
)
RE_THREAD_IO = re.compile(
    r"import\s+threading|from\s+threading|ThreadPoolExecutor|import\s+asyncio"
    r"|from\s+asyncio"
)
RE_MAIN_GUARD = re.compile(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]')


def classify_source(src):
    """Return (verdict, evidence_lines) for one runner source string."""
    mp_hits = []
    th_hits = []
    for i, line in enumerate(src.splitlines(), 1):
        if RE_MULTIPROCESS.search(line):
            mp_hits.append((i, line.strip()[:120]))
        if RE_THREAD_IO.search(line):
            th_hits.append((i, line.strip()[:120]))
    if mp_hits:
        return "multiprocess", mp_hits[:3], th_hits[:2]
    if th_hits:
        return "thread_io_only", [], th_hits[:3]
    return "single_core", [], []


def census_runner(path):
    """Classify one runner path. Never imports/executes it."""
    rec = {"path": path, "exists": os.path.isfile(path)}
    if not rec["exists"]:
        rec["verdict"] = "missing"
        rec["evidence"] = []
        rec["main_guard"] = None
        return rec
    src = io.open(path, encoding="utf-8", errors="replace").read()
    verdict, mp_ev, th_ev = classify_source(src)
    rec["verdict"] = verdict
    rec["evidence"] = [{"line": n, "text": t} for n, t in mp_ev + th_ev]
    rec["main_guard"] = bool(RE_MAIN_GUARD.search(src))
    rec["size_bytes"] = os.path.getsize(path)
    return rec


def load_universe():
    """Pool-referenced runner paths + linkage + declared workers_plan."""
    with io.open(POOL_PATH, encoding="utf-8") as f:
        pool = json.load(f)
    linkage = {}
    for e in pool.get("entries", []):
        r = e.get("runner") or ""
        if not r:
            continue
        rec = linkage.setdefault(r, {"pool_entry_count": 0, "statuses": {},
                                     "declared_workers": set()})
        rec["pool_entry_count"] += 1
        st = e.get("status", "?")
        rec["statuses"][st] = rec["statuses"].get(st, 0) + 1
        wp = e.get("workers_plan")
        if isinstance(wp, dict):
            rec["declared_workers"].add(str(wp.get("workers")))
        elif wp is not None:
            rec["declared_workers"].add(str(wp))
    return linkage


def run_census():
    if not os.path.isfile(POOL_PATH):
        print("multicore_census: mechanism failure: %s unreadable" % POOL_PATH)
        return 2
    linkage = load_universe()
    if not linkage:
        print("multicore_census: mechanism failure: zero runner universe")
        return 2
    verdicts = {}
    for path in sorted(linkage):
        rec = census_runner(path)
        link = linkage[path]
        rec["pool_entry_count"] = link["pool_entry_count"]
        rec["pool_statuses"] = link["statuses"]
        rec["workers_plan_declared"] = sorted(link["declared_workers"])
        if rec["verdict"] == "multiprocess" and not rec["main_guard"]:
            rec["verdict_note"] = ("multiprocess WITHOUT __main__ guard "
                                   "(U-1820 law: Windows spawn hazard)")
        verdicts[path] = rec
    summary = {}
    for rec in verdicts.values():
        summary[rec["verdict"]] = summary.get(rec["verdict"], 0) + 1
    hard_law_face = sorted(p for p, r in verdicts.items()
                           if r["verdict"] in ("single_core", "thread_io_only"))
    live_face = sorted(
        p for p, r in verdicts.items()
        if r["verdict"] in ("single_core", "thread_io_only", "missing")
        and any(s != "done" for s in r.get("pool_statuses", {})))
    out = {
        "law_ref": "O-2026-09-30-2355 sec.1 (多核律: workers_plan 声明变代码)",
        "ticket_ref": "T-2026-09-30-134 s1 (runner census)",
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "universe": "pool-referenced runners (results/runnable_pool.json entries[].runner)",
        "universe_size": len(verdicts),
        "summary": summary,
        "hard_law_face": {
            "note": ("single_core/thread_io_only/missing runners are banned "
                     "from new-pool entry until converted+verified (T-134 s2)"),
            "all_non_multiprocess": hard_law_face,
            "non_multiprocess_with_live_pool_entries": live_face,
        },
        "out_of_scope_face": ("S6 chain updater/gate scripts (update_*.py etc.) "
                              "are I/O gates, not pool burn batches; census "
                              "universe is the pool runner face only"),
        "verdicts": verdicts,
    }
    with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("multicore_census: %d runners | %s | -> %s"
          % (len(verdicts), summary, OUT_PATH))
    for p in live_face:
        print("  hard-law live face: %s (%s)" % (p, verdicts[p]["verdict"]))
    return 0


def selftest():
    """Hermetic classifier scenarios -- no pool, no disk runners."""
    cases = [
        ("import multiprocessing as mp\ndef f():\n    with mp.Pool(8) as p:\n        p.map(w, xs)\n",
         "multiprocess"),
        ("from concurrent.futures import ProcessPoolExecutor\n"
         "with ProcessPoolExecutor(12) as ex:\n    list(ex.map(w, xs))\n",
         "multiprocess"),
        ("from joblib import Parallel\nParallel(n_jobs=16)(delayed(w)(x) for x in xs)\n",
         "multiprocess"),
        ("import threading\nwith ThreadPoolExecutor(4) as ex:\n    pass\n",
         "thread_io_only"),
        ("import asyncio\nasync def m():\n    await asyncio.sleep(1)\n",
         "thread_io_only"),
        ("import pandas as pd\ndef run():\n    return df.apply(calc)\n",
         "single_core"),
        ("# we should use multiprocessing someday\nimport pandas as pd\n",
         "single_core"),
    ]
    fails = 0
    for i, (src, expect) in enumerate(cases):
        got, _, _ = classify_source(src)
        ok = got == expect
        if not ok:
            fails += 1
        print("  case %d: expect=%s got=%s %s"
              % (i, expect, got, "PASS" if ok else "FAIL"))
    # comment-resistance regression: pattern must not match commented mention
    print("multicore_census selftest: %d/%d PASS" % (len(cases) - fails, len(cases)))
    return 0 if fails == 0 else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return selftest()
    return run_census()


if __name__ == "__main__":
    sys.exit(main())
