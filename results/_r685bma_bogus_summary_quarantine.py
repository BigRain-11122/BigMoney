"""r685 bm-a: quarantine-move bogus W3 summary (red finalize run vs 6136-row
dup-carrying checkpoint), then fresh finalize regenerates the face.

Treasure guard rc3'd deletion of the registered face path -> law-prescribed
alternative: extract-aside (quarantine observation window) + regenerate.
Bogus summary was UNTRACKED (never committed/pushed) -- private correction.
"""
import hashlib, json, os, shutil, time

SRC = r"results/mass_trial/w3_screen_summary.json"
TS = time.strftime("%Y%m%d-%H%M%S")
QD = os.path.join("results", "_quarantine", f"{TS}_r685bma_w3_bogus_summary")
DST_DIR = os.path.join(QD, "results", "mass_trial")
os.makedirs(DST_DIR, exist_ok=True)
raw = open(SRC, "rb").read()
dst = os.path.join(DST_DIR, "w3_screen_summary.json")
shutil.move(SRC, dst)
manifest = {
    "ts": TS,
    "reason": "r685 bogus finalize output: ran vs 6136-row checkpoint (1227 dup-id "
              "lines auto-merged from bm-b 53b9f3dec in-flight shard-1 re-burn) -> "
              "n_candidates 6041/complete=false/ledger batch_trials 6041; never "
              "committed (untracked); regenerating face after r482 dedup heal",
    "law": "TREASURE_PROTECTION_LAW v1.0 s2 (guard rc3 -> aside + regenerate)",
    "observation_window_days": 7,
    "moved": [{
        "src": SRC, "dst": dst.replace("\\", "/"),
        "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw),
    }],
}
json.dump(manifest, open(os.path.join(QD, "manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps({"quarantined": dst, "sha256": manifest["moved"][0]["sha256"]}))
