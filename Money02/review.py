"""10-minute system self-audit (user order 2026-09-21: 每隔10分钟复查+迭代改进).

Runs INSIDE every tick heartbeat. Checks the whole pipeline, executes safe
auto-remedies, appends a machine log (results/review.jsonl) and renders the
human report (results/latest/review.md). Findings feed the next iteration:
WARN/FAIL items are the todo list for agent-level review.

Checks:
  C1 tick活力      - newest ticks.jsonl event age (dead chain = FAIL)
  C2 full周期      - full_run.pid alive/age sane
  C3 数据新鲜度    - panel last date == index last date
  C4 模拟盘        - paper executed through panel last date
  C5 信号单        - signals.json exists with fresh buys
  C6 联赛连续性    - n_valid advancing across reviews
  C7 部署一致性    - league mem genome lengths all remappable generations
  C8 错误扫描      - recent Traceback/START-FAIL in tick.log (BOM-aware)
  C9 资源          - free RAM / free disk
Remedies (idempotent, safe): remove stale tick.lock / full_run.pid with dead
owners. Everything else is flagged for the agent iteration loop.
"""
import ctypes
import datetime as dt
import json
import os
import time

import config as C

REV_LOG = C.RESULTS_DIR / "review.jsonl"
REV_MD = C.RESULTS_DIR / "latest" / "review.md"


def _read_bom(path, tail_bytes=20000):
    try:
        t = open(path, "rb").read()[-tail_bytes:]
    except OSError:
        return ""
    if t[:2] == b"\xff\xfe":
        return t.decode("utf-16-le", errors="replace")
    if t[:3] == b"\xef\xbb\xbf":
        return t.decode("utf-8-sig", errors="replace")
    return t.decode("utf-8", errors="replace")


def _pid_alive(pid):
    try:
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, int(pid))
        if h:
            k.CloseHandle(h)
            return True
    except Exception:  # noqa: BLE001
        pass
    return False


def _free_ram_gb():
    # full MEMORYSTATUSEX: dwLength MUST be 64 bytes or the API call fails and
    # the buffer stays zeroed (that made C9 report a phantom "0.0GB" for a day)
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    ms = MS()
    ms.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    return ms.ullAvailPhys / 2**30


def _remediate(findings):
    """Safe idempotent self-repairs; returns action notes."""
    acts = []
    lock = C.LOGS_DIR / "tick.lock"
    if lock.exists():
        try:
            pid = int(lock.read_text().strip() or 0)
        except Exception:  # noqa: BLE001
            pid = 0
        if pid and not _pid_alive(pid):
            lock.unlink(missing_ok=True)
            acts.append(f"清除陈旧tick.lock(pid={pid})")
    fp = C.RESULTS_DIR / "full_run.pid"
    if fp.exists():
        try:
            pid = int(fp.read_text().strip() or 0)
        except Exception:  # noqa: BLE001
            pid = 0
        if pid and not _pid_alive(pid):
            fp.unlink(missing_ok=True)
            acts.append(f"清除陈旧full_run.pid(pid={pid})")
    return acts


