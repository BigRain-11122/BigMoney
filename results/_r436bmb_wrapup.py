"""r436 bm-b wrap-up writes: round report line, state.json, heartbeat, CODELY.md receipt."""
import json
import time

report_line = (
    "2026-09-29T18:16:00+08:00 | r436 | dept:策略+研究 joint (W9 判决落地收官+波全链收口) | "
    "WM-VERDICT: 绿 red=false @18:00 probe (py_low_board_clear 合法=板清 120/120 done·零在飞判决批) | "
    "当前活: W9 十波全链收口完成·板清零在飞·W10 起草为下轮常供线主活 | "
    "最近实物: results/trial_labor_w9/w9_judge.json (243/243 fail @17:47:46) + w9_intake.json lawful-zero + "
    "docs/trial_labor/CEO-REPORT-WAVE9-20260929.md (18:1x·48h 窗内提前~46.6h) + prereg §7/§8 回填 + attrition 两行 | "
    "下个里程碑: W10 prereg 起草 (bm-c MOM gate 泊位候选 MSG-1705 按序采用·r437 起·窗≤48h) | "
    "did: (1) S0 pid20568 收官实证 (17:47:46 finalize exit 0·ckpt 243/243·零死手) -> w9_judge.json 落地 commit 后 push 撞 17-UU "
    "(bm-a r437-439+bm-c r230 同窗) -> 分类器 9 分类+8 UNKNOWN 手工定性 (daily_report/live_usage 四件=当日幂等再生快画面·"
    "scorecard 双件=per-round derive·15 件全快照类) -> 探针实证 origin 17:35-17:36 全面更新鲜 vs 本机 17:30-17:34 -> "
    "_r436bmb_resolve.py 正典解 (15 件取 origin 整字节+compute_audit history union 202 行零丢失+regime history 两侧全同取 origin) "
    "-> rebase 4/4 continue -> push PASS; (2) S0.5 令差集 122/122 双扫零新令·decisions.md 路径不在本机零动作; S1 smoke 26/26; "
    "(3) S3 W9 波全链收口: intake lawful-zero (n_eligible=0·零 TRIAL-* 袖盘·零注册行) + attrition 两行 (SCREEN 17:10:14+JUDGE 17:47:46·"
    "retro_fill=false·gate_attrition.json+bm-b face) + prereg §7/§8 一次定稿回填 (§5 对账 4/5 命中 1 MISS 如实=distinct 2515 低于带·"
    "AMP×TSTATE 分解=narrow 单面拖累 deep 9.41% vs 基线 16.60%·wide 中性 18.34%·AMP 反富集=narrow 7.17%<wide 10.69%<none 11.02%) + "
    "CEO-REPORT-WAVE9 同轮落地 (48h 钟起 17:47:46·窗止 10-01 17:47:46) + 池条目翻 done (120/120 板清) + 波级票 T-121 done 带 result_ref; "
    "(4) S6 链 36 腿 rc=0: dualrun ZERO-DRIFT streak 22/3·compute_audit FLAG supply_floor 如实 (ready 0<3=W9 收官板清过渡态·"
    "W10 起草=供给响应)·py_watermark py_low_board_clear·update_daily 0 新行=09-29 bar 源端未出诚实 no-op (cutoff 09-28)·"
    "update_lhb rc=3 源改史旗标如实 (守卫隔离零改写·bm-b 首观测·r229 bm-c 同型先例)·scorecard/daily_scorecard/dashboard "
    "stale-takeover 合法 (bm-a 心跳>20min·O-2100 s2.4)·live.paper/t35/t24 无新 bar 幂等·REPORT+LIVE 09-29 regen; "
    "(5) S7 三自愈绿 (loop pin=2 no-op·watchdog 就绪·claw 内容匹配) | "
    "verify: judge 断言全过 (n_judged=243·ledger 344,031 活读·pit-112 块嵌入) + intake rc=0 + attrition 拒重复行断言 + "
    "pool 120/120 实读 + resolver JSON 全件 loads 过 + smoke 26/26 | "
    "next: W10 prereg 起草 (bm-c MOM gate 泊位 MSG-1705 按序采用·TRIAL_LABOR_LAW 常供律·r437 主活) [via bm-b]"
)

with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(report_line + "\n")
print("round report: appended r436 line")

# state.json
st = json.load(open("state.json", encoding="utf-8"))
assert st["round_no"] == 435
st["round_no"] = 436
st["note"] = ("r436: W9 WAVE FULL CLOSURE -- judge 243/243 fail 0-G2-eligible (17:47:46), intake lawful-zero, "
              "prereg sec.7/8 backfilled, CEO-REPORT-WAVE9 landed same round, attrition 2 rows, pool 120/120 done, "
              "T-121 done; 17-UU rebase canon-resolved (origin fresher uniform, audit union 202)")
st["last_round_at"] = "2026-09-29 18:16:00"
st["last_round_ts"] = "2026-09-29 18:16:00"
st["ts"] = "2026-09-29 18:16:00"
st["updated"] = "r436 W9 wave closed end-to-end; next standing line = W10 prereg draft (bm-c MOM gate berth)"
json.dump(st, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json: round_no ->", st["round_no"])

# heartbeat
epoch = int(time.time())
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = "2026-09-29T18:16:00+08:00"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = "2026-09-29T18:16:00+08:00"
hb["current_task"] = ("W9 wave closed end-to-end (judge 243/243 fail 0-G2 17:47:46 + intake lawful-zero + "
                      "CEO-REPORT-WAVE9 + pool 120/120 done); next standing line = W10 prereg draft (bm-c MOM gate berth)")
hb["round_no"] = 436
hb["round"] = 436
hb["loop_round"] = 436
hb["verdict"] = "green: W9 wave closed, board clear 120/120, all lanes healthy"
assert isinstance(hb["heartbeat_epoch_utc"], int)
json.dump(hb, open("fleet/machines/bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
back = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int)
print("heartbeat: epoch int", back["heartbeat_epoch_utc"], "| round", back["round_no"])

# CODELY.md one-line receipt (prereg sec.8 mandate: 轮报告+CODELY.md 行级追加同轮)
receipt = ("- [2026-09-29 18:16 r436 bm-b] W9 波全链收口回执：judge 243/243 fail·0 G2·E[FP]=12.15（17:47:46 落地·ledger 344,031），"
           "intake lawful-zero，prereg §7/§8 一次定稿回填，attrition 两行，CEO 报告 docs/trial_labor/CEO-REPORT-WAVE9-20260929.md 同轮窗内落地，"
           "池 120/120 done 板清，T-121 done；研究事实=AMP 反富集（narrow 7.17%<wide 10.69%<none 11.02%·narrow 单面拖累 AMP×TSTATE 分解 deep 9.41% vs 基线 16.60%）"
           "=W10 供给输入（指针=prereg §7/§8+gate_attrition 尾两行，本条不复述）。")
with open("CODELY.md", "a", encoding="utf-8") as f:
    f.write(receipt + "\n")
print("CODELY.md: receipt line appended")
