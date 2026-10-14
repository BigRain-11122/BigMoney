# -*- coding: utf-8 -*-
# mv_full_kf.py - 全曲 44 新镜关键帧生成（Krea2 turbo 本地 8188·串行队列·断点续跑）
# 用法: py mv_full_kf.py [--server http://127.0.0.1:8188] [--only id1,id2]
import argparse, json, os, sys, time, urllib.request, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mv_full_shots import NEW

OUT_DIR = os.path.join(HERE, "frames_full")
os.makedirs(OUT_DIR, exist_ok=True)


def graph(prompt_text, seed):
    return {
        "10": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "11": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "12": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_text, "clip": ["11", 0]}},
        "13": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["6", 0]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1344, "height": 768, "batch_size": 1}},
        "3": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 8, "cfg": 1.0, "sampler_name": "euler",
                "scheduler": "simple", "denoise": 1.0, "model": ["10", 0], "positive": ["6", 0],
                "negative": ["13", 0], "latent_image": ["5", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["12", 0]}},
        "29": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "full_kf"}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://127.0.0.1:8188")
    ap.add_argument("--only", default="")
    ap.add_argument("--seeds", default="20260001")  # 基准种子+序号偏移
    args = ap.parse_args()
    base_seed = int(args.seeds)

    def post(url, payload):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=120).read())

    def get(url):
        return json.loads(urllib.request.urlopen(url, timeout=30).read())

    # 服务器存活探测
    get(args.server + "/system_stats")

    only = set(args.only.split(",")) if args.only else None
    done, fail = [], []
    for i, row in enumerate(NEW):
        sid, t0, t1, v, k, iv = row
        if only and sid not in only:
            continue
        dst = os.path.join(OUT_DIR, sid + ".png")
        if os.path.isfile(dst) and os.path.getsize(dst) > 100000:
            done.append(sid)
            print("SKIP %s (exists)" % sid, flush=True)
            continue
        seed = base_seed + i
        pid = post(args.server + "/prompt", {"prompt": graph(k, seed), "client_id": str(uuid.uuid4())})["prompt_id"]
        t0s = time.time()
        ok = False
        while time.time() - t0s < 900:
            time.sleep(3)
            h = get(args.server + "/history/" + pid)
            if pid in h:
                for nid, out in h[pid]["outputs"].items():
                    for img in out.get("images", []):
                        data = urllib.request.urlopen(
                            "%s/view?filename=%s&subfolder=%s&type=%s" % (
                                args.server, img["filename"], img.get("subfolder", ""), img.get("type", "output")),
                            timeout=60).read()
                        open(dst, "wb").write(data)
                        ok = True
                        break
                break
        if ok:
            done.append(sid)
            print("[%d/%d] %s SAVED (%.0fs)" % (len(done), len(NEW), sid, time.time() - t0s), flush=True)
        else:
            fail.append(sid)
            print("FAIL %s (timeout)" % sid, flush=True)
    print("KF FULL DONE %d ok, %d fail: %s" % (len(done), len(fail), ",".join(fail) or "none"), flush=True)
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
