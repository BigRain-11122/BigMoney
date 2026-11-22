"""One arbiter for both lines on this machine: quant asks, media owns the GPU.

Why
---
Two lines share one box. Media runs i2v / TTS / voice corpora on the GPU and
CPU; the quant bench runs backtests on the CPU. Each line used to start work on
its own: the bench happily began a 5000-symbol panel build while ComfyUI held
25GB of RAM and 100% GPU, and the only thing that stopped it was a hard-coded
RAM guard inside one cell. This script makes that coordination explicit and
machine-checked, following research/RESOURCE-CONTRACT.json.

Rules (short version)
---------------------
* Media owns the GPU on this machine. Quant never asks for it; a cell that
  declares needs=gpu is denied by policy.
* Quant runs cpu_heavy only when media has no CPU jobs, RAM >= 6GB and load <
  50%. Otherwise it waits -- it never preempts.
* cpu_light needs RAM >= 2GB and load < 85%; its slot count shrinks with the
  media's own CPU usage.
* Every decision is one ledger line with the numbers that produced it, and every
  grant writes a lease with a TTL so a crashed runner cannot block the line
  forever.

`--audit` reviews the last 7 days and writes bounded proposals (at most one
cadence step, once per day, only with >= 24 decisions).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACT = os.path.join(ROOT, "research", "RESOURCE-CONTRACT.json")
ARB = os.path.join(ROOT, "results", "arbiter")
LEASES = os.path.join(ARB, "LEASES.json")
LEDGER = os.path.join(ARB, "LEDGER.jsonl")
STATE = os.path.join(ARB, "STATE.json")
PROPOSALS = os.path.join(ARB, "PROPOSALS.json")
BOARD = os.path.join(ROOT, "research", "ARBITER-BOARD.md")
TZ = timezone(timedelta(hours=8))

# Media work on this box, recognised from the command line. Keep the patterns
# broad enough that a renamed runner still matches its family.
MEDIA_PATTERNS = [
    "h3_i2v", "i2v_album", "kf_batch", "comfy", "main.py --listen",
    "vb_worker", "vb_build", "voicebank", "heroine_lora", "tts", "ffmpeg",
    "piper", "kokoro", "drama",
]
QUANT_PATTERNS = ["bench_", "block_board", "iteration_loop", "s6_chain", "smoke_test"]


def now():
    return datetime.now(TZ)


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def ledger(row):
    os.makedirs(ARB, exist_ok=True)
    row = dict(row)
    row.setdefault("ts", now().isoformat(timespec="seconds"))
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------
# measurement
# --------------------------------------------------------------------------
def ram_free_gb():
    try:
        import psutil
        return round(psutil.virtual_memory().available / (1024 ** 3), 2)
    except Exception:
        return None


def cpu_load_pct():
    try:
        import psutil
        return round(psutil.cpu_percent(interval=0.4), 1)
    except Exception:
        return None


def gpu_state():
    exe = shutil.which("nvidia-smi")
    if not exe:
        return {"available": False}
    try:
        out = subprocess.run(
            [exe, "--query-gpu=utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
        util, used, total = [int(x.strip()) for x in out[0].split(",")]
        return {"available": True, "util_pct": util, "vram_used_mb": used,
                "vram_total_mb": total}
    except Exception as e:
        return {"available": False, "error": str(e)}


def comfy_queue(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/queue", timeout=2) as r:
            d = json.load(r)
        return {"running": len(d.get("queue_running", [])),
                "pending": len(d.get("queue_pending", []))}
    except Exception:
        return {"running": None, "pending": None}


def processes():
    """Media vs quant jobs, from command lines; excludes our own probe."""
    media, quant = [], []
    try:
        import psutil
    except Exception:
        return media, quant
    me = os.getpid()
    for p in psutil.process_iter(["pid", "name", "cmdline", "memory_info"]):
        try:
            if p.info["pid"] == me:
                continue
            cmd = " ".join(p.info["cmdline"] or [])
            if not cmd:
                continue
            low = cmd.lower()
            if "line_arbiter" in low or "repo_write_contention" in low:
                continue
            mb = int((p.info["memory_info"].rss if p.info["memory_info"] else 0) / 1048576)
            item = {"pid": p.info["pid"], "mb": mb, "cmd": cmd[:160]}
            if any(k in low for k in MEDIA_PATTERNS):
                media.append(item)
            elif any(k in low for k in QUANT_PATTERNS):
                quant.append(item)
        except Exception:
            continue
    return media, quant


def measure():
    media, quant = processes()
    return {
        "ts": now().isoformat(timespec="seconds"),
        "ram_free_gb": ram_free_gb(),
        "cpu_load_pct": cpu_load_pct(),
        "gpu": gpu_state(),
        "comfy_8188": comfy_queue(8188),
        "comfy_8189": comfy_queue(8189),
        "media_jobs": media,
        "quant_jobs": quant,
        "media_cpu_jobs": len([m for m in media if m["mb"] > 150]),
        "media_ram_gb": round(sum(m["mb"] for m in media) / 1024.0, 2),
    }


# --------------------------------------------------------------------------
# leases
# --------------------------------------------------------------------------
def load_leases():
    d = read_json(LEASES, {}) or {}
    out = {}
    t = now()
    for k, v in (d.get("leases") or {}).items():
        try:
            exp = datetime.fromisoformat(v["expires"])
        except Exception:
            continue
        if exp > t:
            out[k] = v
    return out


def save_leases(leases):
    write_json(LEASES, {"updated": now().isoformat(timespec="seconds"), "leases": leases})


# --------------------------------------------------------------------------
# the decision
# --------------------------------------------------------------------------
def contract():
    return read_json(CONTRACT) or {}


def tuning():
    """Today's applied auto-proposals (at most one step, cleared each day)."""
    p = read_json(PROPOSALS, {}) or {}
    a = p.get("applied") or {}
    if a.get("date") != now().date().isoformat():
        return {}
    return a


