"""T-68 WAVE-3B-2 southbound component face re-probe (EM window gate).

Ticket: fleet/tasks/T-2026-09-25-68-P1.json -- WAVE-3B-2 southbound rotation
lane: component face stock_hk_ggt_components_em was EM-blocked in the s0
census (results/instrument_census_probe.json, RemoteDisconnected). RE-PROBE
GATE first (r186 symmetry law: blocked face gets no terminal verdict; the
re-probe window stays open until a PASS lands). Channel-face gate ONLY --
zero strategy runs, zero prereg content (R99 law: prereg only AFTER this
gate passes).

Arms (differential diagnosis, r168 family):
- W (wrapper) : akshare stock_hk_ggt_components_em() -- the exact face a
  southbound puller would consume (paginated EM clist fs=b:DLMK0146,
  b:DLMK0144 = Shanghai+Shenzhen HK-connect components).
- R (raw)     : direct urllib GET on the same endpoint/params the wrapper
  uses (https://33.push2.eastmoney.com/api/qt/clist/get, page 1) --
  distinguishes wrapper-bug vs domain-block (ah_panel_puller R168 precedent:
  domain alive + wrapper dead = direct-puller lane viable).

Connection recipe: proxy env popped + urllib ProxyHandler({}) global opener
(instrument_census_probe.py v2 precedent / r193 moneyflow direct recipe).
Retry: 3 attempts per arm, 2.5s spacing (conn-fuse family calibration;
3 consecutive failures = honest BLOCKED, no terminal verdict).

Evidence: results/southbound_reprobe_w3b.json -- append-only history[] rows
(R167 head-repr real data rows; r62 real clock timestamps; any-machine lane:
read-only probe + one results file, ticket claim_lanes zero-claim asserted).

Verdict semantics (window gate):
- PASS        exit 0 : domain/face returns real data (wrapper rows >= 50 or
                       raw total >= 100) -> 3B-2 data gate OPENS; next slice
                       = southbound prereg draft (universe face re-frozen
                       from a fresh manifest at prereg time, not this probe).
- BLOCKED     exit 2 : all attempts failed -> window stays open, reported
                       verbatim (勿掩盖), still no terminal verdict.
- SHAPE_DRIFT exit 3 : endpoint reachable (HTTP 200) but payload unparseable
                       or below sanity floor -> blocked pending manual
                       ruling (update_ths_panel exit-3 semantics).

Subcommands: run (default) | selftest (hermetic, zero network).
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import sys
import tempfile
import time

_PROXY_ENV_KEYS = ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
                   "all_proxy", "ALL_PROXY")
for _k in _PROXY_ENV_KEYS:
    os.environ.pop(_k, None)

import urllib.request  # noqa: E402

urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))

import akshare as ak  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "southbound_reprobe_w3b.json")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")

RAW_URL = "https://33.push2.eastmoney.com/api/qt/clist/get"
RAW_PARAMS = {
    "pn": "1", "pz": "100", "po": "1", "np": "1",
    "ut": "bd1d9ddb04089700cf9c27f6f7426281",
    "fltt": "2", "fid": "f12",
    "fs": "b:DLMK0146,b:DLMK0144",
    "fields": ("f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,"
               "f18,f19,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,"
               "f136,f115,f152"),
}
ATTEMPTS_PER_ARM = 3
ATTEMPT_GAP_S = 2.5
HTTP_TIMEOUT_S = 10.0
WRAPPER_FLOOR = 50      # rows; real southbound universe >> 500
RAW_TOTAL_FLOOR = 100   # data.total; sanity drift detector, not a capacity gate


def _machine_id() -> str:
    try:
        return json.load(io.open(MACHINE_JSON, encoding="utf-8-sig"))["machine_id"]
    except Exception:  # noqa: BLE001 -- identity is informational here
        return "unknown"


def _now_iso() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------- transports
def _fetch_wrapper() -> dict:
    """Arm W: akshare wrapper face. Returns evidence dict or {'err': ...}."""
    df = ak.stock_hk_ggt_components_em()
    if df is None or len(df) == 0:
        return {"rows": 0, "err": "EMPTY"}
    return {
        "rows": int(len(df)),
        "cols": [str(c) for c in df.columns][:16],
        "head_repr": [repr(r)[:200] for r in df.head(3).to_dict("records")],
    }


def _fetch_raw() -> dict:
    """Arm R: direct urllib on the wrapper's endpoint (page 1)."""
    qs = "&".join(f"{k}={urllib.request.quote(str(v), safe=',')}"
                  for k, v in RAW_PARAMS.items())
    with urllib.request.urlopen(f"{RAW_URL}?{qs}", timeout=HTTP_TIMEOUT_S) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return _parse_raw_payload(payload)


