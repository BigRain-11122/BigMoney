# -*- coding: utf-8 -*-
"""R245 closing: CODELY memory line + round report + state + heartbeat (bm-a)."""
import json, time, datetime

NOW = datetime.datetime.now()

# 1) CODELY.md memory line (S4, one pit entry)
mem = ("- [2026-09-26 12:3x] 坑律（bm-a R245·S0 轮首 stash-pop 侧语义反转·E1 首遇自捕）："
       "**git stash push→pull --rebase→stash pop 撞同件内容冲突时 ours/theirs 语义与 rebase 面相反——"
       "stash-pop 面 ours=当前分支（pull 后的 origin 新面）、theirs=stash 里的本地旧面；"
       "「snapshot 家族 take-new 取 origin 侧」在此=checkout --ours（rebase 面同操作取 --theirs）**；"
       "解法=轮首遇共享 runtime 态件脏阻 pull：stash push 单件→pull→pop 撞则按 snapshot 配方 "
       "checkout --ours+add+stash drop（本地面=producer 可再生短命快照，弃本地无损）；"
       "连带=bm-b r245 律：pop/解后必重 add 验 staged diff 防 LF 残留 MM 态。指针=R245 S0 实录（autofill_state.json）"
       "+fleet/README.md §4 时间序\n")
with open('CODELY.md', 'a', encoding='utf-8') as f:
    f.write(mem)

# 2) round report line (S5)
rep = ("2026-09-26 12:3x | R245 | [wm:GREEN py_low_board_clear·red=false·next_pick=claimed(moneyflow IC 待面板)] "
       "S0.5 双扫差集空(79/79 ack 无新令)+决策审核零动作(D-20260926-06~11 执行司均他司·本仓在册例已闭口)；"
       "S1 25/25；S3 闭环=T-73 s3 切片1 CN-REVERSAL-TILT 预注册起草+冻结"
       "(research/CN_REV_TILT_PREREG.md：4 判断格 {REV20,REV60}×{裸,政体倾斜}·V1 13bp+x2/x3 压测·"
       "K=50 nulls 新 seed 基 cn_rev_tilt_p1=20260926 跑前登记·G1'v2/G2v2 共享库判据·"
       "硬界三件套+极端日先验 2015-07/2016-01/2024-02·政体轴=构成件 per s2 v2-fail 实证"
       "(252d REV−MOM 差分前向锁 0.9/0.1)；F-04 MSG-20260926-1211 同轮；GRID-SLEEVE 归 T-78 判负在案不重建)；"
       "S0 stash-pop 冲突首遇(autofill_state·take-new=--ours 侧语义反转·坑律入 CODELY)；"
       "S6 24 腿全绿(周六多 no-op·cutoff 2026-09-24 零新行=中秋 09-25 休市·regime ORANGE d2 shadow·"
       "clock ORANGE_COOL 幂等·b_layer 5222 全门过·paper 6 员锚定 OK·prospect 22/22 drift=0·"
       "t35_export traders=6·AGGR marks no-op·alloc/fund_premium 车道诚实 no-op·token delta=9)；"
       "S7 schtasks 实勘四任务全健康 | 验证: smoke 25/25; S6 24 腿 exit 0 全录; prereg 零结果零编数(§7 占位) | "
       "下轮: ①cn_rev_tilt_p1 seed 基登记 SEED_REGISTRY ②scripts/cn_rev_tilt_p1.py 实现"
       "(P1C 同源装载器·top20 等权 h10·cutoff 探针回填 §2 commit 后跑)③池提交 ④s3 其余模型 prereg 切片"
       "⑤盯 moneyflow/AH refresh 完成面\n")
with open('logs/iteration-loop/round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(rep)

# 3) state-bm-a.json: round_no 244->245
st = json.load(open('state-bm-a.json', encoding='utf-8'))
st['round_no'] = 245
st['did'] = ("R245: S0.5 orders diff=empty (79/79) + decisions zero-action for this repo; S1 smoke 25/25; "
             "S3 closure = T-73 s3 slice-1 CN-REVERSAL-TILT prereg DRAFTED+FROZEN "
             "(research/CN_REV_TILT_PREREG.md, 4 cells, regime axis constitutive per s2 v2-fail, "
             "G1'v2/G2v2 shared-lib, K=50 nulls new seed base cn_rev_tilt_p1=20260926, "
             "F-04 MSG-20260926-1211, ticket progress_r245 with exact resume point); "
             "S0 stash-pop conflict first-encounter resolved take-new (--ours side inversion pit -> CODELY); "
             "S6 24 legs all green (weekend no-ops, cutoff 2026-09-24 Mid-Autumn holiday, "
             "regime ORANGE d2 shadow, b_layer 5222 gates pass, token delta=9); S7 schtasks 4/4 healthy")
st['verdict'] = 'GREEN'
st['next'] = ("T-73 s3 implementation slice: register cn_rev_tilt_p1 seed base in SEED_REGISTRY; "
              "implement scripts/cn_rev_tilt_p1.py (P1C loader reuse, top-20-of-decile equal-weight h10, "
              "tilt rule per prereg S3.3, evidence_cutoff probe->fill S2->commit->run); pool-submit; "
              "s3 remaining model preregs; watch moneyflow rank + AH refresh completion; T-70 window to 10-09")
st['ts'] = '2026-09-26 12:3x'
st['updated_at'] = '2026-09-26 12:3x'
st['current_task'] = 'R245 done: T-73 s3 slice-1 CN-REVERSAL-TILT prereg frozen; next=implementation slice (seed registry + runner + pool submit)'
with open('state-bm-a.json', 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# 4) heartbeat fleet/machines/bm-a.json
import psutil
cpu = psutil.cpu_percent(interval=1.5)
vm = psutil.virtual_memory()
hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
hb['last_seen'] = NOW.strftime('%Y-%m-%d %H:%M:%S')
hb['current_task'] = st['current_task']
hb['cpu_cores'] = psutil.cpu_count(logical=True)
hb['cpu_pct'] = round(cpu, 1)
hb['free_ram_gb'] = round(vm.available / (1024**3), 1)
hb['verdict'] = 'alive'
epoch = int(time.time())
assert isinstance(epoch, int)
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec='seconds')
hb['round_no'] = 245
with open('fleet/machines/bm-a.json', 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
# self-verify epoch is int in the written file
back = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(back['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
print('closing OK: epoch=', back['heartbeat_epoch_utc'], 'clock=', back['clock_read'], 'cpu=', hb['cpu_pct'])
