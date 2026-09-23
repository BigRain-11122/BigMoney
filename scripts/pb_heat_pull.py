"""P-B heat-concept data puller (research/shortline/PB_HEAT_CONCEPT_IC.md SS1).

EM taxonomy end-to-end (THS lacks a cons endpoint in akshare 1.18.96):
  stage 1  board list   clist fs=m:90+t:3            -> boards.csv
  stage 2  membership   clist stock universe f102   -> stock_boards.csv
  stage 3  board klines push2his 90.BKxxxx daily    -> klines/BKxxxx.csv

Discipline (round-39 audit pitfalls, all evidence-backed):
  - DIRECT opener only (ProxyHandler({})): Clash hijacks the EM quote domain.
  - Rate limit >=2.5s between requests; burst throttle is request-count based.
  - Checkpoint per stage: existing files are skipped -> resumable across rounds.
  - >=5 consecutive failures = throttle detected -> stop, exit 2 (honest).
  - f102 coverage gate: >=80% of panel syms mapped to >=1 known board, else
    honest abort exit 3 (fallback = per-board cons fetch, next attempt).

Zero engine runs; ledger N untouched. Cache is gitignored (Money02/).
"""
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "Money02", "data", "cache", "pb_heat")
PANEL = os.path.join(ROOT, "Money02", "data", "cache", "p4_batch2_panel")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Referer": "https://quote.eastmoney.com/"}
SLEEP_S = 2.5
MAX_CONSEC_FAIL = 5
END = "20260923"