def media_progress():
    """Media's own queue depth and last progress -- read-only, no touching."""
    base = os.path.join(ROOT, "..", "..", "cph4", "fleet", "mv-album-001-jay")
    base = os.path.abspath(base)
    out = {"clips_dir": None, "clips": None, "newest_h": None, "manifest_units": None}
    for name in ("clips-hei-480", "clips-hei", "clips-local-768", "clips-packA-768"):
        d = os.path.join(base, name)
        if os.path.isdir(d):
            files = [f for f in os.listdir(d) if f.endswith((".mp4", ".png"))]
            out["clips_dir"] = name
            out["clips"] = len(files)
            if files:
                newest = max(os.path.getmtime(os.path.join(d, f)) for f in files)
                out["newest_h"] = round((time.time() - newest) / 3600.0, 1)
            break
    man = os.path.join(base, "plan", "hei-i2v-manifest.json")
    if os.path.exists(man):
        d = read_json(man, {}) or {}
        units = d.get("units") or d.get("shots") or d.get("jobs") or []
        out["manifest_units"] = len(units) if isinstance(units, list) else None
    return out


def decide(asker, want, cell=None):
    """Return {allow, cls, reason, evidence}. Never preempts, never kills."""
    c = contract()
    m = measure()
    leases = load_leases()
    evidence = {
        "ram_free_gb": m["ram_free_gb"], "cpu_load_pct": m["cpu_load_pct"],
        "gpu_util_pct": m["gpu"].get("util_pct"),
        "vram_used_mb": m["gpu"].get("vram_used_mb"),
        "comfy_running": m["comfy_8188"]["running"], "comfy_pending": m["comfy_8188"]["pending"],
        "media_cpu_jobs": m["media_cpu_jobs"], "media_ram_gb": m["media_ram_gb"],
    }

    wants = want or "cpu_light"
    if wants == "gpu":
        return {"allow": False, "cls": "gpu", "reason": "DENY_POLICY_MEDIA_OWNS_GPU",
                "evidence": evidence}
    if any(k in leases for k in ("cpu_heavy", "disk_io")) and wants in ("cpu_heavy", "disk_io"):
        return {"allow": False, "cls": wants, "reason": "HELD_BY_LEASE",
                "evidence": evidence, "lease": leases.get(wants)}

    ram = m["ram_free_gb"] or 0.0
    load = m["cpu_load_pct"] or 0.0
    if wants == "cpu_heavy":
        if ram < 6.0:
            return {"allow": False, "cls": wants, "reason": "DENY_RAM", "evidence": evidence}
        if m["media_cpu_jobs"] > 0:
            return {"allow": False, "cls": wants, "reason": "DENY_MEDIA_CPU_BUSY",
                    "evidence": evidence}
        if load >= 50:
            return {"allow": False, "cls": wants, "reason": "DENY_CPU_LOAD", "evidence": evidence}
        return {"allow": True, "cls": wants, "reason": "GRANT_MEDIA_CLEAR",
                "evidence": evidence, "threads": 6}
    if wants == "disk_io":
        if ram < 2.0:
            return {"allow": False, "cls": wants, "reason": "DENY_RAM", "evidence": evidence}
        return {"allow": True, "cls": wants, "reason": "GRANT_DISK_FREE",
                "evidence": evidence, "threads": 2}
    # cpu_light
    if ram < 2.0:
        return {"allow": False, "cls": "cpu_light", "reason": "DENY_RAM", "evidence": evidence}
    if load >= 85:
        return {"allow": False, "cls": "cpu_light", "reason": "DENY_CPU_LOAD",
                "evidence": evidence}
    mine = [q for q in m["quant_jobs"] if "bench_" in q["cmd"].lower()]
    limit = 2 + int(tuning().get("light_slots_extra", 0))
    if len(mine) >= limit:
        return {"allow": False, "cls": "cpu_light", "reason": "DENY_QUANT_SLOTS_FULL",
                "evidence": evidence, "slots": limit}
    return {"allow": True, "cls": "cpu_light", "reason": "GRANT_LIGHT",
            "evidence": evidence, "threads": 3}


