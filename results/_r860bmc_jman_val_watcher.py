# -*- coding: utf-8 -*-
# _r860bmc_jman_val_watcher.py -- bm-c jman LoRA completion watcher (O-20261010-0025)
# Self-contained: WAIT trainer -> VAL grid (4 scenes x strength {0,0.8,1.0}) -> LOOKBOARD_variant_640 -> recovery debt -> receipt.
# Zero-window: run under pythonw.exe, self-logs to file (bm-c pit law). SLA: board on-chain <= 10:00.
import json, os, shutil, subprocess, sys, time, urllib.request, uuid

OUT_DIR   = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\jman-lora-640\frames"
BOARD     = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\jman-lora-640\LOOKBOARD_variant_640.jpg"
RECEIPT   = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r860bmc_jman_val_receipt.json"
LOG       = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r860bmc_jman_val_watcher.log"
CKPT_DIR  = r"D:\musubi-tuner\outputs\jman_v1_640"
FINAL_CKPT= os.path.join(CKPT_DIR, "jman_v1_rank32_cont-000012.safetensors")
LORA_DST  = r"D:\ComfyUI\ComfyUI\models\loras\jman_v1_640_rank32_final.safetensors"
LORA_NAME = "jman_v1_640_rank32_final.safetensors"
SERVER    = "http://127.0.0.1:8188"
T_START   = time.time()
HARD_KILL_AT = time.mktime(time.strptime("2026-10-11 09:35:00", "%Y-%m-%d %H:%M:%S"))  # r833 precedent: same CEO-line priority kill
CNW = 0x08000000  # CREATE_NO_WINDOW

SCENES = [
    ("promo_closeup", 9011,
     "jman, a young Taiwanese man in his early twenties with heavy-lidded dark eyes and dark hair falling over his forehead, "
     "frontal close-up portrait, face clearly visible, lips slightly parted, wearing a plain dark crew-neck sweater, "
     "dark low-key studio light with soft falloff, 2002 Taiwanese album promotional photograph"),
    ("library_lamplight", 9012,
     "jman, a young Taiwanese man in his early twenties with heavy-lidded dark eyes, half-body view, seated at a heavy wooden "
     "table in a dim ancient library, his face turned toward a tall stack of cloth-bound books, lit by a single warm oil lamp, "
     "chiaroscuro, film still from a Taiwanese music video filmed in 2001, 35mm film grain"),
    ("campus_bicycle", 9013,
     "jman, a young Taiwanese man in his early twenties with heavy-lidded dark eyes, dark hair falling over his forehead, "
     "standing beside an old bicycle in a sunlit university corridor with arched columns, wearing a loose plain white "
     "short-sleeve shirt and straight-leg jeans, late afternoon light, film still from a Taiwanese music video filmed in 2001, 35mm film grain"),
    ("stage_mic", 9014,
     "jman, a young Taiwanese man in his early twenties with heavy-lidded dark eyes, standing close to a vintage microphone "
     "on a dim stage, one warm spotlight from above, plain dark shirt, faint smoke haze in the beam, film still from a "
     "Taiwanese music video filmed in 2001, 35mm film grain"),
]
STRENGTHS = [0.0, 0.8, 1.0]

def log(msg):
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def post(url, payload, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

def get(url, timeout=30):
    return json.loads(urllib.request.urlopen(url, timeout=timeout).read())

def trainer_pids():
    try:
        import psutil
        pids = []
        for p in psutil.process_iter(["pid", "cmdline"]):
            try:
                cl = " ".join(p.info["cmdline"] or [])
                if "krea2_train_network.py" in cl:
                    pids.append(p.info["pid"])
            except Exception:
                pass
        return pids
    except Exception:
        try:
            ps = ("(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                  "Where-Object {$_.CommandLine -like '*krea2_train_network.py*'}).Count")
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                                  capture_output=True, text=True, creationflags=CNW, timeout=30)
            n = int((out.stdout or "0").strip() or 0)
            return ["unknown"] * n
        except Exception:
            return ["unknown"]

def kill_pid(pid):
    try:
        subprocess.run(["taskkill", "/PID", str(pid), "/F", "/T"], capture_output=True, creationflags=CNW, timeout=30)
    except Exception as e:
        log("kill %s failed: %s" % (pid, str(e)[:80]))

def latest_ckpt():
    best, best_t = None, 0
    if os.path.isdir(CKPT_DIR):
        for fn in os.listdir(CKPT_DIR):
            if fn.startswith("jman_v1_rank32_cont-") and fn.endswith(".safetensors"):
                fp = os.path.join(CKPT_DIR, fn)
                t = os.path.getmtime(fp)
                if t > best_t:
                    best, best_t = fp, t
    return best, best_t

