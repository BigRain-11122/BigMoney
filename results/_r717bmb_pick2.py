# r717 pick-2 resolver: 3 bm-b-owned satengine faces -- probe ts, expect churn(:3:), assert
import subprocess, json, re, sys

FACES = ["results/saturation_engine/face_bm-b.json",
         "results/saturation_engine/history_bm-b.jsonl",
         "results/saturation_engine/state_bm-b.json"]

def sh(a): return subprocess.run(a, capture_output=True)

def blob(stage, path):
    r = sh(["git","show",f":{stage}:{path}"])
    assert r.returncode == 0, f"rc={r.returncode} {path}"
    return r.stdout

TSRE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")
for p in FACES:
    b2, b3 = blob("2",p), blob("3",p)
    t2 = max(TSRE.findall(b2.decode("utf-8","replace"))) if TSRE.search(b2.decode("utf-8","replace")) else ""
    t3 = max(TSRE.findall(b3.decode("utf-8","replace"))) if TSRE.search(b3.decode("utf-8","replace")) else ""
    # bm-b-owned lane face: churn side authoritative; ts probe must confirm not-older
    assert t3 >= t2, f"churn side older for bm-b-owned face {p}: t2={t2} t3={t3}"
    if p.endswith(".json"):
        json.loads(b3)
    open(p,"wb").write(b3)
    # re-read: no markers, parse ok
    back = open(p,"rb").read()
    assert b"<<<<<<<" not in back and b">>>>>>>" not in back
    print(f"{p}: take-churn(bm-b-owned) t2={t2} t3={t3} {len(b3)}B")
print("PICK2-RESOLVED 3")
