# -*- coding: utf-8 -*-
# r705 bm-b S7 closeout: state 704->705, heartbeat (epoch int), round report line append.
import io, json, time, datetime

NOW = datetime.datetime.now().isoformat(timespec='seconds')
EPOCH = int(time.time())

# 1) state.json: bump round, rewrite note/next/last_round_at
st = json.load(open('state.json', encoding='utf-8'))
assert st['round_no'] == 704, 'unexpected round_no %r' % st['round_no']
st['round_no'] = 705
st['note'] = ('r705: S0 double-merge heal + D-06 batch-3 pit-pool two-way sub-split. '
             'S0: r704 budget-death delivery gap healed (closeout 8f3bb9ccf + tail-merge 9f74450f1 carried out: '
             'wave-1 merge ab2a32685 incl. bm-a N2-W15 judge P0 crash-loop fix db7c8697e + 12-shard claims + bm-c r507, '
             'single UU crash_fuse.json resolved per-key union r701 lineage side_pick ours1/theirs11, resolver=results/_r705bmb_merge_resolve.py; '
             'wave-2 merge ec3024662 incl. bm-c r507 S6 38/38 closeout wave, zero UU); daemon-refreshed origin ref swept in more than session fetch knew (superset merge, zero loss). '
             'S3: pit-pool.md 52,337B/46 -> pit-pool.md 26,502B/20 (claim/flip semantics/visibility/takeover/double-burn/parked governance/supply reading) '
             '+ pit-pool-edit.md 27,728B/26 (pool-file byte editing/write-paths/settle/conflict basis/reland windows/flip surgery/burn mechanics/ignition gates); '
             'entries sum 48,301B two-file identity, verbatim, variant5 bulletless x3 (r598/r608/r605) preserved in host blobs E16/E18 zero info loss; '
             'r439/r441/r703 ceremony: prescan rc3 acknowledged + TREASURE_REGISTRY in/out row + CODELY pool pointer reroute; '
             'receipt results/_r705bmb_pit_pool_split_receipt.json. '
             'S6 chain skipped this round (budget window consumed by S0 double-merge + split; CEO faces fresh from bm-c r507 38/38 regen same window) -> r706 runs full chain. '
             'smoke 48/48; orders 154/154 double-scan zero unacked; D-19 dual hash unchanged (755428F8/E79E15F9); satengine alive rc0 (RAM gate 2.8GB<4GB legal trio-held); board zero open.')
st['last_round_at'] = NOW
st['ts'] = NOW
st['updated'] = NOW
st['last_seen'] = NOW
st['round_no_label'] = 'round 705 (bm-b)'
st['clock_read'] = NOW
st['next'] = ('(a) D-06 batch-3 remaining three oversized domain files sub-split to <=30KB per r703/r705 recipe '
             '(pit-protocol 50,756B, then pit-git-netpath 46,328B / pit-git-surgery 45,114B), before 10-07 12:00 closeout; '
             '(b) r706 runs full S6 chain (r705 skipped, honest); '
             '(c) N2-W15 judge burn in flight on bm-a (12/12 claimed, P0 grammar fix landed): bm-b claims shards when RAM window opens post trio-V (~10-06T17+); judge-finalize seat first-come; '
             '(d) trio NULLS V/Q/D burn to 10-06T17/10-07T11/10-08T0x; (e) 10-09 post-holiday data-chain check; '
             '(f) untracked backlog cleanup ruling (treasure_guard prescan first).')
io.open('state.json', 'w', encoding='utf-8', newline='').write(json.dumps(st, ensure_ascii=False, indent=1))
json.load(open('state.json', encoding='utf-8'))
print('state 705 written')

# 2) heartbeat: last_seen/epoch(int)/clock_read/verdict/task
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = NOW
hb['round_no'] = 705
hb['round_no_label'] = 'round 705 (bm-b)'
hb['current_task'] = ('r705 done: S0 double-merge heal (r704 closeout delivered, judge P0 fix + bm-c r507 adopted) + D-06 batch-3 pit-pool two-way sub-split '
                      '(26,502B/20 + 27,728B/26, zero-loss verbatim, ceremony complete); D-06 batch-3 remaining 3 files to r706+ before 10-07 12:00')