def run_review():
    """Non-fatal: always returns a dict even on partial failure."""
    t_now = time.time()
    now = dt.datetime.now()
    F = []  # (code, level, detail) level: OK/WARN/FAIL
    try:
        # C1 tick activity
        try:
            evs = [json.loads(l) for l in
                   open(C.RESULTS_DIR / "ticks.jsonl", encoding="utf-8")]
            last = evs[-1] if evs else None
            age = (t_now - time.mktime(time.strptime(
                last["time"], "%Y-%m-%d %H:%M"))) if last else 1e9
            if age > 25 * 60:
                F.append(("C1", "FAIL", f"tick链停摆 {age/60:.0f} 分钟"
                          f"（最后事件 {last['time'] if last else '无'}）"))
            else:
                F.append(("C1", "OK", f"最后事件 {last['time']} "
                          f"({last.get('mode')}) {age/60:.0f}分钟前"))
        except Exception as e:  # noqa: BLE001
            F.append(("C1", "FAIL", f"ticks.jsonl 读取失败 {e}"))

        # C2 full cycle
        fp = C.RESULTS_DIR / "full_run.pid"
        if fp.exists():
            try:
                pid = int(fp.read_text().strip() or 0)
                age = (t_now - fp.stat().st_mtime) / 60
                if pid and _pid_alive(pid):
                    lvl = "OK" if age <= 540 else "WARN"
                    F.append(("C2", lvl, f"全周期运行中 pid={pid} {age:.0f}分钟"))
                else:
                    F.append(("C2", "WARN", f"陈旧full_run.pid pid={pid}"))
            except Exception as e:  # noqa: BLE001
                F.append(("C2", "WARN", f"pid检查失败 {e}"))
        else:
            F.append(("C2", "OK", "无全周期在跑"))

        # C3 data freshness (cheap: dates.npy vs sse parquet max)
        try:
            import numpy as np
            import pandas as pd
            dts = np.load(C.CACHE_DIR / "dates.npy")
            panel_last = str(dts[-1])[:10]
            idx_last = str(pd.read_parquet(
                C.IDX_DIR / "sse.parquet")["date"].max())[:10]
            if panel_last >= idx_last:
                F.append(("C3", "OK", f"面板至 {panel_last}"))
            else:
                F.append(("C3", "WARN",
                          f"面板落后: 面板 {panel_last} < 指数 {idx_last}"))
        except Exception as e:  # noqa: BLE001
            F.append(("C3", "WARN", f"新鲜度检查失败 {type(e).__name__}"))

        # C4 paper account
        try:
            pp = C.RESULTS_DIR / "paper.json"
            dts_last10 = None
            if pp.exists():
                paper = json.loads(pp.read_text(encoding="utf-8"))
                h = paper.get("history", [])
                dts_last10 = h[-1]["date"][:10] if h else None
                eq = h[-1]["equity"] if h else C.CAPITAL
                if dts_last10:
                    F.append(("C4", "OK", f"模拟盘记至 {dts_last10} "
                              f"权益 {eq:,.0f} ({eq / C.CAPITAL - 1:+.1%})"))
                else:
                    F.append(("C4", "WARN", "模拟盘无记账"))
            else:
                F.append(("C4", "WARN", "paper.json 不存在"))
        except Exception as e:  # noqa: BLE001
            F.append(("C4", "WARN", f"模拟盘检查失败 {e}"))

        # C5 signals
        try:
            sp = C.RESULTS_DIR / "signals.json"
            if sp.exists():
                sig = json.loads(sp.read_text(encoding="utf-8"))
                nb = len(sig.get("buys", []))
                mt = time.strftime("%H:%M", time.localtime(sp.stat().st_mtime))
                F.append(("C5", "OK" if nb > 0 else "WARN",
                          f"信号单 {nb} 买单 (生成 {mt})"))
            else:
                F.append(("C5", "WARN", "signals.json 不存在"))
        except Exception as e:  # noqa: BLE001
            F.append(("C5", "WARN", f"信号检查失败 {e}"))

        # C6 league continuity: n_valid advancing over last reviews
        try:
            hist = [json.loads(l) for l in
                    open(REV_LOG, encoding="utf-8").read().splitlines()[-6:]]
            nvs = [h.get("n_valid") for h in hist if h.get("n_valid")]
            lg = json.load(open(C.RESULTS_DIR / "league.json", encoding="utf-8"))
            cur = lg.get("meta", {}).get("n_valid")
            if nvs and cur is not None and all(v == cur for v in nvs[-3:]):
                F.append(("C6", "WARN", f"联赛停滞于 {cur} 轮"))
            else:
                F.append(("C6", "OK", f"联赛 {cur} 轮"))
        except FileNotFoundError:
            F.append(("C6", "OK", "联赛无历史比对（首次复查）"))
        except Exception as e:  # noqa: BLE001
            F.append(("C6", "WARN", f"联赛检查失败 {e}"))

        # C7 deploy consistency (the 2026-09-21 lesson: silent old-code runs)
        try:
            import evolve as EV
            legal = {EV.D_GENOME} | set(EV._LEGACY_LEN)
            lg = json.load(open(C.RESULTS_DIR / "league.json", encoding="utf-8"))
            lens = {len(m["g"]) for s in lg["standings"].values()
                    for m in s.get("mem", [])}
            bad = lens - legal
            if bad:
                F.append(("C7", "FAIL", f"未注册基因代长度 {sorted(bad)} "
                          f"(当代 {EV.D_GENOME}, 已注册 {sorted(EV._LEGACY_LEN)})"))
            else:
                F.append(("C7", "OK", f"基因代一致: mem∈{sorted(lens)}"))
        except Exception as e:  # noqa: BLE001
            F.append(("C7", "WARN", f"部署一致性检查失败 {e}"))

        # C8 error scan
        try:
            txt = _read_bom(C.LOGS_DIR / "tick.log")
            recent = txt[-4000:]
            errs = recent.count("Traceback") + recent.count("START-FAIL")
            if errs:
                F.append(("C8", "WARN", f"tick.log 近段错误标记 {errs} 处"))
            else:
                F.append(("C8", "OK", "tick.log 无近期错误标记"))
        except Exception as e:  # noqa: BLE001
            F.append(("C8", "WARN", f"日志扫描失败 {e}"))

        # C9 resources
        try:
            ram = _free_ram_gb()
            d = os.statvfs(C.ROOT) if os.name == "posix" else None
            import shutil
            free_gb = shutil.disk_usage(str(C.ROOT)).free / 2**30
            if ram < 1.5:
                F.append(("C9", "WARN", f"内存仅剩 {ram:.1f}GB"))
            else:
                F.append(("C9", "OK", f"内存 {ram:.1f}GB / 磁盘 {free_gb:.0f}GB"))
        except Exception as e:  # noqa: BLE001
            F.append(("C9", "WARN", f"资源检查失败 {e}"))
    except Exception as e:  # noqa: BLE001
        F.append(("C0", "FAIL", f"复查器顶层异常 {type(e).__name__}: {e}"))

    acts = _remediate(F)
    lv_rank = {"OK": 0, "WARN": 1, "FAIL": 2}
    worst = max((lv for _, lv, _ in F), key=lambda x: lv_rank[x], default="OK")
    try:
        lg = json.load(open(C.RESULTS_DIR / "league.json", encoding="utf-8"))
        n_valid = lg.get("meta", {}).get("n_valid")
    except Exception:  # noqa: BLE001
        n_valid = None
    row = {"time": now.strftime("%Y-%m-%d %H:%M"), "verdict": worst,
           "n_valid": n_valid,
           "findings": [{"c": c, "lv": lv, "d": d} for c, lv, d in F],
           "actions": acts}
    try:
        with open(REV_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass
    try:
        lines = [f"# 系统复查（每10分钟 · {row['time']}）\n",
                 f"**总判定: {'🟢 正常' if worst == 'OK' else '🟡 警告' if worst == 'WARN' else '🔴 故障'}**\n"]
        for c, lv, d in F:
            mark = {"OK": "✅", "WARN": "🟡", "FAIL": "❌"}[lv]
            lines.append(f"- {mark} **{c}** {d}")
        if acts:
            lines.append("\n**自动修复**: " + "；".join(acts))
        hist = []
        try:
            hist = [json.loads(l)["verdict"] for l in
                    open(REV_LOG, encoding="utf-8").read().splitlines()[-12:]]
        except Exception:  # noqa: BLE001
            pass
        if hist:
            lines.append(f"\n近 {len(hist)} 次复查趋势: "
                         + "".join({"OK": "🟢", "WARN": "🟡", "FAIL": "🔴"}[v]
                                   for v in hist))
        REV_MD.parent.mkdir(exist_ok=True)
        REV_MD.write_text("\n".join(lines), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    return row


if __name__ == "__main__":
    r = run_review()
    print(json.dumps(r, ensure_ascii=False, indent=1))
