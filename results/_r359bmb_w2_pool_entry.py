# -*- coding: utf-8 -*-
"""r359 bm-b: append TRIAL_LAB_W2_GENERATE to results/runnable_pool.json.

Prereg sec.6 pool routing: generate is minutes-scale (sec.0 light face) but
>5min + peak RAM ~1.5-2GB on a machine currently at 0.87GB free (W2B census
burn holds ~12.4GB) -> pool route with waiting status as the ONLY RAM
protection (autofill has no RAM gate; MASS-TRIAL-W1-JUDGE flip-gate
precedent) + in-runner three-sample fail-closed gate (defense in depth).
Idempotent: refuses if the entry id already exists.
"""
import json
import time

POOL = "results/runnable_pool.json"

with open(POOL, encoding="utf-8") as fh:
    p = json.load(fh)

if any(e.get("id") == "TRIAL-LABOR-W2-GENERATE" for e in p["entries"]):
    print("entry TRIAL-LABOR-W2-GENERATE already present -- no-op")
    raise SystemExit(0)

ts = time.strftime("%Y-%m-%d %H:%M:%S")
entry = {
    "id": "TRIAL-LABOR-W2-GENERATE",
    "ticket_ref": "T-2026-09-28-96 WAVE-2 generate slice (CEO O-2026-09-27-2245 thousand-trader order + O-2026-09-27-2250 standing law; prereg FROZEN r357, grammar face frozen r358 sha16=1dd3d95792395cec; runner generate subcommand built bm-b r359 selftest 29/29 hermetic; bm-c MSG-20260928-0450 zero-objection receipt on the MSG-0440 dual disclosures)",
    "prereg_ref": "research/TRIAL_LABOR_W2_PREREG.md FROZEN (sec.3 Sobol raw 5000 = A500/B4500 five-tuple axis incl. initial-stop face; sec.1 four-source exclusion law -- w1_screen.json survivors 149 consumed generate-time, w1_judge + MASS judged declared-unavailable zero rows no fabrication; dedup T-84 s3 fingerprint + |corr|>=0.999 on the effective signal face; D6 max|corr| disclosure column naive caliber; seeds trial_labor_w2_gen/scrnull/unc=20285500/20286000/20286500 R250; TRIAL_GRAMMAR_LEDGER wave-2 row appended at consume point)",
    "runner": "scripts/trial_labor_w2.py",
    "runner_args": ["generate"],
    "lane_owner": None,
    "priority": 1,
    "status": "waiting",
    "entered_at": ts,
    "workers_plan": {
        "workers": 1,
        "priority": "BelowNormal",
        "note": "LIGHT minutes-scale per prereg sec.0 (~10-20min: 5000 signal "
                "builds + vectorized stop-overlay dedup face + 5000x5000 "
                "naive-corr); single-process streaming, masks dropped "
                "per-candidate (W1 r348 RAM law); peak ~1.5-2GB (series "
                "110MB + corr 200MB + core48 panel). FLIP GATE waiting->ready "
                "= machine free RAM >= 4GB three-sample (r354 law; autofill "
                "has no RAM gate so waiting status is the ONLY protection; "
                "W2B census burn holds ~12.4GB until finalize). Flip = round "
                "work per r203 law, any machine.",
    },
    "data_gates": "in-runner fail-closed exit 2: (a) w2_candidates.json "
                  "exists -> refuse (same-grammar rerun ban, single-shot); "
                  "(b) grammar sha anchor != 1dd3d95792395cec -> refuse; "
                  "(c) free RAM three-sample < 4GB -> honest refuse. deps "
                  "all green in-repo git: core48 panel + w2_grammar.json "
                  "(r358) + w1_screen.json survivors 149; w1_judge + MASS "
                  "judged exclusion sources declared-unavailable at generate "
                  "time (pool-waiting, zero rows, disclosed in product "
                  "audit)",
    "shards": [
        {
            "key": "generate-0of1",
            "status": "waiting",
            "owner": None,
            "owner_since": None,
            "checkpoint": "results/trial_labor_w2/w2_candidates.json "
                          "(single-shot product = completion marker; "
                          "refuse-if-exists guard)",
            "note": "single shard minutes-scale; products = w2_candidates.json "
                    "+ TRIAL_GRAMMAR_LEDGER wave-2 row (consume point); "
                    "SCREEN pool entry lands next slice after the runner "
                    "screen subcommand exists (anti-dup: no pool entry "
                    "pointing at a not-yet-built subcommand)",
        }
    ],
}
p["entries"].append(entry)
p["updated_at"] = ts
with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(p, fh, ensure_ascii=False, indent=1)
chk = json.load(open(POOL, encoding="utf-8"))
assert any(e["id"] == "TRIAL-LABOR-W2-GENERATE" for e in chk["entries"])
print(f"appended TRIAL-LABOR-W2-GENERATE (status=waiting, priority=1, "
      f"entered_at={ts}); total entries {len(chk['entries'])}")
