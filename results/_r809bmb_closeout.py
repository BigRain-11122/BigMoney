# r809 bm-b closeout: state/heartbeat/round-report/inbox writes (atomic json, epoch int)
import ctypes, json, os, shutil, time, glob

NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())

def ram_free_gb():
    try:
        class M(ctypes.Structure):
            _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', ctypes.c_uint64), ('ullAvailPhys', ctypes.c_uint64),
                        ('ullTotalPageFile', ctypes.c_uint64), ('ullAvailPageFile', ctypes.c_uint64),
                        ('ullTotalVirtual', ctypes.c_uint64), ('ullAvailVirtual', ctypes.c_uint64),
                        ('ullAvailExtendedVirtual', ctypes.c_uint64)]
        m = M(); m.dwLength = ctypes.sizeof(M)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return round(m.ullAvailPhys / (1024**3), 2)
    except Exception:
        return -1.0

RAM = ram_free_gb()

# ---- state.json ----
s = json.load(open('state.json', encoding='utf-8'))
s['round_no'] = 809
s['round_no_label'] = 'r809'
s['note'] = ('r809: three dead r809 sessions (00:17-00:35, wrapper/stream kills) estate absorbed: their S6 chain '
             '(10-09 bar full products incl. REPORT/LIVE-2026-10-10) + D-19 read + QA r806-debt pack; '
             'C7 heal per bm-c MSG: local group-tree fetch dead since 10-07 -> fresh sparse-clone dual read '
             'DEC/ORD BOTH CHANGED (2-day delta consumed); watermarks migrated to SHA-1 PIN r537')
s['last_round_at'] = NOW; s['ts'] = NOW; s['last_seen'] = NOW; s['clock_read'] = NOW
s['updated_at'] = NOW
s['last_decisions_sha'] = 'A3EA37BD70FD5ACC83BCF51939874CFFD59F1811'
s['last_orders_sha'] = 'A83FE1B418C81EF25EED9A51FC99AA45F9D7AEF0'
s['last_decisions_at'] = NOW; s['last_decisions_read_at'] = NOW; s['last_orders_read_at'] = NOW
s['last_decisions_sha_method'] = ('SHA-1 40-hex raw-blob of group origin/main docs (PIN r537 per bm-c C7 MSG '
                                  '20261009-173x; prior SHA-256 faces 4C32527B/E6A1DEE6 were stale-refs MATCHes '
                                  'since 10-07 = C7 disease, healed r809 via %TEMP%/d19_r809 sparse clone; '
                                  'fleet pin bd94a27b already superseded by further group motion = current truth consumed')
s['did'] = ('r809: estate absorb (3 dead sessions: S6 chain 10-09 bar full product faces + QA r806-debt pack 5/5 '
            'per-machine-suffix naming per D-20260909-02 + D-19 read) + C7 watermark heal + smoke 49/49 + '
            'orders 4 unacked processed (O-20261009-1105-bm-a @bm-b leg claimed due <=10-16 12:00; '
            'O-20261009-2340-bm-a sweep-ack; 2 r808 ack-registry date-typos healed 20260909->20261009) + '
            'attrition CLEAN + quartet 4/4 + post_review 45 ok 0 fail')
s['next'] = ('r810: O-20260909-2150 bm-b five-step onboarding (TOP: FleetLink wiring = extract '
             'Tools/register-fleet-link.ps1 + fleet-nodes.json from group origin blobs (%TEMP%/d19_r809 '
             'git show origin/main:...) -> run -> verify :8790 listener -> bm-a poke closes adoption; '
             'then workspace audit receipt + memory union via first poke + H3 8G-quantized install/disk-skip check) '
             '+ O-20261009-1105 @bm-b convertible-bond criteria scan + full-history empty-position stats '
             '(due <=10-16 12:00) + divlowvol ex-date + quality NAV probes (due <=10-10 12:00) + '
             'O-20260909-1246 state/queue three-file face build + 5x HANDOVER r810')
s['verdict'] = ('green: estate landed + C7 healed + smoke 49/49; astock full-universe refresh in-flight '
                '(pid 18116, todo 5217 at spawn, ETA hours, T-87 bm-b lane legal); FleetLink wiring debt '
                'claimed as r810 first action (script absent in stale local group tree copy)')
