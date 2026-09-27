# -*- coding: utf-8 -*-
"""r86 bm-c close-out: round report append + state file bump + heartbeat refresh.

House styles preserved: round_reports-bm-c.md = LF no-BOM append;
state-bm-c.json = CRLF rewrite (field-preserving); fleet/machines/bm-c.json
heartbeat: epoch MUST be JSON int (R170/R178), clock_read MUST be
ISO-8601 with T separator (R262). Post-write asserts included.
"""
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")

NOW = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

REPORT_LINE = (
    "2026-09-27T15:14+08:00｜R86｜bm-c watermark verdict=绿（red=false 14:40:03 "
    "lane healthy·probe 14:55:07 rc0 py_low_board_clear 合法白名单：板 0 open·30 票全 "
    "claimed 他人线·job_list 0·W2A=bm-b 数据本地车道 14:20:02 在烧·本机无数据分片）"
    "｜S0 pull --rebase up-to-date（autofill_state 2 行小改 stash-pop 回放·本机看门狗产物）"
    "｜S0.5 orders 96/96 双扫零未回执+决策尾扫=D-02（BigCompute 哨兵）/D-03（BigDomain OSS）"
    "两新行不涉本仓执行司=零动作回执｜S1 smoke 25/25 绿｜S3 板空自主扩展=T-16 车道盘点发现 "
    "P0 数据面事故并轮内全恢复：bm-c 09-27 统一根重建（旧树 K:\\金钱牛马 已删·machine.json "
    "note 载明）丢 machine-local data/fund_premium 整面（NAV 全史 48+dividends+panel "
    "76,025 行 retained 资产）·status 镜像 nav 块陈声称 done 48/48 vs 盘上 0=镜像-盘面分歧"
    "（gate 读盘诚实 fail-closed）→分离恢复链 backfill-nav 48/48 coverage 100% 零熔断"
    "（14:54-15:04·checkpoint 逐件）→backfill-dividends 48/48·17 零分红与 r53 实证一致"
    "→build_premium_panel 重建 76,073 行×1633 td（+48=09-24 新 bar 全量·守卫 48/48·"
    "lag med 1td·gates PASS）→gate nav 腿恢复 100%（snapshot 腿=周末合法缺位·周一 15:30 "
    "S6 自愈）·status 镜像盘上再 derive 分歧闭环｜S4 坑律入册（根迁移/仓重建必同轮盘点机器"
    "本地数据面·律=镜像 done 块须可由盘上事实再 derive）·CODELY 9769→8110B<10KB=十六批"
    "当窗整编（r83/r327bmb/r326bma 三条目外迁归档·行级零丢失·10/10 断言）｜S6 32/32 rc=0"
    "（周日合法 no-op 族+lane-guard 诚实 no-op·live_paper OK·t35v PASS 零例·prospect 22/22"
    "·promotion 0/22·export/scorecard/daily_report/build_status/token_meter 全 rc0·audit "
    "CLEAN flags=0）｜证据=results/_r86bmc_fund_premium_data_loss.py/.json（含 recovery_result "
    "回执）+_r86bmc_codely_archive_16th.py+_r86bmc_s6_chain.ps1+_r86bmc_backfill_nav.log+"
    "_r86bmc_backfill_div.log｜下轮指针：周一 09-28 开市窗=新 bar 全链接力（update_daily→"
    "live.paper REGIME_GUARD v3 enforce→t35v→t24×2→aggr→grid→export→scorecard→daily_report·"
    "链形用周一版参考 results/_r329bmb_s6_chain.ps1+REGIME_GUARD env 腿宿主核对面）+T-91 s3 "
    "自动点火 09:15 SYSTEM-V1+REV-OSC 首队列入场+T-87 astock 首续拉 15:30 后+本车道 snapshot "
    "自愈验收（gate snapshot 腿应过线）；MSG-1428（bm-b→bm-a）留置非本机件。 [via bm-c]\n"
)

