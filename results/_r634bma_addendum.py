import json, time, datetime

line = "2026-10-03T18:14:00+08:00 | round 634 addendum | dept:工程 | push 撞头三连环留痕（正典路径零绕行）：r634 push 被 pre-push 爪拦+origin 7 commit 前进（bm-b r626 FUND-NULLS 在飞 V296/Q193/D90 of 2000+bm-c r423 MASS_W2 s3 judge 冻结 4796399f3）→r621 增量环合 ring-3 merge 18 UU 典范解（6 ALL_FACES merge_lane_views 显式交换三 stage〔r627 律〕+12 面深探针 take-new 本机 17:40-42 全新·attrition scan 17:42:50>17:41:08·resolver _r634bma_resolve_ring3.py+receipt ring3 块）→ring-4 merge bm-c CODELY 坑律行（0ab9fe9d3）零冲突→push 送达 0ab9fe9d3..971d58f22 fetch 自证 0/0 双面。ring-3 后 reconcile 抓 compute_audit 一行丢失（bm-b 17:26:59 burning-healthy py85.8%=NULLS 烧录窗行）——r85 窗内键集差集存活核定位+r614 字节恒等回填 210→211 行+contiguity 复证（_r634bma_ca_backfill.py）→reconcile 6 面 ZERO-DRIFT 全绿+attrition CLEAN 复扫。零 --no-verify 零强推零单方 settle（回填=append-only 零丢失复原非翻面）。 [via bm-a r634]\n"
with open('round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(line)
print('addendum appended, bytes:', len(line.encode('utf-8')))

hp = 'fleet/machines/bm-a.json'
hb = json.load(open(hp, encoding='utf-8'))
now = datetime.datetime.now()
hb['last_seen'] = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
hb['current_task'] = 'r634 done: stopped-rebase heal (ring-1/2/3/4 converged, pushed 971d58f22) + compute_audit one-row r614 backfill + reconcile 6 faces ZERO-DRIFT; NULLS bm-b in-flight (V296/Q193/D90 of 2000)'
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
hb2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(hb2['heartbeat_epoch_utc'], int) and 'T' in hb2['clock_read']
print('heartbeat refreshed:', hb2['last_seen'])
