# -*- coding: utf-8 -*-
# bmc_v3_chain_r969.py -- O-20261013-1530 @bm-c MV V3 冲刺批续链（QC-r969 复验后）
# Phase 1: boot ComfyUI (D:\ComfyUI\ComfyUI, default 127.0.0.1:8188)
# Phase 2: refire-2 三席定向重烧（H3 INT8 768P i2v；QC-r969 FAIL 修法：C02 埋碑事件量化+C04
#          方向锚定（亮化行进非衰退）+R05 完底+尘点）→ CDN 上传 + I2V-URL-INDEX 追加
#          （版本梯：C02 v5->v6 · C04 v3->v4 · R05 v3->v4；种子 9240+）
# Phase 3: 服务器重启（H3->Krea2 换模龟速律=杀进程重boot）
# Phase 4: V3-NEWKF 试构图批（7 镜 x 4 种子=28 张·672x384·jman 0.6 影射档·种子 9011-9014）
#          -> bmc/<镜位id>_s<种子>.png + q88 看板（<=1MB）
# Phase 5: 复 pin（重启用 MiniGameOllamaServe/KeepWarm 两任务）
# 律：纯画面无音轨 · FIFO 共服不动他窗队列项 · v2 提示词律（运动优先/量化/零重述/零文化锚）
# 血统：bmc_v3_refire.py（r965）+ bmc_kf_i2v_chain.py（KF 图）verbatim 复用范式。
import json, os, re, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bmc_night_factory as nf  # __main__ guard in place

BMC = os.path.join(HERE, "bmc")
FRAMES_DIR = os.path.join(BMC, "i2v_frames")
OUT_DIR = os.path.join(BMC, "archive_i2v")
ARCH = r"K:\Fluxgroup\archive\mv0001-kf-frames-bmc-r840\frames_full"
SERVER = "http://127.0.0.1:8188"
NEWKF_PACK = os.path.join(HERE, "V3-NEWKF-PACK-v1.md")
COMFY_EXE = r"D:\ComfyUI\python_embeded\python.exe"
COMFY_CWD = r"D:\ComfyUI"

ALIGN = ("For the target video, at 0.00 seconds into the target video, "
         "<Picture 1> (from [Shot 1]) is fully referenced.")
TAIL = (" overall_soundscape: quiet room tone with faint air and dust settling"
        " non_diegetic_music: N/A (song laid in post)"
        " About 5.2 seconds, 16:9 aspect.")

# QC-r969 FAIL 三席定向修法（病灶：C02 埋碑事件全缺+C04 光反向扫+R05 行进未到底零尘）
REFIRE2 = [
    ("C02_sand_bury_v6", os.path.join(ARCH, "C02_sand_bury.png"),
     "Locked-off medium shot. Sand creeps up the base of the stone in visible steps: within the first "
     "second a low drift of loose grains slides in from the right and settles over the lowest carved row, "
     "and with each following second another thin layer settles over the last, the burial line climbing "
     "until the bottom two carved rows read half-swallowed by the final second. Loose grains keep rolling "
     "across the foreground ground the whole time, a few hopping over the drift. The stone itself never "
     "moves and its edges stay free of any glow or halo. Preserve the original amber palette and film grain."),
    ("C04_words_alive_v4", os.path.join(FRAMES_DIR, "C04_words_alive_v2.png"),
     "Locked-off close shot. The narrow row of wedge marks grows brighter in a slow left-to-right pass: "
     "starting from the left edge one column at a time the marks warm toward a stronger gold, the "
     "brightening edge advancing steadily rightward, each column reaching its full glow in turn and then "
     "holding it steady, the columns to the right staying dim until the edge reaches them, the whole band "
     "carrying its full glow by the final second. Fine dust lifts softly where the edge passes. The carved "
     "surface and the framing stay unmoved. Preserve the matte black stone and the original amber palette."),
    ("R05_gold_threads_v4", os.path.join(ARCH, "R05_gold_threads.png"),
     "Locked-off close shot. The gold seam brightens in one continuous downward pass that starts at the "
     "top of the seam and reaches the very bottom of the frame before the final second: the glow stays a "
     "narrow moving edge, passed sections settling to a steady warm shine, the section below staying dark "
     "until the edge arrives. A few fine dust motes drift slowly upward inside the lit stretch of the seam. "
     "The carved rows stay rigid. Preserve the film grain and the original amber palette."),
]