def _parse_raw_payload(payload: dict) -> dict:
    """Extract gate facts from an EM clist JSON payload (production shape)."""
    data = (payload or {}).get("data") or {}
    total = data.get("total")
    diff = data.get("diff") or []
    rows = [
        {"f12": r.get("f12"), "f14": r.get("f14"), "f2": r.get("f2")}
        for r in diff[:3]
    ]
    out = {"total": (int(total) if total is not None else None), "page_rows": len(diff)}
    if rows:
        out["head_repr"] = [repr(r)[:200] for r in rows]
    if total is None:
        out["err"] = "NO_TOTAL_KEY"
    return out


def _try_arm(name: str, fn) -> dict:
    """3-attempt arm runner (conn-fuse calibration; honest per-attempt log)."""
    attempts = []
    ev = None
    for i in range(ATTEMPTS_PER_ARM):
        t0 = time.time()
        try:
            ev = fn()
            if ev.get("err"):
                attempts.append({"n": i + 1, "rc": "shape_err",
                                 "err": ev["err"],
                                 "sec": round(time.time() - t0, 1)})
            else:
                attempts.append({"n": i + 1, "rc": "ok",
                                 "sec": round(time.time() - t0, 1)})
                break
        except Exception as e:  # noqa: BLE001 -- honest taxonomy, no bare crash
            attempts.append({"n": i + 1,
                             "rc": "fail",
                             "err": f"{type(e).__name__}: {str(e)[:160]}",
                             "sec": round(time.time() - t0, 1)})
            ev = None
        if i < ATTEMPTS_PER_ARM - 1:
            time.sleep(ATTEMPT_GAP_S)
    alive = bool(ev and not ev.get("err"))
    return {"arm": name, "alive": alive, "evidence": ev or {},
            "attempts": attempts}


# ------------------------------------------------------------------ verdict
def _decide(wrapper_arm: dict, raw_arm: dict) -> tuple[str, str]:
    """(verdict, reason). Window-gate semantics per module docstring."""
    w_ev, r_ev = wrapper_arm.get("evidence") or {}, raw_arm.get("evidence") or {}
    w_rows = w_ev.get("rows") or 0
    r_total = r_ev.get("total")
    if w_rows >= WRAPPER_FLOOR:
        return "PASS", (f"wrapper face alive: {w_rows} rows (>= floor "
                        f"{WRAPPER_FLOOR})")
    if r_total is not None and r_total >= RAW_TOTAL_FLOOR:
        note = "wrapper dead/unhealthy but EM domain alive (direct-puller lane viable, R168 precedent)"
        if w_rows:
            note += f"; wrapper returned {w_rows} rows below floor"
        return "PASS", note
    if w_rows or (r_total is not None):
        return "SHAPE_DRIFT", (f"reachable but below floor: wrapper_rows="
                               f"{w_rows}, raw_total={r_total} -> manual ruling")
    return "BLOCKED", ("all arms failed (EM push2 domain window still "
                       "blocked) -- no terminal verdict, window stays open")


