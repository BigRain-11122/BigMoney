"""r312 bm-c: real-subcommand-path smoke for the wild_route_lab pool
conversion (T-134 s2). Runs the ACTUAL `run_shard` code path end-to-end
(serial workers=1 vs pool workers=2) on a synthetic frozen cache built from
the selftest fixture, then byte-compares every cell JSON + checkpoint key
set between the two engines.

__main__-guarded: ProcessPool spawn re-imports this module in workers --
top-level execution here would recursively re-run the smoke inside every
worker (the r312 BrokenProcessPool root cause this guard fixed).

Not covered here (data host = bm-a holds the real p1c_stock panel):
production mmap size/latency faces + live 60s core-spread sample -- those
accrue at the next natural burn on bm-a (see
_r312bmc_wr_assembly_check.py face [B]). Hermetic task-level bit-identity
is already proven by the selftest S-mp legs (43/43)."""
import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np

import wild_route_lab as WR

P, _fx = WR._mk_fixture()          # T=420 N=8 engineered fixture
ELIG_SMOKE = os.path.join(tempfile.gettempdir(), "wild_route_smoke_elig.csv")


def _write_elig():
    with open(ELIG_SMOKE, "w", encoding="utf-8") as fh:
        fh.write("code,name,r2_st\n")
        fh.write("600001,平安示例,False\n")
        fh.write("600002,龙腾股,False\n")
        fh.write("300003,ST测试,True\n")
        fh.write("688004,科创,False\n")
        fh.write("600005,普通,False\n")
        fh.write("600006,普通,False\n")
        fh.write("300007,创业板,False\n")
        fh.write("688008,科创,False\n")


def mk_cache(base):
    c = os.path.join(base, "cache")
    b = os.path.join(base, "bars")
    os.makedirs(c, exist_ok=True)
    os.makedirs(b, exist_ok=True)
    np.save(os.path.join(c, "dates.npy"),
            (P["idx"].astype("int64") // 1_000).astype("int64"))  # us
    for f in ("open", "high", "low", "close", "volume", "pct_chg"):
        np.save(os.path.join(c, f + ".npy"), np.asarray(P[f]))
    with open(os.path.join(c, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump({"shape": {"T": P["T"], "N": P["N"], "dtype": "float32"},
                   "generated": "2026-09-24 03:42:50"}, fh)
    for s in P["syms"]:
        open(os.path.join(b, s + ".parquet"), "wb").close()
    return c, b


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run_engine(tag, workers):
    base = tempfile.mkdtemp(prefix=f"wr_smoke_{tag}_")
    c, b = mk_cache(base)
    saved = (WR.CACHE, WR.BARS, WR.ELIG, WR.OUT_DIR, WR.CELL_DIR,
             WR._RAM_GUARD)
    WR.CACHE, WR.BARS, WR.ELIG = c, b, ELIG_SMOKE
    WR.OUT_DIR = os.path.join(base, "out")
    WR.CELL_DIR = os.path.join(WR.OUT_DIR, "cells")
    WR._RAM_GUARD = False        # tiny synthetic cache cannot OOM (F15 class)
    try:
        rc = WR.run_shard(0, 4, workers=workers)
        assert rc in (0, None), f"run_shard rc={rc}"
        cells = sorted(os.listdir(WR.CELL_DIR))
        hashes = {f: sha(os.path.join(WR.CELL_DIR, f)) for f in cells}
        ck = os.path.join(WR.OUT_DIR, "checkpoint-0of4.jsonl")
        keys = {json.loads(ln)["key"]
                for ln in open(ck, encoding="utf-8") if ln.strip()}
        meta = json.load(open(os.path.join(WR.OUT_DIR, "run_meta-0of4.json"),
                              encoding="utf-8"))
        return hashes, keys, meta
    finally:
        WR.CACHE, WR.BARS, WR.ELIG, WR.OUT_DIR, WR.CELL_DIR, WR._RAM_GUARD = (
            saved)
        shutil.rmtree(base, ignore_errors=True)


def main():
    _write_elig()
    hs, ks, ms = run_engine("serial", workers=1)
    hp, kp, mp = run_engine("pool", workers=2)
    assert set(hs) == set(hp), (
        f"cell file sets differ: only-serial={set(hs)-set(hp)} "
        f"only-pool={set(hp)-set(hs)}")
    diff = [f for f in hs if hs[f] != hp[f]]
    assert not diff, f"byte drift in {len(diff)} cells, first 5: {diff[:5]}"
    assert ks == kp, "checkpoint key sets differ"
    assert ms["engine"] == "serial" and mp["engine"] == "pool"
    assert mp["workers"] == 2, mp
    print(f"PASS serial==pool byte-identity on {len(hs)} cell JSONs "
          f"(shard 0 of 4, synthetic frozen cache)")
    print(f"PASS checkpoint key sets equal ({len(ks)} rows); "
          f"run_meta engines serial/pool + workers face present")
    print("real-subcommand-path smoke: ALL PASS")


if __name__ == "__main__":
    main()
