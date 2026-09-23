"""10-minute self-evolution tick (user-set cadence). Hang-immune design
(2026-09-19 重构 per 用户令"假死卡死就自己重构"):

- PID lock: a stale tick (age > 13 min) gets its process KILLED before takeover.
- full cycle (data refresh + WF + report) runs as a DETACHED child process so
  the tick cadence never blocks on it; every tick POLICES that child: a full
  run older than 120 min is force-killed and restarted next time (self-heal).
- market hours (weekday 9:15-15:30): evolution deepening ONLY - daily bars are
  partial intraday; touching data would pollute signals.
- deepen() itself is guarded by the Evaluator (broken-worker/timeout degrade).
"""
import json
import os
import subprocess
import time
import datetime as dt

import config as C
import data as D
import evolve as EV
import report as RP

LOCK = C.LOGS_DIR / "tick.lock"
FULLPID = C.RESULTS_DIR / "full_run.pid"
TICKS = C.RESULTS_DIR / "ticks.jsonl"


def _pid_alive(pid):
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, int(pid))  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        k.CloseHandle(h)
        return True
    except Exception:  # noqa: BLE001
        return False


def _kill_pid(pid):
    try:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                       capture_output=True, timeout=30)
    except Exception:  # noqa: BLE001
        pass


def _log_event(row):
    with open(TICKS, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _try_lock():
    """True if we own the tick. Stale locks get their owner killed (self-heal)."""
    if LOCK.exists():
        try:
            pid = int(LOCK.read_text().strip() or 0)
            age = time.time() - LOCK.stat().st_mtime
        except Exception:  # noqa: BLE001
            pid, age = 0, 999
        if age < 13 * 60 and pid and _pid_alive(pid):
            return False
        if pid and _pid_alive(pid):
            _log_event({"time": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "mode": "recovery", "action": f"kill stale tick pid={pid}"})
            _kill_pid(pid)
        try:
            LOCK.unlink()
        except Exception:  # noqa: BLE001
            pass
    LOCK.write_text(str(os.getpid()))
    return True


def _market_open(now):
    if now.weekday() >= 5:
        return False
    hm = now.hour * 60 + now.minute
    return 9 * 60 + 15 <= hm <= 15 * 60 + 30


def _cache_ready():
    return (C.CACHE_DIR / "dates.npy").exists()


def _police_full_run():
    """Kill a full-cycle run that hung beyond 120 minutes (self-heal)."""
    if not FULLPID.exists():
        return False
    try:
        pid = int(FULLPID.read_text().strip() or 0)
        age = time.time() - FULLPID.stat().st_mtime
    except Exception:  # noqa: BLE001
        return False
    if pid and _pid_alive(pid):
        if age > 540 * 60:  # 30-family WF needs headroom beyond ~4.5h
            _log_event({"time": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "mode": "recovery", "action": f"kill hung full run pid={pid}"})
            _kill_pid(pid)
            FULLPID.unlink(missing_ok=True)
            return False
        return True  # healthy full run in progress
    FULLPID.unlink(missing_ok=True)
    return False


def _launch_full():
    """Detached full cycle (run_daily.py) - tick never blocks on it."""
    flags = 0x00000008 | 0x00000020 | 0x00000200  # DETACHED|CREATE_NEW_PROCESS_GROUP|CREATE_NO_WINDOW
    p = subprocess.Popen(
        ["python", str(C.ROOT / "run_daily.py")],
        stdout=open(C.LOGS_DIR / "full_run.log", "ab"),
        stderr=subprocess.STDOUT, cwd=str(C.ROOT), creationflags=flags)
    FULLPID.write_text(str(p.pid))
    _log_event({"time": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "mode": "full-launch", "pid": p.pid})
    return p.pid


def main():
    now = dt.datetime.now()
    if not _try_lock():
        print("tick skipped: previous tick still running")
        return
    try:
        # 10-minute self-audit (user order 2026-09-21: 每隔10分钟复查+迭代改进)
        rev_verdict = "SKIP"
        try:
            import review
            rev = review.run_review()
            rev_verdict = rev["verdict"]
            if rev_verdict == "FAIL":
                print(f"review: 🔴 FAIL - see {review.REV_MD}")
        except Exception as e:  # noqa: BLE001
            print(f"review failed (non-fatal): {e}")
        full_running = _police_full_run()
        if not _market_open(now) and _cache_ready():
            D.update_index()
            ltd = D.last_trade_date()
            state_p = C.RESULTS_DIR / "state.json"
            state = json.loads(state_p.read_text(encoding="utf-8")) if state_p.exists() else {}
            if ltd is not None and state.get("last_trade_date") != str(ltd) and not full_running:
                _launch_full()
                print(f"tick: full cycle launched (ltd={ltd})")
                return
        # evolve path (market hours or no new data or full run in progress):
        # random-window mad iteration - sample history, validate blind, rank champions
        if not _cache_ready():
            print("tick: no cache yet (run a full backfill first)")
            return
        if _market_open(now):
            try:
                D.pull_live_snapshot()  # full-market realtime -> data/live/
            except Exception as e:  # noqa: BLE001
                print(f"live snapshot failed: {e}")
        res = EV.league_round()
        if not res.get("valid"):
            print("tick[league] budget skip (round invalid, next tick retries)")
            _log_event({"time": now.strftime("%Y-%m-%d %H:%M"),
                        "mode": "league-skip"})
            return
        sig = RP.write_signals(res["cache"], res["live"], res["regime"],
                               res["out_dir"])
        lg = {n: s["pts"] for n, s in res["league"].items()}
        leader = max(lg.items(), key=lambda kv: kv[1])[0]
        _log_event({"time": now.strftime("%Y-%m-%d %H:%M"), "mode": "league",
                    "round": res["round"], "rounds": res["rounds"],
                    "win_regime": res["regime_name"],
                    "winner": res["winner"],
                    "leader": EV.CLAN_CN[leader], "leader_pts": lg[leader],
                    "seat_change": res["took_seat"],
                    "champ_fit": res["champ_fit"], "live_fit": res["live_fit"],
                    "n_buys": len(sig.get("buys", [])),
                    "regime": sig.get("regime"),
                    "full_running": full_running})
        print(f"tick[league] 第{res['round']}轮 "
              f"{res['round_log']['window'][0]}~{res['round_log']['window'][1]} "
              f"市道={EV.REG_CN[res['regime_name']]} "
              f"轮胜={EV.CLAN_CN[res['winner']]} "
              f"榜首={EV.CLAN_CN[leader]}({lg[leader]}分) "
              f"席位易主={res['took_seat']} "
              f"buys={len(sig.get('buys', []))} regime={sig.get('regime')}")
    finally:
        try:
            LOCK.unlink()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
