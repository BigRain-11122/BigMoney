"""r159 bm-c closing bookkeeping: round report line + state writeback + heartbeat.
Heartbeat contract: epoch_utc must be JSON int (R170/R178), clock_read ISO8601
with T separator (R262). Self-verify via json.loads after write.
"""
import json
import time
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone(timedelta(hours=8)))
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

REPORT = (
    "2026-09-28T" + now.strftime("%H:%M:%S") + "+08:00 | r159 | dept:舰队 绿维护轮+C族接管延续: "
    "WM first-line verdict: 绿（probe 11:21:26 py_low_board_clear 合法 idle〔板 0 open+池 2 ready 全 bmb 燃=census W2B+W4-GENERATE+waiting 全 bmb RAM r354 门=zero bm-c-claimable 共识窗延续 r147 起〕；audit v2.3 11:21 CLEAN flags=[] py 0.1% pool-supply-gap 如实）"
    "| did: S0-1 bm-c 锚定→S0 fetch origin 零新提交（pull --rebase 被 autofill_state.bm-c.json 活写面拒=不 stash 不 reset〔r149 毒方律〕·rev-list HEAD..origin=0 实证 up-to-date=pull 等效 no-op）"
    "→S0.5 双扫: orders 99/99 零未回执（S7 复扫同）+decisions 审核步=09-28 批 D-20260928-02/D-03② 回执已闭实读确认〔本机 r154 F-20260928-04 在册·autofill mid-op guard rebase-merge/MERGE_HEAD 三标记探针在树复核 True+watchdog 零 git 写面勘定〕+D-03① 车道化 bma r372-r390 分批推进中勿双头+C-02 席3 意见 F-20260928-01+防漏收指针 F-02 在册=零新义务"
    "→S1 smoke 25/25→S2 双板零开〔98 票 0 open·job_list 0〕"
    "→S3: TRIAL W5 no-draft 裁定延续〔扩容律水位 fail：bmb 双批在燃 RAM 串行〕+W4-GENERATE watch〔w4_candidates 未落地·trial_labor_w4 目录仅 grammar 面 40KB·owner bmb 10:33:46 认领在先〕+T-19 余面=G6 live-run proof 等 15:30 后新 bar〔compose 已接线 live.paper 单点·remaining none post-G6〕+bma 静默 78min 延续〔hb 10:00:06·MSG-1042 预案维持·采集腿接管评估归首个 15:35+ 健康轮·bma 15:35 前复活=自动作废〕"
    "→S6 全 30 腿 rc=0+3 腿 no-new-bar 按门跳（33 面）: audit CLEAN+WM probe+daily 0-new〔pre-15:30·cutoff 09-24〕+regime ORANGE shadow〔hs300<MA200 #10·breadth 0.77〕+scorecard 6/28/7+clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0+lhb 亲跑 quarter 5209 行 0 新事件〔下次披露今晚≥17:00〕+13 外车道守卫腿诚实 no-op〔bma×8+bmb×3+sysv1+alloc〕+fund_premium pre-15:30 no-op〔本机车道首火 15:35 轮〕+fundamental 1.7h fresh skip+blayer gates all_pass〔5222 码〕+t24promo 0/22 NOT-ELIGIBLE 合法+aggr/grid at-cutoff 幂等 no-op+**C 族 stale-takeover derive 三面〔bma hb 陈 82min>O-2100 s2.4：t35_export 2026-09-24 面 18 持仓 equity ¥5,996,645+daily_scorecard 6 员+build_status json/js〕**+daily_report REPORT-2026-09-28 faces=4 token=1+token_meter delta=0"
    "→本轮一瑕疵如实: S6 批脚本拼接双循环（replace new_string 末尾粘新循环头+原循环头仍在=前三腿各双跑一次·幂等腿无污染〔audit/watermark 本机追加面+daily no-op〕·stdout 双行当场暴露=验证网自纠）账面如实注记不入热层"
    "→post_review 3388 行复核〔NO 11 全 YES 翻绿·unresolved=0·new-after-flip 0·latest 10:01:35〕零未决红"
    "→S7: pin=5 :X5 no-op〔Next 11:25 尾 :X5=针位符〕+watchdog Ready 11:40+claw content-identical OK+orders 第二扫 99 零新增+inbox 0 未读+state 159+心跳 epoch int 自证"
    "| 证据: S6 各腿 stdout rc=0 全录〔results/_r159bmc_s6_chain.json〕+bma hb 龄实算 78-82min+schtasks 双查+claw 比对脚本+post_review groupby 验"
    "| 下轮: r160=5x HANDOVER 核对轮+15:30 后新 bar 全链接力〔fund_premium 本机车道首火→live.paper→t35v→t24paper→aggr→grid→export→scorecard→daily_report〕+bma 静默过 15:40 则 MSG-1042 采集腿接管〔8 腿〕+census W2B finalize ~16:00 判官族 flips 归 bmb+W4 harvest 归 landed-marker r244+V2-P1 bmb RAM 窗 watch〔48h 时钟 09-29 22:45〕+CODELY 9,752B 零 append 维持"
)

with open(r"logs\iteration-loop\round_reports-bm-c.md", "a", encoding="utf-8") as f:
    f.write("\n" + REPORT + "\n")

