import json

P = "results/runnable_pool.json"
raw = open(P, "rb").read()
txt = raw.decode("utf-8")
assert txt.endswith("}\r\n]\r\n}\r\n"), "pool tail shape drift (r509 pre-write assert)"

STAMP = "2026-10-01 11:16:30"
FREEZE = "e3cb8961f"
entries = []
for k in range(6):
    entries.append(
        '{\r\n'
        f'"id": "REFINE-REV-STOCK-CENSUS-SHARD-{k}",\r\n'
        '"ticket_ref": "T-2026-10-01-139 family-1 (CEO direct O-2026-10-01-1035, immediate)",\r\n'
        f'"prereg_ref": "research/REFINE_BENCH_STOCK_REV_P1.md (frozen pre-run @ {FREEZE}; R99 zero real-data runs before freeze commit)",\r\n'
        '"consumer_plan": "stage-A axis census ranking -> top-10 independent forms -> stage-B judged prereg (trial-wave STOCK grammar first candidates + REV-OSC refinement, ticket output law)",\r\n'
        '"runner": "scripts/refine_bench_rev_census.py",\r\n'
        '"runner_args": [\r\n"run",\r\n"--shard",\r\n"' + str(k) + '",\r\n"--of",\r\n"6"\r\n],\r\n'
        '"lane_owner": "ANY",\r\n'
        '"priority": 1,\r\n'
        '"status": "ready",\r\n'
        f'"entered_at": "{STAMP}",\r\n'
        '"worker_class": "bm-hosted",\r\n'
        '"data_gates": "in-runner FAIL-CLOSED: p1c_stock frozen panel T=8792 N=5222 cutoff 2026-09-22 + b_layer census + selftest 4/4 pre-burn + RAM floor 16GB + burn+flip atomics (shard file presence=done, r488) + worker claim handshake (r497)",\r\n'
        '"shards": [\r\n'
        '{\r\n'
        f'"key": "rev-census-{k}of6",\r\n'
        '"status": "ready",\r\n'
        f'"checkpoint": "results/refine_bench_stock/rev_census/shard-{k}of6.json (presence=done; census deterministic rerun byte-equal, selftest leg1/3)",\r\n'
        f'"note": "REV stock-face axis census shard {k} of 6 (40 of 240 cells); ~3-5min multicore burn, panel load in worker initializer",\r\n'
        '"owner": null,\r\n'
        '"owner_since": null,\r\n'
        '"claimed_since": null\r\n'
        '}\r\n'
        '],\r\n'
        '"workers_plan": {\r\n'
        '"workers": 6,\r\n'
        '"priority": "BelowNormal",\r\n'
        '"workers_law": "ProcessPoolExecutor via parallel_runner (O-20260930-2355); worker count = min(worker_cap, 6) memory guard ~8GB/worker (stock panel per-worker copy); RAM floor 16GB fail-closed exit 3"\r\n'
        '}\r\n'
        '}'
    )

# surgical: replace final "}\r\n]\r\n}\r\n" with "}\r\n,\r\n" + entries joined + "\r\n]\r\n}\r\n"
# (r509: raw-text anchored replacement, zero re-serialization)
old_tail = '"done_at": "2026-10-01 10:56:46"\r\n}\r\n]\r\n}\r\n'
assert txt.endswith(old_tail), "unexpected tail content for surgical anchor"
new_txt = txt[:-len(old_tail)] + '"done_at": "2026-10-01 10:56:46"\r\n},\r\n' + ',\r\n'.join(entries) + '\r\n]\r\n}\r\n'
open(P, "wb").write(new_txt.encode("utf-8"))

# post-write verification
chk = json.loads(open(P, encoding="utf-8").read())
ids = [e["id"] for e in chk["entries"]]
new = [i for i in ids if i.startswith("REFINE-REV-STOCK-CENSUS")]
assert len(new) == 6, "entry count drift"
assert all(e["status"] == "ready" for e in chk["entries"] if e["id"] in new)
assert len(chk["entries"]) == 249, f"total entry drift: {len(chk['entries'])}"
print("registered 6 ready entries; total:", len(chk["entries"]))
