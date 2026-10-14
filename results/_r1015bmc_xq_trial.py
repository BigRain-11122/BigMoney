# -*- coding: utf-8 -*-
# bmc_xq_trial_r1015.py -- wave3 星晴 A 批试构图（DEADLINE 台账「排队 bm-c：...波3 星晴 A 批 34 KF+选角板 16」第三波队头消费）
# Spec chain (all machine-read from origin blobs, zero transcription):
#   - 星晴-KF-PACK-A-v1.md   = 组装层（共享块/试构图律/验收判据）
#   - 星晴-SHOTLIST-v3.md §一表 = 每帧 KF 正向锚要点正身（英文）+ 光位 + 批
#   - ID 块 = FRAME-GATE-WHITELIST/NEWKF SIL1 verbatim（a young Taiwanese man around twenty...）
# Trial law（KF-PACK §二）: 672x384 · 每镜 1 种子先行 · 8 步 · cfg1 euler simple · ConditioningZeroOut
#   -> 构图人眼抽检（漂移截杀）后升正档 1344x768（正档=另窗·候导演席构图对审）
# 组装策略（KF-PACK §一 + NEWKF 块标先例）: [KF 句] + [ID 句·男主可辨镜] + Setting 世界块 + Lighting 色族词 + Style 官方收尾
# 硬点披露:
#   - 行级试构图：S2-11/12/13 与 S5-26/27/28 两三连行各烧 1 行（变体=装配站 REUSE·C 批法）
#   - 反韩骨相锚 v2（正/侧脸近景必挂）= S5-30 唯一侧脸近景（正身短语自 10-12 KF1v2 判例族正向化）
#   - lint 两处语义保真改写（零否定律）: S4-22 "no camera-facing face"->"his face kept turned away from the camera"
#     S2-15 "without touching"->"a small air gap kept between hand and seat"（语义=留白虚扶·不变）
#   - 35B repin 已省略（O-20261014 CEO 令：bm-c GPU=生成视觉-only·35B 已迁 bm-a）
#   - B 批 12 帧（女主脸依赖镜）不烧=候定脸拍板（点火序法）
import json, os, re, subprocess, sys, time, urllib.request

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
LOGDIR = r"K:\Fluxgroup\archive\mv-album-001-jay\xq-kf-a-trial"
FRAMES = os.path.join(LOGDIR, "frames")
LOG = os.path.join(LOGDIR, "runner_r1015.log")
PROGRESS = os.path.join(LOGDIR, "progress.jsonl")
BOARD = os.path.join(LOGDIR, "XQ-A-TRIAL-BOARD_q88.jpg")
RECEIPT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1015bmc_xq_trial_receipt.json"
SHOTLIST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1015bmc_xq_shotlist_v3.md"
SERVER = "http://127.0.0.1:8188"
COMFY_EXE = r"D:\ComfyUI\python_embeded\python.exe"
COMFY_CWD = r"D:\ComfyUI"

ID_SENT = ("He is a young Taiwanese man around twenty with a soft rounded face, small level eyes, "
           "heavy straight brows, full lips and a thick blunt fringe, dressed in plain 2000-era Taiwan casual clothes.")
ANTI_K_V2 = ("softly puffy single-lid monolid eyes, wide square-rounded jawline, calm quiet expression, "
             "thick blunt fringe fully covering the eyebrows, natural unpolished skin with living warmth")
WORLD = ("Taiwan countryside around Taitung-Danshui hills, 2000 era, faded single center line road, "
         "golden grass fields, small tin-and-brick farmhouse.")
LIGHT = {
    "\u2460": "high-noon gold sunlight flooding the scene",
    "\u2461": "burnt-orange dusk backlight with a strong halation rim",
    "\u2462": "a single warm 2200K lamp as the only light",
    "\u2463": "deep indigo night lit by starlight",
    "\u2464": "slanted warm afternoon window light",
}
ENDING = "35mm film grain, telecine texture, 2001 Taiwan music video look."
ID_FRAMES = {"S0-03", "S1-09", "S2-14", "S2-16", "S3-18", "S3-20", "S4-22", "S5-25", "S5-29", "S5-30"}
LINT_FIXES = [
    (", no camera-facing face", ", his face kept turned away from the camera"),
    ("without touching", "with a small air gap kept between hand and seat"),
]
NEG_RE = re.compile(r"\b(no|not|never|without|avoid|forbidden)\b", re.I)
VAGUE_RE = re.compile(r"\b(very|really|extremely|beautiful|gorgeous|stunning|amazing|masterpiece|best quality)\b", re.I)
CONCEPT_RE = re.compile(r"\b(korean|k-pop|kpop|makeup|watermark)\b", re.I)


