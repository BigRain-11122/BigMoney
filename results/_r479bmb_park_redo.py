"""r479 bm-b fix-up: vocabulary-legal park (defer_note per r378 catch #4) +
harvest done-flip for empirically-complete P2NULL shards S0/S1 (r180 wedge law:
done shards never re-fire; results single-shot complete = empirical done)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARK_NOTE = (
    "r479 bm-b deliberate defer 21:38: astock universe refresh in-flight since "
    "21:09:13 (spawn pid 47564 on bm-b); this burn consumes the astock panel -> "
    "mid-refresh launches die at in-runner FAIL-CLOSED gates as false crashes "
    "(FACEB 20:40 precedent + r479 park-first lesson). Un-defer = bm-b round "
    "post-settle (refresh process exit + panel complete verified), defer_note "
    "cleared on flip-back per r378 convention."
)
PARK_IDS = ["EXCLUSION-MARGINAL-P1-RUN", "CROSS-START-ROBUSTNESS-P1-FACEB-RUN"]
POOL_FILES = [
    os.path.join(ROOT, "results", "runnable_pool.json"),
    os.path.join(ROOT, "results", "runnable_pool.bm-b.json"),
]


def verify_shard(path, n_expected_runs):
    """Single-shot result file integrity: parses, expected run count."""
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception as ex:
        return False, f"parse-fail {ex}"
    runs = d.get("runs")
    if isinstance(runs, list):
        n = len(runs)
    else:
        n = d.get("n_runs") or d.get("n_trials")
        if n is None:
            fams = d.get("families") or d.get("results") or {}
            n = sum(len(v) if isinstance(v, list) else 0
                    for v in fams.values()) if isinstance(fams, dict) else 0
    okflag = isinstance(n, int) and n == n_expected_runs
    return okflag, f"n_runs={n} expected={n_expected_runs} keys={list(d)[:8]}"


def main():
    # 1) vocabulary-legal park
    for pf in POOL_FILES:
        with open(pf, encoding="utf-8") as fh:
            pool = json.load(fh)
        changed = False
        for e in pool.get("entries", []):
            if e.get("id") in PARK_IDS and e.get("status") == "ready":
                e["status"] = "waiting"
                e["defer_note"] = PARK_NOTE
                # drop the unrecognized marker from the first attempt
                e.pop("parked_note", None)
                e.pop("parked_by", None)
                e.pop("parked_at", None)
                changed = True
        if changed:
            with open(pf, "w", encoding="utf-8") as fh:
                json.dump(pool, fh, indent=1, ensure_ascii=False)
            print("PARKED(vocab)", os.path.basename(pf))
    # 2) S0/S1 integrity
    for sh, fn, exp in ((0, "shard-0-of-4.json", 550), (1, "shard-1-of-4.json", 550)):
        p = os.path.join(ROOT, "results", "p2cal_ext", fn)
        ok, msg = verify_shard(p, exp)
        print(f"shard-{sh} integrity: {ok} | {msg}")


if __name__ == "__main__":
    sys.exit(main())