def phase_wait():
    """Wait for training completion. Returns (ckpt_used, mode)."""
    log("WAIT phase start")
    while True:
        final = os.path.exists(FINAL_CKPT) and os.path.getsize(FINAL_CKPT) > 4e8
        age_ok = final and (time.time() - os.path.getmtime(FINAL_CKPT)) > 90
        pids = trainer_pids()
        if final and age_ok and not pids:
            return FINAL_CKPT, "final_clean"
        if final and age_ok and pids and (time.time() - os.path.getmtime(FINAL_CKPT)) > 300:
            log("final ckpt stable 5min, trainer hung on teardown -> kill %s" % pids)
            for pid in pids: kill_pid(pid)
            return FINAL_CKPT, "final_killed_teardown_hang"
        if not pids:
            ck, _ = latest_ckpt()
            if ck:
                return ck, "trainer_gone_fallback_latest"
        if time.time() > HARD_KILL_AT:
            if pids:
                log("HARD_KILL window reached -> kill trainer %s (r833 same-line priority)" % pids)
                for pid in pids: kill_pid(pid)
                time.sleep(10)
            ck, _ = latest_ckpt()
            return (ck or FINAL_CKPT), "hard_kill_timeout_fallback"
        log("wait tick: final=%s stable=%s trainer=%s" % (final, age_ok, pids))
        time.sleep(60)

def comfy_free():
    try:
        post(SERVER + "/free", {"unload_models": True, "free_memory": True}, timeout=60)
        log("comfy /free unload done")
    except Exception as e:
        log("comfy /free failed (continue): %s" % str(e)[:80])

def graph(prompt_text, seed, lora_on, strength):
    model_src = ["10", 0]
    if lora_on:
        model_src = ["15", 0]
    g = {
        "10": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "11": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "12": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "6":  {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_text, "clip": ["11", 0]}},
        "13": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["6", 0]}},
        "5":  {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "3":  {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 8, "cfg": 1.0, "sampler_name": "euler",
               "scheduler": "simple", "denoise": 1.0, "model": model_src, "positive": ["6", 0],
               "negative": ["13", 0], "latent_image": ["5", 0]}},
        "8":  {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["12", 0]}},
        "29": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "jman_val"}},
    }
    if lora_on:
        g["15"] = {"class_type": "LoraLoaderModelOnly",
                   "inputs": {"lora_name": LORA_NAME, "strength_model": strength, "model": ["10", 0]}}
    return g

