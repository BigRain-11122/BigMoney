# -*- coding: utf-8 -*-
"""r768 bm-c: Wan2.2-TI2V-5B i2v segment generation (MV-0001 20s sample,
O-20261008-1715/1755-bm-c CEO order). Six segments for the chorus window
77-97s, cut points = structure.json word-window line starts (77/80/84/88/
92/95), first-frame anchor method (kf PNG defines composition identity,
prompt governs motion per R-ai-premium-craft S3), 24fps direct (no
interpolation), seeds locked (checklist item 12).

Six-module prompt structure (R-ai-premium-craft S1): camera-move phrase
first, camera motion and subject motion in separate sentences, explicit
start/end framing (hold), warm-amber monochrome + 2001 aesthetic anchor,
no Chinese-style materials (negative), negatives three modules 20-30%.

Wan params: 832x480 native 480p, ModelSamplingSD3 shift=8.0 (Wan-family
480p convention), KSampler euler/simple steps=20 cfg=5.0 (non-distilled,
negatives effective), length 4n+1 rule (73/97/49). GGUF loaders per
ComfyUI-GGUF (UnetLoaderGGUF + CLIPLoaderGGUF type=wan), CLIPVisionLoader
clip_vision_h (fetched+verified this round), Wan2.2_VAE, VHS_VideoCombine
h264-mp4 24fps.

Detached pythonw zero-window, self-logging to results/mv_work/i2v_gen.log,
resume-safe (skips segments whose output mp4 already exists)."""
import json
import os
import time
import urllib.parse
import urllib.request

API = "http://127.0.0.1:8188"
WORK = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work"
KF = os.path.join(WORK, "kf")
SEGOUT = os.path.join(WORK, "seg")
LOG = os.path.join(WORK, "i2v_gen.log")

UNET = "Wan2.2-TI2V-5B-Q4_K_M.gguf"
CLIP = "umt5-xxl-encoder-Q4_K_M.gguf"
VAE = "Wan2.2_VAE.safetensors"
CLIPVIS = "clip_vision_h.safetensors"

NEG = ("fast camera movement, whip pan, sudden cuts, zoom pulses, static "
       "frozen frame; morphing objects, warping surfaces, flickering "
       "light, stuttering motion, melting textures, extra fingers, "
       "deformed hands; oversaturated colors, fluorescent lighting, "
       "modern clothing, modern objects, text, subtitles, watermark, "
       "logo, low quality, blurry")

SEGS = [
    ("seg1_carve_77_80", "kf1_carve.png", 73, 20011005,
     "Slow dolly push-in toward the writing hand, ease-in-out, locked "
     "horizon, then hold steady on the final cuneiform stroke. The "
     "scribe's hand presses a reed stylus into wet clay, cuneiform "
     "strokes forming one by one, dust motes drifting through torch "
     "light. Torch key light from the left, warm amber monochrome, 2001 "
     "music video aesthetic, 35mm film grain, ancient Mesopotamia."),
    ("seg2_strata_80_84", "kf2_strata.png", 97, 20011006,
     "Extremely slow lateral dolly along the desert strata "
     "cross-section, ease-in-out, camera gliding sideways then settling "
     "to a hold. Sand particles drift through golden-hour light, layered "
     "sediment texture, the buried clay tablet resting in the earth. "
     "Warm amber monochrome, deep focus, 2001 music video aesthetic, "
     "35mm film grain."),
    ("seg3_unearth_84_88", "kf3_unearth.png", 97, 20011007,
     "Handheld breathing micro-sway, camera slowly tilts down from the "
     "torch flame to the clay tablet, then a very slow push-in on the "
     "revealed cuneiform signs, ending in a hold. A soft brush sweeps "
     "sand off the half-buried clay tablet, carved signs emerging, dust "
     "curling in the light shaft. Hard single key light from upper left, "
     "deep shadows, warm amber monochrome, 2001 music video aesthetic, "
     "film grain."),
    ("seg4_palms_88_92", "kf4_palms.png", 97, 20011008,
     "Very slow push-in on the two hands, ease-in-out, camera closing "
     "distance then holding still. One palm gently covers the other "
     "over the ancient clay tablet with carved cuneiform, fingers "
     "settling softly, dust motes floating. Warm torchlight from the "
     "left, macro detail, shallow depth of field, warm amber monochrome, "
     "2001 music video aesthetic, film grain."),
    ("seg5_carve_reprice_92_95", "kf1_carve.png", 73, 20011009,
     "Slow dolly pull-back from the carved cuneiform close-up to a wider "
     "view of the clay tablet, ease-in-out, then hold on the tablet in "
     "torchlight. The finished cuneiform inscription catches the light, "
     "dust motes drifting. Warm amber monochrome, 2001 music video "
     "aesthetic, 35mm film grain."),
    ("seg6_strata_reprice_95_97", "kf2_strata.png", 49, 20011010,
     "Very slow push-in on the buried clay tablet within the desert "
     "strata, ease-in-out, settling into a hold. Sand particles drift, "
     "layers of earth holding still. Warm amber monochrome, deep focus, "
     "2001 music video aesthetic, film grain."),
]


def log(msg):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))


