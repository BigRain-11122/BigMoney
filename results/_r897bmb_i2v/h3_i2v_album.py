# -*- coding: utf-8 -*-
# h3_i2v_album.py - 《Jay》专辑 53(+12) 单 i2v 本地机队批客户端
# CEO 令 2026-10-11 晚：「视频还是本地弄吧，我的机队全部加入」——云端积分批作废，本地 int8/int4 生产。
# 用法: python h3_i2v_album.py --repo <FluxGroup仓库根> --lane bmc|bma|bmb
#       [--server http://127.0.0.1:8188] [--only ID1,ID2] [--width W] [--height H] [--wf wf.json]
#       [--manifest <repo相对manifest路径>] [--timeout 4200]
# 硬律: 纯画面无音轨（工作流已剥 audio 链·CEO 音轨禁令）·FIFO 共服不动他窗队列项·SKIP 断点续跑·种子确定性（id-MD5）
import argparse, hashlib, io, json, math, os, sys, time, urllib.request, uuid

if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PKG = os.path.join("cph4", "fleet", "mv-album-001-jay", "local-i2v")


def http_json(url, payload=None, timeout=30):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def upload_image(server, path):
    fn = os.path.basename(path)
    data = open(path, "rb").read()
    boundary = "----i2va" + uuid.uuid4().hex
    body = (("--%s\r\nContent-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\n"
             "Content-Type: image/png\r\n\r\n") % (boundary, fn)).encode() + data + \
           ("\r\n--%s--\r\n" % boundary).encode()
    req = urllib.request.Request(server + "/upload/image?overwrite=true", data=body,
                                 headers={"Content-Type": "multipart/form-data; boundary=" + boundary})
    return json.loads(urllib.request.urlopen(req, timeout=180).read()).get("name", fn)


def snap_length(src_s, fps=24.0):
    # H3 length 合法网格 = 17k+5（124≈5s 实证）
    frames = int(round(float(src_s) * fps))
    k = max(0, math.ceil((frames - 5) / 17.0))
    return 17 * k + 5


def seed_for(oid):
    return int.from_bytes(hashlib.md5(oid.encode("utf-8")).digest()[:4], "big") % 999983


