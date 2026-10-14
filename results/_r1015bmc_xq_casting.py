# -*- coding: utf-8 -*-
# bmc_xq_casting_r1015.py -- wave3 星晴女主选角板（星晴-选角案-v1 执行件·定脸前置）
# Spec: 星晴-选角案-v1（4 型×4 种子=16 张 672x384 构图板·黄昏逆光金边+夜场两种光位各一/型）
# 流程律（选角案 §流程）: 试构图律先行 672x384 -> 人眼过构图 -> 选 2 型升正档 1344x768 x3 种子
#   -> 导演席拍板 -> 十席帧审 -> 定脸锁 ID 块（本 runner=第一段·构图板）
# 反向测试=原创脸门（试构图段=4 型代表帧抽测·定脸锁时全 16 张全测·receipt 如实注记）
# 独立选角律: 不承任何他曲脸型（不承徐若瑄型/不承 mv0001 外国女主/不承可爱女人甜美挂）
# jman LoRA: 不挂（女主脸零男主污染·workflow 走 UNETLoader 直连 KSampler）
# Gate: 等 A 批试构图 runner 收口（receipt 文件出现）再接续烧（FIFO 共服零抢道）
import json, os, sys, time

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("xq_trial_mod", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r1015bmc_xq_trial.py"))
_xq = _ilu.module_from_spec(_spec)
sys.modules["xq_trial_mod"] = _xq
# 只借 http_json/server_up/boot 门面；模块级 main 不跑（__main__ guard 在位）

LOGDIR = r"K:\Fluxgroup\archive\mv-album-001-jay\xq-casting-trial"
FRAMES = os.path.join(LOGDIR, "frames")
BOARD = os.path.join(LOGDIR, "XQ-CASTING-TRIAL-BOARD_q88.jpg")
LOG = os.path.join(LOGDIR, "runner_r1015.log")
RECEIPT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1015bmc_xq_casting_receipt.json"
A_BATCH_RECEIPT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1015bmc_xq_trial_receipt.json"
SERVER = "http://127.0.0.1:8188"

TYPES = {
    "A": ("元气马尾", "high dark ponytail, bright crescent-smile eyes, soft rounded cheeks, "
                      "even white teeth, sun-warmed clear skin with a few freckles across the nose"),
    "B": ("温软长发", "long straight dark hair with a soft air fringe, gentle rounded brows, "
                      "quiet smiling eyes, small clean face"),
    "C": ("清爽短发", "chin-length dark bob, bright boyish grin, small expressive face, lively brows"),
    "D": ("素净辫发", "low twin braids, clear bare face, neat simple features, bright honest gaze"),
}
LIGHTS = {
    0: ("dusk golden grass field with burnt-orange backlight, a strong golden rim on her hair, "
        "warm halation, 2000 Taiwan countryside", "黄昏逆光金边"),
    1: ("dusk golden grass field with burnt-orange backlight, a strong golden rim on her hair, "
        "warm halation, 2000 Taiwan countryside", "黄昏逆光金边"),
    2: ("deep indigo night grass field lit by soft starlight, faint star glow rim, "
        "2000 Taiwan countryside", "夜场星光"),
    3: ("deep indigo night grass field lit by soft starlight, faint star glow rim, "
        "2000 Taiwan countryside", "夜场星光"),
}


def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), m))


def http_json(url, payload=None, timeout=30):
    import urllib.request
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


def cast_graph(prompt_text, seed, width, height):
    return {
        "10": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "11": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "12": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_text, "clip": ["11", 0]}},
        "13": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["6", 0]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "3": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 8, "cfg": 1.0, "sampler_name": "euler",
               "scheduler": "simple", "denoise": 1.0, "model": ["10", 0], "positive": ["6", 0],
               "negative": ["13", 0], "latent_image": ["5", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["12", 0]}},
        "29": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "bmc_xq_cast"}},
    }


def burn_one(prompt, seed, dst):
    import urllib.request
    if os.path.isfile(dst) and os.path.getsize(dst) > 50000:
        return "SAVED-RESUME"
    pid = http_json(SERVER + "/prompt", {"prompt": cast_graph(prompt, seed, 672, 384),
                                         "client_id": "bmc-xq-cast-r1015"})["prompt_id"]
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