SERVER_PROC = [None]


def boot_server(tag, wait=240):
    # 杀旧实例（换模龟速律：模型切换一律杀进程重boot）
    subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI",
                    "WINDOWTITLE eq ComfyUI*"], capture_output=True)
    try:
        out = subprocess.check_output(["wmic", "process", "where",
                                       "commandline like '%ComfyUI\\\\main.py%' get processid"],
                                     ).decode("utf-8", "replace")
        for line in out.splitlines():
            line = line.strip()
            if line.isdigit():
                subprocess.run(["taskkill", "/F", "/PID", line], capture_output=True)
    except Exception:
        pass
    log = open(os.path.join(BMC, "comfy_%s.out.log" % tag), "ab")
    err = open(os.path.join(BMC, "comfy_%s.err.log" % tag), "ab")
    p = subprocess.Popen([COMFY_EXE, "-s", "ComfyUI\\main.py", "--windows-standalone-build"],
                         cwd=COMFY_CWD, stdout=log, stderr=err,
                         creationflags=0x08000000)  # CREATE_NO_WINDOW
    SERVER_PROC[0] = p
    t0 = time.time()
    while time.time() - t0 < wait:
        time.sleep(5)
        try:
            nf.http_json(SERVER + "/system_stats", timeout=8)
            nf.log("[boot:%s] server UP in %.0fs (pid=%d)" % (tag, time.time() - t0, p.pid))
            return True
        except Exception:
            continue
    nf.log("[boot:%s] SERVER BOOT FAIL after %ds" % (tag, wait))
    return False


def parse_newkf():
    t = open(NEWKF_PACK, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"### (SIL[1-4]_\w+|SING[1-3]_\w+)（[^\n]*）\n\n(.*?)(?=\n\n### |\n\n## )",
                        t, re.S):
        out[m.group(1)] = m.group(2).strip()
    assert len(out) == 7, "NEWKF pack parse got %d sections" % len(out)
    return out


def kf_graph_trial(prompt_text, seed, width, height):
    return {
        "10": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "15": {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": "jman_v1_rank32.safetensors", "strength_model": 0.6, "model": ["10", 0]}},
        "11": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "12": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_text, "clip": ["11", 0]}},
        "13": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["6", 0]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "3": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 8, "cfg": 1.0, "sampler_name": "euler",
                "scheduler": "simple", "denoise": 1.0, "model": ["15", 0], "positive": ["6", 0],
                "negative": ["13", 0], "latent_image": ["5", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["12", 0]}},
        "29": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "bmc_v3kf"}},
    }


