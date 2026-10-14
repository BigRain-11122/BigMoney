# -*- coding: utf-8 -*-
# bmc_xq_w1_kf_trial.py -- 星晴 W1 A批34 KF + 选角板16 试构图 runner (bm-c r1014)
# 承接链: gap7 7/7 DELIVERED (POOL-0012 done) -> wave3 星晴 A 批 34 KF + 选角板 16 (orders 10-15 01:3x ⑤)
# 规格: 星晴-KF-PACK-A-v1 + 星晴-SHOTLIST-v3 §一 + 星晴-选角案-v1 (machine-parsed, zero transcription)
# 试构图律: 672x384 x 8 steps, 1 seed/帧 -> 构图人眼抽检 -> 正档 1344x768 (whitelist 签章后)
# jman: LoraLoaderModelOnly(jman_v1_rank32, 0.6) on male-lead-figure slots (KF-PACK-A 引用律)
# Detached-safe: stdout guard + file log + checkpoint (skip existing) + progress json
import json, os, re, sys, time, urllib.request, uuid

# --- stdout guard (pythonw detached: sys.stdout is None) ---
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
SHOTLIST = os.path.join(BM, "_r1014bmc_xq_shotlist3.md")
CASTING = os.path.join(BM, "_r1014bmc_xq_casting.md")
OUT = r"K:\Fluxgroup\FluxGroup\media\mv-album-001-jay\w1_xq_kf_trial"
LOG = os.path.join(OUT, "trial_run.log")
PROGRESS = os.path.join(OUT, "v3w1_trial_r1014_progress.json")
MODELS = {
    "diffusion": (r"D:\ComfyUI\models\diffusion_models\krea2_turbo_fp8_scaled.safetensors", 13141730784),
    "textenc": (r"D:\ComfyUI\models\text_encoders\qwen3vl_4b_fp8_scaled.safetensors", 5242467968),
    "vae": (r"D:\ComfyUI\models\vae\qwen_image_vae.safetensors", 253806246),
    "jman": (r"D:\ComfyUI\models\loras\jman_v1_rank32.safetensors", 469315376),
}
ERA_WORLD = ("Taiwan countryside around Taitung-Danshui hills, 2000 era, faded single center line road, "
             "golden grass fields, small tin-and-brick farmhouse, 35mm film grain, telecine texture, "
             "2001 Taiwan music video look")
LIGHT = {"1": "warm 5200K frontal golden sunlight",
         "2": "2800K dusk backlight with golden rim halation",
         "3": "single warm 2200K tungsten lamp light",
         "4": "indigo night sky with starlight",
         "5": "slanted warm afternoon window light with dust motes"}
ID_FACE = ("20-year-old Taiwanese student with heavy-lidded monolid eyes, a thick lower lip, "
           "softly rounded cheeks, a flat round nose tip, a blunt rounded jaw, natural unretouched "
           "skin with visible pores, thick black fringe lying flat over his eyebrows")
SUFFIX = "35mm film grain, telecine texture, 2001 Taiwan music video look"
# male-lead figure slots (jman 0.6 per KF-PACK-A; 背影/剪影/手部 included for body consistency)
JMAN_SLOTS = {"F0-01a", "F0-01b", "S0-03", "S0-05", "S0-06", "S1-09", "S2-14", "S2-15", "S2-16",
              "S3-18", "S3-19", "S3-20", "S4-22", "S4-23", "S4-24", "S5-25", "S5-29", "S5-30",
              "F5-33b", "F5-33c"}
FACE_SLOTS = {"S5-30"}  # A批唯一男主侧脸镜 -> ID block + 反韩骨相锚 (anti-K v2 = ID_FACE clauses)

CIRC = {"①": "1", "②": "2", "③": "3", "④": "4", "⑤": "5"}


def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), m))