def post_json(path, data):
    req = urllib.request.Request(
        API + path, data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def get(path):
    with urllib.request.urlopen(API + path, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def upload(png_path):
    name = os.path.basename(png_path)
    with open(png_path, "rb") as fh:
        data = fh.read()
    boundary = "r768bmcboundary"
    body = (("--%s\r\nContent-Disposition: form-data; name=\"image\"; "
             "filename=\"%s\"\r\nContent-Type: image/png\r\n\r\n"
             % (boundary, name)).encode("utf-8") + data +
            ("\r\n--%s\r\nContent-Disposition: form-data; "
             "name=\"overwrite\"\r\n\r\ntrue\r\n--%s--\r\n"
             % (boundary, boundary)).encode("utf-8"))
    req = urllib.request.Request(
        API + "/upload/image?overwrite=true", data=body,
        headers={"Content-Type":
                 "multipart/form-data; boundary=%s" % boundary})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))["name"]


def workflow(anchor, prompt, frames, seed):
    return {
        "1": {"class_type": "UnetLoaderGGUF",
              "inputs": {"unet_name": UNET}},
        "2": {"class_type": "ModelSamplingSD3",
              "inputs": {"model": ["1", 0], "shift": 8.0}},
        "3": {"class_type": "CLIPLoaderGGUF",
              "inputs": {"clip_name": CLIP, "type": "wan"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "5": {"class_type": "CLIPVisionLoader",
              "inputs": {"clip_name": CLIPVIS}},
        "6": {"class_type": "LoadImage", "inputs": {"image": anchor}},
        "7": {"class_type": "CLIPVisionEncode",
              "inputs": {"clip_vision": ["5", 0], "image": ["6", 0],
                         "crop": "none"}},
        "8": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt, "clip": ["3", 0]}},
        "9": {"class_type": "CLIPTextEncode",
              "inputs": {"text": NEG, "clip": ["3", 0]}},
        "10": {"class_type": "WanImageToVideo",
                "inputs": {"positive": ["8", 0], "negative": ["9", 0],
                           "vae": ["4", 0], "width": 832, "height": 480,
                           "length": frames, "batch_size": 1,
                           "clip_vision_output": ["7", 0],
                           "start_image": ["6", 0]}},
        "11": {"class_type": "KSampler",
                "inputs": {"seed": seed, "steps": 20, "cfg": 5.0,
                           "sampler_name": "euler", "scheduler": "simple",
                           "denoise": 1.0, "model": ["2", 0],
                           "positive": ["10", 0], "negative": ["10", 1],
                           "latent_image": ["10", 2]}},
        "12": {"class_type": "VAEDecode",
                "inputs": {"samples": ["11", 0], "vae": ["4", 0]}},
        "13": {"class_type": "VHS_VideoCombine",
                "inputs": {"frame_rate": 24, "loop_count": 0,
                           "filename_prefix": "mvseg/" + "SEGNAME",
                           "format": "video/h264-mp4",
                           "pingpong": False, "save_output": True,
                           "images": ["12", 0]}},
    }


def run_one(name, anchor_png, frames, seed, prompt):
    dest = os.path.join(SEGOUT, name + ".mp4")
    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
        log("SKIP %s (exists %d B)" % (name, os.path.getsize(dest)))
        return True
    up = upload(os.path.join(KF, anchor_png))
    log("uploaded anchor %s -> %s" % (anchor_png, up))
    wf = workflow(up, prompt, frames, seed)
    wf["13"]["inputs"]["filename_prefix"] = "mvseg/" + name
    pid = post_json("/prompt", {"prompt": wf,
                                "client_id": "r768bmc"})["prompt_id"]
    log("queued %s pid=%s frames=%d seed=%d" % (name, pid, frames, seed))
    t0 = time.time()
    while True:
        time.sleep(8)
        h = get("/history/" + pid)
        if pid not in h:
            if time.time() - t0 > 3600:
                log("TIMEOUT %s (no history after 3600s)" % name)
                return False
            continue
        st = h[pid].get("status", {})
        if st.get("completed"):
            outs = []
            for node_out in h[pid]["outputs"].values():
                for img in (node_out.get("gifs") or []) + \
                        (node_out.get("images") or []):
                    outs.append(img)
            if not outs:
                log("FAIL %s: completed but no outputs" % name)
                return False
            o = outs[0]
            q = urllib.parse.urlencode(
                {"filename": o["filename"],
                 "subfolder": o.get("subfolder", ""),
                 "type": o.get("type", "output")})
            with urllib.request.urlopen(API + "/view?" + q,
                                        timeout=300) as r:
                blob = r.read()
            with open(dest, "wb") as fh:
                fh.write(blob)
            log("OK %s -> %s (%d B, %d s wall)"
                % (name, dest, len(blob), int(time.time() - t0)))
            return True
        if st.get("status_str") == "error":
            log("FAIL %s: %s" % (name, json.dumps(st)[:400]))
            return False


def main():
    os.makedirs(SEGOUT, exist_ok=True)
    log("=== i2v gen start (6 segs, Wan2.2-TI2V-5B Q4_K_M, 832x480 "
        "24fps) ===")
    ok = True
    for name, anchor, frames, seed, prompt in SEGS:
        try:
            ok = run_one(name, anchor, frames, seed, prompt) and ok
        except Exception as exc:
            log("EXC %s: %r" % (name, exc))
            ok = False
    log("=== i2v gen done ok=%s ===" % ok)


if __name__ == "__main__":
    main()
