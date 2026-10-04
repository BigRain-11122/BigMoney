"""r685 bm-a: quarantine-move the wrong-prev_total W3 summary (regenerate #2).

Summary #2 carried prev_total=648,026 (ledger_head saw the quarantined bogus
copy before the scanner exclusion landed). Untracked; aside + regenerate.
"""
import hashlib, json, os, shutil, time

SRC = r"results/mass_trial/w3_screen_summary.json"
TS = time.strftime("%Y%m%d-%H%M%S")
QD = os.path.join("results", "_quarantine", f"{TS}_r685bma_w3_wrongprev_summary")
DST_DIR = os.path.join(QD, "results", "mass_trial")
os.makedirs(DST_DIR, exist_ok=True)
raw = open(SRC, "rb").read()
dst = os.path.join(DST_DIR, "w3_screen_summary.json")
shutil.move(SRC, dst)
d = json.loads(raw.decode("utf-8"))
manifest = {
    "ts": TS,
    "reason": "r685 regenerate #2: summary ledger built prev_total=648,026 "
              "(ledger_head consumed quarantine #1 bogus copy before the "
              "r685 _quarantine exclusion landed in science_gates); "
              "complete=true but chain position inflated by 6,041; "
              "untracked, aside + regenerate clean",
    "law": "TREASURE_PROTECTION_LAW v1.0 s2 (guard rc3 -> aside + regenerate)",
    "observation_window_days": 7,
    "moved": [{
        "src": SRC, "dst": dst.replace("\\", "/"),
        "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw),
    }],
    "ledger_state": d.get("trials_ledger"),
}
json.dump(manifest, open(os.path.join(QD, "manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps({"quarantined": dst, "ledger": manifest["ledger_state"]},
                 ensure_ascii=False))
