# -*- coding: utf-8 -*-
# r1035 bm-c: jayredo i2v harvest repair (delivery-face bug: SaveVideo node puts mp4 under
# outputs['15']['images'] with 'animated':[true] flag -- runner checked only gifs/videos).
# All 11 clips BURNED OK (~460s each, status success); runner marked ok:False and moved on.
# This script: wait runner exit -> harvest all 11 from /history -> fix progress json ->
# patch runner harvest line -> report. Re-ignition + Phase C/E delivery = separate step.
import io, json, os, sys, time, urllib.request

if not sys.stdout:
    sys.stdout = open(os.devnull, "w")

BASE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012"
MEDIA = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001"
PROG_PATH = os.path.join(MEDIA, "jayredo", "jayredo_v4_r1032_progress.json")
RECEIPT = os.path.join(BASE, "bmc", "jayredo_reshake6_r1032_receipt.json")
I2V_OUT = os.path.join(BASE, "bmc", "i2v", "jayredo")
RUNNER = os.path.join(BASE, "jayredo_v4_r1032.py")
SERVER = "http://127.0.0.1:8188"
LOG = open(os.path.join(MEDIA, "logs", "jayredo_harvest_repair_r1035.log"), "a", encoding="utf-8", buffering=1)

def P(*a):
    print(*a); print(*a, file=LOG)

def http_json(u, timeout=30):
    return json.loads(urllib.request.urlopen(u, timeout=timeout).read())

# ---- wait runner 78884 exit (B02 burn ends ~20:08:35; runner exits right after) ----
t0 = time.time()
while True:
    alive = False
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        h = k32.OpenProcess(0x1000, False, 78884)  # PROCESS_QUERY_LIMITED_INFORMATION
        if h:
            alive = True; k32.CloseHandle(h)
    except Exception:
        pass
    if not alive:
        P("runner 78884 exited after %ds wait" % int(time.time() - t0))
        break
    if time.time() - t0 > 900:
        P("runner still alive after 900s -- ABORT (will not race progress file)")
        sys.exit(2)
    time.sleep(15)

time.sleep(5)  # let runner's final save_prog land

# ---- load receipt plan + progress ----
receipt = json.load(io.open(RECEIPT, encoding="utf-8"))
plan = receipt["i2v_plan"]            # [{"slot": name, "frame": ..., "seed": 9700+i, ...}]
PROG = json.load(io.open(PROG_PATH, encoding="utf-8"))

# ---- harvest from history ----
h = http_json(SERVER + "/history?max_items=100", timeout=60)
got = {}
for k, v in h.items():
    if v.get("status", {}).get("status_str") != "success":
        continue
    pv = v.get("prompt"); p = pv[2] if isinstance(pv, list) else pv
    if not isinstance(p, dict) or "10" not in p:
        continue
    seed = p["10"].get("inputs", {}).get("noise_seed")
    if not isinstance(seed, int) or not (9700 <= seed <= 9710):
        continue
    o15 = v.get("outputs", {}).get("15", {})
    vids = (o15.get("images") or []) + (o15.get("gifs") or []) + (o15.get("videos") or [])
    if not vids:
        P("seed %d success but NO output file face" % seed)
        continue
    got[seed] = vids[0]

if len(got) < 11:
    P("history only has %d/11 -- B02 (9710) may still be missing" % len(got))

ok_n = 0
for it in plan:
    name, seed = it["slot"], it["seed"]
    out = os.path.join(I2V_OUT, name)
    if os.path.isfile(out) and os.path.getsize(out) > 500000:
        ok_n += 1
        PROG["i2v"][name] = {"ok": True, "file": name, "seed": seed,
                             "sec": round(os.path.getsize(out) / 1048576.0, 2),
                             "adj": it.get("adjustment", ""), "ts": time.strftime("%H:%M:%S")}
        continue
    if seed not in got:
        P("MISS seed %d (%s) -- not in history" % (seed, name))
        continue
    v = got[seed]
    u = "%s/view?filename=%s&subfolder=%s&type=%s" % (SERVER, v["filename"], v.get("subfolder", ""), v.get("type", "output"))
    data = urllib.request.urlopen(u, timeout=300).read()
    io.open(out, "wb").write(data)
    if len(data) > 500000:
        PROG["i2v"][name] = {"ok": True, "file": name, "seed": seed,
                             "sec": round(len(data) / 1048576.0, 2),
                             "adj": it.get("adjustment", ""), "ts": time.strftime("%H:%M:%S")}
        ok_n += 1
        P("SAVED %s (%.2f MB, seed %d, src %s)" % (name, len(data) / 1048576.0, seed, v["filename"]))
    else:
        P("BAD SIZE %s (%d bytes)" % (name, len(data)))

json.dump(PROG, io.open(PROG_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- patch runner harvest line (defense-in-depth: images key + animated flag semantics) ----
src = io.open(RUNNER, encoding="utf-8", newline="").read()
OLD = 'for vid in (out.get("gifs") or []) + (out.get("videos") or []):'
NEW = 'for vid in (out.get("gifs") or []) + (out.get("videos") or []) + (out.get("images") or []):'
if OLD in src:
    io.open(RUNNER, "w", encoding="utf-8", newline="").write(src.replace(OLD, NEW, 1))
    P("runner harvest line PATCHED (images key added)")
elif NEW in src:
    P("runner harvest line already patched")
else:
    P("runner harvest line NOT FOUND -- manual review needed")

P("harvest complete: %d/11 files ok" % ok_n)
if ok_n == 11:
    print("HARVEST-REPAIR OK 11/11")
    sys.exit(0)
print("HARVEST-REPAIR PARTIAL %d/11" % ok_n)
sys.exit(1)
