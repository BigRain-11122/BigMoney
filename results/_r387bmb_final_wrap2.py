# r387 bm-b final wrap v2: heartbeat final touch + round report addendum 3.
import json, os, time, datetime, io

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
p = r"fleet\machines\bm-b.json"
h = json.load(open(p, encoding="utf-8-sig"))
h["last_seen"] = now_iso
h["clock_read"] = now_iso
h["heartbeat_epoch_utc"] = int(time.time())
h["current_task"] = (
    "r387 done: W2-JUDGE full closure (burn 404/404 -> finalize -> "
    "w2_judge.json receipt: E[FP]=20.2 G2 eligible 0 honest zero-reg, "
    "ledger 310810+404=311214 -> entry done-flip shared+lane) + W1-JUDGE "
    "burn 149/149 shard done-flip + W1 judge-finalize detached pid 4084 "
    "in-flight (est 7-17min) -> next round: w1_judge.json harvest + "
    "entry done-flip + W1 intake; 15:30 new-bar dual lanes; CEO 48h "
    "report 09-29 22:45"
)
h["verdict"] = (
    "healthy: smoke 25/25; orders 99/99; S6 33 legs rc=0; storm face fully "
    "resolved in-window (W1/W2 shard status re-assert done shared+lane "
    "with reload assertions per new pitlaw, lane authority re-mirrored); "
    "W2 wave funnel closed honest zero G2 registration; W1 finalize in-"
    "flight pid 4084 behind landed W2 (chain-linearity law honored); "
    "CODELY 3 pitlaws batch-53/54/55 zero-loss reorgs 9,774B"
)
tmp = p + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
os.replace(tmp, p)
h2 = json.load(open(p, encoding="utf-8-sig"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and "T" in h2["clock_read"]

line = (
    f"{now_iso} | round 387 addendum 3 bm-b | dept:工程/舰队 (判决链主闭"
    "环全额收割) | W2 finalize pid 23800 落地 ~14:40（墙钟 27min·cpu "
    "1426s）=w2_judge.json：404 judged·E[FP]=20.2·G2 eligible 0 诚实零注册"
    "（千人试用漏斗 wave-2 判负如实）·family_pbo/descriptive/audit 面齐·"
    "trials_ledger TRIAL_LAB_W2_JUDGE prev 310810+404=311214 跨波线性零"
    "重置·evidence_cutoff 2026-09-22 锁箱 → entry done-flip shared+lane "
    "双面（r387 新坑律执行首例：翻转必双面同步+写后双 reload 断言）"
    "86eb50ea 推 LANDED | W1 finalize 排队条件满足=同窗 detach pid 4084"
    "（log logs/w1_judge_finalize_r387.log·n_trials 快照将含 311214·est "
    "7-17min·entry note 留痕 queue discharged）| verify: 产品 json 解析+"
    "四面断言（n_judged_cells=404/n_eligible_g2=0/ledger total/"
    "evidence_cutoff）+池双面 reload 断言+pid 4084 活度 | 下轮: (a) "
    "w1_judge.json 收割+entry done-flip+W1 intake（D6 绑定门实弹首跑="
    "r366 续作点唯一未探面=checkpoint row join）; (b) 15:30 新 bar 窗双车"
    "道+三件套; (c) CEO 48h 报告 09-29 22:45 | marks/账本/SEED 全+0\n"
)
with io.open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(line)
print("final wrap v2 OK:", now_iso)