def main():
    os.makedirs(FRAMES, exist_ok=True)
    log("=== XQ casting trial start (r1015) -- waiting for A-batch gate ===")
    t0 = time.time()
    while not os.path.isfile(A_BATCH_RECEIPT):
        if time.time() - t0 > 3600:
            log("FATAL: A-batch gate timeout 60min -- abort (disclosed)")
            sys.exit(2)
        time.sleep(20)
    try:
        ab = json.load(open(A_BATCH_RECEIPT, encoding="utf-8"))
        log("gate open: A-batch verdict=%s (%s ok)" % (ab.get("verdict"), ab.get("count_ok")))
    except Exception as e:
        log("gate receipt unreadable %r -- proceeding (A runner finished)" % e)
    if not server_up():
        log("server down at gate -- reboot via A-module boot")
        if not _xq.boot_server("krea2-cast"):
            log("FATAL: server reboot fail")
            sys.exit(3)
    receipt = {"round": "r1015", "spec": "星晴-选角案-v1（4型x4种子 672x384 构图板·两光位）",
               "engine": "Krea2 turbo fp8 t2i, NO jman LoRA (female-face zero-male-pollution per independent casting law)",
               "seed_base": 9401, "frames": [], "reverse_test_note":
               "trial-phase reverse test = 4 type representatives at harvest; full-16 reverse test = 定脸锁 stage per spec",
               "independent_casting_law": "本曲脸不承任何他曲（徐若瑄型/mv0001 外国女主/可爱女人甜美挂全不承）"}
    ok = {}
    i = 0
    for t, (cn, idb) in TYPES.items():
        for s in range(4):
            seed = 9401 + i
            scene, light_name = LIGHTS[s]
            prompt = ("A young Taiwanese woman around nineteen with %s, half-body portrait facing the camera with a "
                      "warm natural smile, fresh clean bare-face look, natural healthy skin with fine living grain, "
                      "hair in its natural state, plain 2000-era summer clothes. Setting: %s. "
                      "Style: 35mm film grain, telecine texture, 2001 Taiwan music video look.") % (idb, scene)
            dst = os.path.join(FRAMES, "XQ-CAST-%s_s%d.png" % (t, seed))
            st = burn_one(prompt, seed, dst)
            log("[cast %s s%d %s] %s" % (t, seed, light_name, st))
            if st.startswith("SAVED"):
                ok["%s_%d" % (t, seed)] = dst
            receipt["frames"].append({"type": t, "name_cn": cn, "seed": seed, "light": light_name,
                                      "status": st, "words": len(prompt.split()), "prompt": prompt})
            i += 1
    try:
        from PIL import Image, ImageDraw
        tw, th, cols = 320, 183, 4
        board = Image.new("RGB", (cols * (tw + 8) + 8, 4 * (th + 30) + 8), (12, 12, 12))
        d = ImageDraw.Draw(board)
        order = [(t, s) for t in TYPES for s in range(4)]
        for idx, (t, s) in enumerate(order):
            r, c = divmod(idx, cols)
            x, y = 8 + c * (tw + 8), 8 + r * (th + 30)
            seed = 9401 + idx
            d.text((x, y + 2), "%s %s s%d" % (t, LIGHTS[s][1], seed), fill=(220, 200, 150))
            p = ok.get("%s_%d" % (t, seed))
            if p:
                board.paste(Image.open(p).resize((tw, th)), (x, y + 16))
        q = 88
        while True:
            board.save(BOARD, "JPEG", quality=q)
            if os.path.getsize(BOARD) <= 1000000 or q <= 55:
                break
            q -= 6
        log("CAST BOARD SAVED %s (%dKB q%d, imgs=%d)" % (BOARD, os.path.getsize(BOARD) // 1024, q, len(ok)))
    except Exception as e:
        log("BOARD FAIL (non-blocking): %r" % e)
    receipt["count_ok"] = len(ok)
    receipt["count_total"] = 16
    receipt["board"] = BOARD if os.path.isfile(BOARD) else None
    receipt["verdict"] = "COMPLETE" if len(ok) == 16 else "PARTIAL %d/16" % len(ok)
    receipt["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    log("=== XQ casting trial done: %s ===" % receipt["verdict"])


if __name__ == "__main__":
    main()