hb['verdict'] = ('healthy burning (trio NULLS three-family RAM-held = legal cap window 2.8GB<4GB floor; N2-W15 judge burn in flight on bm-a 12/12 claimed; '
                 'board zero open; S6 chain deferred to r706 - faces fresh from bm-c r507 same-window regen)')
hb['ts'] = NOW
hb['updated'] = NOW
hb['updated_at'] = NOW
io.open('fleet/machines/bm-b.json', 'w', encoding='utf-8', newline='').write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
print('heartbeat written, epoch int ok:', chk['heartbeat_epoch_utc'])

# 3) round report line append (bm-b file = logs/iteration-loop/round_reports.md)
REPORT = 'logs/iteration-loop/round_reports.md'
row = ('%s+08:00 | round 705 (bm-b·dept:工程+舰队·S0 治愈+D-06 batch-3 拆件轮) | '
       '[watermark verdict: GREEN (red=false lane=healthy·py_low_with_work_cands=合法 RAM 窗·trio NULLS 三族在烧持阈)] | '
       '当前活=S0 双波合并治愈 r704 预算死遗留送达缺口+pit-pool 两分拆件 | '
       '最近实物=research/pit-pool-edit.md 新件 27,728B/26 条+pit-pool.md 再平衡 26,502B/20 条（条目和 48,301B 两件恒等零丢失·receipt results/_r705bmb_pit_pool_split_receipt.json）'
       '+origin 送达 commit ab2a32685+ec3024662（含 r704 closeout 8f3bb9ccf 治愈送达）@02:2x | '
       '下个里程碑=D-06 全线收口 10-07 12:00（余 pit-protocol/pit-git-netpath/pit-git-surgery 三件·r706 起）+judge 池烧收口 ≤10-12 | '
       'S0=轮首三探零残留态·pull --rebase 后本地 autofill daemon 刷新 origin ref→merge 实收超集（bm-a judge P0 grammar 修复 db7c8697e+shard-0 烧录件+12 分片 claims+bm-c r507 churn）'
       '·单 UU crash_fuse.json r701 血统 per-key union 解毕（ours1/theirs11·receipt results/_r705bmb_merge_resolve.json）·push 撞 non-FF（bm-c r507 收口波再进）→churn-absorb-2→merge-2 零冲突→送达 | '
       'S0.5=令扫双查零未回执（154/154）| D-19=双哈希不变（decisions 755428F8/orders E79E15F9·_r702bmb_d19_read.py 复用）零动作 | '
       'S1 smoke 48/48 | S2=板空（job_list 0+票板 0 open）| S3=水牌 green·satengine alive rc0（RAM 门 2.8GB<4GB 合法持阈·queue 13）·常设线=判决批在飞（bm-a 12/12 在烧·P0 修复已上）免新起草 | '
       'S3 主活=D-06 batch-3 pit-pool 拆件（r703 配方复刻·prescan rc3 留痕+登记册出入行+CODELY 指针改道·变体⑤ bullet-less 三条随宿主 blob 原样迁移零信息损失）| '
       'S6=本轮如实跳过（预算窗耗尽于 S0 双合并+拆件；CEO 面 38/38 已由 bm-c r507 同窗再生新鲜）→r706 跑全链 | '
       'S7=claws 双爪本均在位实证（pre-commit 过 3 commit·pre-push 过 2 push 拦 non-FF 正确执法）·attrition 未跑=r706 补 | '
       '本地未达 origin commit 数=0（push 后 fetch+rev-list 双向自证）| '
       '产品分=1（D-06 域件再平衡=mandated 实际文件改动+新子件落地；S0 治愈=送达面修复；无新算法批）| '
       '下轮指针=(a)D-06 batch-3 余三件（pit-protocol 先行）(b)S6 全链复跑+attrition 补 (c)judge 池烧观察（bm-a 独烧·bm-b RAM 窗开后照池认领）(d)trio V 收口 10-06T17 (e)10-09 节后数据链核验 (f)未跟踪 backlog 清扫裁定（treasure_guard prescan 先行）'
       % NOW)
raw = open(REPORT, 'rb').read()
assert raw.count(b'\r\n') == 0 and raw.endswith(b'\n'), 'report host shape unexpected'
cur = raw.decode('utf-8')
assert 'round 705 (bm-b' not in cur, 'report row already present'
io.open(REPORT, 'a', encoding='utf-8', newline='').write(row + '\n')
print('report row appended %dB' % len(row.encode('utf-8')))
