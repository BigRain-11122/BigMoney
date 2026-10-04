"""r668 bm-a THEME-JUDGE-P1 panel-build pre-pool probe (cheap census before
burn; zero simulate calls, zero burn_state writes). Validates the real-data
faces the hermetic selftest cannot: dedup/strata/twin/drop gates/calendar/
ride windows/digest. Pool burn re-checks everything fail-closed anyway."""
import json
import sys
import time

sys.path.insert(0, "scripts")
sys.path.insert(0, "results")

import theme_judge_p1 as R  # noqa: E402


def main() -> int:
    t0 = time.time()
    kept, byday, facts = R._load_episodes()
    meta, _, _ = R._build_panels(kept, byday, facts)
    rides = meta["rides"]
    by_st = {}
    for r in rides:
        by_st[r["stratum"]] = by_st.get(r["stratum"], 0) + 1
    out = {
        "facts": facts,
        "digest": meta["digest"],
        "n_calendar_days": len(meta["calendar"]),
        "n_rides": len(rides),
        "rides_by_stratum": by_st,
        "n_famous_rides": sum(1 for r in rides if r["famous"]),
        "tercile_sizes": {g: sum(1 for r in rides if r["tercile"] == g)
                          for g in range(3)},
        "wlen_stats": {
            "min": min(r["wlen"] for r in rides),
            "max": max(r["wlen"] for r in rides),
            "full_751": sum(1 for r in rides if r["wlen"] == 751),
        },
        "elapsed_sec": round(time.time() - t0, 1),
    }
    print(json.dumps(out, ensure_ascii=False, indent=1)[:2400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
