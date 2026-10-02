# fund_pit_audit.py -- T-145 leg-A PIT audit over data/fund_history (5224 symbols x 6 faces)
# GM personal-execution burn per O-20261002-2115 (CEO: do-it-now + use local compute).
# Laws honored: O-1820 meaning gate (consumer = T-145 family preregs PIT gate);
# O-2355 ProcessPool mandatory; CPU reserve law (below-normal priority, 24 workers <= 26-cap);
# __main__ guard (O-1820); self-logging (U060 pythonw pattern); read-only over data.
import json, os, sys, time, math, ctypes, statistics
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "fund_history")
OUT  = os.path.join(ROOT, "results", "fund_pit_audit")
LOG  = os.path.join(OUT, "audit.log")
STATUS = os.path.join(ROOT, "results", "fund_history_status.json")
WORKERS = 24
CUTOFF = "2026-09-22"

# Leg-C core: conservative PIT map -- report period end -> statutory disclosure deadline (A-share law)
PERIOD_AVAIL = {"03-31":"04-30","06-30":"08-31","09-30":"10-31","12-31":"04-30"}
QUARTERS = set(PERIOD_AVAIL.keys())

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")

def set_below_normal():
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    except Exception:
        pass

def d10(s):
    return (s or "")[:10]

def avail_date(period_end):
    # period_end like 'YYYY-MM-DD' -> available date (conservative statutory window)
    mmdd = period_end[5:10]
    if mmdd not in PERIOD_AVAIL:
        return None, None
    y = int(period_end[:4])
    if mmdd == "12-31":
        return "%d-04-30" % (y + 1), 120  # FY -> next-year Apr 30
    return "%d-%s" % (y, PERIOD_AVAIL[mmdd]), None

def audit_symbol(code):
    res = {"code": code, "faces": {}, "flags": []}
    d = os.path.join(DATA, code)
    if not os.path.isdir(d):
        res["error"] = "no-dir"
        return res
    pe_ttm_mid = None; pe_static_mid = None
    for face in ("pe_ttm", "pe_static", "pb", "total_mv", "roe_q", "div_events"):
        p = os.path.join(d, face + ".json")
        info = {}
        if not os.path.isfile(p):
            info["missing"] = True
            res["faces"][face] = info
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                j = json.load(f)
        except Exception as e:
            info["parse_error"] = str(e)[:80]
            res["faces"][face] = info
            res["flags"].append(face + ":parse_error")
            continue
        rows = j.get("rows", []) if isinstance(j, dict) else []
        info["n"] = len(rows)
        if not rows:
            info["empty"] = True
            res["faces"][face] = info
            continue
        if face in ("pe_ttm", "pe_static", "pb", "total_mv"):
            dates = [d10(x.get("date")) for x in rows]
            vals  = [x.get("value") for x in rows]
            info["d0"], info["d1"] = min(dates), max(dates)
            info["unsorted"] = (dates != sorted(dates))
            fin = [v for v in vals if v is not None and isinstance(v, (int, float)) and math.isfinite(v)]
            info["nulls"] = len(vals) - len(fin)
            info["nonfinite"] = sum(1 for v in vals if v is not None and not (isinstance(v,(int,float)) and math.isfinite(v)))
            if fin:
                info["v_min"], info["v_max"] = min(fin), max(fin)
                if face in ("pe_ttm", "pe_static"):
                    if face == "pe_ttm": pe_ttm_mid = statistics.median(fin)
                    else: pe_static_mid = statistics.median(fin)
            if info["unsorted"]:
                res["flags"].append(face + ":unsorted")
        elif face == "roe_q":
            per = [d10(x.get("日期")) for x in rows]
            info["d0"], info["d1"] = min(per), max(per)
            info["period_like"] = all(p[5:10] in QUARTERS for p in per if len(p) == 10)
            if not info["period_like"]:
                res["flags"].append("roe_q:nonperiod_keys")
            # Leg C: quantify lookahead exposure if anchored at period end
            lag_days = []
            for p in per:
                av, fy_lag = avail_date(p)
                if av is None:
                    continue
                # rough lag in days (FY special-cased 120)
                if fy_lag:
                    lag_days.append(fy_lag)
                else:
                    t0 = time.mktime(time.strptime(p, "%Y-%m-%d"))
                    t1 = time.mktime(time.strptime(av, "%Y-%m-%d"))
                    lag_days.append(int((t1 - t0) / 86400))
            if lag_days:
                info["pit_lag_days_min"] = min(lag_days)
                info["pit_lag_days_max"] = max(lag_days)
                info["pit_lag_days_med"] = int(statistics.median(lag_days))
        else:  # div_events
            info["n_events"] = len(rows)
            if rows and isinstance(rows[0], dict):
                info["key_sample"] = list(rows[0].keys())[:6]
        res["faces"][face] = info
    # Leg D sample: pe_ttm vs pe_static median ratio (E_ttm/E_static should be slow-moving)
    if pe_ttm_mid and pe_static_mid and pe_static_mid != 0:
        res["pe_ratio_med"] = round(pe_ttm_mid / pe_static_mid, 4)
    return res