def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), m))
    with open(PROGRESS, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "ev": str(m)[:300]}, ensure_ascii=False) + "\n")


def parse_rows():
    rows = []
    for line in open(SHOTLIST, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 9 or c[0] in ("镜位", "---", "※") or set(c[0]) <= {"-", " ", ":"}:
            continue
        if c[7] != "A":
            continue
        fid = c[0].replace("/", "-")
        light = next((LIGHT[ch] for ch in c[5] if ch in LIGHT), LIGHT["\u2460"])
        rows.append({"id": fid, "scene": c[1], "content": c[2], "light_code": c[5],
                     "kf": c[8], "light": light})
    return rows


def assemble(row):
    kf = row["kf"]
    fixes = []
    for a, b in LINT_FIXES:
        if a in kf:
            kf = kf.replace(a, b)
            fixes.append({"frame": row["id"], "from": a, "to": b})
    parts = [kf.rstrip(".")]
    if row["id"] in ID_FRAMES:
        id_s = ID_SENT
        if row["id"] == "S5-30":
            id_s = id_s[:-1] + ", " + ANTI_K_V2 + "."
        parts.append(id_s.rstrip("."))
    parts.append("Setting: " + WORLD.rstrip("."))
    parts.append("Lighting: " + row["light"])
    parts.append("Style: " + ENDING.rstrip("."))
    prompt = ". ".join(parts) + "."
    return prompt, fixes


def lint(prompt):
    return (NEG_RE.search(prompt) is not None,
            VAGUE_RE.search(prompt) is not None,
            CONCEPT_RE.search(prompt) is not None)


def http_json(url, payload=None, timeout=30):
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    with urllib.request.urlopen(req, data, timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def server_up():
    try:
        http_json(SERVER + "/system_stats", timeout=8)
        return True
    except Exception:
        return False


def boot_server(tag, wait=300):
    try:
        out = subprocess.check_output(["wmic", "process", "where",
                                       "commandline like '%ComfyUI\\\\main.py%' get processid"],
                                      ).decode("utf-8", "replace")
        for line in out.splitlines():
            if line.strip().isdigit():
                subprocess.run(["taskkill", "/F", "/PID", line.strip()], capture_output=True)
    except Exception:
        pass
    lg = open(os.path.join(LOGDIR, "comfy_%s.out.log" % tag), "ab")
    er = open(os.path.join(LOGDIR, "comfy_%s.err.log" % tag), "ab")
    subprocess.Popen([COMFY_EXE, "-s", "ComfyUI\\main.py", "--windows-standalone-build"],
                     cwd=COMFY_CWD, stdout=lg, stderr=er, creationflags=0x08000000)
    t0 = time.time()
    while time.time() - t0 < wait:
        time.sleep(5)
        if server_up():
            log("[boot:%s] server UP in %.0fs" % (tag, time.time() - t0))
            return True
    log("[boot:%s] SERVER BOOT FAIL after %ds" % (tag, wait))
    return False


def kf_graph(prompt_text, seed, width, height):
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
        "29": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "bmc_xq_trial"}},
    }


