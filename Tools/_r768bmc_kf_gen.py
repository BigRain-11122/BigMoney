# -*- coding: utf-8 -*-
"""r768 bm-c: MV-0001 20s sample keyframe generation (SDXL base, local law).
Four anchor keyframes for the 77-97s chorus window per HANDOVER.md S2 +
R-craft-deep 落点A scene specs (four-scene ladder: 刻字->深埋->出土->掌心相覆).
Six-module prompt structure + three-module negatives at 20-30% token ratio
(R-ai-premium-craft S1); 禁中国风 + 暖橙一统 enforced in negative/positive.
Seed-locked for reproducibility (R-craft S3.11). Outputs to results/mv_work/kf/.
Polls ComfyUI API synchronously (each SDXL run ~20-40s on 3070 16GB)."""
import json
import os
import time
import urllib.request
import urllib.error

API = "http://127.0.0.1:8188"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\kf"
CKPT = "sd_xl_base_1.0.safetensors"

NEG = ("plastic skin, wax figure, mannequin, over-smoothed texture, airbrushed, "
       "symmetrical perfection, fluorescent lighting, flat shadows, over-exposed "
       "highlights, HDR, oversaturated colors, morphing textures, watermark, text, "
       "logo, cgi, 3d render, anime, illustration, painting, chinese ink painting, "
       "watercolor, modern clothing, blurry, low quality, deformed hands, extra "
       "fingers, cropped")

KFS = [
    ("kf1_carve", "extreme close-up, a scribe hand pressing a reed stylus into a "
     "wet clay tablet, cuneiform strokes forming, torch key light from the left, "
     "macro 100mm lens feel, razor-thin depth of field, dust motes floating in "
     "the light, warm amber monochrome, 2001 music video still, 35mm film grain, "
     "ancient Mesopotamian hands, dark background", 20011005),
    ("kf2_strata", "desert strata cross-section with a buried clay tablet, layered "
     "sediment, assyrian relief band carved in stone, golden-hour side light "
     "raking the texture, 35mm wide shot, deep focus, sand particles drifting, "
     "warm amber monochrome, 2001 music video still, film grain", 20011006),
    ("kf3_unearth", "dark chamber lit by a single torch, clay tablet half-uncovered "
     "in sand, a soft brush revealing carved cuneiform signs, hard single key "
     "light from upper left, deep shadows, 50mm medium shot, volumetric glow, "
     "warm amber monochrome, 2001 music video still, film grain", 20011007),
    ("kf4_palms", "extreme close-up of two hands, one palm gently covering the "
     "other over an ancient clay tablet with clearly carved cuneiform "
     "inscriptions, warm torchlight from the left, macro detail, shallow depth "
     "of field, dust motes, warm amber monochrome, 2001 music video still, film "
     "grain", 20011008),
]


def wf(name, prompt, neg, seed):
    return {
        "3": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": 30, "cfg": 6.5, "sampler_name": "dpmpp_2m",
            "scheduler": "karras", "denoise": 1.0,
            "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0],
            "latent_image": ["5", 0]}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {
            "width": 1024, "height": 576, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {
            "text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {
            "text": neg, "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode", "inputs": {
            "samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {
            "filename_prefix": "mvkf/" + name, "images": ["8", 0]}},
    }


def post(path, data):
    req = urllib.request.Request(API + path,
                                 data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def get(path):
    with urllib.request.urlopen(API + path, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def run_one(name, prompt, seed, log):
    pid = post("/prompt", {"prompt": wf(name, prompt, NEG, seed),
                           "client_id": "r768bmc"})["prompt_id"]
    log("queued %s pid=%s" % (name, pid))
    while True:
        time.sleep(3)
        h = get("/history/" + pid)
        if pid not in h:
            continue
        status = h[pid].get("status", {})
        if status.get("completed"):
            outs = []
            for node_out in h[pid]["outputs"].values():
                for img in node_out.get("images", []):
                    outs.append(img)
            if outs:
                img = outs[0]
                src = "%s/view?filename=%s&subfolder=%s&type=%s" % (
                    API, img["filename"], img.get("subfolder", ""),
                    img.get("type", "output"))
                dest = os.path.join(OUT, name + ".png")
                with urllib.request.urlopen(src, timeout=60) as r, \
                        open(dest, "wb") as fh:
                    fh.write(r.read())
                log("OK %s -> %s (%d B)" % (name, dest, os.path.getsize(dest)))
                return True
            log("FAIL %s: no outputs" % name)
            return False
        if status.get("status_str") == "error":
            log("FAIL %s: %s" % (name, json.dumps(status)[:300]))
            return False


def main():
    os.makedirs(OUT, exist_ok=True)
    logf = open(os.path.join(os.path.dirname(OUT), "kf_gen.log"), "a",
                encoding="utf-8")

    def log(msg):
        logf.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        logf.flush()

    log("=== kf gen start (4 anchors) ===")
    ok = True
    for name, prompt, seed in KFS:
        try:
            ok = run_one(name, prompt, seed, log) and ok
        except Exception as exc:
            log("EXC %s: %r" % (name, exc))
            ok = False
    log("=== kf gen done ok=%s ===" % ok)


if __name__ == "__main__":
    main()
