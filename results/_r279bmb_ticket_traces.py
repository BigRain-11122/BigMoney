"""r279 bm-b: progress traces on T-86 + T-87 (byte-face preserving, R255/R257 law)."""
import json

def update(path, fields):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in raw
    tail_nl = raw.endswith(b"\n")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines()
    indent = len(lines[1]) - len(lines[1].lstrip(" ")) if len(lines) > 1 else 1
    d = json.loads(text)
    for k, v in fields.items():
        d[k] = v
    out = json.dumps(d, ensure_ascii=False, indent=indent)
    if tail_nl:
        out += "\n"
    if crlf:
        out = out.replace("\n", "\r\n")
    b = ("\xef\xbb\xbf" + out.encode("utf-8")) if bom else out.encode("utf-8")
    open(path, "wb").write(b)
    d2 = json.loads(open(path, "rb").read().decode("utf-8-sig"))
    for k in fields:
        assert k in d2
    print(f"{path}: wrote {list(fields)} bom={bom} crlf={crlf} tail={tail_nl} indent={indent}")

update("fleet/tasks/T-2026-09-26-87-P1.json", {
    "progress_r279_bmb": ("bm-b r279 supply-face lane claim per O-2330 sec3/O-2335 sec3 (A-share daily face, fleet-collector lane, "
        "bm-a/bm-b both-legal per order text; commit=this trace=lane lock): akshare full-A daily collector owned by bm-b, "
        "build opens r280. Precise pointer: (1) endpoint verify FIRST -- probe_akshare.py only probed list faces (ETF list/A-spot/fund list), "
        "daily-bar endpoints (stock_zh_a_hist EM vs stock_zh_a_daily sina) UNPROBED = collector step-0; "
        "(2) mirror collector-family conventions (update_futures/sina_mf pattern: 2.5s throttle, per-stock checkpoint resume, conn-fuse 3-fail, "
        "separated background full-universe pass, overlap row-verify, selftest subcommand); "
        "(3) universe=ashare_list.csv x eligibility.csv ST/delisting face (O-1820 supply, 11,626 rows measured r279); "
        "(4) consumption=T-87 REV-OSC stock sleeve + O-2335 refine-furnace stock mirror (first-bullish+bear-gate+take-profit default params "
        "from REFINE-BENCH-20260926-P1). Anti-dup: Money02/data/cache/p1c_stock frozen panel (census-drift assert, 2026-09-24) = "
        "read-only backtest precedent only, forward continuation structurally unavailable -> collector is the only forward-capable channel; "
        "D:\\Money TRANSFER = backup pending CEO 3-path decision (not started, zero double-build risk from this lane).")
})

update("fleet/tasks/T-2026-09-26-86-P1.json", {
    "progress_r279_bmb": ("bm-b r279 workers_plan pool-entry face: BLOCKED on s1 registry (honest physical dependency per immediate-law "
        "exemption clause) -- probe 23:2x: research/FACTOR_CENSUS_REGISTRY.md absent + results/factor_census/ empty (bm-a s1 in flight, "
        "their claim_note semantics). bm-b readiness: census batch pool entries (workers_plan per O-2130 s1.1, autofill C8 read-gate) "
        "register the round registry+runner land; shard participation per pool shard law (science lock bm-a, shards open). "
        "Census supply donation from r279 T-88 s1 audit (research/DOMAIN_AUDIT.md sec2, all measured tonight): "
        "ext_slots faces dzjy(gd-block trades)/gdhs(holder-count)/margin(financing) previously unregistered as factor-census candidates; "
        "fundamental eligibility 11,626-row ST/delisting face (B-layer filter law supply); money-market ETF gap (511880/511990/511660 "
        "absent from data/daily 1724 face). Lowamp20 GM-prior consumed per r278 pointer.")
})
print("done")
