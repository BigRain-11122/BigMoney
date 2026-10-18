# r1059 bm-a closeout: state round_no +1, heartbeat refresh, round report line
# (single-writer discipline; read-modify-write each face)
import json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
EPOCH = int(time.time())

# 1) state round_no 1059 -> 1060
sp = 'state-bm-a.json'
s = json.load(open(sp, encoding='utf-8'))
assert s['round_no'] == 1059, f"unexpected round_no {s['round_no']}"
s['round_no'] = 1060
json.dump(s, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
s2 = json.load(open(sp, encoding='utf-8'))
assert s2['round_no'] == 1060
print('state round_no ->', s2['round_no'])

# 2) heartbeat fleet/machines/bm-a.json
hp = 'fleet/machines/bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
h['last_seen'] = NOW
h['clock_read'] = NOW
h['ts'] = NOW
h['heartbeat_epoch_utc'] = EPOCH
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['free_ram_gb'] = 50
h['gpu_free_vram_mb'] = 3993
h['cpu_cores'] = 32
h['current_task'] = 'r1059 guard round closed; next r1060 = W269 splice landing watch + MF Monday adjudication <=10-19'
h['last_action'] = 'r1059: S0 pull autostash (1 pop-UU watermark_red probe face newer-wins r1028 zero loss) + D-19 ord advance 43a18d01 dual-face (non-BigMoney rows, no action owed) + smoke 49/49 + W269 chain watch (prereg frozen 67fe12710c @ bm-c, splice pending bm-c r1093) + S6 43 legs rc0 bad=0 + live_paper rc0 + guards (loop pin=8 no-op, watchdog S4U flip denied = carried C-20261016-04, claws x2) + idle --worked'
h['last_action_at'] = NOW
h['last_artifact'] = 'docs/daily_report/REPORT-2026-10-18.md + docs/live_usage/LIVE-2026-10-18.md (S6 refreshed 15:0x, Sunday light) | results/_r1059bma_s6chain_rc.log bad=0'
h['did'] = 'r1059 guard round: W269 chain watch observed (bm-c owns, zero skip-claim), D-19 orders delta consumed (all BigStream/bm-c/bm-b rows, zero BigMoney dispatches), S6 43 legs all rc0, smoke 49/49, guards reinstalled, watermark green'
h['verdict'] = ('GREEN: r1059: guard round all green -- S0 autostash UU probe face newer-wins zero loss + D-19 ord 43a18d01 advanced dual-face '
                '(delta rows all non-BigMoney, no action owed) + smoke 49/49 + W269 chain watch (prereg frozen @ bm-c, splice pending, zero bm-a obligation) '
                '+ S6 43 legs + live_paper rc0 bad=0 + satengine ALIVE + orphan 0 + claws x2 + loop pin=8 + idle --worked 0->0; '
                'honest face = waiting-state guard round (wave supply = bm-c lane, boards drained, channels blocked/reserved; MF Monday adjudication armed)')
json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
h2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in h2['clock_read'] and '+' in h2['clock_read'], 'clock_read must be ISO8601 T-separated with offset'
print('heartbeat synced, epoch int OK:', h2['heartbeat_epoch_utc'])

# 3) round report line
rp = 'round_reports-bm-a.md'
line = (
    NOW + ' | r1059 | 守门轮：S0 pull --rebase --autostash（1 pop-UU watermark_red.json 探针面→ts newer-wins 保本机 14:59>14:48·r1028 族零损·stash drop 留痕）'
    '+orders_ack_scan CLEAN 102/111/0+D-19 ord 变 5d871243→43a18d01 新行全读裁决=全 BigStream/bm-c/bm-b 域零 BigMoney 派工零物理件新行（券商模拟盘=在册未动）→--advance 双面 sync 3（r1090 in-tool·state/heart 双验）'
    '+smoke 49/49+W269 链观察=prereg FREEZE 已上链（67fe12710c）·五面 splice 未落=bm-c r1093 首动作·本机零义务零抢跑'
    '+板面 T/E 复核全 done（E17 judged 0/32 判负收口文面确认）+backlog 无本机行+satengine ALIVE queue0+MF 周一 <=10-19 armed（周日 S6 腿 rc0）'
    '+S6 43 腿全 rc0 bad=0（周日 light·dualrun streak 延续·REPORT/LIVE-10-18 原地刷新·token 行照读）+live_paper rc0'
    '+loop pin=8 no-op+watchdog S4U flip 拒=carried（C-20261016-04）+双爪重装+idle --worked 0→0（basis=S6 管线+守门面·r1050 先例）'
    ' | 证据=results/_r1059bma_s6chain_rc.log bad=0+orders_ack_scan CLEAN 回执+watermark_red.json red=false healthy+d19 update ADVANCED read-back OK '
    '| 本轮=守门轮 0 分如实（波链在飞=bm-c 车道·板空·余通道全堵/保留） '
    '| 下轮指针=r1060：W269 五面 splice 落地观察（落则验证 W270 命名 sec.7/8 backfill）+MF 周一裁决 <=10-19（day-11/12 证据点已收）+委员会 §六 首轮裁决表 <=10-20 12:00+E20 三轴=GM/委员会署名保留面+S4U 提权窗 carried\n'
)
with open(rp, 'a', encoding='utf-8') as f:
    f.write(line)
print('round report line appended')
print('CLOSEOUT_OK')