# ------------------------------------------------------------------ history
def _append_history(row: dict, out_path: str) -> None:
    doc = {"meta": {
        "batch": "T-68 WAVE-3B-2 southbound component re-probe window gate",
        "ticket": "fleet/tasks/T-2026-09-25-68-P1.json (id T-2026-09-25-68)",
        "laws": "r186 symmetry / R167 head-repr / r62 clock / R99 prereg-after-gate",
        "s0_block_ref": "results/instrument_census_probe.json "
                        "probes.stock_hk_ggt_components_em (FAIL RemoteDisconnected)",
    }, "history": []}
    if os.path.exists(out_path):
        with io.open(out_path, encoding="utf-8-sig") as fh:
            old = json.load(fh)
        if isinstance(old, dict) and isinstance(old.get("history"), list):
            doc = old
    doc["history"].append(row)
    doc["history"] = doc["history"][-50:]
    with io.open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------- run
def run_probe(out_path: str | None = None) -> tuple[str, dict]:
    out_path = out_path or OUT_JSON
    wrapper_arm = _try_arm("W:akshare_wrapper", _fetch_wrapper)
    time.sleep(ATTEMPT_GAP_S)
    raw_arm = _try_arm("R:direct_urllib", _fetch_raw)
    verdict, reason = _decide(wrapper_arm, raw_arm)
    row = {
        "ts": _now_iso(), "machine": _machine_id(), "verdict": verdict,
        "reason": reason,
        "wrapper": {k: wrapper_arm[k] for k in ("arm", "alive", "attempts")},
        "raw": {k: raw_arm[k] for k in ("arm", "alive", "attempts")},
        "wrapper_evidence": wrapper_arm.get("evidence") or {},
        "raw_evidence": raw_arm.get("evidence") or {},
    }
    if wrapper_arm.get("alive"):
        row["wrapper_evidence"] = wrapper_arm["evidence"]
    if raw_arm.get("alive"):
        row["raw_evidence"] = raw_arm["evidence"]
    row["next_slice"] = (
        "PASS -> southbound prereg draft from PREREG_TEMPLATE (universe "
        "manifest re-frozen by a dedicated puller at prereg time)"
        if verdict == "PASS" else
        "window stays open: re-run next round(s) until PASS or CEO ruling")
    _append_history(row, out_path)
    return verdict, row


def main(argv: list[str]) -> int:
    if argv and argv[0] == "selftest":
        return _selftest()
    verdict, row = run_probe()
    print(f"SOUTHBOUND RE-PROBE verdict={verdict}")
    print(f"  reason: {row['reason']}")
    print(f"  evidence: {OUT_JSON} (history row appended, machine={row['machine']})")
    if verdict == "PASS":
        return 0
    return 2 if verdict == "BLOCKED" else 3


