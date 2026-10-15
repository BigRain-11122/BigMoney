# -*- coding: utf-8 -*-
# r1018 bm-a closeout: round report line (binary append-only, r948+ precedent) + state + heartbeat
import json, time, datetime

REPORT_LINE = (
"2026-10-15T16:10:00+08:00 | r1018 bm-a (dept:research-N1链finalize+席位供给) | "
"WM-VERDICT: insufficient_history (合法态·近收盘采样窗史不足·red=false lane healthy; satengine ALIVE idle queue0 waits W247 freeze chain) | "
"当前活=W246 finalize one-pass 收口+W247 席首发; "
"最近实物=results/perpetual_faces/n1_w246_results.json (ledger 963,335+2,200=965,535 EXACT / merged pool K=539,120 / skill_line 1.1935->1.1935 K-lift +0.0000 in-band / five-key ALL PASS / sixgate ALL PASS / prereg sec7-8 backfilled, commit e06f4ee2a) + fleet/inbox/MSG-20261015-1608-bma-w247-seat.md (origin ls-tree 送达验证 PASS); "
"下个里程碑=W247 prereg derive+五面冻结+点火 (窗≤48h; probe ADMIT 已面世: A 559_501..561_500 hops=0 第九连续 seed-gap / B 544_501..544_700 hops=1 撞注册 W239 A 带 542_501..544_500 staircase band-hop 首现面; seat-first publish 已履行·freezer 义务承接); "
"did: S0-1 孤儿面=0/29; S0 脏树 4M+8?? 全 bm-a 自有 r1017 scratch estate (定向提交纪律·无 rebase 需求 origin==HEAD); "
"S0.5 ORD 首扫+收尾双扫差集 EMPTY + DEC 水位 MATCH ab3f0cc9 零动作; S1 smoke 49/49; S2 job_list EMPTY + idle green (claimable=1=BigHouse 席循环班议程行·非本司面·idle_rounds 已 --worked 清零); "
"S3 satengine ALIVE exit0 + W246 引擎自燃 12/12 毕 15:44 -> sixgate ALL PASS (_w246bma_sixgate_prereg.json) -> finalize one-pass -> fivekeys ALL PASS -> backfill OK -> W247 preflight origin 四查绿 (_r1018bma_w247_preflight.py) -> probe ADMIT (_w247bma_20261015_probe_receipt.json) -> seat MSG 发布+push+origin 送达验证; "
"S6 链 44 legs+live_paper rc0 全绿 16:00:18-16:04:02 (dualrun streak44 连绿 drift=0 / audit 零旗 / WM insufficient_history 合法态 / REPORT+LIVE-2026-10-15 当日幂等再生); "
"S7 四件套: loop pin=8 no-op / watchdog 在位 (S4U XML flip 拒权=LogonType 回归面·缺省 principal 照发 16:06·如实注记) / pre-commit+pre-push 双爪已装; attrition guard scan CLEAN; "
"inbox 幂等归档 2 件陈旧重复 (MSG-0825/0952 r1011 已消费面·同 sha 验证后移除) + MSG-0104 留箱 (致 CEO-Proxy 收卡席·非本机面·POOL.json 写手制不归本机); "
"r1017 轮报告行缺口诚实注记 (其窗内容=三笔提交 7cdd57a29/9cb87f530/650953086 可考·根级文件 r1016 行后直接续 r1018); "
"本地未达 origin commit 数=0 (e06f4ee2a 推送验证+收尾 commit 后复验); 记账预算: 本轮簿记≤5 处合规 (state/心跳/轮报告行=标准收口三件+零额外) | "
"dept:research-N1链+舰队收口 [via bm-a r1018]\n"
)
with open('round_reports-bm-a.md', 'ab') as f:
    f.write(REPORT_LINE.encode('utf-8'))
print('report line appended, bytes:', len(REPORT_LINE.encode('utf-8')))

# --- state update: round_no +1 (1017 -> 1018) + closeout fields ---
s = json.load(open('state-bm-a.json', encoding='utf-8'))
s['round_no'] = 1018
now_iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
s['last_round'] = 1018
s['last_round_at'] = now_iso
s['last_round_closed'] = now_iso
s['now_active'] = 'W246 finalize one-pass closeout + W247 seat-first published (idle, next round: W247 prereg derive + five-face freeze + engine self-burn ignite)'
s['last_artifact'] = 'results/perpetual_faces/n1_w246_results.json (ledger 965,535 EXACT / K=539,120 / five-key ALL PASS) + fleet/inbox/MSG-20261015-1608-bma-w247-seat.md (origin verified)'
s['next_milestone'] = 'W247 prereg derive + five-face freeze + self-burn ignite (window <=48h; probe ADMIT A 559501-561500 hops=0 / B 544501-544700 hops=1; seat published=reserved)'
s['orphan_face'] = 0
s['ts'] = now_iso
json.dump(s, open('state-bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state round_no ->', s['round_no'])

# --- heartbeat update ---
h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
h['last_seen'] = now_iso
h['ts'] = now_iso
h['clock_read'] = now_iso
h['heartbeat_epoch_utc'] = int(time.time())
h['current_task'] = 'W246 finalize closeout + W247 seat published; next W247 prereg derive + freeze'
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['verdict'] = 'green (W246 finalize landed ledger 965535/K=539120 five-key ALL PASS; W247 seat on origin; satengine alive queue0 waits W247 freeze)'
h['did'] = 'r1018: W246 sixgate+finalize+fivekeys+backfill all green (ledger 963,335+2,200=965,535 EXACT / merged K=539,120 / K-lift +0.0000 in-band) + W247 seat-first published (probe ADMIT A 559501-561500 / B 544501-544700 hops=1 W239 band-hop; seed_admit FREE both; origin vacancy held) + S6 44 legs rc0 + inbox 2 stale dups idempotent-archived'
json.dump(h, open('fleet/machines/bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# self-verify epoch is int
h2 = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
assert 'T' in h2['clock_read'], 'clock_read must be T-separated ISO8601 (R262 law)'
print('heartbeat ok: epoch int=', h2['heartbeat_epoch_utc'], 'clock=', h2['clock_read'])
