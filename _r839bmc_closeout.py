# -*- coding: utf-8 -*-
# r839 bm-c S7: state round_no increment + heartbeat + round report line + d19 orders watermark
import json, time, hashlib, subprocess, datetime

now = datetime.datetime.now()
iso = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())
rnd = 839

VERDICT = ('r839 bm-c: pit-protocol.md sub-split ceremony discharged (31,433B>30,720B r859 debt) -- '
           'r529/r583/r645 state-ledger family 3 entries 2,034B verbatim -> pit-protocol-lane.md, '
           'header enforcement-face rerouted to lane (post_main 29,472B identity 31433-2034+73), '
           'CODELY.md ptr row + registry movement row + receipt _r839bmc_pit_protocol_lanesplit.json; '
           'S4 text-mode newline-translation law row appended (main 30,510B); '
           'S6 39 legs rc0 (dualrun ZERO-DRIFT streak 13; supply_gap flag = fleet-level W17-drain/W18-draft wait, yielded non-bmc lanes); '
           'py_low_with_work_cands = legal idle whitelist (board 0/0, bandit 0, pool 4 ready all claimed 0 unclaimed, satengine queue empty); '
           'S7 quartet green + attrition CLEAN + smoke 49/49 + orders/d19 watermarks updated; '
           'no new bar (Sat), no fleet orders unacked (O-1945 last acked r838), no pause flag (O-2006 resume broadcast = zero action for bm-c)')

NEXT_PTR = ('r840: (1) D-05 write leg first-of-day 10-11 00:00; (2) W17-JUDGE drain watch + W18 berth gate recheck (drain-gated); '
            '(3) T-182 co-sign awaiting bm-a P0 runner output (10-16 window); (4) 10-14 regime verify window v1.1 re-cut; '
            '(5) CODELY.md main 30,510B headroom 210B -- next append likely re-triggers mini-split cycle (designed)')
NEXT_MILESTONE = 'D-05 write leg (10-11 00:00 first) + T-182 co-sign (10-16) + W17-JUDGE drain observation'
ARTIFACT = 'results/_r839bmc_pit_protocol_lanesplit.json (byte identity 31433-2034+73=29472) + pit-protocol.md 29,472B + CODELY.md r839 law row'

# ---- state file ----
sp = 'state-bm-c.json'
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = rnd
st['round_no_label'] = 'r839'
st['last_round'] = rnd
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['last_round_closed'] = iso
st['clock_read'] = iso
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
st['last_seen'] = iso
st['last_seen_at'] = iso
st['verdict'] = VERDICT
st['last_round_summary'] = VERDICT
st['next'] = NEXT_PTR
st['next_pointer'] = NEXT_PTR
st['next_milestone'] = NEXT_MILESTONE
st['last_artifact'] = ARTIFACT
st['recent_artifact'] = ARTIFACT
st['latest_artifact'] = ARTIFACT
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['last_run_at'] = iso
st['last_action'] = 'pit-protocol sub-split ceremony + S6 39 legs + S7 closeout'

# d19/orders watermarks (orders.md hash changed this round)
blob = subprocess.run(['git', '-C', 'K:/Fluxgroup/FluxGroup', 'show', 'origin/main:docs/orders.md'], capture_output=True).stdout
st['last_orders_sha'] = hashlib.sha256(blob).hexdigest()
st['last_orders_read_at'] = iso
st['last_orders_at'] = iso
st['last_orders_sha_method'] = 'sha256-git-show-origin-main-blob'
# decisions hash unchanged (verified equal this round) -- refresh read time only
blob2 = subprocess.run(['git', '-C', 'K:/Fluxgroup/FluxGroup', 'show', 'origin/main:docs/decisions.md'], capture_output=True).stdout
st['last_decisions_sha'] = hashlib.sha256(blob2).hexdigest()
st['last_decisions_read_at'] = iso

json.dump(st, open(sp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding='utf-8'))
assert isinstance(chk['round_no'], int) and chk['round_no'] == rnd
print('state-bm-c.json -> r%d ok' % rnd)

# ---- heartbeat ----
hp = 'fleet/machines/bm-c.json'
hb = json.load(open(hp, encoding='utf-8'))
hb['last_seen'] = iso
hb['last_seen_at'] = iso
hb['ts'] = iso
hb['clock_read'] = iso
hb['heartbeat_epoch_utc'] = epoch
hb['verdict'] = VERDICT
hb['next'] = NEXT_PTR
hb['next_milestone'] = NEXT_MILESTONE
hb['last_artifact'] = ARTIFACT
hb['recent_artifact'] = ARTIFACT
hb['latest_artifact'] = ARTIFACT
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['activity_now'] = 'r839 closeout: pit-protocol sub-split ceremony + S6/S7'
hb['current_task'] = 'r839 pit-protocol sub-split ceremony + S6 chain + S7 closeout'
hb['current_task_at'] = iso
hb['current_task_ts'] = iso
hb['last_round'] = rnd
hb['last_round_at'] = iso
hb['orphan_face'] = 0
hb['orphan_faces'] = 0
json.dump(hb, open(hp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
chk2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
print('heartbeat ok, epoch int:', chk2['heartbeat_epoch_utc'])

# ---- round report ----
rp = 'fleet/round_reports-bm-c.md'
line = ('%s | r%d | pit-protocol.md sub-split ceremony（31,433B>30,720B r859 欠账承接）：r529/r583/r645 state 簿记族 3 条 2,034B verbatim 迁 pit-protocol-lane.md+主件头部执法面改道 lane 件；TREASURE §2 三件齐=prescan rc3 命中 4 件留痕（fail-closed 面·r441 交集裁定=零丢失迁移非删除类）+登记册出入行+零丢失断言；S4 新坑律=text-mode 换行翻译坑（CODELY.md 30,510B）；S6 39 腿全 rc0（dualrun streak 13·supply_gap 旗=W17 drain/W18 起窗 fleet 级等待面非本机违令·py_low 合法白名单=板 0/0+bandit 0+池 4 ready 全 claimed+satengine 队空）；S7 四件绿+attrition CLEAN；d19 NOOP（hash 未变）+orders 水位更新；孤儿面=0；本地未达 origin commit 数=0（本轮 commit 后自证） | receipt=results/_r839bmc_pit_protocol_lanesplit.json·byte identity 31433-2034+73=29472·smoke 49/49 | %s\n' % (iso, rnd, NEXT_PTR))
with open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('round report appended')