def _direct(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def _clist(fs, fields, pz):
    """clist GET with large-pz single shot + pagination fallback."""
    url = ("https://push2.eastmoney.com/api/qt/clist/get?"
           f"pn=1&pz={pz}&po=1&np=1&fltt=2&invt=2&fs={fs}&fields={fields}")
    d = _direct(url)
    data = d.get("data") or {}
    total = data.get("total") or 0
    rows = list(data.get("diff") or [])
    pn = 2
    while rows and len(rows) < int(total):
        time.sleep(SLEEP_S)
        url = ("https://push2.eastmoney.com/api/qt/clist/get?"
               f"pn={pn}&pz={pz}&po=1&np=1&fltt=2&invt=2&fs={fs}&fields={fields}")
        d = _direct(url)
        data = d.get("data") or {}
        chunk = list(data.get("diff") or [])
        if not chunk:
            break
        rows.extend(chunk)
        pn += 1
    return total, rows


def stage_boards():
    fp = os.path.join(CACHE, "boards.csv")
    if os.path.exists(fp):
        print("[boards] cached, skip")
        with open(fp, encoding="utf-8") as f:
            lines = f.readlines()
        return len(lines) - 1
    total, rows = _clist("m:90+t:3", "f12,f14", 60000)
    with open(fp + ".tmp", "w", encoding="utf-8") as f:
        f.write("code,name\n")
        for it in rows:
            f.write(f"{it.get('f12')},{it.get('f14')}\n")
    os.replace(fp + ".tmp", fp)
    print(f"[boards] total={total} saved={len(rows)}")
    return len(rows)


def stage_membership():
    fp = os.path.join(CACHE, "stock_boards.csv")
    if os.path.exists(fp):
        print("[membership] cached, skip")
        return
    total, rows = _clist(
        "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23", "f12,f102", 60000)
    import numpy as np
    panel_syms = set(np.load(os.path.join(PANEL, "panel_symbols.npy"))
                     .astype(str).tolist())
    name_set = {}
    with open(os.path.join(CACHE, "boards.csv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            code, name = line.strip().split(",", 1)
            name_set[name] = code
    mapped = unmatched = empty = 0
    unmatched_names = {}
    with open(fp + ".tmp", "w", encoding="utf-8") as f:
        f.write("sym,boards\n")
        for it in rows:
            sym = str(it.get("f12") or "").zfill(6)
            raw = str(it.get("f102") or "")
            codes = []
            for nm in [x for x in raw.split(",") if x]:
                code = name_set.get(nm)
                if code:
                    codes.append(code)
                else:
                    unmatched_names[nm] = unmatched_names.get(nm, 0) + 1
            if codes:
                mapped += 1
                f.write(f"{sym};{','.join(sorted(set(codes)))}\n")
            elif raw:
                unmatched += 1
            else:
                empty += 1
    cov = mapped / max(1, len(panel_syms))
    with open(os.path.join(CACHE, "membership_report.json"), "w",
              encoding="utf-8") as f:
        json.dump({"em_rows": len(rows), "mapped": mapped,
                   "mapped_ratio_of_em": round(mapped / max(1, len(rows)), 4),
                   "panel_syms": len(panel_syms),
                   "coverage_vs_panel": round(cov, 4),
                   "unmatched_board_names": unmatched_names,
                   "empty_f102": empty}, f, ensure_ascii=False, indent=1)
    if cov < 0.80:
        os.remove(fp + ".tmp")
        print(f"[membership] coverage {cov:.3f} < 0.80 gate -> honest abort")
        sys.exit(3)
    os.replace(fp + ".tmp", fp)
    print(f"[membership] rows={len(rows)} mapped={mapped} cov={cov:.3f}")


def stage_klines(max_boards=None):
    kdir = os.path.join(CACHE, "klines")
    os.makedirs(kdir, exist_ok=True)
    with open(os.path.join(CACHE, "boards.csv"), encoding="utf-8") as f:
        next(f)
        boards = [ln.strip().split(",", 1) for ln in f]
    todo = [(c, n) for c, n in boards
            if not os.path.exists(os.path.join(kdir, f"{c}.csv"))]
    print(f"[klines] boards={len(boards)} todo={len(todo)}")
    if max_boards:
        todo = todo[:max_boards]
    consec = 0
    done = 0
    manifest_fp = os.path.join(CACHE, "kline_manifest.jsonl")
    for code, name in todo:
        fp = os.path.join(kdir, f"{code}.csv")
        url = ("https://push2his.eastmoney.com/api/qt/stock/kline/get?"
               f"secid=90.{code}&klt=101&fqt=1&beg=19900101&end={END}"
               "&fields1=f1,f2,f3&fields2=f51,f53,f56,f57")
        try:
            k = _direct(url)
        except Exception as e:  # noqa: BLE001 - honest throttle record
            consec += 1
            print(f"  {code} FAIL {type(e).__name__} ({consec}/{MAX_CONSEC_FAIL})")
            if consec >= MAX_CONSEC_FAIL:
                print("[klines] throttle detected -> stop, checkpoint kept")
                return 2
            time.sleep(30)
            continue
        consec = 0
        kl = ((k.get("data") or {}).get("klines")) or []
        with open(fp + ".tmp", "w", encoding="utf-8") as f:
            f.write("date,close,volume,amount\n")
            for row in kl:
                p = row.split(",")
                if len(p) >= 4:
                    f.write(f"{p[0]},{p[1]},{p[2]},{p[3]}\n")
        os.replace(fp + ".tmp", fp)
        with open(manifest_fp, "a", encoding="utf-8") as f:
            f.write(json.dumps({"code": code, "name": name,
                                "bars": len(kl),
                                "first": kl[0].split(",")[0] if kl else None,
                                "last": kl[-1].split(",")[0] if kl else None},
                               ensure_ascii=False) + "\n")
        done += 1
        if done % 25 == 0:
            print(f"  {done} pulled", flush=True)
        time.sleep(SLEEP_S)
    return 0


def status():
    b = os.path.join(CACHE, "boards.csv")
    m = os.path.join(CACHE, "stock_boards.csv")
    k = os.path.join(CACHE, "klines")
    n_boards = sum(1 for _ in open(b, encoding="utf-8")) - 1 \
        if os.path.exists(b) else 0
    n_kl = len([x for x in os.listdir(k) if x.endswith(".csv")]) \
        if os.path.exists(k) else 0
    print(json.dumps({"boards": n_boards,
                      "membership": os.path.exists(m),
                      "klines_done": n_kl,
                      "klines_todo": max(0, n_boards - n_kl)}))


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "pull"
    if cmd == "status":
        status()
        sys.exit(0)
    if cmd == "pull":
        t0 = time.time()
        rc = 0
        stage_boards()          # fast throttle probe (1-2 requests)
        stage_membership()      # 1 big-pz request
        rc = stage_klines()
        print(f"pull done rc={rc} elapsed={time.time()-t0:.0f}s")
        sys.exit(rc)
    print("usage: pb_heat_pull.py [pull|status]")
