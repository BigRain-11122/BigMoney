# r299 bookkeeping: round report line + state-bm-c.json + heartbeat (format-preserving indent2+CRLF)
import json, time, datetime

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

# 1) round report line
rr = r'round_reports-bm-c.md'
line = (
    now + '｜r299｜watermark verdict=灰（insufficient_history·窗 n=1 采样不足=烧批刚收口合法静默面；'
    'compute_audit 旗=idle_with_work/supply_gap/supply_floor——点名：池 ready=2<floor 3 池饿，'
    '整改=试用劳动力常设线下轮起草下一波候选大考批）｜'
    '实况三行：当前活=69-commit 集成积压治愈收口+主干推送成功（cf60ecbe2..2a43c751a·main=origin 同步）；'
    '最近实物=results/_r298bmc_rebase_resolver.py（可跑冲突解器 4 批族法）+REPO/日报告/CEO 一页纸再derive（REPORT-2026-10-01·LIVE-2026-10-01）；'
    '下个里程碑=常供线供给波起草（窗≤48h·下轮启动）+REGIME_GUARD v3 enforce 今日 15:30 后新 bar 首跑（设计面）｜'
    '产品分=2（集成收口=可跑/已推实物）｜'
    'S1 47/47；S6 20 腿 rc0（lane 护栏 no-op 诚实·无新 bar 腿诚实跳过·月度三件 r294 已 discharge）；'
    'orders 133/133 差集 EMPTY；D-19 ED4E0EAB UNCHANGED；MSG-0231 收档回执；attrition CLEAN；'
    'RAM 0.8GB 低水位观察；loop Running/pin:05 no-op；watchdog Ready；claw 装好\r\n'
)
with open(rr, 'ab') as f:
    f.write(line.encode('utf-8'))

# 2) state-bm-c.json
sp = r'state-bm-c.json'
s = json.load(open(sp, encoding='utf-8'))
s['round_no'] = 299
s['last_round_at'] = now
s['last_round_ts'] = epoch
s['updated'] = now
s['cpu_pct'] = 22.0
s['idle_ram_gb'] = 0.8
s['gpu_free_vram_mib'] = 12843
s['verify'] = ('S1 smoke 47/47; S6 compact 20 legs rc0 (lane no-ops honest, no-new-bar legs honest-skip, '
               'monthly trio discharged r294); orders 133/133 EMPTY; D-19 ED4E0EAB UNCHANGED (raw-blob); '
               'attrition CLEAN; claw installed; watchdog Ready; pin :05 no-op; MSG-0231 archived with receipt')
s['did'] = ('r299: REBASE INTEGRATION CURED — 69-commit backlog zeroed, main pushed cf60ecbe2..2a43c751a (synced); '
            '5 conflict batches resolved (CODELY/x2 union-ts; cells AA set-equal take-origin; shards equal-except-audit; '
            'attrition probe-newer; NULLS claim 3-wave newest-wins + relay provenance, final killed_duplicate anti-ghost; '
            'crash_fuse keyed-union x2 waves sigs->43); autostash pop recovered + stash dropped; '
            'autostash-decay pit canonized CODELY r299')
s['current_task'] = ('idle post-integration; pool supply_gap (ready 2 < floor 3) -> trial-labor wave drafting = '
                     'next-round priority; cross_start_robustness WIP committed (r299), line continues next window')
s['next'] = ('(a) trial-labor standing line: draft next candidate wave (supply floor breach, O-2250 law); '
             '(b) T-131 awaiting GM sign (P1 unclaimable, unchanged); '
             '(c) REGIME_GUARD v3 enforce date-gate open TODAY: first post-15:30 round with new bar runs live.paper enforce (design); '
             '(d) RAM watch 0.8GB; (e) r293 stale stash@{0} (push-window transient) inspection next quiet window')
s['heartbeat_epoch_utc'] = epoch
s['clock_read'] = now
s['note'] = 'r299 product score=2 (integration cure pushed + resolver runnable artifact + S6 derive outputs)'
s['last_ts'] = now
s['last_decisions_read_at'] = now
s['last_round'] = ('2026-10-01 r299: integration cure (69-commit backlog -> main synced push 2a43c751a) '
                   '+ S6 compact 20 legs rc0 + orders/D-19 clean + MSG-0231 archived')
data = json.dumps(s, ensure_ascii=False, indent=2).replace('\n', '\r\n')
open(sp, 'wb').write(data.encode('utf-8'))

# 3) heartbeat fleet/machines/bm-c.json
hp = r'fleet\machines\bm-c.json'
h = json.load(open(hp, encoding='utf-8'))
h['last_seen'] = now
h['current_task'] = 'r299 done: integration cured, main synced; next=trial-labor wave draft'
h['cpu_cores'] = 32
h['idle_ram_gb'] = 0.8
h['gpu_free_vram_mib'] = 12843
h['verdict'] = 'idle_post_integration (supply_gap pool ready2<floor3 -> next-round trial-labor wave)'
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now
data = json.dumps(h, ensure_ascii=False, indent=2).replace('\n', '\r\n')
open(hp, 'wb').write(data.encode('utf-8'))

# post-asserts
for p in (sp, hp):
    j = json.load(open(p, encoding='utf-8'))
    assert isinstance(j['heartbeat_epoch_utc'], int), p
    assert 'T' in j['clock_read'], p
print('bookkeeping written; epoch int asserted; round_no=', json.load(open(sp, encoding='utf-8'))['round_no'])
