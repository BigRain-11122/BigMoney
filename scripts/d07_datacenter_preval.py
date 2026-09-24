"""D-20260924-07(2) datacenter alternative-source pre-validation (P-C lane).

PC_COLLECTOR.md §1 D-07② clause executor: the P-C lane (guba popularity)
runs on emappdata.eastmoney.com, same-family as the push2 block-prone family
(bm-b r40 + heat_source_audit.json 14 probes). Before the lane expands
(L3 news leg / IC batches / any new leg), re-run this probe: it verifies
whether a datacenter-web replacement source exists for the popularity
dataset, or the downgrade registration stays in force.

Faces (request budget: exactly ONE network request):
  A. emappdata today evidence — today's L1 snapshot file existence
     (zero request; produced by update_heat.py daily collection).
  B. datacenter-web aliveness — one direct (no-proxy, PC_COLLECTOR §2.4)
     request to /api/data/v1/get (RPT_HOLDERNUMLATEST, pageSize=1).
  C. alternative-source search (offline) — scan the installed akshare
     source tree: every popularity/hot-rank function and the domain it
     calls; every datacenter-web-hosted API family. Intersection empty
     => no datacenter popularity equivalent.

Verdict -> results/shortline/d07_datacenter_preval.json (append-only history
keyed by probe ts). Exit 0 = probe recorded (verdict either way is legal);
exit 2 = probe mechanics failure (honest, no history rewrite). `selftest`
subcommand = offline guard tests (zero network, zero real write).
"""
from __future__ import annotations

import io
import json
import re
import sys
import urllib.request
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "shortline" / "d07_datacenter_preval.json"
SNAPSHOT_DIR = ROOT / "data" / "heat" / "popularity"

POP_PAT = re.compile(r"hot_rank|stockrank|人气|热度排行")
DC_HOST = "datacenter-web.eastmoney.com"
URL_PAT = re.compile(r"https?://[A-Za-z0-9.\-]+")


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def emappdata_today_face(today: str) -> dict:
    f = SNAPSHOT_DIR / f"{today.replace('-', '')}.json"
    meta = None
    if f.exists():
        try:
            meta = json.loads(f.read_text(encoding="utf-8")).get("meta", {})
        except Exception:  # noqa: BLE001 - evidence face, honest degrade
            meta = None
    return {"face": "emappdata_today_evidence", "snapshot_file": f.name,
            "exists": f.exists(), "meta": meta,
            "note": "today L1 snapshot existence = emappdata alive-today "
                    "evidence (zero extra request; snapshot by update_heat.py)"}


def datacenter_alive_face() -> dict:
    """ONE direct request to a known-good datacenter-web report."""
    url = ("https://" + DC_HOST + "/api/data/v1/get?"
           "sortColumns=HOLD_NOTICE_DATE&sortTypes=-1&pageSize=1&pageNumber=1"
           "&reportName=RPT_HOLDERNUMLATEST&columns=SECURITY_CODE,SECURITY_NAME_ABBR"
           "&source=WEB&client=WEB")
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                      "Referer": "https://data.eastmoney.com/"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    t0 = datetime.now()
    with opener.open(req, timeout=12) as r:
        raw = r.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    res = data.get("result") or {}
    latency_ms = int((datetime.now() - t0).total_seconds() * 1000)
    return {"face": "datacenter_web_alive", "route": "direct",
            "latency_ms": latency_ms, "success": data.get("success"),
            "n_rows": len(res.get("data") or []),
            "request_count": 1}


def alt_search_face() -> dict:
    """Offline scan of installed akshare source: popularity functions vs
    datacenter-hosted functions. Zero network."""
    import akshare
    pkg = Path(akshare.__file__).resolve().parent
    pop_hits, dc_hits = {}, {}
    for p in pkg.rglob("*.py"):
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001 - file-level isolation
            continue
        if POP_PAT.search(t):
            domains = sorted({m.group(0) for m in URL_PAT.finditer(t)
                              if "eastmoney" in m.group(0)})
            pop_hits[p.stem] = domains
        if DC_HOST in t:
            dc_hits[p.stem] = DC_HOST
    pop_on_dc = sorted(k for k, v in pop_hits.items()
                      if any(DC_HOST in d for d in v))
    return {"face": "alternative_search_offline", "akshare_version":
            getattr(akshare, "__version__", "unknown"),
            "popularity_functions": {k: v for k, v in sorted(pop_hits.items())},
            "datacenter_hosted_families": sorted(dc_hits),
            "popularity_functions_on_datacenter": pop_on_dc,
            "note": "popularity dataset is guba-community specific; datacenter "
                    "families = fundamental/structured reports (margin, block "
                    "trade, holders, etc.)"}