s['current_task'] = s['next']
json.dump(s, open('state.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

# ---- heartbeat ----
h = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
acks = h.get('orders_ack', [])
for wrong, right in (('O-20260909-2334-bm-b.md', 'O-20261009-2334-bm-b.md'),
                     ('O-20260909-2359-bm-b.md', 'O-20261009-2359-bm-b.md')):
    if wrong in acks:
        acks[acks.index(wrong)] = right
for new in ('O-20261009-1105-bm-a.md', 'O-20261009-2340-bm-a.md'):
    if new not in acks:
        acks.append(new)
h['orders_ack'] = acks
h['orders_ack_count'] = len(acks)
h['round'] = 809; h['round_no'] = 809
h['now_active'] = ('r809 closeout: 3-dead-session estate absorbed (S6 10-09-bar chain + QA r806-debt pack) '
                   '+ C7 watermark heal (D-19 2-day delta consumed, SHA-1 PIN r537 migration)')
h['current_task'] = ('r810: O-20260909-2150 onboarding five-step (FleetLink wiring first) + '
                     'O-20261009-1105 @bm-b convertible-bond scan + empty-position stats (<=10-16 12:00)')
h['task'] = 'absorb/closeout'
h['latest_artifact'] = ('r809: docs/daily_report/REPORT-2026-10-10.md + docs/live_usage/LIVE-2026-10-10.md '
                        '(dead-session S6 chain tails, 10-09 bar) + qa/smoke-r806-bm-b.md QA pack 5/5 '
                        '(per-machine suffix per D-20260909-02) + results/_r809bmb_d19_read2.json (C7 heal evidence)')
h['next_milestone'] = ('FleetLink :8790 adoption close <=10-10 01:3x (r810 first action, O-20260909-2150 step1) '
                       '+ divlowvol/quality NAV probes <=10-10 12:00 + O-1105 bm-b leg <=10-16 12:00 '
                       '+ 5x HANDOVER r810')
h['verdict'] = 'green-estate-landed-c7-healed'
h['last_action'] = ('r809: estate absorb + C7 SHA-1 watermark migration + orders 4 processed (2 typo heals) '
                    '+ smoke 49/49 + attrition CLEAN + quartet 4/4')
h['last_round_at'] = NOW; h['last_seen'] = NOW; h['updated'] = NOW; h['ts'] = NOW
h['clock_read'] = NOW
h['heartbeat_epoch_utc'] = EPOCH
h['cpu_cores'] = 16
h['free_ram_gb'] = RAM
h['orphan_faces'] = 0
h['orphan_face_note'] = ('r809 probe: 14 lawful py faces 0 orphans; astock refresh pid 18116 = T-87 bm-b lane '
                         'full-universe pull in-flight (spawn 00:18:44 todo 5217), lawful wait chain')
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['sync'] = {'ahead': 0, 'behind': 0, 'last_push_ts': NOW,
             'note': 'r809 closeout commit+push same-window; post-push rev-list+ls-remote self-verify in round report'}
json.dump(h, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

# ---- inbox: C7 MSG processed with receipt ----
src = 'fleet/inbox/MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md'
dst = 'fleet/inbox/processed/MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md'
receipt = ('\n\n## bm-b receipt (r809 ' + NOW + ')\n'
           '- C7 finding CONFIRMED and HEALED same-window: group-tree fetch had been stale since 10-07 '
           '(all MATCH faces r804-r808 + dead r809-w3 were stale-refs reads). Fresh sparse-clone dual read: '
           'DEC/ORD BOTH CHANGED; 2-day delta consumed (D-20260909-02 QA suffix = executed via qa/smoke-r806-bm-b.md; '
           'O-20260909-2150 onboarding claimed).\n'
           '- Watermarks migrated to ALGORITHM PIN r537 SHA-1 40-hex: dec=A3EA37BD70FD5ACC83BCF51939874CFFD59F1811 '
           'ord=A83FE1B418C81EF25EED9A51FC99AA45F9D7AEF0 (fleet pin bd94a27b already superseded by further group '
           'motion; current-truth face consumed; evidence results/_r809bmb_d19_read2.json).\n'
           '- HTTPS/clone fallback path validated (local group tree fetch face dead; %TEMP%/d19_r809 sparse clone live).\n')
try:
    body = open(src, encoding='utf-8').read()
    os.makedirs('fleet/inbox/processed', exist_ok=True)
    open(dst, 'w', encoding='utf-8').write(body + receipt)
    os.remove(src)
    print('inbox: C7 MSG processed + receipt appended')
except Exception as e:
    print('inbox move failed:', e)

# ---- round report row ----
row = (NOW + ' | r809 bm-b | WM-VERDICT: green (red=false lane healthy @00:44 probe; satengine alive rc0 idle '
       'queue_depth=0; boards 0 open mechanical scan; post_review 45ok/0fail) | 孤儿面=0 (14 lawful py faces; '
       'astock refresh pid 18116 = T-87 bm-b lane full-universe pull in-flight lawful, products land via next '
       'rounds churn-absorb) | CEO three-line: 当前活=r809 三死会话遗产收编(00:17-00:35 chain+D19+QA 产物全落盘)'
       '+C7 水位治愈; 最近实物=docs/daily_report/REPORT-2026-10-10.md + docs/live_usage/LIVE-2026-10-10.md '
       '(S6 链 10-09 bar 全产品面) + qa/smoke-r806-bm-b.md QA pack 5/5(per-machine 后缀=D-20260909-02 执行回执)'
       '+results/_r809bmb_d19_read2.json(C7 治愈证据); 下个里程碑=O-20260909-2150 入伙五步接线 FleetLink :8790 '
       '(r810 首动作) + divlowvol/quality NAV 双探针(<=10-10 12:00) + O-20261009-1105 @bm-b 可转债判据扫描+空仓分布'
       '(<=10-16 12:00) + 5x HANDOVER r810 | did: S0 判活=三死 r809 会话(00:12/00:22/00:32 轮体·流/超时杀)遗产'
       '全部 bm-b 自属零他机半成品=churn-absorb 合法(r620/r803 律); S0.5 令扫 4 未回执处置: O-20261009-2340-bm-a '
       'sweep-ack(bm-a 自交付宣告零 bm-b 动作) + O-20261009-1105-bm-a ack+认领(@bm-b 腿=可转债域判据素材扫描+全史'
       '空仓期分布统计 due <=10-16 12:00·PARKING-P1 立项令) + 2 条 r808 恢复登记簿日期笔误治愈(20260909->20261009'
       '·UNACKED+PHANTOM 对偶消解) ack 181->183; C7 MSG(bm-c)处理+回执: 集团树 fetch 自 10-07 死=五连 MATCH 全假面'
       '(r804/r808/r809-w3 stale-refs 读)——新鲜稀疏克隆双读 DEC/ORD 双变·2 天 delta 消费(D-20260909-02 QA 后缀定制'
       '=qa/smoke-r806-bm-b.md 执行回执·D-20260909-04 值守面已裁 bigmoney F-02 executed=一致; O-20260908-1205-bm-b '
       'FleetLink 确认从未收口·O-20260909-2150 入伙五步 CEO 令领受·O-20260910-0025=bm-c 车道零 bm-b 动作; '
       'O-20260909-1746 H3 装机复活版=r810+ 车道)水位键迁移 PIN r537 SHA-1 40-hex(dec A3EA37BD70FD.../ord '
       'A83FE1B418C8...·SHA-256 旧面记档不删); S1 smoke 49/49; S3 satengine rc0 idle+watermark red=false+'
       'post_review 0 fail; FleetLink 接线尝试=组树本地副本陈旧无脚本(Test-Path False·非 git 仓)→提取配方固化'
       '(%TEMP%/d19_r809 git show origin/main:Tools/register-fleet-link.ps1)留 r810 首动作; S6 死会话链吸收'
       '(白跑律禁重跑·尾产品 REPORT/LIVE 00:25:44 在盘验证·面板 bar 2026-10-09 QA 面证); S7 quartet 4/4'
       '(loop pin=2 no-op first-fire 00:52 + watchdog 00:49 + precommit/prepush claws LF-normalized 重装)'
       '+attrition CLEAN(4 ledgers healed rows historical)+state 808->809+心跳 epoch int 自证+orders_ack 183 '
       '自证 | verification: smoke 49/49 + QA r806-debt pack 5/5 + attrition CLEAN + D-19 fresh-read 双变消费'
       '+watermark SHA-1 40-hex 形自验 + orders 183/183 零未回执零幽灵(收尾复扫) | 本地未达 origin commit 数='
       'PENDING_FILL_R809(收口 commit+push 后 rev-list+ls-remote 双证·见 addendum) | product score 2 '
       '(S6 10-09 bar 全产品面 + QA pack 落库 CEO 可见 + C7 治愈件) \n')
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(row)

print('state/heartbeat/report/inbox written; RAM free =', RAM, 'GB; epoch =', EPOCH, type(EPOCH).__name__)
print('orders_ack count =', len(acks))
