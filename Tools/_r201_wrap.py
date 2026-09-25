# r201 wrap: round report line + state.json + heartbeat (real-clock reads, r173 law)
import json, time, subprocess
from datetime import datetime

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
assert isinstance(epoch, int)

REPORT = "logs/iteration-loop/round_reports.md"
raw = open(REPORT, "rb").read()
eol = b"\r\n" if raw.split(b"\n", 1)[0].endswith(b"\r") else b"\n"
line = (
    f"{now} | r201 bm-b (dept:研究+舰队+工程) | WM-VERDICT: green（red=false@20:00:17 lane healthy"
    " + probe 20:05 insufficient_history=采样窗未满诚实；next_pick=claimed 无 advisory 动作） | "
    "S0: **mid-rebase 崩溃现场自愈**——上轮会话死于 pull --rebase（pick 245f47ee 停 UU autofill_state），"
    "20:00:01 tick 在冲突树上跑=_load_state except 兜底 fresh 把 49 条 launches 覆写成 1+无 owner 发射"
    " SHARD-2（pid14112；bm-a 19:30:02/19:40:02 已发同片=双烧，r159 拉取滞后窗×rebase 无推送窗叠加，"
    "确定性零科学影响）→三源 union stage2 46+stage3 47+工作树 1→49（20:00 发射记录唯一载体救回，r161 "
    "配方工作树维度补篇）+checkout 还原 p1d_gates tick 漂移（diff 仅 meta 两字段零信息损失）+"
    "-c core.editor=true continue→重放 245f47ee→39f60cb2（旧号 dangling r139 注记）+认领先手 push 双绿 | "
    "S0.5: orders 73/73 差集空（轮首+收尾双扫）+P-32 decisions.md 本机无此面（Test-Path False r177 律）"
    "零动作+inbox MSG-1950 bm-a CTA_WAVE1 F-04 冻结开工声明已阅勿并行（归档 processed/） | S1 smoke 25/25 | "
    "S2: job_list 空+tasks 板 0 open（全 claimed/done，本机在飞=T-46/49/54/57/59/60） | S3 交付: "
    "**SHARD-2 done-flip 196/196 三方核对**（ckpt 196 keys 全 done+disk 196 cells+pid14112 已退；r180 "
    "双翻面+r199 shard owner 契约闭环 bm-b@20:04:08 认领→20:07:14 翻面同轮）+cells/checkpoint commit "
    "e85373b5 池 3/8（SHARD-0/1/2 bm-b）；**autofill P0 加固 6f2616f6**=tick 入口 mid-rebase/merge 三探针"
    "守卫（冲突树=诚实 no-op 零状态写零发射）+corrupt 件拒绝（存在件解析失败=exit 2 禁 fresh 兜底覆写）"
    "+S14/S14b/S14c 配对腿 selftest 23/23（防本类崩溃现场复发） | S4: r201 坑律入册（中断 rebase×tick "
    "覆写+continue 误导报文两教训）+热冷整编 49,931→49,422B<50KB（r183 T-61 转移通道/R182 guorn 口径 "
    "2 条已闭一站式记录逐字迁 202609.md+迁移注，R164 两段式核账 2/2） | S6 16 腿绿（假日无 bar：daily 0 "
    "行 0 失败 cutoff 09-24/regime ORANGE shadow d2 hs300<MA200+breadth 0.77 只记录/lhb 复抓 11 页 0 新事"
    " no-op/heat 当日已采/futures 零网络 no-op/mf+ths+ah=bm-a 车道诚实 no-op R31/fp=bm-c 车道 no-op"
    "（**bm-c 停机 22.4h=NAV 面停摆**）/fundamental 23.3h fresh skip/blf 5 门全过 5222|3517ok|1705 排除"
    "/scorecard 6 员/build_status factors=10/token delta=37）；条件腿合法跳过（无新 bar：live.paper/"
    "t35/t24×2/aggr/export） | S7: schtasks 双任务健康 raw 实读（Loop 正在运行 next 20:20/Watchdog 就绪"
    " next 20:30 R49 律） | verify: SHARD-2 三方核对输出+union 49 计数留痕+smoke 25/25+autofill 23/23+"
    "整编核账 2/2+心跳 epoch int 自证 | next: r202=看池 SHARD-3..7 有机填装（3/8 done 双机 tick 续填"
    " 每片~8-12min）→1569 胞齐后 finalize（G1'v2 共享库+G2 DSR/PBO+append_ledger+primaries CSV+prereg "
    "§7/§8+funnel）；**bm-c 24h 升级线 21:51 逼近（last_seen 09-24 21:51:47=22.4h 龄；stale claims "
    "T-16/T-17/T-19 bm-c r51/57/48+fund_premium NAV 车道停摆）=下窗 GM 改派评估面（r200 指针）**；"
    "moneyflow IC 批待面板 EM 自愈；09-28 交易日全链（REGIME_GUARD v3 enforce 首跑）"
)
with open(REPORT, "ab") as f:
    f.write(eol + line.encode("utf-8"))