def derive_verdict(em: dict, dc: dict, alt: dict) -> dict:
    """Data-driven verdict; fixed rules, no result-peeking adjustments."""
    equiv = alt.get("popularity_functions_on_datacenter") or []
    has_equiv = len(equiv) > 0
    if has_equiv:
        verdict = "datacenter_equivalent_found"
        downgrade = ("candidate source: " + ", ".join(equiv)
                     + " — gate through heat_source_audit depth checks before use")
    else:
        verdict = "no_datacenter_equivalent"
        downgrade = ("downgrade registered: P-C lane stays emappdata "
                     "single-source (same-family block risk per bm-b r40); on "
                     "persistent subdomain block = honest exit 2 + 30min "
                     "throttle + no cooling assumption (update_heat.py §2 "
                     "mechanics), lane pauses, zero fabricated data; L2 "
                     "backfill checkpoint-resumable; consumption clauses "
                     "(PC_COLLECTOR §3/§4.1) unchanged; any lane expansion "
                     "re-runs this probe first")
    return {"verdict": verdict, "downgrade_registration": downgrade,
            "emappdata_alive_today": bool(em.get("exists")),
            "datacenter_web_alive": bool(dc.get("success"))}


def run() -> int:
    today = date.today().isoformat()
    rec: dict = {"probe": "d07_datacenter_preval",
                 "order_ref": "D-20260924-07 item-2 (P-32 decision row, "
                              "executor BigMoney; PC_COLLECTOR.md §1 D-07②)",
                 "ts": _now(), "today": today, "machine": "bm-a",
                 "request_budget": "exactly 1 (datacenter aliveness)"}
    try:
        em = emappdata_today_face(today)
        dc = datacenter_alive_face()
        alt = alt_search_face()
        rec.update({"emappdata_face": em, "datacenter_face": dc,
                    "alt_search": alt, "verdict_block": derive_verdict(em, dc, alt)})
    except Exception as e:  # noqa: BLE001 - honest mechanics failure
        rec["mechanics_failure"] = f"{type(e).__name__}: {e}"[:400]
        _append(rec)
        print(f"[d07-preval] MECHANICS FAILURE recorded: {e}")
        return 2
    _append(rec)
    vb = rec["verdict_block"]
    print(f"[d07-preval] verdict={vb['verdict']} "
          f"emappdata_today={vb['emappdata_alive_today']} "
          f"datacenter_alive={vb['datacenter_web_alive']}")
    print(f"[d07-preval] {vb['downgrade_registration'][:160]}")
    return 0


def _append(rec: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    hist = []
    if OUT.exists():
        try:
            hist = json.loads(OUT.read_text(encoding="utf-8")).get("history", [])
        except Exception:  # noqa: BLE001 - corrupted ledger = honest restart
            hist = []
    hist.append(rec)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps({"history": hist}, ensure_ascii=False, indent=1,
                              default=str), encoding="utf-8")
    tmp.replace(OUT)


def selftest() -> int:
    """Offline guard tests: zero network, zero real write."""
    fails = []
    # G1: verdict derivation is rule-fixed both ways
    em = {"exists": True}
    dc = {"success": True}
    alt_none = {"popularity_functions_on_datacenter": []}
    alt_some = {"popularity_functions_on_datacenter": ["stock_hot_rank_fake"]}
    v1 = derive_verdict(em, dc, alt_none)
    v2 = derive_verdict(em, dc, alt_some)
    if v1["verdict"] != "no_datacenter_equivalent" or \
       "downgrade registered" not in v1["downgrade_registration"]:
        fails.append("G1a verdict-downgrade derivation")
    if v2["verdict"] != "datacenter_equivalent_found":
        fails.append("G1b verdict-equivalent derivation")
    # G2: emappdata evidence face never raises on missing file
    e = emappdata_today_face("1999-01-01")
    if e["exists"] is not False:
        fails.append("G2 missing-snapshot guard")
    # G3: history append round-trip via temp sandbox
    import tempfile
    global OUT
    keep = OUT
    try:
        with tempfile.TemporaryDirectory() as td:
            OUT = Path(td) / "prev.json"
            _append({"ts": "t1"})
            _append({"ts": "t2"})
            h = json.loads(OUT.read_text(encoding="utf-8"))["history"]
            if [x["ts"] for x in h] != ["t1", "t2"]:
                fails.append("G3 append-only history round-trip")
    finally:
        OUT = keep
    # G4: request budget honest — probe URL must cap pageSize=1
    consts = [c for c in datacenter_alive_face.__code__.co_consts
              if isinstance(c, str)]
    if not any("pageSize=1" in c for c in consts):
        fails.append("G4 request budget")
    if fails:
        print("selftest FAIL: " + "; ".join(fails))
        return 1
    print("selftest: all guard cases PASS")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