def parse_shotlist():
    txt = open(SHOTLIST, encoding="utf-8").read()
    jobs = []
    for line in txt.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 9 or cells[0] in ("镜位", "---", "※") or set(cells[0]) <= {"-", " "}:
            continue
        if cells[0].startswith("镜位") or "批" == cells[7][:1] and False:
            pass
        slot_raw, light_raw, batch, prompt = cells[0], cells[5], cells[7], cells[8]
        if batch != "A":
            continue
        # expand 三连 rows: "S2-11/12/13" -> S2-11, S2-12, S2-13
        m = re.match(r"^(S\d-\d\d)(/(\d\d))*$", slot_raw)
        ids = []
        if "/" in slot_raw:
            head, rest = slot_raw.split("/", 1)
            prefix = head.rsplit("-", 1)[0]
            ids.append(head)
            for tail in rest.split("/"):
                tail = tail.strip()
                ids.append(prefix + "-" + tail if len(tail) == 2 else prefix + tail)
        else:
            ids.append(slot_raw)
        light = ""
        for ch, d in CIRC.items():
            if ch in light_raw:
                light = LIGHT[d]
                break
        for sid in ids:
            jobs.append({"id": sid, "prompt": prompt, "light": light})
    return jobs


def parse_casting():
    txt = open(CASTING, encoding="utf-8").read()
    types = {}
    for line in txt.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4 or cells[0] in ("型", "---") or set(cells[0]) <= {"-"}:
            continue
        types[cells[0]] = cells[2]
    return types


def build_jobs():
    a_jobs = parse_shotlist()
    cast_types = parse_casting()
    # 33 KF burns = 27 singles + 2 三连 rows expanded x3 each; KF-PACK "34 帧" counts the
    # 数星 REUSE 4th frame which belongs to assembly C-batch (SHOTLIST "×4 含 REUSE" verbatim) --
    # table is 生产权威 (KF-PACK-A §二: "34 帧逐帧参数=SHOTLIST §一表正身"), disclose in receipt.
    assert len(a_jobs) == 33, "A-batch job count %d != 33 (SHOTLIST parse drift)" % len(a_jobs)
    assert len(cast_types) == 4, "casting types %d != 4" % len(cast_types)
    jobs = []
    for i, j in enumerate(a_jobs):
        p = j["prompt"]
        parts = [p]
        if j["id"] in FACE_SLOTS:
            parts.insert(0, ID_FACE)
        if j["light"]:
            parts.append(j["light"])
        parts.append(ERA_WORLD)
        jobs.append({"id": "A_%s" % j["id"], "prompt": ", ".join(dict.fromkeys(
            [x.strip() for x in parts if x.strip()])) if False else _join(parts),
            "jman": j["id"] in JMAN_SLOTS, "seed": 21100000 + i})
    scenes = [
        ("dusk", "waist-up portrait turning three-quarter toward the camera, face clearly visible, "
                 "gentle closed-mouth smile, standing in golden grass field at dusk, warm 2800K "
                 "backlight with golden rim halation on hair, 2000 Taiwan countryside"),
        ("night", "waist-up portrait, face clearly visible, soft smile, under indigo starry night "
                  "sky with faint starlight rim on shoulders, grass field at night, 2000 Taiwan countryside"),
    ]
    ti = 0
    for tname in sorted(cast_types):
        base = ("18-20 year old Taiwanese girl next door, %s, fresh bare-skin look with natural "
               "pores and texture, era-authentic 2000 Taiwan styling, %s" % (cast_types[tname], SUFFIX))
        for si in range(4):
            sc = scenes[si % 2]
            jobs.append({"id": "CAST_%s_%d" % (tname, si + 1), "prompt": "%s, %s" % (base, sc[1]),
                         "jman": False, "seed": 21101000 + ti * 4 + si})
        ti += 1
    assert len(jobs) == 49, "total jobs %d != 49 (33 A + 16 CAST)" % len(jobs)
    return jobs


def _join(parts):
    seen, out = set(), []
    for p in parts:
        p = p.strip().rstrip(",")
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return ", ".join(out)


def graph(prompt_text, seed, use_jman):
    g = {
        "10": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "11": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "12": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_text, "clip": ["11", 0]}},
        "13": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["6", 0]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 672, "height": 384, "batch_size": 1}},
    }
    model_src = ["10", 0]
    if use_jman:
        g["40"] = {"class_type": "LoraLoaderModelOnly",
                   "inputs": {"lora_model": "jman_v1_rank32.safetensors", "strength_model": 0.6, "model": ["10", 0]}}
        model_src = ["40", 0]
    g["3"] = {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 8, "cfg": 1.0,
              "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
              "model": model_src, "positive": ["6", 0], "negative": ["13", 0], "latent_image": ["5", 0]}}
    g["8"] = {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["12", 0]}}
    g["29"] = {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "xq_w1_trial"}}
    return g


