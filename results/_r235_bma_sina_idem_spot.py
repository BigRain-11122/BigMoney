"""bm-a R235 spot closure of T-72 s2 prereg SINA_MF_PREREG.md sec-4 line 3
(same-day rerun idempotency, byte-level zero growth) -- LIVE-FIRE on 8 frozen
sample symbols via checkpoint surgery (remove from done -> refresh limit=8 ->
merge-skip path on real rows) + full-universe rerun face (refresh no-limit with
empty todo = zero requests, byte zero growth by construction).

Sample frozen BEFORE any result observation (anti-snooping): 2 SZ main
(000001/000858), 1 ChiNext (300750), 1 empty-history new IPO (301569), 2 SH
main incl. largest-magnitude netamount rows (600519/601318), 1 SH mid
(603259), 1 STAR (688981). 8 requests total (request account: 5228+2 probes
already spent; spot +8 = 5238 < runaway line 10456).

Verdict faces:
- byte_identity: sha256 per/<code>.csv before vs after equal for all 8
  (allowed exception: 301569 may legitimately GROW if sina now returns rows
  it lacked at 04:4x -- source drift on new-IPO face, disclosed separately,
  not a merge-law violation).
- zero_growth: appended_total==0 and mismatches==0 for the 8 (301569 growth
  counted under source_drift if it occurs).
- panel_restored: done back to 5228, attempts clean, status mirror
  complete=true after no-limit restore pass (zero network).
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import update_sina_mf as mf

SAMPLE = ["000001", "000858", "300750", "301569",
          "600519", "601318", "603259", "688981"]
OUT = os.path.join(ROOT, "results", "_r235_bma_sina_idem_spot.json")
BAK = os.path.join(mf.DATA_DIR, "_progress.json.r235bak")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def rows_n(p):
    with open(p, "r", encoding="utf-8") as f:
        return max(0, sum(1 for _ in f) - 1)


def main():
    paths = {c: os.path.join(mf.PER_DIR, c + ".csv") for c in SAMPLE}
    before = {c: {"sha": sha(paths[c]), "rows": rows_n(paths[c])} for c in SAMPLE}
    prog = mf.load_progress()
    shutil.copyfile(os.path.join(mf.DATA_DIR, "_progress.json"), BAK)
    prog["done"] = {c for c in prog["done"] if c not in SAMPLE}
    mf.save_progress(prog)

    r1 = subprocess.run([sys.executable, os.path.join("scripts", "update_sina_mf.py"),
                         "refresh", "8"], cwd=ROOT, capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, os.path.join("scripts", "update_sina_mf.py"),
                         "refresh"], cwd=ROOT, capture_output=True, text=True)

    after = {c: {"sha": sha(paths[c]), "rows": rows_n(paths[c])} for c in SAMPLE}
    prog2 = mf.load_progress()
    st = json.load(io.open(os.path.join(ROOT, "results", "sina_mf_update_status.json"),
                           encoding="utf-8"))

    identical = [c for c in SAMPLE if before[c]["sha"] == after[c]["sha"]]
    grown = [c for c in SAMPLE if after[c]["rows"] > before[c]["rows"]]
    shrunk = [c for c in SAMPLE if after[c]["rows"] < before[c]["rows"]]
    drift = {c: {"rows_before": before[c]["rows"], "rows_after": after[c]["rows"]}
             for c in SAMPLE if before[c]["sha"] != after[c]["sha"]}

    out = {
        "ts": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "machine": "bm-a", "round": "R235",
        "claim": "T-20260926-72-bm-a-sina-mf-collector s2 sec-4 line-3 spot",
        "sample_frozen": SAMPLE,
        "spot_stdout_tail": r1.stdout.strip().splitlines()[-3:],
        "restore_stdout_tail": r2.stdout.strip().splitlines()[-3:],
        "byte_identical": identical,
        "hash_drift_detail": drift,
        "row_growth": grown, "row_shrink": shrunk,
        "attempts_after": {c: (prog2["attempts"].get(c) or 0) for c in SAMPLE},
        "done_n_after": len(prog2["done"]),
        "status_mode": st.get("mode"), "panel_complete": st.get("panel", {}).get("complete"),
        "panel_cutoff": st.get("panel", {}).get("cutoff"),
        "verdict_byte_identity_all8": len(identical) == len(SAMPLE),
        "verdict_zero_growth": (not grown) and (not shrunk),
        "verdict_panel_restored": (len(prog2["done"]) == 5228
                                   and all((prog2["attempts"].get(c) or 0) == 0
                                           for c in SAMPLE)
                                   and st.get("panel", {}).get("complete") is True),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    if all([out["verdict_byte_identity_all8"], out["verdict_zero_growth"],
            out["verdict_panel_restored"]]):
        os.remove(BAK)
        print("SPOT PASS: byte-identity 8/8, zero growth, panel restored")
        return 0
    print("SPOT NOT CLEAN -- see", OUT, "(backup kept:", os.path.exists(BAK), ")")
    return 1


if __name__ == "__main__":
    sys.exit(main())
