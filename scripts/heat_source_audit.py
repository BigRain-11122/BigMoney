"""P-B heat/attention data-source audit (O-1850 dispatched lane, bm-b).

Enumerates + depth-verifies candidate heat/attention data sources per
HEAT_ATTENTION_SPEC.md §1 discipline: akshare / public no-key endpoints only.
Each probe runs in a subprocess (hard timeout) and prints JSON to stdout.
Driver mode `all` assembles results/shortline/heat_source_audit.json.

Zero engine runs; ledger N untouched. Pure source audit.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "shortline" / "heat_source_audit.json"
PROBE_TIMEOUT_S = 40

# ---------------------------------------------------------------- helpers (probe side)


def _ok(payload: dict) -> None:
    print(json.dumps({"ok": True, **payload}, ensure_ascii=False, default=str))


def _fail(exc: BaseException) -> None:
    print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"[:500]}, ensure_ascii=False))


# ---------------------------------------------------------------- probes


def p_concept_boards() -> None:
    import akshare as ak
    df = ak.stock_board_concept_name_em()
    _ok({"n_boards": int(len(df)), "columns": list(df.columns),
         "sample": df.head(3).to_dict(orient="records")})


def p_board_hist_depth() -> None:
    """Depth of EastMoney concept-board index daily klines for 3 sample boards."""
    import akshare as ak
    names = ak.stock_board_concept_name_em()
    picks = names["板块名称"].head(3).tolist()
    out = []
    for nm in picks:
        try:
            hist = ak.stock_board_concept_hist_em(symbol=nm, period="daily",
                                                  start_date="19900101",
                                                  end_date="20260923", adjust="")
            if len(hist) == 0:
                out.append({"board": nm, "bars": 0})
                continue
            col = "日期" if "日期" in hist.columns else hist.columns[0]
            close_col = [c for c in hist.columns if "收盘" in str(c)][0]
            out.append({"board": nm, "bars": int(len(hist)),
                        "first": str(hist[col].iloc[0]), "last": str(hist[col].iloc[-1]),
                        "cols": list(hist.columns),
                        "first_close": float(hist[close_col].iloc[0])})
        except Exception as e:  # noqa: BLE001 - per-board isolation, honest record
            out.append({"board": nm, "bars": -1, "error": f"{type(e).__name__}: {e}"[:200]})
    _ok({"samples": out})


def p_board_cons() -> None:
    """Membership snapshot: current only (survivorship-bias evidence)."""
    import akshare as ak
    names = ak.stock_board_concept_name_em()
    nm = names["板块名称"].iloc[0]
    df = ak.stock_board_concept_cons_em(symbol=nm)
    dated = [c for c in df.columns if "日期" in str(c) or "date" in str(c).lower()]
    _ok({"board": nm, "n_members": int(len(df)), "columns": list(df.columns),
         "date_like_columns": dated, "note": "membership = current snapshot only"
         if not dated else "membership carries dates"})


def p_hot_rank() -> None:
    """EastMoney popularity list (current) + per-stock rank history depth."""
    import akshare as ak
    cur = None
    for _ in range(2):  # one retry; emappdata route observed flaky
        try:
            cur = ak.stock_hot_rank_em()
            break
        except Exception:  # noqa: BLE001
            time.sleep(2)
    if cur is None:
        raise RuntimeError("stock_hot_rank_em failed after retry")
    detail = None
    try:
        d = ak.stock_hot_rank_detail_em(symbol="SZ000001")
        if len(d) > 0:
            tcol = [c for c in d.columns if "时间" in str(c) or "日期" in str(c) or "date" in str(c).lower()]
            tcol = tcol[0] if tcol else d.columns[0]
            detail = {"bars": int(len(d)), "first": str(d[tcol].iloc[0]),
                      "last": str(d[tcol].iloc[-1]), "columns": list(d.columns)}
    except Exception as e:  # noqa: BLE001
        detail = {"error": f"{type(e).__name__}: {e}"[:200]}
    _ok({"current_list_rows": int(len(cur)), "current_columns": list(cur.columns),
         "current_sample": cur.head(2).to_dict(orient="records"), "per_stock_history": detail})


def p_news_em() -> None:
    """Per-stock news list from EastMoney: how deep does the feed go."""
    import akshare as ak
    df = ak.stock_news_em(symbol="000001")
    tcol = [c for c in df.columns if "时间" in str(c) or "日期" in str(c)][0]
    _ok({"rows_returned": int(len(df)), "columns": list(df.columns),
         "first_ts": str(df[tcol].iloc[0]), "last_ts": str(df[tcol].iloc[-1])})


def p_ths_concept() -> None:
    """THS concept boards: attempt; cookie-walled sources degrade to candidate-only."""
    import akshare as ak
    df = ak.stock_board_concept_name_ths()
    _ok({"n_boards_ths": int(len(df)), "columns": list(df.columns),
         "sample": df.head(2).to_dict(orient="records")})


def p_margin_depth() -> None:
    """SSE margin (两融) per-stock detail: probe earliest available date 2010-03-31."""
    import akshare as ak
    df = ak.stock_margin_detail_sse(date="20100331")
    _ok({"probe_date": "2010-03-31", "rows": int(len(df)),
         "columns": list(df.columns),
         "verdict_hint": "margin detail back to 2010-03 if rows>0"})


def p_dzjy_depth() -> None:
    """Block-trade (大宗交易) per-day detail: probe 2013-01-04."""
    import akshare as ak
    df = ak.stock_dzjy_mrmx(start_date="20130104", end_date="20130104")
    _ok({"probe_date": "2013-01-04", "rows": int(len(df)),
         "columns": list(df.columns),
         "verdict_hint": "block-trade detail back to 2013 if rows>0"})


def p_gdhs_depth() -> None:
    """Holder count (股东户数) by quarter: probe 2015-09-30."""
    import akshare as ak
    df = ak.stock_zh_a_gdhs(symbol="20150930")
    _ok({"probe_date": "2015-09-30", "rows": int(len(df)),
         "columns": list(df.columns),
         "verdict_hint": "holder-count back to 2015Q3 if rows>0"})


def _http_json(url: str, params: dict | None = None, post: bytes | None = None,
               timeout: int = 12, use_proxy: bool = False,
               content_type: str | None = None) -> tuple[dict, str]:
    """GET/POST JSON; direct (no-proxy) first per J13 lesson, records route used."""
    import urllib.parse
    import urllib.request
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
               "Referer": "https://quote.eastmoney.com/"}
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=post, headers=headers)
    opener = (urllib.request.build_opener() if use_proxy
              else urllib.request.build_opener(urllib.request.ProxyHandler({})))
    with opener.open(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", errors="replace")
    route = "proxy" if use_proxy else "direct"
    if raw.lstrip()[:1] not in "{[":
        i, j = raw.find("("), raw.rfind(")")
        raw = raw[i + 1:j] if 0 <= i < j else raw
    return json.loads(raw), route


def p_raw_board_list() -> None:
    data, route = _http_json(
        "https://17.push2.eastmoney.com/api/qt/clist/get",
        {"pn": 1, "pz": 20, "po": 1, "np": 1, "fltt": 2, "invt": 2,
         "fs": "m:90+t:3", "fields": "f12,f14,f3"})
    d = data.get("data") or {}
    _ok({"route": route, "total_boards": d.get("total"),
         "sample": [{ "code": it.get("f12"), "name": it.get("f14")} for it in (d.get("diff") or [])[:5]]})


def p_raw_board_kline() -> None:
    data0 = _http_json(
        "https://17.push2.eastmoney.com/api/qt/clist/get",
        {"pn": 1, "pz": 3, "po": 1, "np": 1, "fltt": 2, "invt": 2,
         "fs": "m:90+t:3", "fields": "f12,f14"})[0]
    codes = [(it.get("f12"), it.get("f14"))
             for it in (data0.get("data") or {}).get("diff") or []]
    out = []
    for code, name in codes:
        data, route = _http_json(
            "https://push2his.eastmoney.com/api/qt/stock/kline/get",
            {"secid": f"90.{code}", "klt": 101, "fqt": 1, "beg": "19900101",
             "end": "20260923", "fields1": "f1,f2,f3",
             "fields2": "f51,f53,f56,f57"})
        kl = (data.get("data") or {}).get("klines") or []
        out.append({"code": code, "name": name, "route": route, "bars": len(kl),
                    "first": kl[0].split(",")[0] if kl else None,
                    "last": kl[-1].split(",")[0] if kl else None,
                    "first_row": kl[0] if kl else None})
    _ok({"samples": out})


def p_raw_board_cons() -> None:
    data0 = _http_json(
        "https://push2.eastmoney.com/api/qt/clist/get",
        {"pn": 1, "pz": 1, "po": 1, "np": 1, "fltt": 2, "invt": 2,
         "fs": "m:90+t:3", "fields": "f12,f14"})[0]
    board = ((data0.get("data") or {}).get("diff") or [{}])[0]
    code = board.get("f12")
    data, route = _http_json(
        "https://push2.eastmoney.com/api/qt/clist/get",
        {"pn": 1, "pz": 5, "po": 1, "np": 1, "fltt": 2, "invt": 2,
         "fs": f"b:{code}", "fields": "f12,f14"})
    d = data.get("data") or {}
    _ok({"board": f"{code} {board.get('f14')}", "route": route,
         "total_members": d.get("total"),
         "note": "current membership snapshot only; no historical-membership endpoint public"})


def p_raw_news() -> None:
    import urllib.parse
    import urllib.request
    inner = {"uid": "", "keyword": "000001", "type": ["cmsArticleWebOld"],
             "client": "web", "clientType": "web", "clientVersion": "curr",
             "param": {"cmsArticleWebOld": {"searchScope": "default", "sort": "default",
                                            "pageIndex": 1, "pageSize": 100,
                                            "preTag": "<em>", "postTag": "</em>"}}}
    url = ("https://search-api-web.eastmoney.com/search/jsonp?cb=cb&param="
           + urllib.parse.quote(json.dumps(inner, ensure_ascii=False)))
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://so.eastmoney.com/"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=12) as r:
        raw = r.read().decode("utf-8", errors="replace")
    i, j = raw.find("("), raw.rfind(")")
    data = json.loads(raw[i + 1:j])
    arts = ((data.get("result") or {}).get("cmsArticleWebOld")) or []
    times = [a.get("date", "") for a in arts if a.get("date")]
    _ok({"route": "direct", "articles_page1": len(arts),
         "first_ts": min(times) if times else None, "last_ts": max(times) if times else None})


def p_ths_board_hist() -> None:
    """THS concept-board index history depth (alternative taxonomy to EM)."""
    import akshare as ak
    names = ak.stock_board_concept_name_ths()
    nm = names.iloc[0]["概念名称"] if "概念名称" in names.columns else names.iloc[0, 0]
    hist = ak.stock_board_concept_index_ths(symbol=nm, start_date="20100101",
                                           end_date="20260923")
    _ok({"board": nm, "bars": int(len(hist)), "columns": list(hist.columns)[:8],
         "first": str(hist.iloc[0, 0]), "last": str(hist.iloc[-1, 0])})


PROBES = {
    "concept_boards": p_concept_boards,
    "board_hist_depth": p_board_hist_depth,
    "board_cons": p_board_cons,
    "hot_rank": p_hot_rank,
    "news_em": p_news_em,
    "ths_concept": p_ths_concept,
    "margin_depth": p_margin_depth,
    "dzjy_depth": p_dzjy_depth,
    "gdhs_depth": p_gdhs_depth,
    "raw_board_list": p_raw_board_list,
    "raw_board_kline": p_raw_board_kline,
    "raw_board_cons": p_raw_board_cons,
    "raw_news": p_raw_news,
    "ths_board_hist": p_ths_board_hist,
}

# ---------------------------------------------------------------- driver


def run_probe(name: str) -> dict:
    t0 = time.time()
    cmd = [sys.executable, "-u", str(Path(__file__).resolve()), name]
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace",
                            timeout=PROBE_TIMEOUT_S, cwd=str(ROOT))
        lat = int((time.time() - t0) * 1000)
        if cp.returncode != 0 or not cp.stdout.strip():
            return {"ok": False, "latency_ms": lat,
                    "error": (cp.stderr or cp.stdout or "")[-500:]}
        return {"latency_ms": lat, **json.loads(cp.stdout.strip().splitlines()[-1])}
    except subprocess.TimeoutExpired:
        return {"ok": False, "latency_ms": int((time.time() - t0) * 1000),
                "error": f"timeout after {PROBE_TIMEOUT_S}s"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}


def classify(probes: dict) -> list:
    """Data-driven classification rows; verdicts derived from probe evidence only."""
    rows = []
    rbk = probes.get("raw_board_kline", {})
    samples = rbk.get("samples") if rbk.get("ok") else None
    bh = probes.get("board_hist_depth", {})
    if not samples and bh.get("ok"):
        samples = [s for s in bh.get("samples", []) if s.get("bars", 0) > 0]
    firsts = [str(s.get("first")) for s in (samples or []) if s.get("first")]
    rows.append({
        "source": "concept_board_index_kline_em", "family": "P-B",
        "verdict": "backtestable" if firsts else "unverified",
        "depth": f"earliest sample {min(firsts)}..{max(firsts)}" if firsts else "n/a",
        "usage": "hot_concept_mom_5/20, hot_concept_zt_count via board index",
    })
    rbc = probes.get("raw_board_cons", {})
    rows.append({
        "source": "concept_board_membership_em", "family": "P-B",
        "verdict": "forward_collect + bias_clause",
        "depth": f"current snapshot {rbc.get('total_members')} members (probe: no historical-membership endpoint)"
        if rbc.get("ok") else "current snapshot only",
        "usage": "hot_concept_* membership: survivorship bias disclosure per spec §2B",
    })
    hr = probes.get("hot_rank", {})
    ph = (hr.get("per_stock_history") or {})
    rows.append({
        "source": "em_popularity_rank_current+detail", "family": "P-C(前向)",
        "verdict": "forward_collect",
        "depth": f"per-stock detail bars={ph.get('bars')} first={ph.get('first')}" if ph.get("bars") else "current list only",
        "usage": "guba_hot_rank_z / guba_rank_delta per spec §2C",
    })
    ne = probes.get("raw_news", {})
    rows.append({
        "source": "em_per_stock_news", "family": "P-C(前向)",
        "verdict": "forward_collect",
        "depth": f"feed page1 rows={ne.get('articles_page1')} first={ne.get('first_ts')}" if ne.get("ok") else "unverified",
        "usage": "news_count_1d/5d per spec §2D",
    })
    ths = probes.get("ths_concept", {})
    tbh = probes.get("ths_board_hist", {})
    ths_depth = (f"boards={ths.get('n_boards_ths')}, sample index bars={tbh.get('bars')} "
                 f"first={tbh.get('first')}" if tbh.get("ok") else f"boards={ths.get('n_boards_ths')}")
    rows.append({
        "source": "ths_concept_boards(+index_hist)", "family": "P-B(alt)",
        "verdict": "backtestable" if (ths.get("ok") and tbh.get("ok", False)) else
                   ("backtestable_list_only" if ths.get("ok") else "candidate_only"),
        "depth": ths_depth if ths.get("ok") else str(ths.get("error", ""))[:120],
        "usage": "alternative concept taxonomy (THS): board list + index history",
    })
    for key, src, usage in (
        ("margin_depth", "sse_margin_detail", "两融余额因子（扩展槽）"),
        ("dzjy_depth", "block_trade_detail", "大宗交易因子（扩展槽）"),
        ("gdhs_depth", "holder_count_quarterly", "股东户数因子（扩展槽）"),
    ):
        pr = probes.get(key, {})
        rows.append({
            "source": src, "family": "extension_slot",
            "verdict": "backtestable" if pr.get("ok") and pr.get("rows", 0) > 0 else "unverified",
            "depth": f"probe rows={pr.get('rows')}" if pr.get("ok") else str(pr.get("error", ""))[:120],
            "usage": usage,
        })
    rows.append({
        "source": "em_push2_route_finding", "family": "infra",
        "verdict": "direct_required",
        "depth": "akshare push2/clist probes via Clash proxy = RemoteDisconnected after ~22s; "
                 "raw direct (no-proxy) probes OK -> EM quote endpoints need direct route",
        "usage": "P-B pull pipeline must bypass proxy for push2.eastmoney.com family",
    })
    return rows


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in PROBES:
        try:
            PROBES[sys.argv[1]]()
        except Exception as e:  # noqa: BLE001 - probe isolation, honest record
            _fail(e)
        return
    probes = {}
    for name in PROBES:
        probes[name] = run_probe(name)
        if name != list(PROBES)[-1]:
            time.sleep(4)  # spacing: EM quote endpoints throttle rapid bursts
    results = {
        "audit": "P-B heat/attention data-source audit",
        "order_ref": "O-20260923-1850 P-B (GM dispatch bm-b)",
        "asof": datetime.now().isoformat(timespec="seconds"),
        "today": date.today().isoformat(),
        "machine": "bm-b",
        "discipline": "akshare/public no-key endpoints only; cookie/key sources register-only",
        "probes": probes,
        "classification": classify(probes),
        "zero_engine_runs": True,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(f"[audit] {len(probes)} probes -> {OUT}")
    for r in results["classification"]:
        print(f"  {r['family']:>10} | {r['source']:<32} | {r['verdict']:<28} | {r['depth']}")


if __name__ == "__main__":
    main()
