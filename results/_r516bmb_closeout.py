"""r516 bm-b closeout: state bump + heartbeat + round report + CODELY lesson."""
import json
import time

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# --- state.json (round 514 -> 516, r515 crashed pre-closeout, healed) ---
state = {
    "machine_id": "bm-b",
    "round_no": 516,
    "note": ("r516: W16 FINALIZE landed (SIXTH engine wave, bm-b 4th own wave: "
             "K=33,120 merged mu -0.09193 sigma 0.24470 se_mu 0.001345, "
             "skill_line_v2 @397,548 1.1488->1.1506 K-lift +0.0018, ledger "
             "397,548+2,200=399,748 in science_gates.ledger, prereg S5 4/4 "
             "PASS + S7/S8 backfill, two-state selftest green). r515 crashed "
             "post-commit pre-closeout (911aa5a34 W16 FREEZE landed, "
             "state/heartbeat/report never written) -- tail adopted+healed by "
             "r516: derive-fix (wave-set from WAVE_CONFIGS registry, N1 gap "
             "wave 15 held by N2) compile+selftest PASS; round_no jumps "
             "514->516 (515 consumed by crashed session's commit). S0: 2x "
             "surgical onto moved origin (9c57353e55 onto 1c34788cf; "
             "057ccc7fdd onto 66b12b264) + inbox-move fixup 38f2e3eb7. "
             "MSG-175x berth-holder position (293 candidates = quarantine "
             "pending GM) + MSG-176x ledger superset verification. S6 37 legs "
             "rc0 (dualrun 5/3, holiday no-ops, host-guard skips). Engine "
             "alive idle queue 0 (56 ledger rows superset-verified)."),
    "last_round_at": NOW,
    "last_round_ts": NOW,
    "ts": NOW,
    "updated": NOW,
    "updated_at": NOW,
    "last_decisions_sha":
        "753F99E81A27DB3E1B4F2C76CD991CA50D52B80AA7FAA63D6412CC2DA1F5FB01",
    "last_decisions_at": "2026-10-01T15:44:00+08:00",
}
with open("state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)
print("state.json: round_no 516")

# --- heartbeat fleet/machines/bm-b.json ---
with open("fleet/machines/bm-b.json", encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "last_seen": NOW,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW,
    "current_task": ("W16 finalize landed (K=33,120, ledger 399,748, S5 4/4 "
                     "PASS); r515 crashed-tail healed; next: observe bm-c W17 "
                     "sovereignty + GM ruling on W14/N2-W15, bm-b next own "
                     "wave = W19"),
    "round_no": 516,
    "verdict": ("W16 judgment face landed same round (K-lift +0.0018, se_mu "
                "0.001345 narrowed); standing WM-red = r513-family rotation "
                "gap (GM waiver O-1612), root-cure shipped by bm-a r528 "
                "claim-lock fix + this finalize; fresh probe cands EMPTY"),
})
with open("fleet/machines/bm-b.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
assert isinstance(hb["heartbeat_epoch_utc"], int)
print("heartbeat: epoch int OK")

# --- round report line ---
line = (
    f"\n{NOW} | r516 bm-b | dept:研究/工程 | [watermark verdict: RED(standing "
    "r513-family rotation-gap, GM waiver O-1612)——本窗根治面双落：bm-a r528 "
    "WM claim-lock fix（T-141 open+claimed 形状从 work-cands 排除·chronic "
    "false-red 根治）+ 本轮 W16 finalize 落账；18:04 新 probe=insufficient_history"
    "（窗重置 n=1）·cands 空·bandit 0·local_batch 无（p1d gates probe 17:54-18:00 "
    "已毕 pass:true）——红牌族预期下窗翻绿观察] | 本轮主产出（实物）：(1) **W16 "
    "finalize 判决面落地**（本机第四枚自有引擎波·第六枚机队引擎波·轮值律 W16=bm-b）："
    "12/12 引擎自驱烧录（60s cadence·pool telemetry multicore_burn 逐片行）→r310 "
    "origin 完备性门 12/12 →FAIL-CLOSED 合并 K=**33,120**（canon 120+W1 2,200+W2..W14 "
    "13×2,200+W16 2,200=§0 预期逐位）；merged mu **−0.09193**·sigma **0.24470**·"
    "se_mu **0.001345**（W14 0.00139→收窄）；skill_line_v2 @n_eff 397,548："
    "1.1488→**1.1506**（K-lift **+0.0018**）；账本 **397,548+2,200=399,748**"
    "（append_ledger dict 持久化 science_gates.ledger=r509 零幻影律·voids_applied="
    "LOWAMP-P1）；prereg §5 四项预测 **4/4 PASS**（mu 漂移 0.00456<0.02/sigma +0.12%"
    "<±10%/A p95 0.3306 vs 0.3126 Δ+0.018<0.05/K-lift +0.0018≤0.02）+§7/§8 机械回填"
    "（r307 两态 selftest 绿）(2) **r515 猝死半成品收编**（r471 律）：perpetual_faces_n1.py "
    "波集 derive 修正（range(2,WAVE)→WAVE_CONFIGS 键集 derive·N1 波号 15 空位=N2-W15 "
    "并行持有·r511 律变体）compile+selftest 全绿后当窗采纳并实弹=finalize 跑通本体"
    " (3) **S0 三段外科**：surgical 9c57353e55 onto 1c34788cf（28 payload 逐件 origin-"
    "overlap 断言+push 重试环）→push 被拒（bm-a r528 窗）→rebroadcast 057ccc7fdd "
    "onto 66b12b264（变更集交集=∅ 机证后重建）→inbox-move fixup 38f2e3eb7 | "
    "验证：S1 smoke 47/47；S6 37 腿全 rc0（reconcile ZERO-DRIFT streak 5/3=flip 门"
    "数据续累积〔GM 决策面〕·国庆假日诚实 no-op 面·host-guard 诚实 skip 8 面·"
    "REPORT/LIVE 当日再生）；orders 轮首+S7 双扫 139/139 EMPTY；D-19 753F99E8 "
    "MATCH-unchanged（temp partial clone·python raw-bytes·大小写归一）；attrition "
    "CLEAN（4 台账·1 healed 历史缩行照录）；post_review 0 ✗；引擎活检查 rc0"
    "（idle·56 shards·queue 0·ledger 键集超集断言 PASS 对 r513 基线）；三任务健康"
    "（Loop 正在运行 pin=2 no-op/Watchdog 就绪/SatEngine 就绪·schtasks 面查证 R49 "
    "律）；claw MATCH；月度三件=r488 已跑不双跑·季度审视=Q4 槽位已 discharge | "
    "坑律（已入 CODELY 一条）：temp-index 外科 payload 删除 staging 坑（MSG move "
    "删除未入树→inbox/processed 双拷贝·git rm fixup 治愈·payload 计数断言+post-tree "
    "ls-tree 删除断言为后续正法） | inbox：MSG-173x（bm-a W14-GENERATE 披露+裁定请求"
    "）→泊位持有机立场回执 MSG-175x（293 候选=方案 a 隔离待 GM·W14 线零触碰承诺）；"
    "MSG-174x（bm-c r526 扫树治愈回执）→ledger 完整性自验回执 MSG-176x（键集超集 "
    "PASS·活体权威副本已推 origin）双件已处理入 processed | executive 三行实况："
    "当前活=W16 finalize 已落账·引擎 idle 队空（轮值下一枚 N1 波=W17=bm-c 槽位）·"
    "等待面=GM 双裁（W14 线/N2-W15/LOWAMP-P2）；最近实物=results/perpetual_faces/"
    "n1_w16_results.json（K=33,120·账本 399,748）@18:0x+research/PERPETUAL_N1_W16_"
    "PREREG.md §7/§8 回填+origin 38f2e3eb7；下个里程碑=bm-c W17 冻结点火（轮值法"
    "节奏·窗≤48h）→bm-b 下一自有位 W19 | 下轮指针：(1) W17=bm-c 主权观察（本机零"
    "冻结动作·fetch-first 查法典 §4 表尾）(2) bm-b 下一自有位=W19（轮值律·W17/W18 "
    "落地后展行）(3) GM 双裁观察：W14 293 候选存量/N2-W15 重带裁定（31_000 系撞 "
    "N1-W8 A 带）/LOWAMP-P2 E1 (4) WM 红牌翻绿观察（claim-lock fix 后首完整窗）"
    " (5) MSG-175x/176x 对侧消费观察 | 本地未达 origin commit 数=0（收轮 push+fetch"
    "+自证） [via bm-b]\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)
print("round report: appended")

# --- CODELY.md lesson (memory-entry gate: new pitfall, one thing, <1.5KB) ---
lesson = (
    "- [2026-10-01 18:1x r516 bm-b] temp-index 外科 payload 删除 staging 坑"
    "（inbox move 撞实弹）：surgical rebroadcast 以 git diff --name-only 取 payload"
    "＋GIT_INDEX_FILE git add 暂存工作树已删路径——删除面未入新树（057ccc7fdd 的 "
    "ls-tree 实证 inbox/MSG-173x/174x 双拷贝共存）且 payload 计数 16≠真变更 17"
    "（drop 点未定谳：diff 面缺行 vs add 面 skip 均未排除）；治愈=git rm 定向 fixup"
    " commit（38f2e3eb7·宣称-实况一致律自证删除集）。How to apply：一切 surgical/"
    "commit-tree 载运「文件移动/删除」的 payload，写树后必 ls-tree <tree> <被删路径>"
    " 断言空集+payload 计数对 diff 行数断言，缺一=fixup 前禁宣称 move 完成；同族="
    "r525 删除归属律的 staging 面变体。\n")
with open("CODELY.md", "a", encoding="utf-8") as f:
    f.write(lesson)
print("CODELY.md: lesson appended")