STATE_NOTE = (
    "r86: fund_premium machine-local data-face loss DIAGNOSED + FULLY RECOVERED "
    "in-round -- bm-c 09-27 unified-root rebuild dropped gitignored "
    "data/fund_premium/ (old tree K:\\金钱牛马 deleted; NAV history x48 + "
    "dividends + panel 76,025-row retained asset); status mirror nav block "
    "stale-claimed done 48/48 vs disk 0 = mirror-disk divergence (gate reads "
    "disk = honest fail-closed); recovery chain: backfill-nav 48/48 cov 100% "
    "zero-fuse -> backfill-dividends 48/48 (17 zero-div matches r53) -> panel "
    "rebuild 76,073 rows x 1633 td gates PASS (+48 = 09-24 bar x48) -> gate nav "
    "leg restored, snapshot leg weekend-legal absence self-heals Monday 15:30; "
    "pitlaw appended + CODELY 16th-batch in-window archival (8110B < 10KB); "
    "S6 32/32 rc=0; smoke 25/25; orders 96/96; D-02/D-03 zero-action receipts."
)


def cpu_ram():
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_Processor | Measure-Object -Property "
             "LoadPercentage -Average).Average; [math]::Round("
             "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/"
             "1048576,1); [math]::Round((Get-CimInstance "
             "Win32_OperatingSystem).TotalVisibleMemorySize/1048576,1)"],
            capture_output=True, text=True, timeout=60).stdout.strip().split("\n")
        cpu = float(out[0].strip())
        free_ram = float(out[1].strip())
        total_ram = float(out[2].strip())
    except Exception:
        cpu, free_ram, total_ram = 0.0, 0.0, 0.0
    return cpu, free_ram, total_ram


def main():
    # 1) round report append (LF, no BOM, must end with newline before append)
    with io.open(REPORT, "rb") as f:
        rb = f.read()
    assert rb[:3] != b"\xef\xbb\xbf" and b"\r\n" not in rb and rb.endswith(b"\n")
    marker = "｜R86｜bm-c watermark verdict=绿"
    if marker.encode("utf-8") in rb:
        print("report line already appended (idempotent skip)")
    else:
        with io.open(REPORT, "a", encoding="utf-8", newline="\n") as f:
            f.write(REPORT_LINE)

    # 2) state file bump (CRLF host style)
    with io.open(STATE, "r", encoding="utf-8", newline="") as f:
        st = json.load(f)
    st["round_no"] = 86
    st["updated"] = NOW[:16]
    st["note"] = STATE_NOTE
    st["last_round_ts"] = NOW
    with io.open(STATE, "w", encoding="utf-8", newline="\r\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    with io.open(STATE, "rb") as f:
        sb = f.read()
    assert sb[:3] != b"\xef\xbb\xbf" and sb.count(b"\r\n") >= 6

    # 3) heartbeat refresh
    cpu, free_ram, total_ram = cpu_ram()
    with io.open(HB, "r", encoding="utf-8", newline="") as f:
        hb = json.load(f)
    hb["last_seen"] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["clock_read"] = NOW
    hb["current_task"] = (
        "R86 done: fund_premium data-face loss (unified-root rebuild dropped "
        "machine-local panel) diagnosed + fully recovered in-round -- "
        "backfill-nav 48/48 + dividends 48/48 + panel rebuild 76,073 rows "
        "gates PASS + gate nav leg restored (snapshot leg Monday self-heal), "
        "pitlaw + 16th-batch CODELY archival, S6 32/32"
    )
    hb["cpu_util_pct"] = cpu
    hb["free_ram_gb"] = free_ram
    hb["total_ram_gb"] = total_ram
    hb["gpu_free_vram_mb"] = hb.get("gpu_free_vram_mb", 1730)
    hb["verdict"] = (
        "legal idle: board 0 open (30 claimed by other lanes), pool W2A "
        "burning bm-b (data-local, not burnable here), wm red=false probe "
        "14:55:07 py_low_board_clear legal, audit CLEAN 14:54:59, "
        "fund_premium lane recovered 48/48 panel gates PASS"
    )
    with io.open(HB, "w", encoding="utf-8", newline="\r\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    with io.open(HB, "rb") as f:
        hbb = f.read()
    assert hbb[:3] != b"\xef\xbb\xbf" and hbb.count(b"\r\n") >= 100
    with io.open(HB, "r", encoding="utf-8") as f:
        chk = json.load(f)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in chk["clock_read"] and " " not in chk["clock_read"], \
        "clock_read must be T-separated ISO8601"
    assert len(chk["orders_ack"]) == 96
    print("close-out written: report+state+heartbeat; epoch=", EPOCH,
          "cpu=", cpu, "free_ram=", free_ram)


if __name__ == "__main__":
    main()