def gen_one(name, prompt_text, seed, lora_on, strength, out_path, deadline_s=1800):
    pid = post(SERVER + "/prompt", {"prompt": graph(prompt_text, seed, lora_on, strength),
                                    "client_id": str(uuid.uuid4())})["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < deadline_s:
        time.sleep(3)
        h = get(SERVER + "/history/" + pid)
        if pid in h:
            if "status" in h[pid] and h[pid]["status"].get("status_str") == "error":
                return False, "execution_error"
            for nid, out in h[pid]["outputs"].items():
                for img in out.get("images", []):
                    data = urllib.request.urlopen(
                        "%s/view?filename=%s&subfolder=%s&type=%s" % (
                            SERVER, img["filename"], img.get("subfolder", ""), img.get("type", "output")),
                        timeout=120).read()
                    with open(out_path, "wb") as f:
                        f.write(data)
                    return True, round(time.time() - t0, 1)
    return False, "timeout"

def phase_val(ckpt_path):
    log("VAL phase start, ckpt=%s" % ckpt_path)
    shutil.copyfile(ckpt_path, LORA_DST)
    log("lora copied -> %s (%d B)" % (LORA_DST, os.path.getsize(LORA_DST)))
    os.makedirs(OUT_DIR, exist_ok=True)
    comfy_free()
    results, gen_meta = {}, {}
    for si, (sname, seed, prompt) in enumerate(SCENES):
        for strength in STRENGTHS:
            tag = "%s_s%s" % (sname, int(strength * 10))
            out_path = os.path.join(OUT_DIR, tag + ".png")
            ok, info = gen_one(tag, prompt, seed, True, strength, out_path)
            results[tag] = {"ok": ok, "seed": seed, "strength": strength, "info": info,
                            "bytes": os.path.getsize(out_path) if ok else 0}
            log("gen %s -> ok=%s %ss" % (tag, ok, info))
            gen_meta[tag] = ok
    comfy_free()
    return results, all(gen_meta.values())

def phase_board():
    log("BOARD phase start")
    from PIL import Image, ImageDraw
    cell = 440
    pad, lab_h, head_h = 12, 34, 56
    cols = len(STRENGTHS)
    rows = len(SCENES)
    W = pad + cols * (cell + pad)
    H = head_h + lab_h + rows * (cell + lab_h + pad)
    board = Image.new("RGB", (W, H), (18, 16, 14))
    d = ImageDraw.Draw(board)
    ck_name = os.path.basename(FINAL_CKPT)
    d.text((pad, 16), "JMAN LoRA LOOKBOARD variant_640 | 4 canonical scenes x strength {0, 0.8, 1.0} | ckpt %s (16 ep) | fixed seed per scene | bm-c 2026-10-11" % ck_name, fill=(225, 210, 180))
    for c, st in enumerate(STRENGTHS):
        d.text((pad + c * (cell + pad) + 8, head_h + 8), "strength %.1f%s" % (st, "  (base model)" if st == 0 else ""), fill=(200, 190, 170))
    ok_cells = 0
    for r, (sname, seed, _) in enumerate(SCENES):
        y = head_h + lab_h + r * (cell + lab_h + pad)
        d.text((pad, y + 10), "%s  seed=%d" % (sname, seed), fill=(210, 200, 180))
        for c, st in enumerate(STRENGTHS):
            tag = "%s_s%s" % (sname, int(st * 10))
            fp = os.path.join(OUT_DIR, tag + ".png")
            x = pad + c * (cell + pad)
            if os.path.exists(fp):
                try:
                    im = Image.open(fp).convert("RGB").resize((cell, cell), Image.LANCZOS)
                    board.paste(im, (x, y))
                    ok_cells += 1
                except Exception as e:
                    d.text((x + 8, y + cell // 2), "IMG ERR %s" % str(e)[:30], fill=(200, 80, 80))
            else:
                d.rectangle([x, y, x + cell, y + cell], outline=(120, 60, 60), width=2)
                d.text((x + 8, y + cell // 2), "MISSING %s" % tag, fill=(200, 90, 90))
    os.makedirs(os.path.dirname(BOARD), exist_ok=True)
    board.save(BOARD, "JPEG", quality=88)
    return ok_cells, os.path.getsize(BOARD)

def phase_recovery():
    log("RECOVERY phase start (debt trio)")
    res = {}
    for tn in ("MiniGameOllamaServe", "MiniGameOllamaKeepWarm"):
        try:
            r = subprocess.run(["schtasks", "/change", "/tn", tn, "/enable"],
                               capture_output=True, text=True, creationflags=CNW, timeout=30)
            res[tn + "_enable"] = (r.returncode == 0)
            if tn == "MiniGameOllamaServe":
                r2 = subprocess.run(["schtasks", "/run", "/tn", tn],
                                    capture_output=True, text=True, creationflags=CNW, timeout=30)
                res[tn + "_run"] = (r2.returncode == 0)
        except Exception as e:
            res[tn] = "err:%s" % str(e)[:60]
    log("recovery: %s" % res)
    return res

def main():
    log("=== jman val watcher start (python %s) ===" % sys.version.split()[0])
    receipt = {"machine": "bm-c", "order": "O-20261010-0025", "sla": "board<=10:00",
               "started_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    try:
        ckpt, mode = phase_wait()
        receipt["wait_mode"], receipt["ckpt_used"] = mode, ckpt
        log("WAIT done mode=%s ckpt=%s" % (mode, ckpt))
        results, all_ok = phase_val(ckpt)
        receipt["gens"] = {k: v["ok"] for k, v in results.items()}
        receipt["gen_details"] = results
        receipt["all_gens_ok"] = all_ok
        ok_cells, board_bytes = phase_board()
        receipt["board"] = {"path": BOARD, "bytes": board_bytes, "cells_ok": ok_cells, "cells_total": len(SCENES) * len(STRENGTHS)}
        rec = phase_recovery()
        receipt["recovery"] = rec
        receipt["status"] = "OK" if (all_ok and ok_cells == len(SCENES) * len(STRENGTHS)) else ("PARTIAL" if ok_cells > 0 else "FAIL")
    except Exception as e:
        import traceback
        receipt["status"] = "EXCEPTION"
        receipt["error"] = str(e)[:500]
        receipt["trace"] = traceback.format_exc()[-1500:]
        log("EXCEPTION: %s" % receipt["trace"][-400:])
    receipt["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    receipt["elapsed_s"] = round(time.time() - T_START, 1)
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=1, ensure_ascii=False)
    log("=== watcher done status=%s receipt=%s ===" % (receipt.get("status"), RECEIPT))

if __name__ == "__main__":
    main()
