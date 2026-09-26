"""R299 bm-a SW L3 industry mapping fetch (queue #4 sector-leader face, R99 probe facts).

One-shot research probe fetch (not an S6 chain gate): builds the frozen
sector taxonomy asset for CN_SECTOR_LEADER_P1 -- SW level-3 industries
(current-snapshot constituents, 2026-09-27) -> data/basic/sw_l3_map.csv.

Discipline: checkpoint resume, per-industry retry x2, conn-fuse 3
consecutive industry failures -> honest partial exit 2. Throttle 0.3s.
"""
import json
import os
import time

import akshare as ak

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
OUT_CSV = os.path.join(ROOT, "data", "basic", "sw_l3_map.csv")
PROG = os.path.join(ROOT, "results", "_r299bma_sw_l3_fetch_progress.json")
FETCHED_AT = time.strftime("%Y-%m-%d %H:%M:%S")

# resume state
if os.path.exists(PROG):
    st = json.load(open(PROG, encoding="utf-8"))
else:
    st = {"rows": [], "done_industries": [], "fuse": 0, "started": FETCHED_AT}

done = set(st["done_industries"])
rows = st["rows"]

info = ak.sw_index_third_info()
industries = info.iloc[:, 0].tolist()          # industry code 850111.SI
names = info.iloc[:, 1].tolist()                # industry name
parents = info.iloc[:, 2].tolist()              # L2 parent
todo = [(c, n, p) for c, n, p in zip(industries, names, parents) if c not in done]
print(f"industries total={len(industries)} done={len(done)} todo={len(todo)}", flush=True)

fuse = 0
for i, (code, name, parent) in enumerate(todo):
    got = None
    backoffs = (1.5, 4.0, 8.0, 15.0)
    for attempt in range(4):
        try:
            cons = ak.sw_index_third_cons(symbol=code)
            got = cons
            break
        except Exception as e:
            print(f"  retry {code} {type(e).__name__}", flush=True)
            time.sleep(backoffs[min(attempt, 3)])
    if got is None:
        fuse += 1
        print(f"  FAIL {code} fuse={fuse}", flush=True)
        if fuse >= 5:
            st["done_industries"] = list(done)
            json.dump(st, open(PROG, "w", encoding="utf-8"), ensure_ascii=False)
            print(f"CONN-FUSE at {code}; partial {len(done)} industries saved", flush=True)
            raise SystemExit(2)
        continue
    fuse = 0
    for _, r in got.iterrows():
        sc = str(r.iloc[1])                      # 股票代码 600313.SH
        sym = sc.split(".")[0]
        if not (len(sym) == 6 and sym.isdigit()):
            continue
        rows.append({"code": sym, "stock_name": str(r.iloc[2]),
                     "industry_code": code, "industry_name": name,
                     "l2_parent": parent,
                     "listed_date": str(r.iloc[3]),
                     "fetched_at": FETCHED_AT})
    done.add(code)
    if (i + 1) % 25 == 0:
        st["done_industries"] = list(done); st["rows"] = rows; st["fuse"] = 0
        json.dump(st, open(PROG, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"  progress {len(done)}/{len(industries)}", flush=True)
    time.sleep(1.0)

st["done_industries"] = list(done); st["rows"] = rows; st["fuse"] = 0
json.dump(st, open(PROG, "w", encoding="utf-8"), ensure_ascii=False)

# finalize CSV
seen = {}
dupes = 0
for r in rows:
    if r["code"] in seen:
        dupes += 1
        continue
    seen[r["code"]] = r
hdr = "code,stock_name,industry_code,industry_name,l2_parent,listed_date,fetched_at"
with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
    fh.write(hdr + "\n")
    for sym in sorted(seen):
        r = seen[sym]
        def esc(x):
            return str(x).replace('"', "'")
        fh.write(",".join([r["code"], esc(r["stock_name"]), r["industry_code"],
                            esc(r["industry_name"]), esc(r["l2_parent"]),
                            r["listed_date"], r["fetched_at"]]) + "\n")
n_ind = len(set(r["industry_code"] for r in seen.values()))
print(f"FINAL rows={len(seen)} dupes_dropped={dupes} industries={n_ind} -> {OUT_CSV}", flush=True)