def main():
    os.makedirs(OUT, exist_ok=True)
    log("runner start (wave3 XQ W1 A34 + CAST16 trial, 672x384)")
    # 1) wait for weights (self-sequencing behind the r1014 ModelScope download)
    t0 = time.time()
    while time.time() - t0 < 90 * 60:
        missing = []
        for k, (p, sz) in MODELS.items():
            if k == "jman" and not os.path.isfile(p):
                missing.append(k)  # jman required for 20 slots -> hard gate too
                continue
            if not os.path.isfile(p) or os.path.getsize(p) != sz:
                missing.append(k)
        if not missing:
            break
        log("waiting for models: %s" % ",".join(sorted(set(missing))))
        time.sleep(60)
    else:
        log("MODEL-WAIT TIMEOUT 90min; abort (checkpoint safe, rerun resumes)")
        sys.exit(2)
    log("models present: all 4 (size-verified)")
    server = "http://127.0.0.1:8188"

    def post(url, payload):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=180).read())

    def get(url):
        return json.loads(urllib.request.urlopen(url, timeout=60).read())

    for _ in range(30):
        try:
            get(server + "/system_stats")
            break
        except Exception:
            log("comfyui not reachable, retry 10s")
            time.sleep(10)
    else:
        log("COMFYUI UNREACHABLE; abort")
        sys.exit(2)

    jobs = build_jobs()
    prog = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "total": len(jobs), "done": [], "fail": [],
            "spec": {"shotlist": "星晴-SHOTLIST-v3 (origin main)", "casting": "星晴-选角案-v1 (origin main)",
                     "kfpack": "星晴-KF-PACK-A-v1", "trial": "672x384x8steps 1seed/frame",
                     "jman_slots": sorted(JMAN_SLOTS), "face_slots": sorted(FACE_SLOTS)}}
    if os.path.isfile(PROGRESS):
        try:
            prog["done"] = json.load(open(PROGRESS, encoding="utf-8")).get("done", [])
        except Exception:
            pass
    for j in jobs:
        dst = os.path.join(OUT, "%s_t%s.png" % (j["id"], j["seed"]))
        if j["id"] in prog["done"] and os.path.isfile(dst) and os.path.getsize(dst) > 30000:
            continue
        try:
            pid = post(server + "/prompt", {"prompt": graph(j["prompt"], j["seed"], j["jman"]),
                                            "client_id": str(uuid.uuid4())})["prompt_id"]
            t_s = time.time()
            ok = False
            while time.time() - t_s < 600:
                time.sleep(3)
                h = get(server + "/history/" + pid)
                if pid in h:
                    for nid, out in h[pid]["outputs"].items():
                        for img in out.get("images", []):
                            data = urllib.request.urlopen("%s/view?filename=%s&subfolder=%s&type=%s" % (
                                server, img["filename"], img.get("subfolder", ""), img.get("type", "output")),
                                timeout=120).read()
                            open(dst, "wb").write(data)
                            ok = True
                            break
                    if ok or True:
                        break
            if ok:
                if j["id"] not in prog["done"]:
                    prog["done"].append(j["id"])
                log("SAVED %s (%.0fs)" % (j["id"], time.time() - t_s))
            else:
                prog["fail"].append(j["id"])
                log("FAIL %s (timeout)" % j["id"])
        except Exception as e:
            prog["fail"].append(j["id"])
            log("ERROR %s: %r" % (j["id"], e))
        prog["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
        tmp = PROGRESS + ".tmp"
        open(tmp, "w", encoding="utf-8").write(json.dumps(prog, ensure_ascii=False, indent=1))
        os.replace(tmp, PROGRESS)
    log("TRIAL DONE ok=%d fail=%d %s" % (len(prog["done"]), len(prog["fail"]), ",".join(prog["fail"]) or "none"))
    sys.exit(1 if prog["fail"] else 0)


if __name__ == "__main__":
    main()
