# r863 escape: backup MM churn -> checkout clean -> (caller continues) -> restore own-lane live-wins
import shutil, subprocess, sys, os

GIT = r"C:\Program Files\Git\cmd\git.exe"
CHURN = [
    "results/saturation_engine/face_bm-a.json",
    "results/saturation_engine/history_bm-a.jsonl",
    "results/saturation_engine/state_bm-a.json",
]
BAK = os.path.join("results", "_r920bma_r863_backup")
os.makedirs(BAK, exist_ok=True)

if sys.argv[1:] == ["backup"]:
    for f in CHURN:
        shutil.copy2(f, os.path.join(BAK, os.path.basename(f)))
    print("backed up:", CHURN)
    r = subprocess.run([GIT, "checkout", "--"] + CHURN, capture_output=True)
    print("checkout rc:", r.returncode, r.stderr.decode("utf-8", "replace")[:200])
elif sys.argv[1:] == ["restore"]:
    for f in CHURN:
        shutil.copy2(os.path.join(BAK, os.path.basename(f)), f)
    print("restored live-wins:", CHURN)
