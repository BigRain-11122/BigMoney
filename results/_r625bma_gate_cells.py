import json, os

NOTE = ("keep blocked on bm-a: OFF-CALIBER CACHE containment (r625, r615 family) -- "
        "fund_divlowvol_p1.py eligibility gate amt20-median>=Y10M consumes the p1c_stock "
        "npy amount column (688/689 at 100x raw, r615 probe CONFIRMED) so any burn on "
        "bm-a's local cache passes phantom-liquid 688/689 stocks into the universe; "
        "count=0 = no crash, gate is data-caliber not crash-loop; the x1/x2 CELL faces "
        "burned on bm-a 2026-10-03 10:36-13:00 are OFF-CALIBER SUSPECT (see "
        "results/fund_divlowvol_p1/OFF_CALIBER_NOTE.md) and must be re-burned after "
        "T-156 transfer+verify; clear ONLY after p1c_stock TRANSFER+verify (fleet "
        "decision) or runner edit (fix-first hash-drift auto-clear); bm-b = "
        "correct-caliber rightful burner")
sha16 = "2744ee595d0faeb3"
sigs = {
    "scripts/fund_divlowvol_p1.py|run,--cell,DIVLOWVOL-YIELDVOL,--face,x1": dict(
        count=0, refusals=0, code_sha256=sha16, entry="FUND-DIVLOWVOL-P1-CELL-DIVLOWVOLYIELDVOL-X1",
        shard="fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1", machine="bm-a", note=NOTE),
    "scripts/fund_divlowvol_p1.py|run,--cell,DIVLOWVOL-YIELDVOL,--face,x2": dict(
        count=0, refusals=0, code_sha256=sha16, entry="FUND-DIVLOWVOL-P1-CELL-DIVLOWVOLYIELDVOL-X2",
        shard="fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1", machine="bm-a", note=NOTE),
}
for path in ("results/crash_fuse.bm-a.json", "results/crash_fuse.json"):
    d = json.load(open(path, encoding="utf-8"))
    d.setdefault("sigs", {}).update(sigs)
    tmp = path + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    print("gated:", path)