def phase4_trial_batch():
    prompts = parse_newkf()
    ok = []
    seeds = (9011, 9012, 9013, 9014)
    total = 0
    for mid, prose in prompts.items():
        for sd in seeds:
            total += 1
            dst = os.path.join(BMC, "%s_s%d.png" % (mid, sd))
            if os.path.isfile(dst) and os.path.getsize(dst) > 50000:
                ok.append(dst)
                continue
            pid = nf.http_json(SERVER + "/prompt", {"prompt": kf_graph_trial(prose, sd, 672, 384),
                                                    "client_id": "bmc-v3kf-trial"})["prompt_id"]
            t0 = time.time()
            got = False
            while time.time() - t0 < 600:
                time.sleep(4)
                h = nf.http_json(SERVER + "/history/" + pid, timeout=30)
                if pid not in h:
                    continue
                for nid, out in h[pid]["outputs"].items():
                    for img in out.get("images", []):
                        data = urllib.request.urlopen("%s/view?filename=%s&subfolder=%s&type=%s" % (
                            SERVER, img["filename"], img.get("subfolder", ""), img.get("type", "output")),
                            timeout=120).read()
                        open(dst, "wb").write(data)
                        got = True
                        break
                    break
                break
            nf.log("[trial %s s%d] %s (%.0fs)" % (mid, sd, "SAVED" if got else "FAIL", time.time() - t0))
            if got:
                ok.append(dst)
    # q88 看板：4 列（种子）x 7 行（镜位）
    try:
        from PIL import Image
        ims = {}
        for p in ok:
            m = re.match(r"(SIL\d_\w+|SING\d_\w+)_s(\d+)\.png", os.path.basename(p))
            if m:
                ims.setdefault(m.group(1), {})[int(m.group(2))] = p
        tw, th = 320, 183
        board = Image.new("RGB", (4 * tw + 5 * 8, 7 * th + 8 * 16), (12, 12, 12))
        from PIL import ImageDraw
        d = ImageDraw.Draw(board)
        order = list(prompts.keys())
        for r, mid in enumerate(order):
            d.text((8, r * (th + 16) + 4), mid, fill=(220, 200, 150))
            for c, sd in enumerate(seeds):
                p = ims.get(mid, {}).get(sd)
                if p:
                    board.paste(Image.open(p).resize((tw, th)), (8 + c * (tw + 8), r * (th + 16) + 16))
        dst = os.path.join(BMC, "V3-NEWKF-TRIAL-BOARD_q88.jpg")
        q = 88
        while True:
            board.save(dst, "JPEG", quality=q)
            if os.path.getsize(dst) <= 1000000 or q <= 55:
                break
            q -= 6
        nf.log("TRIAL BOARD SAVED %s (%dKB q%d, imgs=%d/%d)" % (
            dst, os.path.getsize(dst) // 1024, q, len(ok), total))
    except Exception as e:
        nf.log("TRIAL BOARD FAIL (non-blocking): %r" % e)
    return len(ok), total


def repin_ollama():
    for tn in ("MiniGameOllamaServe", "MiniGameOllamaKeepWarm"):
        subprocess.run(["schtasks", "/change", "/tn", tn, "/enable"], capture_output=True)
    nf.log("REPIN: ollama tasks re-enabled (35b re-pin by KeepWarm schedule)")


def main():
    results = {}
    # Phase 1: boot
    if not boot_server("h3"):
        repin_ollama()
        sys.exit(2)
    # Phase 2: refire-2（H3 INT8 在首boot 即烧）
    for i, (tag, frame, prose) in enumerate(REFIRE2):
        if not (os.path.isfile(frame) and os.path.getsize(frame) > 100000):
            nf.log("[%s] FRAME MISSING %s -- skipped (disclosed)" % (tag, frame))
            results[tag] = "FRAME_MISSING"
            continue
        prompt = ALIGN + " integrated_multimodal_description: " + prose + TAIL
        out = os.path.join(OUT_DIR, tag + ".mp4")
        okflag = nf.run_i2v(frame, prompt, 9240 + i, out, tag)
        if okflag:
            furl = nf.cdn_upload(out, tag)
            results[tag] = furl or "BURNED_UPLOAD_FAIL"
        else:
            results[tag] = "BURN_FAIL"
        nf.log("REFIRE2 %s -> %s" % (tag, results[tag]))
    nf.log("REFIRE2 COMPLETE: %s" % results)
    # Phase 3: restart server (H3 -> Krea2 换模)
    if not boot_server("krea2"):
        repin_ollama()
        sys.exit(3)
    # Phase 4: trial batch
    ok_n, total = phase4_trial_batch()
    # Phase 5: repin
    repin_ollama()
    nf.log("V3 CHAIN r969 COMPLETE: refire2=%s trial=%d/%d" % (results, ok_n, total))


if __name__ == "__main__":
    main()
