# -*- coding: utf-8 -*-
# r491 bm-a: bar-gated paper family runner (probe FIXED per r286 bm-c pit law:
# new-bar face = update_daily-maintained data/daily/<code>.csv bare-code panel,
# NOT the sh<code>.csv bm-b five-member lane file).
import subprocess, io, time, json, os, csv

LOG = r"logs\iteration-loop\s6_r491_chain.log"
SUMMARY = r"results\_r491bma_s6_gated.json"

BAR_GATED = [
    ("livepaper", ["python", "-m", "live.paper"]),
    ("t35v",      ["python", "scripts\\t35_open_fill_verify.py"]),
    ("t24paper",  ["python", "scripts\\t24_prospect_paper.py", "run"]),
    ("t24promo",  ["python", "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggr",      ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc",     ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid",      ["python", "scripts\\grid_paper.py", "run"]),
    ("sysv1",     ["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35exp",    ["python", "scripts\\t35_paper_export.py", "run"]),
]

def panel_tail_date():
    # r286 bm-c law: read update_daily's bare-code panel face
    p = r"data\daily\510300.csv"
    with io.open(p, encoding="utf-8-sig", errors="replace") as fh:
        rows = list(csv.reader(fh))
    for row in reversed(rows):
        if row and len(row[0].split("-")) == 3:
            return row[0]
    return "UNKNOWN"

def run_leg(log, name, cmd):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=900,
                           encoding="utf-8", errors="replace")
        rc, out, err = p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as e:
        rc, out, err = -99, "", repr(e)
    dt = time.time() - t0
    log.write("[gated][%s] rc=%d %.1fs %s\n" % (name, rc, dt, out[-600:].replace("\n", " | ")[:600]))
    if err:
        log.write("[gated][%s] stderr: %s\n" % (name, err[-300:].replace("\n", " | ")))
    log.flush()
    return rc

def main():
    tail = panel_tail_date()
    today = time.strftime("%Y-%m-%d")
    has_new_bar = (tail == today)
    log = io.open(LOG, "a", encoding="utf-8")
    log.write("S6 chain r491 GATED %s probe FIXED (bare-code face) tail=%s new_bar=%s\n"
              % (time.strftime("%Y-%m-%d %H:%M:%S"), tail, has_new_bar))
    log.flush()
    results, bad = {}, []
    if has_new_bar:
        for name, cmd in BAR_GATED:
            env = dict(os.environ)
            env["BIGMONEY_REGIME_GUARD"] = "enforce"
            t0 = time.time()
            try:
                p = subprocess.run(cmd, capture_output=True, timeout=900,
                                   encoding="utf-8", errors="replace", env=env)
                rc, out, err = p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
            except Exception as e:
                rc, out, err = -99, "", repr(e)
            dt = time.time() - t0
            log.write("[gated][%s] rc=%d %.1fs %s\n" % (name, rc, dt, out[-600:].replace("\n", " | ")[:600]))
            if err:
                log.write("[gated][%s] stderr: %s\n" % (name, err[-300:].replace("\n", " | ")))
            log.flush()
            results[name] = rc
            if rc not in (0,):
                bad.append((name, rc))
    else:
        log.write("[gated] honest skip: tail=%s != today\n" % tail)
    log.write("S6 chain r491 GATED done %s non_green=%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), bad))
    log.close()
    with io.open(SUMMARY, "w", encoding="utf-8") as fh:
        json.dump({"round": "r491 bm-a (gated)", "panel_tail": tail, "new_bar": has_new_bar,
                   "legs": results, "non_green": bad,
                   "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")},
                  fh, ensure_ascii=False, indent=1)
    print("gated done new_bar=%s non_green=" % has_new_bar, bad)

if __name__ == "__main__":
    main()