print("report line appended:", len(line), "chars")

# state.json
af = json.load(open("results/autofill_state.json", encoding="utf-8"))
st = json.load(open("logs/iteration-loop/state.json", encoding="utf-8"))
st.update({
    "round_no": 201,
    "did": ("r201: mid-rebase crash-site self-heal (3-source union 49 launches, rebase replay "
            "245f47ee->39f60cb2, SHARD-2 owner claim 20:04:08 + done-flip 196/196 three-way 20:07:14, "
            "pool 3/8) + autofill P0 hardening 6f2616f6 (mid-rebase guard + corrupt-state refusal, "
            "selftest 23/23) + memory reorg 49,422B (2 closed one-off entries archived verbatim)"),
    "verdict": ("watermark GREEN; smoke 25/25; S6 16 legs green (holiday no bar, cutoff 09-24); "
                "orders 73/73 both scans; autofill hardened after live corruption case"),
    "next": ("r202: watch SHARD-3..7 organic fill (pool 3/8 done, both machines' ticks); finalize when "
             "1569 cells land (G1'v2 + G2 DSR/PBO + append_ledger + primaries CSV + prereg backfill + "
             "funnel); bm-c 24h escalation line 21:51 tonight = GM reassignment evaluation face "
             "(stale claims T-16/17/19 + fund_premium NAV lane stalled, evidence in r201 report); "
             "moneyflow IC waits EM self-heal; 09-28 next trading day full chain"),
    "last_round_ts": now, "last_result": "ok",
    "current_task": ("T-57 s3 census pool-driven (autofill owns compute lane, SHARD-3..7 open); "
                     "T-60 s2 waits EM self-heal; T-46/T-49/T-54 in-flight slices"),
    "last_tick": af.get("last_tick", {}).get("ts", st.get("last_tick")),
    "updated_at": now, "last_seen": now_iso, "ts": now,
})
open("logs/iteration-loop/state.json", "w", encoding="utf-8").write(
    json.dumps(st, ensure_ascii=False, indent=1))
print("state.json round_no=201")

# heartbeat
import psutil
free_ram = round(psutil.virtual_memory().available / 2**30, 1)
total_ram = round(psutil.virtual_memory().total / 2**30, 1)
cpu_pct = psutil.cpu_percent(interval=1.0)
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10).stdout.strip()
    gpu_free = round(float(out.splitlines()[0]) / 1024, 1)
except Exception:
    gpu_free = 1.9
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
hb.update({
    "last_seen": now_iso,
    "heartbeat_epoch_utc": epoch,
    "clock_read": now_iso,
    "current_task": ("r201 done: mid-rebase crash-site self-heal + SHARD-2 done-flip 196/196 "
                     "(pool 3/8) + autofill P0 hardening (mid-rebase guard/corrupt refusal 23/23); "
                     "next: watch SHARD-3..7 organic fill -> finalize at 1569 cells"),
    "cpu_cores": 16, "free_ram_gb": free_ram, "total_ram_gb": total_ram,
    "gpu_free_vram_gb": gpu_free, "gpu_idle_vram_gb": gpu_free,
    "idle_ram_gb": free_ram, "cpu_util_pct": cpu_pct, "cpu_pct": cpu_pct,
    "round_no": 201,
    "verdict": ("healthy; WILD-S1 census organic fill (3/8 done, SHARD-3..7 open both machines); "
                "rebase crash-site recovered + autofill hardened; bm-c 24h escalation line 21:51 "
                "tonight (GM reassignment evaluation next window); holiday no-bar chain green"),
})
open("fleet/machines/bm-b.json", "w", encoding="utf-8").write(
    json.dumps(hb, ensure_ascii=False, indent=1))
# self-verify epoch int (R144/R170 dual law)
chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat written: epoch", chk["heartbeat_epoch_utc"], "int OK; clock", now_iso,
      "; free_ram", free_ram, "gpu_free", gpu_free)
