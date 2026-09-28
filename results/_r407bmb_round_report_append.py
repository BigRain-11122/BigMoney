# -*- coding: utf-8 -*-
"""r407 bm-b: round report line append (S5 ledger, file-face law)."""
import io

PATH = "logs/iteration-loop/round_reports.md"

with io.open(PATH, encoding="utf-8") as f:
    lines = f.readlines()

tail = lines[-1]
new = (
    "2026-09-29T03:58:00+08:00 | r407 bm-b | dept:工程/舰队 (W5-JUDGE 判决链全额收割闭环·假死亡诊断自纠) | "
    "WM-VERDICT: 绿牌 red=false @03:20 lane=healthy; probe 03:45 py_low_with_work_cands=合法在飞供给(本地批 running=astock repull 锁活+板全闭环 open=0+bandit 0+池 ready 1=finalize 在烧非可认领), §四合法 idle 白名单注记; audit v2.4.1 双旗 supply_gap/supply_floor standing(供给在飞=W5 判决烧+astock repull+V3 bm-c runner 未建+W6 prereg bm-a r410 已落不碰) | "
    "did: (1) S0-1 bm-b 锚定+S0 stash-pull-pop 干净 up-to-date(轮首脏=autofill_state 本机运行态); (2) S0.5 双扫 122/122 零未回执+集团 decisions.md 两路径缺位=P-32 诚实 no-op+inbox 零未读; (3) S1 smoke 26/26; (4) S2 双板 job_list 空+票板 0 open(T-116=bm-c 自领 s1 done 不碰; T-114=bm-a WAVE-5 票 judge 收割面归池 lane 本机合法); (5) S3 主闭环=W5-JUDGE 全链收割: finalize pid3108(r406 detach 03:26:33)03:48:39 落地 w5_judge.json——372 judged==survivors/E[FP]=18.6/G2 eligible 0(唯一 G1 pass=gate none|vol none|yang none 1/109 未过 G2)/family PBO 11 族(momentum 0.9143, sentiment 0.9286, composite_rotation 0.8571, patterns 0.1714)/ledger 328615+372=328987 跨波线性/cutoff 2026-09-22 → entry done-flip 双面同步+双 reload 断言(results/_r407bmb_w5_judge_entry_flip.py; r387 五十五批律) → w5_intake.json 零面(W3 形制镜像; prereg sec.6 s4 实际存活数条款; D6/library/纸盘全零面) → 48h CEO 报告钟起算(deadline 2026-10-01 03:48); **假死亡诊断自纠**: 03:44 以直觉路径 results\\w5_judge.json 探活误判 pid3108 死亡无回执(真路径=results/trial_labor_w5/w5_judge.json, JUDGE_FILE 源码常量 trial_labor_w5.py:118), 读代码序(_dump 先于 print)+正路径验活后定谳=finalize 从未死, 22min 静默烧与 W2/W4 25-27min 同构, 零重启零双跑, 坑律八十一批入册 CODELY(收割回执路径必须源码常量解析律+静默长活死亡推断禁律+PS git show > 重定向 UTF-16 转码取证坑); (6) S6 ~36 腿全 rc=0: update_daily 0 新行 cutoff 09-28 盘前+regime ORANGE shadow(hs300<MA200 #10+breadth 0.83)+scorecard derive=合法 stale-takeover(bm-a 心跳 27.7min>20min STALE_MIN; 语义零差 verified 仅 generated/elapsed 漂移; HEAD 版 indent=2 非脚本正典序列化(写者未定谳, r406 会话遗留观察项), 本机 derive 恢复 indent=1 脚本正典)+clock CALL-0928 ORANGE_COOL sleeves4 act0+采集器车道守卫诚实 no-op x11(bm-a x9+bm-c x1+fundamental fresh 18h skip)+astock_daily repull 锁活 no-op+etf_daily cutoff 覆盖+rev_osc 面板 incomplete 等待诚实+minute_feed 09:15 前门+b_layer 全过+live.paper 新 bar 条件链合法跳过(无新 bar)+daily_scorecard stale-takeover derive+REPORT-20260929 faces4 token1+LIVE-20260929 ORANGE cap50%+build_status derive+token L2 0 today+post_review 0 开口负判定=零 P0; (7) S7 自愈三查绿(schtasks Loop 正在运行 pin=2 no-op 04:02+Watchdog 就绪 04:20+claw IN-SYNC)+state 407+心跳 epoch 1790625326 int 自证+orders 二扫 122/122 | "
    "verify: smoke 26/26+finalize 回执四面断言(n_judged 372/n_eligible 0/ledger 328615+372=328987/cutoff 09-22)+池双面 flip 后 reload 断言+intake json 重载断言+scorecard 语义等价 diff=0(python 双向 walk)+S6 逐腿 rc=0 | "
    "下轮: (a) astock repull ~04:30 收口 → rev_osc SIG/BARS 导出解锁(bm-b 双车道); (b) CEO 48h 报告窗 W5 判决面(deadline 2026-10-01 03:48); (c) V3-TOURNAMENT bm-c runner 落地后本机烧判就位; (d) W6 prereg bm-a T-114 在飞不碰; (e) T-116 lane 迁移 s3 wave-1=bm-c 票在飞不碰 | marks/账本/SEED 本轮全 +0(判决面 w5_judge.json+intake 零面=判词落地零注册, ledger 328987 经 finalize 内嵌账本)"
)
lines[-1] = tail.rstrip("\n") + "\n" + new + "\n"
with io.open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lines)
with io.open(PATH, encoding="utf-8") as f:
    check = f.readlines()
assert "r407 bm-b" in check[-1], "append failed"
print("round report appended, total lines:", len(check))