def burn_one(row, prompt, seed, dst):
    if os.path.isfile(dst) and os.path.getsize(dst) > 50000:
        return "SAVED-RESUME"
    pid = http_json(SERVER + "/prompt", {"prompt": kf_graph(prompt, seed, 672, 384),
                                         "client_id": "bmc-xq-trial-r1015"})["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < 600:
        time.sleep(4)
        try:
            h = http_json(SERVER + "/history/" + pid, timeout=30)
        except Exception:
            continue
        if pid not in h:
            continue
        for nid, out in h[pid]["outputs"].items():
            for img in out.get("images", []):
                data = urllib.request.urlopen("%s/view?filename=%s&subfolder=%s&type=%s" % (
                    SERVER, img["filename"], img.get("subfolder", ""), img.get("type", "output")),
                    timeout=120).read()
                open(dst, "wb").write(data)
                return "SAVED"
        return "HISTORY-EMPTY"
    return "TIMEOUT"


def build_board(frames_ok, order):
    try:
        from PIL import Image, ImageDraw
        tw, th, cols = 320, 183, 6
        rows_n = (len(order) + cols - 1) // cols
        board = Image.new("RGB", (cols * (tw + 8) + 8, rows_n * (th + 26) + 8), (12, 12, 12))
        d = ImageDraw.Draw(board)
        for i, fid in enumerate(order):
            r, c = divmod(i, cols)
            x, y = 8 + c * (tw + 8), 8 + r * (th + 26)
            d.text((x, y + 2), fid, fill=(220, 200, 150))
            p = frames_ok.get(fid)
            if p:
                board.paste(Image.open(p).resize((tw, th)), (x, y + 14))
        q = 88
        while True:
            board.save(BOARD, "JPEG", quality=q)
            if os.path.getsize(BOARD) <= 1000000 or q <= 55:
                break
            q -= 6
        log("BOARD SAVED %s (%dKB q%d, imgs=%d)" % (BOARD, os.path.getsize(BOARD) // 1024, q, len(frames_ok)))
    except Exception as e:
        log("BOARD FAIL (non-blocking): %r" % e)


def main():
    os.makedirs(FRAMES, exist_ok=True)
    log("=== XQ A-batch trial start (r1015) ===")
    if not server_up() and not boot_server("krea2"):
        log("FATAL: server boot failed")
        sys.exit(2)
    rows = parse_rows()
    log("parsed A-rows=%d (row-level trial; triptych rows burn once per row)" % len(rows))
    receipt = {"round": "r1015", "engine": "Krea2 turbo fp8 + jman_v1_rank32 @0.6, 672x384, 8 steps, cfg1 euler/simple, neg=ConditioningZeroOut",
               "trial_law": "KF-PACK-A v1 section-2: 672x384 x 1 seed/frame -> composition sampling -> fullres 1344x768 after signoff",
               "seed_base": 9301, "frames": [], "lint_fixes": [], "consistency_hardpoints": [
                   "S0-03 vs F0-01b cassette/PLAY same composition slot (26-year echo)",
                   "F5-33a/b/c vs S4-24 same cassette wear",
                   "S3-20 vs S5-29 back-to-back same setup different daylight"],
               "disclosures": ["35B repin omitted per O-20261014 (bm-c GPU=generation-visual only)",
                               "triptych rows S2-11/12/13 + S5-26/27/28 burned once per row (variants=assembly REUSE per C-batch law)",
                               "B-batch 12 frames not burned (await casting decision per ignition order)"]}
    frames_ok = {}
    lint_fail = 0
    for i, row in enumerate(rows):
        prompt, fixes = assemble(row)
        receipt["lint_fixes"].extend(fixes)
        n, v, c = lint(prompt)
        if n or v or c:
            log("[LINT-FAIL %s] neg=%s vague=%s concept=%s -- frame ABORTED" % (row["id"], n, v, c))
            receipt["frames"].append({"id": row["id"], "seed": 9301 + i, "status": "LINT_FAIL", "prompt": prompt})
            lint_fail += 1
            continue
        dst = os.path.join(FRAMES, "%s_s%d.png" % (row["id"], 9301 + i))
        st = burn_one(row, prompt, 9301 + i, dst)
        log("[trial %s s%d] %s (%d words)" % (row["id"], 9301 + i, st, len(prompt.split())))
        if st.startswith("SAVED"):
            frames_ok[row["id"]] = dst
        receipt["frames"].append({"id": row["id"], "seed": 9301 + i, "status": st,
                                  "words": len(prompt.split()), "prompt": prompt})
    build_board(frames_ok, [r["id"] for r in rows])
    receipt["count_ok"] = len(frames_ok)
    receipt["count_total"] = len(rows)
    receipt["lint_fail"] = lint_fail
    receipt["board"] = BOARD if os.path.isfile(BOARD) else None
    receipt["verdict"] = "COMPLETE" if len(frames_ok) == len(rows) else ("PARTIAL %d/%d" % (len(frames_ok), len(rows)))
    receipt["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    log("=== XQ A-batch trial done: %s ===" % receipt["verdict"])


if __name__ == "__main__":
    main()
