#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r818 bm-c H3 768P T2V test launcher (O-20261009-1746 bm-c lane; 1-gen
adaptation of cph4 canon h3_t2v_client.py, bm-a proven pattern):
- workflow = canon h3_t2v_local_768p_bmc.json (1344x768, 124f ~=5s@24fps,
  4-step turbo LoRA, clay-tablet cuneiform prompt per O-1746 spec)
- CEO audio-ban compliance (O-20261009-1901): workflow is video-ONLY by
  construction (no VAEDecodeAudio / no CreateVideo audio input) -> output
  MP4 carries no audio track; the workflow JSON is the evidence.
- FIFO discipline: shared 8188 server, never touches other queued items.
- Delivery: output MP4 -> cph4/fleet/h3-local-test/outbound/local/ (group
  canon, committed by the closing leg of the round); runner state ->
  results/_r818bmc_h3_client_state.json for next-round verification.
Usage: python Tools/_r818bmc_h3_client.py [--seed 20261009] [--wait 5400]
ASCII-only prints (GBK console safety)."""
import argparse
import json
import os
import shutil
import sys
import time
import urllib.request
import urllib.error

R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
WF_PATH = os.path.join(r"K:\Fluxgroup\FluxGroup\cph4\fleet\h3-local-test",
                       "h3_t2v_local_768p_bmc.json")
COMFY_OUTPUT_ROOT = r"D:\ComfyUI\ComfyUI\output"
OUTBOUND_LOCAL = os.path.join(r"K:\Fluxgroup\FluxGroup\cph4\fleet\h3-local-test",
                              "outbound", "local")
STATE = os.path.join(R, "results", "_r818bmc_h3_client_state.json")
CLIENT_ID = "bmc-h3-local-test"
POLL_SEC = 10


def http_json(url, payload=None, timeout=30):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def save_state(obj):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261009)
    ap.add_argument("--server", default="http://127.0.0.1:8188")
    ap.add_argument("--wait", type=int, default=5400)
    args = ap.parse_args()

    st = {"phase": "submit", "seed": args.seed, "t0": time.time()}
    save_state(st)
    with open(WF_PATH, "r", encoding="utf-8") as f:
        wf = json.load(f)
    wf["10"]["inputs"]["noise_seed"] = args.seed

    t0 = time.time()
    try:
        resp = http_json(args.server + "/prompt",
                         {"prompt": wf, "client_id": CLIENT_ID})
    except Exception as e:
        st.update(phase="failed", err="submit: %s" % e)
        save_state(st)
        print("SUBMIT FAILED: %s" % e)
        return 2
    pid = resp.get("prompt_id")
    if not pid:
        st.update(phase="failed", err="no prompt_id: %s" % resp)
        save_state(st)
        print("SUBMIT FAILED: %s" % resp)
        return 2
    st.update(phase="queued", prompt_id=pid)
    save_state(st)
    print("SUBMITTED prompt_id=%s seed=%d" % (pid, args.seed))

    while True:
        time.sleep(POLL_SEC)
        if time.time() - t0 > args.wait:
            st.update(phase="timeout")
            save_state(st)
            print("TIMEOUT after %ds" % args.wait)
            return 5
        try:
            hist = http_json(args.server + "/history/" + pid, timeout=15)
        except urllib.error.URLError:
            print("[%4ds] poll err, retrying..." % (time.time() - t0))
            continue
        entry = hist.get(pid)
        if entry is None:
            # r646 law: no history entry before completion = RUNNING, not lost
            print("[%4ds] running..." % (time.time() - t0))
            continue
        status = entry.get("status", {})
        if not status.get("completed", False):
            st.update(phase="failed",
                      err="not completed: %s" % json.dumps(status)[:300])
            save_state(st)
            print("[%4ds] NOT COMPLETED: %s"
                  % (time.time() - t0, json.dumps(status)[:300]))
            return 3
        outputs = entry.get("outputs", {})
        saved = []
        for node_out in outputs.values():
            for item in (node_out.get("videos") or []):
                saved.append(item)
        print("DONE in %.0fs, saved=%s"
              % (time.time() - t0, json.dumps(saved)[:300]))
        os.makedirs(OUTBOUND_LOCAL, exist_ok=True)
        copied = []
        for item in saved:
            src = os.path.join(COMFY_OUTPUT_ROOT,
                               item.get("subfolder", ""), item.get("filename", ""))
            if os.path.isfile(src):
                dst = os.path.join(OUTBOUND_LOCAL, item.get("filename", ""))
                shutil.copy2(src, dst)
                copied.append({"src": src, "dst": dst,
                               "bytes": os.path.getsize(dst)})
        st.update(phase="delivered" if copied else "no_output",
                  delivered=copied, elapsed_sec=int(time.time() - t0),
                  audio_note="video-only workflow (no audio nodes) = "
                            "constructive no-audio per O-20261009-1901")
        save_state(st)
        for c in copied:
            print("DELIVERED: %s (%d bytes)" % (c["dst"], c["bytes"]))
        return 0 if copied else 4


if __name__ == "__main__":
    sys.exit(main())
