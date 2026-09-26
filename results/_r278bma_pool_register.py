"""R278 bm-a: register REV-OSC-STOCK-P1 into results/runnable_pool.json.

Byte faces probed (R255/R257 laws): no BOM, CRLF, indent=1, no trailing
newline -- written back with identical faces. Appends one entry; existing
entries byte-untouched.
"""
import json
import os

POOL = os.path.join("results", "runnable_pool.json")
raw = open(POOL, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" in raw and not raw.endswith(b"\n")
pool = json.loads(raw)
assert not any(e.get("id") == "REV-OSC-STOCK-P1" for e in pool["entries"]), \
    "entry already present"

entry = {
    "id": "REV-OSC-STOCK-P1",
    "ticket_ref": "T-2026-09-26-87 s2 first-priority slot (CEO O-2026-09-26-2330 oversold-rebound special pick + O-2026-09-26-2335 refine-bench dispatch; claimed bm-a R277)",
    "prereg_ref": "research/REV_OSC_STOCK_PREREG.md FROZEN a7761433 precedes runner build 0182a8cf precedes ANY run (R99); zero-run amendments: dual-face universe sentinel 4ac879f9 (r251 probe-authoritative); seed rev_osc_stock_p1=20261230 registered at freeze commit; RANDOM_LARGE_SAMPLE_LAW v1.0 binding (7 judged cells x2 faces + 2000 nulls + full-census virtual starts + block-bootstrap/sign-flip dual nulls)",
    "runner": "scripts/rev_osc_stock_p1.py",
    "runner_args": ["run"],
    "lane_owner": "bm-a",
    "priority": 1,
    "status": "ready",
    "entered_at": "2026-09-27 00:31:00",
    "data_gates": "in-runner fail-closed exit 2: cache shape T==8792/N==5222 + dates[0]==1990-12-19 + dates[-1]==2026-09-22 (D2 lockbox) + sse coverage>=0.97 + mask rows 5222 + ok_static 3517 + bars symbol census + dual-face universe sentinel (full-grid median>=150 AND 2010+ median>=500); free-RAM<16GB exit 3; per-cell JSON+npy idempotent checkpoints; finalize single-shot (REV_OSC_STOCK_P1_REFINALIZE=1 = only redo); selftest 15/15 pre-pooling (r263 law); real-data gate probe PASSED 2026-09-27 00:2x (medians 194/1116, thin-1990s honest skip verified)",
    "workers_plan": {
        "workers": 1,
        "priority": "BelowNormal",
        "note": "single finalize dependency chain (panel load ~90s + 14 cell-face serial sims + 2000 null cohorts + 2000 synthetic null runs + vstarts/bootstrap vectorized); RAM peak ~3GB (float32 panels + column copies); workers=1 light-batch precedent T33/GRID-P1/CN-family; autofill sets BelowNormal on launch; est 10-30min wall"
    },
    "shards": [
        {
            "key": "revosc-0of1",
            "status": "ready",
            "owner": None,
            "owner_since": None,
            "checkpoint": "results/rev_osc/cells/<cell>_<face>.json (+.npy, gitignored t22 precedent) per-cell-face idempotent skip; landed marker = results/rev_osc/p1_results.json with ledger block; harvest = pool flip done by next round per r244 landed-marker law (batch does not flip itself)"
        }
    ],
    "note": "lane pinned bm-a (r188 precedent): p1c_stock cache + b_layer mask + ew6 D6 member faces machine-local; data channel = p1c cache in-place (O-2330 s3 faster path -- akshare forward collector = bm-b r279 supply lane, zero collision: judged batch consumes frozen panel, forward/paper leg consumes the collector later)"
}
pool["entries"].append(entry)
pool["updated_at"] = "2026-09-27 00:31:00"
text = json.dumps(pool, ensure_ascii=False, indent=1)
data = text.replace("\n", "\r\n").encode("utf-8")
assert not data.endswith(b"\n")
with open(POOL, "wb") as fh:
    fh.write(data)
chk = json.loads(open(POOL, "rb").read())
assert len(chk["entries"]) == 51 and chk["entries"][-1]["id"] == entry["id"]
print("pool entry appended: REV-OSC-STOCK-P1 ready (51 entries)")
