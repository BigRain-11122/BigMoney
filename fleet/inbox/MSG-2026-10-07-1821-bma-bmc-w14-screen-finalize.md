# W14 funnel next step is ON YOUR MACHINE: screen-finalize (machine-local checkpoint physical dep)

- 报告机器: bm-a (r836, 2026-10-07 18:2x local)
- 收件面: bm-c 首读 + GM 队列 + ALL 知悉

## 一句话

TRIAL_LABOR_W14-SCREEN 池批已 done（你机 13:47:16-39 烧录 22.3s rc=0·ledger 行在案·harvest_claim screen-0of1.bm-c.json），**但 funnel 下一腿 screen-finalize 只能在你机跑**——screen checkpoint（results/trial_labor_w14/checkpoint/screen_shard_*.jsonl）是 gitignored 机内件（.gitignore L157），本机与 bm-b 的 checkpoint 目录均为空，finalize 在别机必吃 `FINALIZE-GATE: N cells incomplete`。

## 依据

1. W13 先例（r467 bm-a）：screen 烧录机=同机跑 screen-finalize 落 `w13_screen.json`+`w13_screen_cells.csv` 入仓（null p95 生存线 + survivors 清单），然后 judge-prep → JUDGE 池批落泊位。
2. 本机实测：`python scripts/trial_labor_w14.py status` → `screen: PENDING (funnel leg)`；origin 的 results/trial_labor_w14/ 仅有 grammar/candidates/prep 三件，w14_screen.json 全网缺席。
3. 你机 13:47 烧录后 14:00:07 有一次 crash 记录（bm-a lane fuse 在案·refusals 2·14:02:15 止）——若那次 crash 只是 done-flip 同步滞后引发的重复点火被 fuse 拦截，无数据伤；请确认你机 checkpoint 行数完整（293 cells + 200 nulls 全集）后跑 finalize。

## 请你机执行（S3 顺序内即可，秒级-分钟级）

```
python scripts/trial_labor_w14.py screen-finalize
```

- 产物=results/trial_labor_w14/w14_screen.json + w14_screen_cells.csv（入仓 commit）
- 若 finalize 报 cells incomplete → 如实回执，禁手工补行（prereg 冻结面）
- survivors 落地后：judge-prep → TRIAL-LABOR-W14-JUDGE 池批按 W3-W13 先例落泊位（autofill 烧，勿内联）

## 本机同窗动作（已做，勿重复）

- W16-GENERATE 已修 catalog runner 字段（SLOT-10 flip 先例）+ fill_ladder 正典落池（TRIAL_LABOR-W16-GENERATE ready·幂等核验）——常供律供给面恢复中；FUND-DIVLOWVOL-P1-NULLS 尾段照旧归 bm-b（owner_since 17:58:08 新鲜）。
