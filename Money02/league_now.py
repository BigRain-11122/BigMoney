"""Run one league round now (guarded: Windows spawn requires __main__ guard).
Manual tool: reuses the same tick lock so it never races the OS-scheduled
league round; standings/meta persist (no reset - league continuity)."""
import os
import time

import config as C
import evolve as EV

LOCK = C.LOGS_DIR / "tick.lock"


def _acquire():
    if LOCK.exists() and time.time() - LOCK.stat().st_mtime < 13 * 60:
        return False  # a scheduled tick is running right now
    LOCK.write_text(str(os.getpid()))
    return True


def main():
    if not _acquire():
        print("a tick holds the lock - retry in a few minutes")
        return
    try:
        res = EV.league_round()
        if not res.get("valid"):
            print("round invalid (budget skip) - next tick retries")
            return
        rl = res["round_log"]
        print(f"第{res['round']}轮 窗口={rl['window'][0]}~{rl['window'][1]} "
              f"市道={EV.REG_CN.get(rl['regime'], rl['regime'])} "
              f"基准={rl['bench_ret'] * 100:+.1f}%")
        print(f"  本轮冠军: {EV.CLAN_CN[res['winner']]} ｜ "
              f"席位易主={res['took_seat']} ｜ {rl['insight']}")
        for c in sorted(rl["clans"], key=lambda x: -x["excess"]):
            print(f"  {EV.CLAN_CN[c['clan']]}: {c['ret'] * 100:+.1f}% "
                  f"(超额{c['excess'] * 100:+.1f}pp 夏普{c['sharpe']:.2f}) "
                  f"+{c['pts']}分")
        print("  积分榜:")
        for n, st in sorted(res["league"].items(), key=lambda kv: -kv[1]["pts"]):
            print(f"    {EV.CLAN_CN[n]}: {st['pts']}分 ({st['rounds']}轮)")
    finally:
        try:
            LOCK.unlink()
        except OSError:
            pass


if __name__ == "__main__":
    main()