def resolve_option(server, node, key, musts):
    spec = http_json(server + "/object_info/" + node)[node]["input"]["required"][key]
    opts = spec[0] if spec and isinstance(spec[0], list) else []
    for o in opts:
        ol = str(o).lower()
        if all(m.lower() in ol for m in musts):
            return o
    raise SystemExit("RESOLVE FAIL %s.%s musts=%s options=%d" % (node, key, musts, len(opts)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--lane", required=True, help="bmc|bma|bmb")
    ap.add_argument("--server", default="http://127.0.0.1:8188")
    ap.add_argument("--only", default="", help="逗号分隔 id 子集（回收/插队用·优先于 lane 过滤）")
    ap.add_argument("--width", type=int, default=0)
    ap.add_argument("--height", type=int, default=0)
    ap.add_argument("--wf", default="", help="工作流覆盖（repo 相对 PKG 路径或绝对路径）")
    ap.add_argument("--manifest", default="", help="manifest 覆盖（repo 相对路径）")
    ap.add_argument("--timeout", type=int, default=4200)
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    server = args.server
    assignment = json.load(open(os.path.join(repo, PKG, "assignment-album-v1.json"), encoding="utf-8"))
    lane = assignment["lanes"][args.lane]

    man_rel = args.manifest or lane.get("manifest") or "cph4/fleet/mv-album-001-jay/i2v-wave-manifest.json"
    man = json.load(open(os.path.join(repo, man_rel), encoding="utf-8"))
    units = man["units"] if isinstance(man, dict) and "units" in man else man

    only = set(x.strip() for x in args.only.split(",") if x.strip())
    if only:
        sel = [u for u in units if u["id"] in only]
    elif "manifest" in lane and not args.manifest:
        sel = list(units)  # lane 自带预备好的清单（bmc：XQ+V2_KFL）
    elif lane.get("all"):
        sel = list(units)
    elif lane.get("track"):
        sel = [u for u in units if u.get("track") == lane["track"]]
    else:
        sel = list(units)

    w = args.width or int(lane["width"])
    h = args.height or int(lane["height"])
    quant = lane.get("quant", "int8")
    wf_path = args.wf if args.wf else os.path.join(repo, PKG, lane["wf"])
    if not os.path.isabs(wf_path) and not os.path.isfile(wf_path):
        wf_path = os.path.join(repo, PKG, args.wf)

    out_dir = os.path.join(repo, lane["out"])
    os.makedirs(out_dir, exist_ok=True)
    prog = os.path.join(out_dir, "progress-%s.jsonl" % args.lane)

    def logp(d):
        d["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
        open(prog, "a", encoding="utf-8").write(json.dumps(d, ensure_ascii=False) + "\n")

    wf = json.load(open(wf_path, encoding="utf-8"))
    # 模型名模糊解析（各机文件名可能不同·按 int8/int4+turbo+nvfp4+video_vAE 匹配）
    wf["1"]["inputs"]["unet_name"] = resolve_option(server, "UNETLoader", "unet_name",
                                                    ["int8", "convrot"] if quant == "int8" else ["int4", "convrot"])
    wf["2"]["inputs"]["lora_name"] = resolve_option(server, "LoraLoaderModelOnly", "lora_name", ["turbo", "4step"])
    wf["3"]["inputs"]["clip_name"] = resolve_option(server, "CLIPLoader", "clip_name", ["nvfp4"])
    wf["4"]["inputs"]["vae_name"] = resolve_option(server, "VAELoader", "vae_name", ["video", "fp16"])
    print("LANE=%s orders=%d res=%dx%d quant=%s wf=%s" % (args.lane, len(sel), w, h, quant, wf_path), flush=True)
    print("UNET=%s LORA=%s CLIP=%s VAE=%s" % (wf["1"]["inputs"]["unet_name"],
          wf["2"]["inputs"]["lora_name"], wf["3"]["inputs"]["clip_name"], wf["4"]["inputs"]["vae_name"]), flush=True)

    try:
        http_json(server + "/free", {"unload_models": True}, timeout=90)
    except Exception:
        pass

    fails, ok = [], 0
    submit_fail = 0
    for u in sel:
        oid = u["id"]
        clip = os.path.join(out_dir, oid + ".mp4")
        if os.path.isfile(clip) and os.path.getsize(clip) > 100000:
            print("[%s] SKIP (exists %dKB)" % (oid, os.path.getsize(clip) // 1024), flush=True)
            continue
        fp = str(u["frame"])
        i = fp.find("media")
        frame = os.path.join(repo, fp[i:]) if i >= 0 else fp
        if not os.path.isfile(frame):
            print("[%s] MISSING FRAME %s" % (oid, frame), flush=True)
            fails.append(oid)
            logp({"id": oid, "status": "missing_frame", "frame": frame})
            continue
        seed = seed_for(oid)
        length = snap_length(u.get("src_s", 5.0))
        try:
            img = upload_image(server, frame)
        except Exception as e:
            print("[%s] UPLOAD FAIL %s" % (oid, e), flush=True)
            fails.append(oid)
            submit_fail += 1
            if submit_fail >= 5:
                print("ABORT: 5 consecutive submit failures (ComfyUI down?)", flush=True)
                break
            continue
        wf["16"]["inputs"]["image"] = img
        n6 = wf["6"]["inputs"]
        n6["prompt"] = u["i2v_prompt"]
        n6["length"] = length
        n6["width"] = int(u.get("width", 0)) or w   # 单内分辨率 override（V2_KFL 竖版 768x1344）
        n6["height"] = int(u.get("height", 0)) or h
        wf["10"]["inputs"]["noise_seed"] = seed
        try:
            resp = http_json(server + "/prompt", {"prompt": wf, "client_id": "album-" + args.lane}, timeout=60)
        except Exception as e:
            print("[%s] SUBMIT FAIL %s" % (oid, e), flush=True)
            fails.append(oid)
            submit_fail += 1
            if submit_fail >= 5:
                print("ABORT: 5 consecutive submit failures", flush=True)
                break
            continue
        if resp.get("node_errors"):
            print("NODE ERRORS (batch abort, config problem): %s" % json.dumps(resp["node_errors"])[:1200], flush=True)
            logp({"id": oid, "status": "node_errors", "errors": resp["node_errors"]})
            sys.exit(2)
        submit_fail = 0
        pid = resp["prompt_id"]
        t0 = time.time()
        err_streak = 0
        saved = False
        print("[%s] SUBMITTED frame=%s len=%d seed=%d (%.1fs src)" % (oid, img, length, seed, float(u.get("src_s", 5))), flush=True)
        while time.time() - t0 < args.timeout:
            time.sleep(15)
            try:
                hist = http_json(server + "/history/" + pid, timeout=20)
            except Exception:
                err_streak += 1
                if err_streak >= 40:
                    print("[%s] POLL LOST (server unreachable 10min)" % oid, flush=True)
                    break
                continue
            err_streak = 0
            e = hist.get(pid)
            if e is None:
                if int(time.time() - t0) % 60 < 16:
                    print("[%s] %4ds running..." % (oid, time.time() - t0), flush=True)
                continue
            if e.get("status", {}).get("status_str") == "error":
                print("[%s] ERROR %s" % (oid, json.dumps(e["status"].get("messages", []))[:400]), flush=True)
                break
            for nid, out in e.get("outputs", {}).items():
                vids = out.get("gifs", []) or out.get("videos", []) or out.get("images", [])
                for v in vids:
                    url = "%s/view?filename=%s&subfolder=%s&type=%s" % (
                        server, v["filename"], v.get("subfolder", ""), v.get("type", "output"))
                    data = urllib.request.urlopen(url, timeout=600).read()
                    if len(data) < 50000:
                        print("[%s] OUTPUT TOO SMALL %dKB (reject)" % (oid, len(data) // 1024), flush=True)
                        break
                    open(clip, "wb").write(data)
                    secs = time.time() - t0
                    print("[%s] SAVED %s (%.0fs, %dKB)" % (oid, clip, secs, len(data) // 1024), flush=True)
                    logp({"id": oid, "status": "ok", "secs": round(secs, 1), "length": length,
                          "seed": seed, "kb": len(data) // 1024})
                    ok += 1
                    saved = True
                    break
                if saved:
                    break
            if saved or e.get("status", {}).get("completed"):
                if not saved:
                    print("[%s] finished but no video output" % oid, flush=True)
                    logp({"id": oid, "status": "no_output"})
                break
        if not saved:
            fails.append(oid)
            logp({"id": oid, "status": "timeout_or_fail"})
    open(os.path.join(out_dir, "fails-%s.txt" % args.lane), "w").write("\n".join(fails))
    print("ALBUM LANE DONE lane=%s ok=%d fail=%d(%s) out=%s" % (
        args.lane, ok, len(fails), ",".join(fails) or "none", out_dir), flush=True)


if __name__ == "__main__":
    main()
