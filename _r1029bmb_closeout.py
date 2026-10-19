# r1029 bm-b closeout: dual-face state + heartbeat + round report. (ASCII-safe mixed CN)
import datetime
import io
import json
import os
import time

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
S_MAIN = os.path.join(ROOT, 'state.json')
S_MIRROR = os.path.join(ROOT, 'logs', 'iteration-loop', 'state.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
RR = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')

NOW = datetime.datetime.now().isoformat(timespec='seconds')
EPOCH = int(time.time())
R = 1029

DID = ("r1029: (a) S0 clean: fetch behind=0/ahead=0 (r1028 estate fully landed pre-round; r1028_main_push "
       "PENDING marker closed PUSHED_VERIFIED); orphan probe 0/7 faces. (b) D-19 dual probes (FIRST ACTION + "
       "chain leg) both ZERO-DELTA: dec=95879dd9 hold, ord=bd527746 hold (sprint cadence quiet this window; "
       "r1028 consumed through 16:4x); advance NOOP read-back OK, mirrors synced 2; S0.5 orders diff empty, "
       "inbox 0 unread. (c) NATS three-machine GREEN acceptance ACHIEVED: state.bm-c appeared live 17:05:08 "
       "(rev 118, node=FLUXGROUP host, ram_free 7.8GB cpu 25%) -- bm-c deployed its bus node; state.bm-b rev "
       "117 continuous every-1min; fleet bus = bm-a hub + bm-b node (r1028) + bm-c node ALL GREEN; r1028 watch "
       "item CLOSED; cli path pit logged (C:\\Fluxgroup\\Tools\\nats\\bin\\nats.exe). (d) honest-starvation "
       "round: green_idle=true (ram 55%/13.5GB, vram 3.7GB), claimable_pool_lines=0 (backlog all "
       "claimed/done), local self-drive pool W001-W009 all done/retired (restock face = secretariat), "
       "board/tasks/P2/P3 queues all empty, W279 prereg NOT landed on bm-c (N1 feed blocked upstream; "
       "supply_family_streak 808.7min), day-stations exhausted (ST-013 done r1024; ST-002 CEO-gate closed; "
       "ST-012 night-window 22:0x) -- --worked NOT declared, idle_rounds honest 1, agenda_starved=true "
       "(O-20261007-2315 semantics: masking the supply-line signal violates the meaning law); compute_audit "
       "honest flags pool_starvation+supply_floor 0/3 breach carried. (e) S6 chain 43 legs rc0 3.0min (smoke "
       "49/49 pre-chain 17:03; papers family honest SKIP x4 = 4th round, 10-19 bar not landed, cutoff 10-16, "
       "evening window ~20:4x retry; pool_dualrun ZERO-DRIFT streak 51; scorecard/paper_export/"
       "daily_scorecard/build_status stale-takeover derives bm-a hb stale 98-99min; REPORT/LIVE-2026-10-19 "
       "regen; market_clock ORANGE_COOL sleeves=4 activated=0; attrition scan healed 2-row bm-a historical "
       "shrink rc0 legal). (f) CODELY hot-cold integration MANDATED: 10KB hard-line breach 11,153B (r1028 "
       "append without integrate) healed same window -> 4 rows (r1020 x2 / r1021 / r1024) verbatim migrated "
       "to archive 202610.md r1029 window-batch + merged pointer row + new NATS cli pit row; prescan rc3 "
       "x2 recorded (authorized face, r1009 precedent); line-level zero-loss 4/4 verified; size back under "
       "line.")
VERDICT = ("GREEN: r1029 NATS 三机全绿验收轮+CODELY 硬线整编轮+诚实断供轮——state.bm-c 17:05:08 上线（rev 118）→"
           "三机总线全绿（bm-a 中枢+bm-b r1028 节点+bm-c 节点·r1028 观察项闭案）；D-19 双探零增量（dec 95879dd9/"
           "ord bd527746 hold·冲刺窗静默）；CODELY 10KB 硬线破线 11153B 当窗治愈（4 行 verbatim 迁 archive r1029 窗批·"
           "零丢失 4/4·prescan rc3 授权面留痕·新坑行=NATS CLI bin 子路径）；S6 43 腿 rc0 3min（papers 族四连诚实跳过="
           "10-19 bar 未落 cutoff 10-16·晚间窗 ~20:4x 重试·pool_dualrun 51 连绿·REPORT/LIVE 再生·market_clock "
           "ORANGE_COOL）；诚实断供面：green_idle+池/板/队列全空+W279 候 bm-c+日间站耗尽——idle_rounds 如实 1 不清零"
           "（--worked 不申报=供给线信号不遮蔽·意义律执法）；下窗=r1030 papers 晚间窗重试+22:0x 日进化班 DOR BigMoney "
           "行自报+ST-012 夜窗 LoRA 首训（REBUILD-PLAN-v2+v2Pro 门先行）")
NEXT = ("r1030: 1) papers chain conditional retry when 10-19 bar lands (evening ~20:4x-21:xx: live.paper "
        "family + marks + export) 2) 22:0x daily evolution shift: DAILY-OUTPUT-REPORT BigMoney row "
        "self-report via group inbox MSG channel (tracked-file zero-touch law; honest four-clause: external "
        "output 0 as-is) 3) ST-012 night window 22:0x: REBUILD-PLAN-v2 full read + v2Pro 8G profile "
        "adaptation gate BEFORE first LoRA train run 4) supply watch: W279 prereg bm-c side -> bm-b N1 "
        "pool feed after it lands; pool_starvation+supply_floor 0/3 = standing honest flags for duty "
        "rounds / secretariat restock 5) NATS: bus green, next = bm-a P2/P3 rollout per R- three-step plan "
        "6) RepoSlim first daily run tomorrow 09:03 live-anchor verify 7) audit-order KPI line carried")
ART = ("NATS three-machine GREEN (state.bm-c rev 118 + state.bm-b rev 117 live on FLEET_STATE KV; r1028 "
       "watch closed) + CODELY hot-cold integration receipt (results/_r1029bmb_codely_hotcold_receipt.json "
       "zero-loss 4/4, 11153B->under-10KB) + S6 regen faces (REPORT/LIVE-2026-10-19 + market_clock "
       "CALL-2026-10-16 ORANGE_COOL + DUALARM-2026-09-30) + r1029 work files (_r1029bmb_s6chain.ps1 / "
       "_r1029bmb_codely_hotcold.py / _r1029bmb_closeout.py / _r1029bmb_s6_log.txt)")


def rd(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return json.load(f)


def wr(p, obj):
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def upd_state(path, note):
    s = rd(path)
    s.update({
        'round': R, 'round_no': R, 'round_no_label': 'r%d' % R,
        'clock_read': NOW, 'ts': NOW, 'updated': NOW, 'updated_at': NOW,
        'last_round_at': NOW, 'last_round_ts': NOW, 'last_seen': NOW,
        'last_action_at': NOW,
        'last_action': 'r1029: NATS three-machine green (state.bm-c live) + CODELY 10KB heal '
                       '(4 rows migrated zero-loss) + honest starvation face + S6 43 rc0',
        'current_task': 'r1029: NATS three-machine GREEN acceptance + CODELY hot-cold heal + D-19 '
                        'zero-delta + S6 43 rc0 (papers skip round 4)',
        'task': 'r1029: NATS three-machine GREEN acceptance + CODELY hot-cold heal + D-19 '
                'zero-delta + S6 43 rc0 (papers skip round 4)',
        'did': DID, 'verdict': VERDICT, 'current': VERDICT,
        'last_artifact': ART, 'latest_artifact': ART,
        'next': NEXT, 'now_active': 'r1029 closed',
        'orphan_face': 0, 'orphan_face_note': 'r1029 S0 probe (17:02): 7 py faces / 0 orphans',
        'orphan_faces': 'n/a',
        'state_face_note': 'r1029: mirror-written per r1020 dual-face law. ' + note,
    })
    s['r1029_ord_note'] = ('r1029: ORD/DEC dual probes ZERO-DELTA both faces (FIRST ACTION 17:04 + chain '
                           '17:08): dec=95879dd9 hold, ord=bd527746 hold; sprint cadence quiet this window; '
                           'r1030 FIRST ACTION = fresh d19 probe per law')
    s['r1030_first_action_note'] = ('r1030: 1) D-19 fresh probe FIRST ACTION 2) papers conditional retry on '
                                    'bar landing (evening window) 3) 22:0x shift: DOR BigMoney row '
                                    'self-report via group inbox MSG (zero-touch law) 4) ST-012 night 22:0x '
                                    'REBUILD-PLAN-v2 + v2Pro gate 5) supply: W279 prereg watch (bm-c) -> '
                                    'N1 feed 6) RepoSlim tomorrow 09:03')
    s['sat_engine'] = {
        'status': 'alive (r1029 chain status leg rc0; idle verdict; honest supply starvation '
                  'pool_ready=0 queue_depth=0 -- W279 prereg = bm-c side pending; N1 feed blocked upstream)',
        'checked_at': NOW,
    }
    sync = s.setdefault('sync', {})
    p28 = sync.get('r1028_main_push')
    if p28 is not None:
        p28['status'] = 'PUSHED_VERIFIED (verified at r1029 S0: fetch behind=0 ahead=0, r1028 payload on origin)'
        p28['consumed_at'] = NOW
        p28['pushed_sha'] = p28.get('pushed_sha') or 'landed (verified r1029 S0 behind=0/ahead=0)'
    sync['r1029_main_push'] = {
        'status': 'PENDING (this commit)', 'pushed_sha': 'pending',
        'consumed_at': 'pending r1030', 'behind_origin_main': 0,
        'note': 'r1029 payload = CODELY hot-cold integration (CODELY.md + archive 202610.md r1029 window-'
                'batch + receipt) + closeout faces (state/heartbeat/round-report dual-face) + r1029 work '
                'files (s6chain/hotcold/closeout + s6 log) + own regen/product faces (daily_report/live_'
                'usage docs + scorecard/paper_export/daily_scorecard/dashboard stale-takeover derives + '
                'market_clock + regime_state + DUALARM + d19/orphan/attrition evidence faces); EXCLUDED '
                'per r982/r1015/r1020/r1028 policy: drama lane 3 daemon faces, machine-health, '
                'token_usage.json shared union face, unsuffixed lhb/futures/astock/etf status faces; '
                'base = origin tip fresh at S0 (behind=0/ahead=0)',
    }
    wr(path, s)


def main():
    upd_state(S_MAIN, 'authoritative face.')
    upd_state(S_MIRROR, 'mirror face.')
    hb = rd(HB)
    hb.update({
        'last_seen': NOW, 'ts': NOW, 'clock_read': NOW,
        'heartbeat_epoch_utc': EPOCH,
        'idle_rounds': 1, 'agenda_starved': True,
        'cpu_cores': 16, 'free_ram_gb': 13.5, 'gpu_free_vram_mb': 3813,
        'round_no': R, 'round': R,
        'current_task': 'r1029: NATS three-machine green + CODELY hot-cold heal + honest starvation + S6 43 rc0',
        'verdict': 'GREEN: r1029 NATS 三机全绿（state.bm-c rev 118 上线·观察项闭案）+CODELY 10KB 硬线治愈'
                   '（4 行迁移零丢失）+诚实断供轮（池/板/队列全空·W279 候 bm-c·idle_rounds 如实 1 不清零）'
                   '+S6 43 rc0（papers 四连跳过·cutoff 10-16）',
        'did': 'r1029: NATS three-machine GREEN (state.bm-c live rev 118) + D-19 zero-delta x2 + CODELY '
               'hot-cold heal (11153B breach -> under line, zero-loss 4/4) + honest starvation '
               '(idle_rounds=1, no --worked) + S6 43 rc0',
        'task': 'r1029: NATS three-machine green + CODELY hot-cold heal + honest starvation + S6 43 rc0',
        'last_action': 'r1029: NATS three-machine green + CODELY heal + honest starvation face',
        'last_action_at': NOW,
        'last_artifact': 'results/_r1029bmb_codely_hotcold_receipt.json (zero-loss 4/4, breach healed)',
        'latest_artifact': ART,
        'next': NEXT,
        'now_active': 'r1029 closed',
    })
    wr(HB, hb)
    chk = rd(HB)
    assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
    row = ('%s | r%d | %s | %s | %s' % (
        NOW, R,
        'NATS three-machine GREEN acceptance (state.bm-c live rev 118 @17:05:08 + state.bm-b rev 117 '
        'continuous -- r1028 watch closed, fleet bus bm-a+bm-b+bm-c all green) + D-19 dual probes '
        'zero-delta (dec 95879dd9/ord bd527746 hold, sprint window quiet) + CODELY 10KB hard-line heal '
        '(breach 11153B: 4 rows r1020x2/r1021/r1024 verbatim migrated to archive 202610.md r1029 窗批 + '
        'merged pointer + new NATS cli pit row) + honest starvation face (green_idle, pools/board/queues '
        'all empty, W279 prereg pending bm-c, day-stations exhausted -- idle_rounds honest 1, --worked NOT '
        'declared) + S6 43 legs rc0 (papers SKIP x4 round 4: 10-19 bar not landed, cutoff 10-16, evening '
        'retry)',
        'NATS KV get state.bm-c rev 118 + state.bm-b rev 117 + chain log 43 rc0 + smoke 49/49 pre-chain '
        '17:03 + idle json green_idle=true idle_rounds=1 + hotcold receipt zero-loss 4/4 + prescan rc3 '
        'recorded (authorized face TPL, r1009 precedent; 登记簿命中=2 如实留痕非零命中) + pool_dualrun '
        'ZERO-DRIFT streak 51 + 未达 origin commit 数=1 (本 commit 在途·push 后归零·r1030 S0 验)',
        NEXT))
    with io.open(RR, 'a', encoding='utf-8') as f:
        f.write(row + '\n')
    print(json.dumps({'closed': 'r%d' % R, 'ts': NOW, 'epoch_int': True},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