def main():
    os.makedirs(OUT, exist_ok=True)
    open(LOG, "w").close()
    set_below_normal()
    log("start: fund PIT audit (T-145 leg-A, GM personal exec, workers=%d)" % WORKERS)
    codes = sorted(x for x in os.listdir(DATA) if x.isdigit())
    log("symbols on disk: %d" % len(codes))
    st = {}
    try:
        with open(STATUS, "r", encoding="utf-8") as f:
            st = json.load(f)
    except Exception:
        pass
    quarantined = set(st.get("quarantined", []))
    with Pool(WORKERS) as pool:
        results = pool.map(audit_symbol, codes, chunksize=64)
    log("audit pass complete: %d symbols" % len(results))

    agg = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "n_symbols": len(results),
           "status_done_symbols": st.get("done_symbols"), "quarantined": sorted(quarantined),
           "faces": {}, "flags_n": 0, "flagged_symbols": [], "pit": {}}
    per_face = {}
    pe_ratios = []
    lag_mins, lag_maxs, lag_meds = [], [], []
    for r in results:
        if r.get("error"):
            agg.setdefault("errors", []).append(r["code"])
            continue
        for face, info in r.get("faces", {}).items():
            fa = per_face.setdefault(face, {"n_missing": 0, "n_empty": 0, "n_parse_error": 0, "n": 0,
                                            "n_unsorted": 0, "n_nulls": 0, "n_nonfinite": 0, "d0_all": [], "d1_all": []})
            if info.get("missing"): fa["n_missing"] += 1; continue
            if info.get("parse_error"): fa["n_parse_error"] += 1; continue
            if info.get("empty"): fa["n_empty"] += 1; continue
            fa["n"] += 1
            fa["n_nulls"] += info.get("nulls", 0)
            fa["n_nonfinite"] += info.get("nonfinite", 0)
            if info.get("unsorted"): fa["n_unsorted"] += 1
            if "d0" in info: fa["d0_all"].append(info["d0"]); fa["d1_all"].append(info["d1"])
            if face == "roe_q":
                if "pit_lag_days_min" in info: lag_mins.append(info["pit_lag_days_min"])
                if "pit_lag_days_max" in info: lag_maxs.append(info["pit_lag_days_max"])
                if "pit_lag_days_med" in info: lag_meds.append(info["pit_lag_days_med"])
        if r.get("pe_ratio_med"): pe_ratios.append(r["pe_ratio_med"])
        if r.get("flags"):
            agg["flags_n"] += 1
            if len(agg["flagged_symbols"]) < 40:
                agg["flagged_symbols"].append({"code": r["code"], "flags": r["flags"]})
    for face, fa in per_face.items():
        if fa["d0_all"]:
            fa["d0_global"] = min(fa["d0_all"]); fa["d1_global"] = max(fa["d1_all"])
        del fa["d0_all"]; del fa["d1_all"]
        agg["faces"][face] = fa
    # Leg-C verdict: statutory PIT mapping (MUST enter T-145 preregs)
    agg["pit"]["financial_face_rule"] = (
        "roe_q rows are keyed by REPORT PERIOD END. Anchoring at period end = lookahead of "
        "Q1 30d / H1 62d / Q3 31d / FY 120d. MANDATORY prereg gate: any fundamental factor using "
        "financial faces MUST anchor at the statutory availability date "
        "(Q1->04-30, H1->08-31, Q3->10-31, FY->next-04-30) or later; period-end anchoring = "
        "prereg rejection (M02 exit-axis-style dual gate precedent)."
    )
    if lag_meds:
        agg["pit"]["statutory_lag_days"] = {"min_of_medians": min(lag_meds), "median_of_medians": int(statistics.median(lag_meds)), "max_of_medians": max(lag_meds)}
    if pe_ratios:
        agg["leg_d_pe_ratio"] = {"n": len(pe_ratios), "median": round(statistics.median(pe_ratios), 4),
                                 "lo": round(min(pe_ratios), 4), "hi": round(max(pe_ratios), 4)}
    agg["leg_b_limitation"] = ("single one-shot acquisition (2026-10-02): future-rewrite probe requires "
                               "quarterly re-pull diff -- scheduled as follow-up slice note")
    out_json = os.path.join(OUT, "audit_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=1)
    log("written: %s" % out_json)
    log("done: flags_n=%d quarantined=%s faces=%s" % (agg["flags_n"], len(quarantined), sorted(per_face.keys())))

if __name__ == "__main__":
    main()
