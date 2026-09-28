"""r386 bm-b T-99 bonsai tight-envelope GPU trial orchestrator.

CEO order P-2026-09-28-07 / fleet task T-2026-09-28-99.
Sole spec = cph4/research/R-20260928-bonsai-fleet-trial.md (HQ FluxGroup repo).
bm-b lane per spec sec.2: RTX 3070 8GB = tight envelope, bare-window run.

Four-piece receipt (spec sec.5):
  1. deploy  = byte anchors + llama-server /health ok
  2. speed   = llama-bench tg128 (+pp512) vs fleet envelope (bm-a 4070S anchor 54.7)
  3. coexist = same-card verdict with in-service stack, stated honestly
  4. quality = >=3 in-domain (BigMoney) probes, self-graded + verifiable

Idempotent per phase; every number here is a live-run number (zero pre-write).
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEN = os.path.join(ROOT, "labbench", "bonsai")
MODEL = os.path.join(BEN, "Ternary-Bonsai-2-27B-PTQ1_0.gguf")
RUNTIME_DIR = os.path.join(BEN, "runtime")
RESULT = os.path.join(ROOT, "results", "_r386bmb_bonsai_trial_result.json")
PORT = 8079  # bm-a trial used 8077; bm-b picks 8079 (spec sec.1.4 self-chosen, avoid in-service)

BYTE_ANCHORS = {
    "model": (MODEL, 5946648928),
    "llama-bin.zip": (os.path.join(BEN, "llama-bin.zip"), 257322810),
    "cudart.zip": (os.path.join(BEN, "cudart.zip"), 391443627),
}

PROBES = [
    {
        "id": "P1-numeric-summary",
        "lane": "BigMoney deep-QA / research summary (numbers must survive)",
        "context": (
            "BigMoney 市场时钟 2026-09-24 判定：市场政体状态 ORANGE_COOL，"
            "可动用袖面 4 个，今日激活 0 个。触发面：沪深300 收盘价低于其 "
            "MA200（第 10 次采集）；市场宽度 0.77，阈值为 65%。"
        ),
        "prompt": "用不超过 60 字总结上文，保留全部数字，不要添加任何新数字。",
        "verify": ["ORANGE_COOL", "4", "0", "MA200", "10", "0.77", "65%"],
        "max_tokens": 300,
    },
    {
        "id": "P2-first-review-lookahead",
        "lane": "BigMoney complex first-review doc (advisory, T-70 boundary: not production coding)",
        "context": (
            "def add_signal(df):\n"
            "    df['ma5'] = df['close'].rolling(5).mean().shift(-1)\n"
            "    df['sig'] = df['close'] < df['ma5']\n"
            "    return df\n"
            "这是一个 A 股日频回测的信号函数，次日开盘价成交。"
        ),
        "prompt": (
            "一审这份回测信号代码：信号是否存在未来数据（look-ahead bias）问题？"
            "若有，指出具体哪一行并给出修复方法。50 字以内。"
        ),
        "verify": ["shift(-1)", "未来"],  # expected diagnosis: shift(-1) leaks future data; fix shift(1)/drop
        "max_tokens": 300,
    },
    {
        "id": "P3-t1-cost-arithmetic",
        "lane": "BigMoney risk/cost model arithmetic",
        "context": (
            "A股实行 T+1 交易制度；本司回测成本模型冻结为单边 13.041 bp。"
        ),
        "prompt": (
            "两个问题：① 周一收盘前买入的股票，按 T+1 制度最早哪一天可以卖出？"
            "② 一次完整的一买一卖，双边合计成本是多少 bp？只给答案与一句理由。"
        ),
        "verify": ["周二", "26.082"],  # T+1 => next trading day Tuesday; 13.041*2=26.082bp
        "max_tokens": 300,
    },
]


def fail(msg):
    print(f"[TRIAL-FAIL] {msg}", flush=True)
    sys.exit(2)


def phase_byte_check():
    out = {}
    for name, (path, anchor) in BYTE_ANCHORS.items():
        if not os.path.exists(path):
            fail(f"byte-check: {name} missing (download incomplete)")
        size = os.path.getsize(path)
        ok = size == anchor
        out[name] = {"bytes": size, "anchor": anchor, "match": ok}
        print(f"[bytes] {name}: {size} vs anchor {anchor} -> {'MATCH' if ok else 'MISMATCH'}", flush=True)
        if not ok:
            fail(f"byte-check: {name} mismatch (spec sec.1.1: re-download, no sick deployment)")
    return out


def phase_unpack():
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    marker = os.path.join(RUNTIME_DIR, ".unpacked")
    if os.path.exists(marker):
        print("[unpack] already unpacked (idempotent)", flush=True)
        return
    for zname in ("llama-bin.zip", "cudart.zip"):
        print(f"[unpack] {zname} ...", flush=True)
        rc = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Expand-Archive -Path '{os.path.join(BEN, zname)}' -DestinationPath '{RUNTIME_DIR}' -Force"],
            capture_output=True, text=True)
        if rc.returncode != 0:
            fail(f"unpack {zname} rc={rc.returncode}: {rc.stderr[-500:]}")
    with open(marker, "w") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%S"))
    print("[unpack] done", flush=True)


def find_exe(name):
    for root, dirs, files in os.walk(RUNTIME_DIR):
        if name in files:
            return os.path.join(root, name)
    return None


def phase_bench(res):
    bench = find_exe("llama-bench.exe")
    if not bench:
        fail("llama-bench.exe not found after unpack")
    # bm-a anchor methodology: ngl 99, fa on, tg128 + pp512
    cmd = [bench, "-m", MODEL, "-ngl", "99", "-fa", "on", "-p", "512", "-n", "128", "-r", "3"]
    print(f"[bench] {' '.join(cmd)}", flush=True)
    t0 = time.time()
    rc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    dur = round(time.time() - t0, 1)
    print(rc.stdout[-2000:], flush=True)
    if rc.returncode != 0:
        fail(f"llama-bench rc={rc.returncode}: {rc.stderr[-800:]}")
    res["bench"] = {"cmd": " ".join(cmd), "wall_sec": dur, "stdout_tail": rc.stdout[-1500:]}
    for line in rc.stdout.splitlines():
        if line.strip().startswith("|") and "512" in line and "128" in line:
            res["bench"]["raw_row"] = line.strip()
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            try:
                res["bench"]["pp512_tok_s"] = float(parts[2])
                res["bench"]["tg128_tok_s"] = float(parts[3])
            except (ValueError, IndexError):
                pass


def http_json(url, payload=None, timeout=600):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def phase_server_probes(res):
    server = find_exe("llama-server.exe")
    if not server:
        fail("llama-server.exe not found after unpack")
    cmd = [server, "-m", MODEL, "-ngl", "99", "-fa", "on", "--host", "127.0.0.1",
           "--port", str(PORT), "-c", "4096", "--no-webui"]
    print(f"[server] starting: {' '.join(cmd)}", flush=True)
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    healthy_at = None
    try:
        for _ in range(300):
            if proc.poll() is not None:
                fail(f"llama-server exited early rc={proc.returncode} (likely VRAM envelope breach)")
            try:
                http_json(f"http://127.0.0.1:{PORT}/health", timeout=3)
                healthy_at = time.time() - t0
                break
            except Exception:
                time.sleep(1)
        if healthy_at is None:
            fail("llama-server /health not ok within 300s")
        res["server"] = {"port": PORT, "health_ok_sec": round(healthy_at, 1)}
        print(f"[server] /health ok after {healthy_at:.1f}s", flush=True)

        res["probes"] = []
        for p in PROBES:
            body = {
                "model": "bonsai", "messages": [
                    {"role": "system", "content": "你是 BigMoney 量化公司的助手，回答简洁准确。"},
                    {"role": "user", "content": p["context"] + "\n\n" + p["prompt"]},
                ],
                "max_tokens": p["max_tokens"],
                "temperature": 0.2,
                "chat_template_kwargs": {"enable_thinking": False},
            }
            t0 = time.time()
            r = http_json(f"http://127.0.0.1:{PORT}/v1/chat/completions", body, timeout=600)
            wall = time.time() - t0
            text = r.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
            usage = r.get("usage", {})
            gen_tok = usage.get("completion_tokens", 0)
            hits = [k for k in p["verify"] if k in text]
            grade = len(hits) == len(p["verify"])
            res["probes"].append({
                "id": p["id"], "lane": p["lane"], "wall_sec": round(wall, 1),
                "completion_tokens": gen_tok,
                "tok_s": round(gen_tok / wall, 2) if wall and gen_tok else None,
                "expected_keys": p["verify"], "hit_keys": hits,
                "grade_pass": grade, "text": text,
            })
            print(f"[probe] {p['id']}: pass={grade} ({len(hits)}/{len(p['verify'])} keys, "
                  f"{gen_tok} tok in {wall:.1f}s)", flush=True)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except Exception:
            proc.kill()
        print("[server] stopped (bare window closed, restore step follows)", flush=True)


def main():
    res = {"ts_start": time.strftime("%Y-%m-%dT%H:%M:%S"), "machine": "bm-b",
           "task": "T-2026-09-28-99", "spec": "cph4/research/R-20260928-bonsai-fleet-trial.md"}
    res["byte_check"] = phase_byte_check()
    phase_unpack()
    phase_bench(res)
    phase_server_probes(res)
    res["ts_end"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(RESULT, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"[done] receipt evidence -> {RESULT}", flush=True)


if __name__ == "__main__":
    main()