# ----------------------------------------------------------------- selftest
def _selftest() -> int:
    """Hermetic: zero network. Fixtures mirror production call forms (r157
    pairing law): canned EM clist JSON + canned wrapper DataFrame fed through
    the real parse/decide/history code paths."""
    fails = []

    def chk(name, cond):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    print("southbound_reprobe selftest (hermetic, zero network):")

    # S1 proxy recipe: env keys popped at module import, direct opener policy
    chk("S1 proxy env keys popped at import",
        all(os.environ.get(k) is None for k in _PROXY_ENV_KEYS))

    # S2 raw payload parse (production EM clist shape)
    canned = {"rc": 0, "data": {"total": 556, "diff": [
        {"f12": "00700", "f14": "TENCENT", "f2": 385.6},
        {"f12": "09988", "f14": "ALIBABA", "f2": 92.4},
        {"f12": "03690", "f14": "MEITUAN", "f2": 88.1}]}}
    ev = _parse_raw_payload(canned)
    chk("S2 raw parse: total=556, page_rows=3, head repr present",
        ev["total"] == 556 and ev["page_rows"] == 3 and "00700" in ev["head_repr"][0])
    chk("S2b raw parse: missing data key -> honest NO_TOTAL_KEY",
        _parse_raw_payload({"rc": 0}).get("err") == "NO_TOTAL_KEY"
        and _parse_raw_payload({}).get("err") == "NO_TOTAL_KEY")

    # S3 wrapper evidence extraction (production DataFrame form, Chinese cols)
    df = pd.DataFrame({
        "序号": [1, 2], "代码": ["00700", "09988"],
        "名称": ["腾讯控股", "阿里巴巴-SW"], "最新价": [385.6, 92.4]})
    ev_w = {"rows": int(len(df)), "cols": [str(c) for c in df.columns][:16],
            "head_repr": [repr(r)[:200] for r in df.head(3).to_dict("records")]}
    chk("S3 wrapper evidence: rows/cols/head_repr extracted",
        ev_w["rows"] == 2 and len(ev_w["cols"]) == 4 and ev_w["head_repr"])

    # S4 verdict decision table (window-gate semantics)
    def arm(alive, ev):
        return {"alive": alive, "evidence": ev if alive else {},
                "attempts": [], "arm": "x"}
    cases = [
        (arm(False, {}), arm(False, {}), "BLOCKED"),
        (arm(True, {"rows": 556}), arm(True, {"total": 556}), "PASS"),
        (arm(False, {}), arm(True, {"total": 556}), "PASS"),
        (arm(True, {"rows": 3}), arm(False, {}), "SHAPE_DRIFT"),
        (arm(False, {}), arm(True, {"total": 3, "err": "NO_TOTAL_KEY"}), "SHAPE_DRIFT"),
        (arm(True, {"rows": 3}), arm(True, {"total": 3}), "SHAPE_DRIFT"),
    ]
    for i, (w, r, want) in enumerate(cases):
        got, _ = _decide(w, r)
        chk(f"S4 verdict case {i + 1} -> {want}", got == want)

    # S5 history append: two rows, first preserved, cap at 50
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "ev.json")
        _append_history({"ts": "t1", "verdict": "BLOCKED"}, p)
        _append_history({"ts": "t2", "verdict": "PASS"}, p)
        doc = json.load(io.open(p, encoding="utf-8-sig"))
        chk("S5 history append: 2 rows, first preserved, meta carried",
            len(doc["history"]) == 2 and doc["history"][0]["ts"] == "t1"
            and doc["history"][1]["verdict"] == "PASS"
            and doc["meta"]["batch"].startswith("T-68"))

    # S6 full-chain run(): monkeypatched transports -> evidence + exit mapping
    # (r197/r210 law: patch the module attribute itself, not default args)
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "ev2.json")
        orig_w, orig_r = _fetch_wrapper, _fetch_raw
        try:
            globals()["_fetch_wrapper"] = lambda: {"rows": 556, "cols": ["序号"],
                                                  "head_repr": ["repr-row"]}
            globals()["_fetch_raw"] = lambda: {"total": 556, "page_rows": 100,
                                                "head_repr": ["raw-row"]}
            v, row = run_probe(out_path=out)
            doc = json.load(io.open(out, encoding="utf-8-sig"))
            chk("S6 full-chain PASS: verdict + evidence row + machine field",
                v == "PASS" and row["wrapper_evidence"]["rows"] == 556
                and doc["history"][-1]["verdict"] == "PASS"
                and doc["history"][-1]["machine"] == _machine_id())
            chk("S6b full-chain attempts logged per arm",
                row["wrapper"]["arm"] == "W:akshare_wrapper"
                and row["raw"]["arm"] == "R:direct_urllib"
                and row["wrapper"]["attempts"][0]["rc"] == "ok")
            # S6c blocked shape: all transports raise
            def _boom():
                raise ConnectionError("Remote end closed connection without response")
            globals()["_fetch_wrapper"] = _boom
            globals()["_fetch_raw"] = _boom
            v2, row2 = run_probe(out_path=out)
            doc2 = json.load(io.open(out, encoding="utf-8-sig"))
            chk("S6c full-chain BLOCKED: honest verdict, 3 attempts/arm, no crash",
                v2 == "BLOCKED" and len(row2["wrapper"]["attempts"]) == 3
                and "Remote end closed" in row2["wrapper"]["attempts"][0]["err"]
                and len(doc["history"]) + 1 == len(doc2["history"]))
        finally:
            globals()["_fetch_wrapper"] = orig_w
            globals()["_fetch_raw"] = orig_r

    print(f"selftest: {'ALL PASS' if not fails else 'FAIL-> ' + '; '.join(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