def release(cls):
    """Give a lease back as soon as the job ends; TTL is only a crash net."""
    leases = load_leases()
    if cls in leases:
        leases.pop(cls, None)
        save_leases(leases)
        return True
    return False


def ask(asker, want, cell=None):
    d = decide(asker, want, cell)
    if d["allow"]:
        leases = load_leases()
        leases[d["cls"]] = {
            "holder": asker, "cell": (cell or {}).get("id"), "pid": os.getpid(),
            "granted": now().isoformat(timespec="seconds"),
            "expires": (now() + timedelta(minutes=int(
                (contract().get("leases") or {}).get("ttl_minutes", 30)))
            ).isoformat(timespec="seconds"),
        }
        save_leases(leases)
    ledger({"asker": asker, "cell": (cell or {}).get("id"), "class": d["cls"],
            "decision": "GRANT" if d["allow"] else "DENY", "reason": d["reason"],
            "evidence": d["evidence"]})
    return d


# --------------------------------------------------------------------------
# self-audit (bounded proposals)
# --------------------------------------------------------------------------
def read_ledger(days=7):
    if not os.path.exists(LEDGER):
        return []
    cut = (now() - timedelta(days=days)).isoformat()
    rows = []
    for line in open(LEDGER, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("ts", "") >= cut:
            rows.append(r)
    return rows


def audit():
    rows = read_ledger(7)
    if len(rows) < 24:
        payload = {"generated": now().isoformat(timespec="seconds"), "samples": len(rows),
                   "state": "INSUFFICIENT_SAMPLE", "proposals": []}
        write_json(PROPOSALS, payload)
        return payload

    denies = [r for r in rows if r.get("decision") == "DENY"]
    grants = [r for r in rows if r.get("decision") == "GRANT"]
    ratio = len(denies) / max(len(rows), 1)
    reasons = {}
    for r in denies:
        reasons[r.get("reason")] = reasons.get(r.get("reason"), 0) + 1
    ram_share = sum(v for k, v in reasons.items() if "RAM" in k) / max(len(denies), 1)

    proposals = []
    if ratio > 0.6:
        proposals.append({
            "id": "quant_wait_high", "evidence": {"deny_ratio": round(ratio, 2),
                                                  "top_reasons": reasons},
            "propose": "把 bench tick 从 20 分钟放到 30 分钟；heavy 格改到 media 空窗",
            "auto_apply": False, "why_not_auto": "改变节律需人确认一次",
        })
    if ratio < 0.1 and grants:
        proposals.append({
            "id": "quant_wait_low", "evidence": {"deny_ratio": round(ratio, 2)},
            "propose": "media 空闲时可允许 2 个 cpu_light 并发",
            "auto_apply": True, "step": "+1 slot",
        })
    if ram_share > 0.5:
        proposals.append({
            "id": "ram_denies", "evidence": {"ram_share_of_denies": round(ram_share, 2)},
            "propose": "heavy 格改分片或先 GC 面板缓存，不要硬等 RAM",
            "auto_apply": False, "why_not_auto": "改格子实现属研究席决定",
        })

    payload = {"generated": now().isoformat(timespec="seconds"), "samples": len(rows),
               "grants": len(grants), "denies": len(denies),
               "deny_ratio": round(ratio, 3), "reasons": reasons,
               "ram_share_of_denies": round(ram_share, 3),
               "state": "OK", "proposals": proposals}

    # bounded auto-apply: at most one name per day, only the safe ones
    applied = tuning() or {"date": now().date().isoformat()}
    auto = [p for p in proposals if p.get("auto_apply")]
    if auto and "light_slots_extra" not in applied:
        applied["light_slots_extra"] = 1
        applied["source"] = auto[0]["id"]
        applied["note"] = "one extra cpu_light slot today; resets at midnight"
    payload["applied"] = applied
    write_json(PROPOSALS, payload)
    return payload


# --------------------------------------------------------------------------
# board
# --------------------------------------------------------------------------
def render_board(m=None, d=None):
    m = m or measure()
    c = contract()
    mp = media_progress()
    tun = tuning()
    lines = ["# 资源共享仲裁看板（量化 × 自媒体）", "",
             f"generated {m['ts']} | 契约 v{c.get('version')}"
             + (f" | 今日自动调档 {tun.get('source')}（+{tun.get('light_slots_extra')} 轻槽）"
                if tun.get("light_slots_extra") else ""), "",
             "| 资源 | 实测 | 谁在用 | 规则 |",
             "|---|---|---|---|",
             f"| GPU | util {m['gpu'].get('util_pct')}% · VRAM {m['gpu'].get('vram_used_mb')}/"
             f"{m['gpu'].get('vram_total_mb')}MB · Comfy 队列 "
             f"{m['comfy_8188']['running']}/{m['comfy_8188']['pending']} | "
             f"media（本机 GPU 归自媒体） | 量化永不申请 GPU |",
             f"| CPU | load {m['cpu_load_pct']}% | media {m['media_cpu_jobs']} 个活 · "
             f"quant {len(m['quant_jobs'])} 个 | heavy 要求 media 空且 load<50 |",
             f"| RAM | free {m['ram_free_gb']}GB | media 占 {m['media_ram_gb']}GB | "
             f"heavy 需 ≥6GB · light 需 ≥2GB |",
             f"| 自媒体排队 | 清单 {mp.get('manifest_units')} 单 · {mp.get('clips_dir')} 已有 "
             f"{mp.get('clips')} 个产物 · 最近推进 {mp.get('newest_h')}h 前 | "
             f"media 产线 | 自媒体有活时量化 heavy 让路 |"]
    lines += ["", "## 当前在跑", ""]
    if m["media_jobs"]:
        for j in m["media_jobs"][:8]:
            lines.append(f"- media pid {j['pid']} · {j['mb']}MB · `{j['cmd'][:110]}`")
    else:
        lines.append("- media：无（可放行量化 heavy）")
    if m["quant_jobs"]:
        for j in m["quant_jobs"][:8]:
            lines.append(f"- quant pid {j['pid']} · {j['mb']}MB · `{j['cmd'][:110]}`")
    else:
        lines.append("- quant：无")
    if d:
        lines += ["", "## 最近一次裁决", "",
                  f"- {d.get('class')} → **{'GRANT' if d.get('allow') else 'DENY'}** "
                  f"({d.get('reason')})", f"- 证据：{json.dumps(d.get('evidence'), ensure_ascii=False)}"]
    lines += ["", "## 边界", "",
              "- 仲裁只决定「开不开新活」，不杀任何正在跑的进程；被拒的格子保持 pending。",
              "- 租约 30 分钟自动过期；执行体崩溃不会永久占坑。",
              "- 自动调参只 ±1 档、每天最多一次、需 ≥24 次决策样本；其余提案只报不改。"]
    with open(BOARD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def selftest():
    checks = []
    c = contract()
    checks.append(("contract readable", bool(c.get("classes"))))
    checks.append(("media owns gpu", (c.get("classes", {}).get("gpu", {}).get("holder") == "media-only")))
    m = measure()
    checks.append(("measure has ram", m.get("ram_free_gb") is not None))
    checks.append(("measure has cpu", m.get("cpu_load_pct") is not None))
    d = decide("selftest", "cpu_light")
    checks.append(("decide returns verdict", isinstance(d.get("allow"), bool)))
    denied = decide("selftest", "gpu")
    checks.append(("gpu denied by policy", denied["allow"] is False
                   and denied["reason"] == "DENY_POLICY_MEDIA_OWNS_GPU"))
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    return 0 if all(ok for _, ok in checks) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", action="store_true")
    ap.add_argument("--ask", nargs=2, metavar=("ASKER", "CLASS"))
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.audit:
        print(json.dumps(audit(), ensure_ascii=False, indent=1))
        return 0
    if a.ask:
        d = ask(a.ask[0], a.ask[1])
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return 0 if d["allow"] else 3
    m = measure()
    write_json(STATE, m)
    leases = load_leases()
    d = {"class": "tick", "allow": None, "reason": "STATE_ONLY", "evidence": {}}
    render_board(m, d)
    print(json.dumps({"ts": m["ts"], "ram_free_gb": m["ram_free_gb"],
                      "cpu_load_pct": m["cpu_load_pct"],
                      "gpu_util_pct": m["gpu"].get("util_pct"),
                      "media_cpu_jobs": m["media_cpu_jobs"],
                      "media_ram_gb": m["media_ram_gb"],
                      "leases": list(leases)}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
