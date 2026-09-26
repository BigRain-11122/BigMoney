# r284 bm-a pool register: CN_SOE_ETF_P1 entry append (single_writer =
# session round). Byte-face mirror: no BOM / CRLF / indent=1 /
# ensure_ascii=False / no trailing newline (r255/r257 laws); write-back
# must land as a field-increment-level diff (--stat gate).
import json, time

POOL = "results/runnable_pool.json"
raw = open(POOL, "rb").read()
crlf = b"\r\n" in raw
assert not raw[:3] == b"\xef\xbb\xbf", "BOM face drift"
assert not raw.endswith(b"\n"), "trailing-newline face drift"
p = json.loads(raw.decode("utf-8"))

assert not any(e["id"] == "CN_SOE_ETF_P1" for e in p["entries"]), \
    "entry already present (idempotence guard)"

entry = {
    "id": "CN_SOE_ETF_P1",
    "ticket_ref": "T-2026-09-26-87 s2 queue #2 zhongtegu SOE sleeve "
                 "(SCHOOL_SUPPLY_S1.md sec.2 queue order, zero-invention; "
                 "claimed bm-a R277; F-04 MSG-20260927-0135-bm-a declared "
                 "R283 before freeze commit)",
    "prereg_ref": "research/CN_SOE_ETF_PREREG.md FROZEN ba54b43f precedes "
                  "runner build precedes ANY run (R99); seed "
                  "cn_soe_etf_p1=20272301 registered at freeze commit "
                  "(band 20272301..20274300); RANDOM_LARGE_SAMPLE_LAW v1.0 "
                  "binding (5 judged x2 cells + 2000 same-mask "
                  "weekly-Bernoulli nulls p=LEGMA200 duty + full-census "
                  "virtual starts vs sleeve-EW baseline + "
                  "block-bootstrap/sign-flip dual nulls)",
    "runner": "scripts/cn_soe_etf_p1.py",
    "runner_args": ["run"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "data_gates": "in-runner fail-closed exit 2: name-face universe "
                  "re-derive==frozen 8 roster cross-check + truncated-face "
                  "last==2026-09-22 zero-NaN + sse coverage>=0.95 + "
                  "per-cell JSON+npy idempotent checkpoints + finalize "
                  "single-shot (CN_SOE_ETF_P1_REFINALIZE=1 = only redo); "
                  "selftest 34/34 pre-pooling (r263 law, incl r286 family "
                  "legs: np-native coercion + _compute_cells assembly "
                  "glue + div-cross dated reconstruction); real-data gate "
                  "probe PASSED 2026-09-27 01:5x bm-a (T=2445 N=8 "
                  "sse_cover 1.0, panel load 0.2s, SOE_HOLD x2 sharpe "
                  "0.3915 entries=8 structural, SOE_REPAIR 13 entries 3 "
                  "episodes 2020-03/2022-04/2022-10 within prereg s5 "
                  "band, LOWVOL3 30 entries, all dump sites json-clean)",
    "workers_plan": {
        "workers": 4, "priority": "BelowNormal",
        "note": "nulls via shared parallel_runner run_cells_parallel "
                "(4 procs, keyed consumption r259 law); judged 10 "
                "cell-face serial sims ~0.5s each; est wall 4-8min; RAM "
                "peak <1GB"},
    "shards": [{"key": "cnsoe-0of1", "status": "ready", "owner": None,
                "owner_since": None, "checkpoint": None}],
    "note_done": None,
}
p["entries"].append(entry)
p["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

out = json.dumps(p, ensure_ascii=False, indent=1)
data = out.encode("utf-8")
if crlf:
    data = data.replace(b"\n", b"\r\n")
json.loads(data.decode("utf-8"))            # parse-verify BEFORE write
with open(POOL, "wb") as fh:
    fh.write(data)
print("entry appended: CN_SOE_ETF_P1 ready, entries=%d" % len(p["entries"]))