state = {
    "machine_id": "bm-c",
    "round_no": 159,
    "updated": ts,
    "note": ("r159: green-maintenance (board 0 open, pool 2 ready all bmb-burn census W2B+W4-GENERATE, "
             "zero bm-c-claimable consensus r147-cont) + bma silence 78min watch (hb 10:00:06, MSG-1042 plan holds "
             "till 15:35+ healthy round) + C-family stale-takeover derive x3 (t35_export/daily_scorecard/build_status, "
             "O-2100 s2.4) + S6 30 legs rc=0 + 3 no-new-bar skips + smoke 25/25 + orders 99/99 double-scan + "
             "decisions D-02/D-03 receipts confirmed closed (F-20260928-04 r154 in-tree re-verified) + "
             "W4 generate watch (grammar only, candidates not landed, owner bmb) + T-19 remaining=G6 awaits 15:30 bar"),
    "last_round_ts": ts,
    "did": ("S0-1 anchor bm-c -> S0 fetch zero-new (pull refused by autofill live-write face, r149 poison-path avoided, "
            "rev-list 0) -> S0.5 orders 99/99 double-scan zero unacked + decisions review (D-02/D-03 closed receipts "
            "re-verified in-tree, C-02 seat-3 F-20260928-01/02 on file, zero new duty) -> S1 smoke 25/25 -> S2 both boards "
            "zero open -> S3 TRIAL W5 no-draft continuation + W4 watch + T-19 G6 watch + bma silence 78min watch -> "
            "S6 30 legs rc=0 + 3 gated skips (33 faces) incl. C-family stale-takeover derive x3 @ bma stale 82min -> "
            "post_review 3388 rows zero open red -> S7 pin=5 no-op + watchdog Ready + claw IDENTICAL + state 159 + "
            "heartbeat epoch-int self-verified"),
    "verify": ("S6 all legs stdout rc=0 logged in results/_r159bmc_s6_chain.json + WM probe 11:21:26 py_low_board_clear "
               "(legal idle: board 0 open + bandit 0 + pool 2 ready all bmb) + audit CLEAN flags=[] + smoke 25/25 + "
               "orders 99/99 double-scan + inbox 0 + claw IDENTICAL + Loop pin=5 (:X5) + watchdog Ready 11:40 + "
               "post_review unresolved=0 new-after-flip=0 + CODELY hot 9,752B zero-append maintained + "
               "S6-batch double-loop defect honestly disclosed (pre-3 legs double-ran, idempotent no-pollution)"),
    "next": ("r160 = 5x HANDOVER check round + post-15:30 new-bar full chain relay (fund_premium own-lane first-fire -> "
             "live.paper -> t35v -> t24paper -> aggr -> grid -> export -> scorecard -> daily_report) + bma silent past "
             "15:40 = MSG-1042 collector takeover (8 legs) + census W2B finalize ~16:00 judge flips (bmb) + "
             "W4 harvest on landed-marker r244 + V2-P1 48h clock 09-29 22:45 + CODELY 9,752B zero append"),
    "last_round_at": ts,
    "current_task": "r159 closed: green-maintenance + C-family takeover derive x3; next = r160 5x HANDOVER + 15:30 relay",
    "updated_at": now.strftime("%Y-%m-%d %H:%M:%S") + "+08:00",
    "last_round": "2026-09-28T10:51:49+08:00",
    "round": 159,
    "loop_round": 159,
    "ts": now.strftime("%Y-%m-%d %H:%M:%S"),
}
with open(r"state-bm-c.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

# heartbeat: merge into existing file, keep orders_ack intact
hb = json.load(open(r"fleet\machines\bm-c.json", encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["round_no"] = 159
hb["current_task"] = "green-maintenance r159 done (S6 30 legs rc=0 + C-family stale-takeover derive x3 @ bma silent 82min; zero bm-c-claimable r147-cont; W4/T-95/V2-P1 all watch)"
hb["verdict"] = ("green-maintenance (S6 33 faces rc=0; board 0 open; pool 2 ready all bmb-burn census+W4; "
                 "zero bm-c-claimable consensus r147-cont; bma silent 78min MSG-1042 plan holds till 15:35)")
hb["prod_lanes"] = ("BigMoney-compute-node: autofill pool BelowNormal (zero bmc-claimable since r147; W2B census + "
                    "W4-GENERATE owner=bmb) | S6 lane owner: update_fund_premium snapshot (T-16, Mon >=15:30 first-fire "
                    "armed for 15:35 round) | C-family single-writer faces covered via stale-takeover this window "
                    "(host=bm-a silent 78min, O-2100 s2.4) | MiniGame image main line in-service (ComfyUI RTX3070 16GB, "
                    "O-0913 ruling) | cloud antenna U218 (TJGenerators/cloudF-queue, bm-c only)")
import psutil
hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=1), 1)
hb["free_ram_gb"] = round(psutil.virtual_memory().available / 1024**3, 1)
hb["idle_ram_gb"] = hb["free_ram_gb"]
hb["cpu_pct"] = hb["cpu_util_pct"]
try:
    import subprocess
    g = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=15)
    hb["gpu_free_vram_mb"] = int(g.stdout.strip().splitlines()[0])
except Exception:
    pass
hb["gpu_free_vram_mib"] = hb.get("gpu_free_vram_mb")
hb["gpu_idle_vram_mb"] = hb.get("gpu_free_vram_mb")
hb["updated"] = ts
hb["updated_at"] = now.strftime("%Y-%m-%d %H:%M:%S") + "+08:00"
hb["last_round_ts"] = ts
with open(r"fleet\machines\bm-c.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-verify
chk = json.load(open(r"fleet\machines\bm-c.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock_read must be T-separated"
print("bookkeeping OK: state round_no=%d hb epoch=%d clock=%s cpu=%s%% ram_free=%sGB gpu_free=%sMB" % (
    state["round_no"], chk["heartbeat_epoch_utc"], chk["clock_read"], chk["cpu_util_pct"],
    chk["free_ram_gb"], chk.get("gpu_free_vram_mb")))
