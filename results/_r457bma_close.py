# r457 bm-a close-out: state 458 + heartbeat + round report + CODELY lesson append.
import json, time, datetime, psutil

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec='seconds')
epoch = int(time.time())

# 1) state-bm-a.json
st = json.load(open('state-bm-a.json', encoding='utf-8'))
st['round_no'] = 458
st['did'] = ('r457: r456 dead-tick S7 storm closure (r240 adopt-verify-close) -- push collision left rebase'
             ' dead on 15-UU batch with stale onto 31636c669; forensics=sole bigmoney executor (pid 75524, pin 8),'
             ' commit f0d33ff7d intact; abort + explicit replay onto origin/main (r449 precedent, origin double-hop'
             ' 3606e2d82->c84f70c6f); 15-UU canonical resolve: CODELY r327 entry-level bidirectional union 11,021B'
             ' -> over-line hot-cold reorg moved r443/r445/r444 verbatim to archive (moved 3/lost 0, final 9,328B'
             '<10,240B) + ALL_FACES x6 merge_lane_views resolve + twins x6 ts-probe same-side (local 03:45 > origin'
             ' 03:28) + guard_scan scan-moment monotonic take-new (03:48 > 03:44) + fundamental snapshot take-new;'
             ' landed c81d3cc2c, reconcile 6-face ZERO-DRIFT + 2-face drift observation-recorded')
st['verify'] = ('smoke 26/26; orders 122/122 zero unacked; attrition guard scan CLEAN; rebase zero-loss'
                ' (both-side entries verbatim in tree); CODELY 9,328B<10,240B; watermark insufficient_history n=1'
                ' honest (board 0 open + bandit 0 + pool ready=1 W12-SCREEN); token delta=0')
st['next'] = ('r458: (1) W12-SCREEN pool burn watch -> JUDGE landing opens W13 adoption freeze window (draft berthed,'
              ' seeds 20323000/20323500/20324000 three-step reverify per r441); (2) 10-01 month-first-round trio'
              ' (science_audit + monthly_briefing + self_review) + REGIME_GUARD v3 date-gate hands-off; (3) next 5x'
              ' HANDOVER check = bm-a r460; (4) S9C amend veto window to 10-07')
st['last_round_at'] = ts
st['current_task'] = 'r457 closed (storm adoption); next = W12-SCREEN watch + W13 window + 10-01 trio'
st['updated'] = ts
json.dump(st, open('state-bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 2) heartbeat fleet/machines/bm-a.json (write own file only)
hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
hb['last_seen'] = ts
hb['clock_read'] = ts
hb['heartbeat_epoch_utc'] = epoch
assert isinstance(hb['heartbeat_epoch_utc'], int)
hb['current_task'] = st['current_task']
hb['task'] = st['current_task']
hb['round_no'] = 458
hb['verdict'] = 'healthy'
hb['cpu_pct'] = psutil.cpu_percent(interval=0.3)
vm = psutil.virtual_memory()
hb['free_ram_gb'] = round(vm.available / 1024**3, 1)
json.dump(hb, open('fleet/machines/bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
ck = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(ck['heartbeat_epoch_utc'], int) and 'T' in ck['clock_read']
assert len(ck['orders_ack']) == 122, 'ack set must stay 122'

# 3) round report line (canonical path per r455 fix)
line = (f"{ts} | r457 | dept:工程·舰队 (r456 死 tick S7 风暴收口·rebase 遗产 adopt-verify-close) | WM verdict: "
        f"insufficient_history 窗 n=1（板 0 open+bandit 0+pool ready=1=W12-SCREEN 合法 idle 白名单面） | 当前活: r456 "
        f"push 撞车死于 rebase 15-UU 批（onto 31636c669 陈旧）→本轮取证三步=进程链核本机唯一 bigmoney 执行体（75524 针位8）"
        f"→abort+onto origin/main 显式重放（r449 先例·origin 双跳 3606e2d82→c84f70c6f autofill 单发零冲突二轮）→15-UU 正典解："
        f"CODELY r327 条目级双向覆盖 union 11,021B→超 10,240B 硬线当窗热冷整编 moved r443/r445/r444 verbatim 入 archive"
        f"（行级零丢失 moved 3/lost 0·final 9,328B）+ALL_FACES×6 merge_lane_views resolve+孪生×6 ts 探针同侧取齐"
        f"（local 03:45>origin 03:28）+guard_scan 扫描时刻差单调计数 take-new（03:48>03:44·r444 范式 deep-compare 定性）"
        f"+fundamental snapshot take-new（03:44>03:27）| 最近实物: commit c81d3cc2c push 落地（r456 W13 泊位全套+探针双件零丢失"
        f"·resolver=results/_r457bma_resolve.py·archive『热冷整编 2026-09-30 r457 bm-a 窗批』节）| did: S0.5 orders 122/122 "
        f"零未回执+decisions 尾 D-07 已在 prompt 生效零新动作；S1 smoke 26/26；S2 双板零 open+W12 ledger 核（GENERATE "
        f"consumed 03:35:28·SCREEN ready 池 1·JUDGE 未至=W13 冻结触发器未满足窗口未开如实记·泊位开放任何健康机）；S6 链 r456 "
        f"03:48 链 38min 窗+bm-b/bm-c 双反射合法不重跑（r444/r448 先例）·轻腿补跑 watermark probe+token delta=0；reconcile "
        f"6 面 ZERO-DRIFT+2 面 drift 观察相照录（gate_attrition/crash_fuse） | verify: smoke 26/26; orders 122/122; "
        f"attrition guard CLEAN; CODELY 9,328B<10,240B; 心跳 epoch int 自证 | next: (1) W12-SCREEN 池烧批 watch→JUDGE 落地即开"
        f"W13 收编冻结窗（seeds 三步律复验）(2) 10-01 月首轮三件套+REGIME_GUARD v3 日期门 hands-off (3) 下轮 5x=bm-a r460 "
        f"HANDOVER 核对 (4) S9C amend 否决窗至 10-07\n")
with open('logs/iteration-loop/round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(line)

# 4) CODELY lesson (S4, one entry, <=1.5KB, four-question gate passed)
lesson = ("- [2026-09-30 04:2x r457 bm-a] 风暴 resolver 非幂等追加坑（本窗实弹：resolver 迭代修补后重跑=archive 窗批节双追加"
          " 248,046→250,770 字节实证）：append 型收口脚本对同一目标文件的写回必须带幂等守卫（目标节 tag in-file 探测先行，已存在"
          "=跳过 append 仅验 verbatim 在位）；半途失败修复后重跑前先 git checkout -- 从 index 恢复被上轮写花的派生面再跑。"
          "How to apply：一切 _r<N>_resolve.py 类收口脚本=add 前必过「重跑一次不双写」自检；勿直接续跑已写花的树。\n")
with open('CODELY.md', 'a', encoding='utf-8') as f:
    f.write(lesson)

print(json.dumps({'ts': ts, 'epoch': epoch, 'codely_B': len(open('CODELY.md', 'rb').read()),
                  'ack': len(ck['orders_ack'])}, ensure_ascii=False))
