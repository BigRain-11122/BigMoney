# -*- coding: utf-8 -*-
# krea2_kf_pipeline_bmc.py - bm-c pipeline: download Krea2 three-piece (ModelScope mirror), then run kf_fix2_fleet.py
# CEO order O-20261010-1105/113x: install Krea2 (~15GB) -> generate female-lead 3 frames (KF8/KF9/KF10)
# Batch C1783. Pattern proven by int8_dit_downloader_bmc.py (8-segment ranged, resume-capable).
import os, sys, json, time, threading, urllib.request, struct, subprocess

BASE_URL = "https://modelscope.cn/models/Comfy-Org/Krea-2/resolve/master/"
MODELS = "D:\\ComfyUI\\ComfyUI\\models"
PARTS_DIR = MODELS + "\\_krea2_parts"
FILES = [
    ("diffusion_models/krea2_turbo_fp8_scaled.safetensors", 13141730784, MODELS + "\\diffusion_models\\krea2_turbo_fp8_scaled.safetensors"),
    ("text_encoders/qwen3vl_4b_fp8_scaled.safetensors", 5242467968, MODELS + "\\text_encoders\\qwen3vl_4b_fp8_scaled.safetensors"),
    ("vae/qwen_image_vae.safetensors", 253806246, MODELS + "\\vae\\qwen_image_vae.safetensors"),
]
NSEG = 8
REPO = "K:/Fluxgroup/FluxGroup"
KF_SCRIPT = REPO + "/cph4/fleet/mv0001-handover/outbound/krea2/30s-reel-v1/kf_fix2_fleet.py"
FRAMES_DIR = REPO + "/cph4/fleet/mv0001-handover/outbound/krea2/30s-reel-v1/frames"
DONE_MARKER = FRAMES_DIR + "/_krea2_kf_pipeline_done.json"
LOG = "K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\results\\_c1783_krea2_kf_pipeline.log"
SERVER = "http://127.0.0.1:8188"


def log(msg):
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def seg(url, total, idx, part):
    lo = total * idx // NSEG
    hi = total * (idx + 1) // NSEG - 1
    want = hi - lo + 1
    have = os.path.getsize(part) if os.path.exists(part) else 0
    if have >= want:
        log("seg%d already complete (%d)" % (idx, have))
        return
    t0 = time.time()
    while True:
        try:
            req = urllib.request.Request(url, headers={"Range": "bytes=%d-%d" % (lo + have, hi)})
            r = urllib.request.urlopen(req, timeout=60)
            with open(part, "ab") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    have += len(chunk)
            break
        except Exception as e:
            have = os.path.getsize(part) if os.path.exists(part) else 0
            log("seg%d retry at %d: %s" % (idx, have, str(e)[:100]))
            time.sleep(3)
    dt = time.time() - t0
    log("seg%d done %d bytes in %.0fs (%.1f MB/s)" % (idx, have, dt, have / dt / 1e6 if dt > 0 else 0))


def fetch_file(rel, total, final):
    if os.path.exists(final) and os.path.getsize(final) == total:
        log("FINAL already present with correct size: %s" % rel)
        return
    url = BASE_URL + rel
    log("download start %s total=%d" % (rel, total))
    ths = [threading.Thread(target=seg, args=(url, total, i, os.path.join(PARTS_DIR, rel.replace("/", "__") + ".part%d" % i)), daemon=True) for i in range(NSEG)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    sizes = [os.path.getsize(os.path.join(PARTS_DIR, rel.replace("/", "__") + ".part%d" % i)) for i in range(NSEG)]
    if sum(sizes) != total or any(s != (total * (i + 1) // NSEG - total * i // NSEG) for i, s in enumerate(sizes)):
        log("SIZE MISMATCH %s parts=%s" % (rel, sizes))
        sys.exit(2)
    with open(final, "wb") as out:
        for i in range(NSEG):
            with open(os.path.join(PARTS_DIR, rel.replace("/", "__") + ".part%d" % i), "rb") as f:
                while True:
                    chunk = f.read(1 << 22)
                    if not chunk:
                        break
                    out.write(chunk)
    fs = os.path.getsize(final)
    with open(final, "rb") as f:
        hlen = struct.unpack("<Q", f.read(8))[0]
    ok = fs == total and 0 < hlen < 100_000_000
    log("FINAL assembled %s size=%d (expect %d) header_len=%d -> %s" % (rel, fs, total, hlen, "OK" if ok else "BAD"))
    if not ok:
        sys.exit(3)
    for i in range(NSEG):
        os.remove(os.path.join(PARTS_DIR, rel.replace("/", "__") + ".part%d" % i))


def main():
    os.makedirs(PARTS_DIR, exist_ok=True)
    t_all = time.time()
    for rel, total, final in FILES:
        os.makedirs(os.path.dirname(final), exist_ok=True)
        fetch_file(rel, total, final)
    log("all three Krea2 files in place (%.0fs total)" % (time.time() - t_all))
    # free ComfyUI VRAM before loading Krea2
    try:
        urllib.request.urlopen(urllib.request.Request(SERVER + "/free", data=json.dumps({"unload_models": True}).encode(), headers={"Content-Type": "application/json"}), timeout=30).read()
        log("comfy /free unload_models done")
    except Exception as e:
        log("comfy /free failed (continuing): %s" % str(e)[:100])
    t_kf = time.time()
    log("launching kf_fix2_fleet.py ...")
    p = subprocess.run([sys.executable, KF_SCRIPT, "--repo", REPO], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=7200)
    log("kf_fix2_fleet.py exit=%d stdout_tail:" % p.returncode)
    for ln in (p.stdout or "").splitlines()[-12:]:
        log("  | " + ln)
    if p.returncode != 0:
        for ln in (p.stderr or "").splitlines()[-12:]:
            log("  ! " + ln)
    frames_ok = {}
    for name in ("KF8_case", "KF9_profile", "KF10_walkaway"):
        fp = os.path.join(FRAMES_DIR, name + ".png")
        frames_ok[name] = (os.path.getsize(fp) if os.path.exists(fp) else 0)
    marker = {
        "batch": "C1783",
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kf_exit": p.returncode,
        "frames_bytes": frames_ok,
        "download_seconds": round(time.time() - t_all),
        "machine": "bm-c",
    }
    with open(DONE_MARKER, "w", encoding="utf-8") as f:
        json.dump(marker, f, indent=1)
    log("PIPELINE DONE marker written: %s" % DONE_MARKER)
    log("ALL DONE frames_ok=%s" % frames_ok)


if __name__ == "__main__":
    main()
