"""R256 bm-a: pool submit CN-REGIME-POLICY-P1 (T-73 s3 slice-3).

Single-writer law (pool schema): the submitter writes the entry.
Byte faces probed from the HEAD blob per R254/R255 four-face law:
no BOM / LF-only / indent=1 / ensure_ascii=False (verified this round).
"""
import io
import json
import subprocess
import time

POOL = "results/runnable_pool.json"

raw = subprocess.run(["git", "show", "HEAD:results/runnable_pool.json"],
                     capture_output=True).stdout
assert raw[:3] != b"\xef\xbb\xbf", "unexpected BOM face"
lines = raw.decode("utf-8").split("\n")
indent = len(lines[1]) - len(lines[1].lstrip())
assert indent == 1, f"unexpected indent face {indent}"

p = json.load(io.open(POOL, encoding="utf-8"))
assert not any(e.get("id") == "CN-REGIME-POLICY-P1"
               for e in p["entries"]), "entry already exists"

ts = time.strftime("%Y-%m-%d %H:%M:%S")
p["entries"].append({
    "id": "CN-REGIME-POLICY-P1",
    "ticket_ref": "T-2026-09-26-73 s3 slice-3 (CEO O-20260926-0926 "
                  "CN-native combo models; bm-a lane)",
    "prereg_ref": "research/CN_REGIME_POLICY_PREREG.md (frozen R256 "
                  "commit 124b360c, precedes any run; scope-down face "
                  "per s2-sliceB digest law: policy axis = defensive "
                  "risk-condition only, P4B={4,7,10,12}; zero runs)",
    "runner": "scripts/cn_regime_policy_p1.py",
    "runner_args": ["run"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": ts,
    "data_gates": "in-runner fail-closed exit 2: corpus 3483 bars "
                  "2012-05-28..2026-09-22 + OHLCV zero NaN + volume>0 "
                  "+ v3 states full-cover (imported frozen deep-replay "
                  "layer) + state set == ladder key set + cutoff=="
                  "2026-09-22 (D2 lockbox) + C(12,4)==495 exhaustive "
                  "assert + T+1 asserted (R240 law) + zero-trades void "
                  "refusal + 1% ADV cap runtime-asserted non-binding "
                  "(probe margin 3.8x; violation = refusal). Judge face "
                  "x2; buys lot-rounded with r251 afford loop; sells "
                  "exact-share; ADV20 warmup 19 bars cash-honest.",
    "shards": [{
        "key": "regimepolicy-0of1",
        "status": "ready",
        "owner": None,
        "owner_since": None,
        "checkpoint": "results/cn_regime_policy/sims.npz (exact-resume "
                      "contract: n_days+first+last match else recompute); "
                      "landed marker = results/cn_regime_policy/"
                      "p1_results.json with trials_ledger block "
                      "(r252 canonical key); idempotent fast path exit 0 "
                      "after finalize (CN_REGIME_POLICY_P1_REFINALIZE=1 = "
                      "only redo); harvest = pool flip done by next "
                      "round per r244 landed-marker law",
    }],
    "workers_plan": {
        "workers": 1,
        "note": "single finalize dependency chain (3 cells x3 faces -> "
                "990 exhaustive variants -> null pool -> gates A/B/C -> "
                "D6/PBO -> ledger); est 1-2 min (10-variant probe 0.1s -> "
                "990 ~14s + deep-replay 1s + shared-lib gates); "
                "single-writer ledger finalize = 1 worker",
    },
    "note": "N=993 on the D1 bill (3 judged cells + 990 exhaustive "
            "C(12,4) month-set nulls, zero RNG zero seeds per slice-B "
            "exhaustive precedent); supply-line duty answer to "
            "pool_starvation flag (R255 disclosure: research landed -> "
            "prereg -> runner+pool same round R256)",
    "updated_at": ts,
})
p["updated_at"] = ts
with io.open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(p, fh, ensure_ascii=False, indent=1)
print("pool entry appended: CN-REGIME-POLICY-P1 ready at", ts)
