# r986 closeout part A: astock segment-3 settle-cycle -> complete snapshot -> update_daily -> NEWBAR chain legs.
# Sequencing law (this round): segment-3 must settle the 11 n=2 symbols at exp=10-14 BEFORE
# update_daily lands 10-15 (a new expected cutoff re-arms settled counters -> 3 fresh cycles needed).
import subprocess, json, time, io, os, datetime, sys

def run(args, cap=None, inp=None):
    if cap:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE if inp else None)
        dl = time.time() + cap
        while p.poll() is None and time.time() < dl:
            time.sleep(1)
        if p.poll() is None:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
            out, err = p.communicate(inp)
            raise RuntimeError("TIMEOUT %s :: %s" % (args[:3], (err or b"")[-300:].decode("utf-8", "replace")))
        out, err = p.communicate(inp)
        return out
    r = subprocess.run(args, capture_output=True, input=inp)
    return r.stdout

def status_face():
    out = run(["python", "scripts/update_astock_daily.py", "status"]).decode("utf-8", "replace")
    return json.loads(out)

# ---- 1) wait for segment-3 spawn window, spawn, wait for complete ----
deadline = time.time() + 900
complete = False
face = None
spawned = False
while time.time() < deadline:
    face = status_face()
    if face.get("panel", {}).get("complete"):
        complete = True
        break
    if not spawned:
        out = run(["python", "scripts/update_astock_daily.py"]).decode("utf-8", "replace").strip()
        print("[gate]", out[-160:])
        spawned = ("throttle" not in out)
        time.sleep(60 if not spawned else 90)
        continue
    time.sleep(45)

face = status_face()
complete = bool(face.get("panel", {}).get("complete"))
print("astock complete=%s quarantined=%s settled_face_n=%s per_files=%s cutoff=%s mode=%s" % (
    complete, face.get("quarantined_n"), face.get("settled_n"),
    face.get("panel", {}).get("per_files"), face.get("panel", {}).get("cutoff"), face.get("mode")))

# snapshot the completion face as the rebuild evidence artifact (package head)
with io.open("results/_r986bmb_astock_complete.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump({
        "captured_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "rebuild_cycle": "tree-loss recovery full-universe re-pull, closed after 3 gate segments (r985 17:38, r986 18:25, r986 19:0x)",
        "complete": complete,
        "status_face": face,
        "disclosure": ("8 symbols quarantined at 3-strike (attempts=3: 000019/001235/001381/301718/688089/688143/688173/689009); "
                        "11 suspended-settled at exp=2026-10-14 (n=3 settle law r305); universe 5229; per_files on disk counted"),
    }, f, ensure_ascii=False, indent=1)
print("snapshot written: results/_r986bmb_astock_complete.json complete=%s" % complete)

if not complete:
    print("HONEST DEFER: rebuild not complete -> update_daily held (settle-cycle sequencing), package defers to next round")
    sys.exit(0)

# ---- 2) update_daily: land the 10-15 ETF bars (expected cutoff face moves) ----
out = run(["python", "scripts/update_daily.py"], cap=300)
tail = out.decode("utf-8", "replace").strip().splitlines()[-3:]
print("[update_daily]", " | ".join(tail))
