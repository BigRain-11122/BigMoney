# r270 bm-b -- heartbeat write: last_seen/round/current_task/verdict/epoch(int)/clock_read(T-sep), byte-face mirrored.
import json, subprocess, time, datetime as dt

P = "fleet/machines/bm-b.json"
blob = subprocess.run(["git", "cat-file", "blob", "HEAD:" + P.replace("\\", "/")],
                      capture_output=True, check=True).stdout
bom = blob.startswith(b"\xef\xbb\xbf")
crlf = b"\r\n" in blob
trailing = blob.endswith(b"\n")
txt = blob.decode("utf-8-sig")
hb = json.loads(txt)
lines = txt.rstrip("\n").split("\n")
indent = len(lines[1]) - len(lines[1].lstrip(" "))

try:
    import psutil
    ram = round(psutil.virtual_memory().available / (1 << 30), 1)
    svmem = psutil.virtual_memory()
except Exception:
    ram = None
gpu_idle = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
    t, u = [int(x.strip()) for x in out.stdout.strip().split(",")]
    gpu_idle = t - u
except Exception:
    pass

now = dt.datetime.now().astimezone()
hb["last_seen"] = now.isoformat(timespec="seconds")
hb["round_no"] = 270
hb["current_task"] = ("r270 done: post_review sha-anchor oscillation P0 fixed (producers LF-normalize + criteria "
                      "re-anchored, reviewer 28 YES/0 NO); T-76 face (a) channels closed = wave-10 all-faces; "
                      "next: Monday 09-28 window channels run-6/10/4 + marks on new bar")
hb["cpu_cores"] = 16
if ram is not None:
    hb["idle_ram_gb"] = ram
if gpu_idle is not None:
    hb["gpu_idle_vram_mb"] = gpu_idle
hb["verdict"] = ("healthy r270: P0 sha-oscillation root-fixed both ends (reviewer 28 YES/0 NO post-fix); "
                 "T-76 wave-10 five faces closed; S6 ~24 legs exit 0; smoke 25/25; pool 49/49; orders 83/83")
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now.isoformat(timespec="seconds")
out = json.dumps(hb, ensure_ascii=False, indent=indent)
if crlf:
    out = out.replace("\n", "\r\n")
if trailing:
    out += "\r\n" if crlf else "\n"
if bom:
    out = "\xef\xbb\xbf" + out
with open(P, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)

# self-verify per R170/R178/R262 law
chk = json.loads(open(P, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO"
print("hb written: epoch=%d (int ok) | clock=%s | ram=%s | gpu_idle=%s | faces bom=%s crlf=%s trail=%s indent=%d"
      % (chk["heartbeat_epoch_utc"], chk["clock_read"], ram, gpu_idle, bom, crlf, trailing, indent))
