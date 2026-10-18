"""r1018 bm-b closeout: state.json + heartbeat + round-report row.
Fresh-read-modify-write (multi-writer law); epoch = python int(time.time())
directly as JSON number (R170/R178 law); clock = ISO8601 T-separated with
offset (R262 law). argv: free_ram_gb gpu_free_vram_mb cpu_load_pct
"""
import datetime
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, 'state.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
RPT = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')

ram = round(float(sys.argv[1]), 1)
vram = int(sys.argv[2])
load = round(float(sys.argv[3]), 1)
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

DID = ("r1018: (a) S0 local==origin zero-pull (8 daemon faces local churn per r982 policy, "
       "not committed); S0.5 orders 105/105 zero-unacked + D-19 dual probe zero-drift "
       "(DEC 8706acd8/ORD 04050fda); S1 smoke 49/49; sat engine alive idle. "
       "(b) FIRST ACTION: ST-008 canon voice-bank entries station seeded (engine lock held, "
       "r1015 pattern) + engine-claimed + executed done -- 5/7 chars admitted (CH 3 / XIONG 3 / "
       "RED 2 / XIONGWEI 2 / FATHER 1 clips, 音色一致检 v0.1 all pass, FATHER single-clip "
       "vacuous), MANCANG+BOY honest gaps (all-7-满仓-lines CLIPPED / zero child-voice material); "
       "products: voice_bank/manifest.json ref_clips admitted + versioned driver "
       "runner_assets/voice_bank_entries.py (selftest 14/14) + receipt VOICE-BANK-ENTRIES-v0.1.md "
       "+ status face results/drama_env/voice_bank_entries.json; engine runner registered in "
       "Tools/content_loop_step.py (round-27 syntax slip rolled back honestly by engine, "
       "fixed in-window, round-28 entries-admitted). (c) S6 41 legs rc0: ZERO-DRIFT streak 51, "
       "update_daily 0 new rows (cutoff 2026-10-16, new-bar=no -> live.paper/t35_fill/t24_paper "
       "legally skipped), scorecard+dashboard = bm-a heartbeat stale 69min -> legal stale-takeover "
       "derive (O-2100 s2.4 STALE_MIN law), REPORT+LIVE-2026-10-19 regenerated, compute_audit "
       "flags pool_starvation+supply_floor = known wait-bm-c-W276 state. (d) idle face: "
       "green_idle 9-round counter cleared via Tools/idle_trigger.py --worked (real output work "
       "this round, O-20261007-2315 law).")

VERDICT = ("GREEN: r1018 ST-008 正典声银行条目站播种+引擎认领+执行收站 done（5/7 角色参考音入行："
           "CH 3 片/XIONG 3 片/RED 2 片/XIONGWEI 2 片/FATHER 1 片·音色一致检 v0.1 全 pass；"
           "MANCANG=7 条满仓行全 CLIPPED 诚实缺口+BOY 无素材缺口·如实不入行·寻源=后续站）；"
           "driver 版本化 selftest 14/14；S6 41 rc0（D-19 双零·新bar=否纸盘链依法跳过·"
           "scorecard/dashboard 合法 stale-takeover）；supply_floor 诚实饿 0/3 候 bm-c W276 prereg"
           "（r1110 首动作·落地即引擎供给腿检查）；idle 9 轮计数经 --worked 清零；"
           "下窗=r1019 O-0948 判决窗 10-19 ~10:2x+BOY/MANCANG 寻源站播种+BigMoney 席位计划贡献 ≤10-25")

NEXT = ("r1019: 1) O-20260924-0948 window close judgment 10-19 ~10:2x (v1 wall-clock census order) "
        "2) BOY/MANCANG ref-clip sourcing station seed (child-voice license review first / "
        "de-clip re-production for 满仓) 3) character differentiation station eval (voice_07/"
        "voice_05 shared-base debt before full-episode casting) 4) BigMoney seat automation plan "
        "contribution <=10-25 (bm-a r1069 3762f3dafa consume-no-rebuild) 5) supply_floor: on bm-c "
        "W276 prereg freeze landing -> engine supply leg check 6) CONTENT-LOOP 10-28 "
        "continuous-run judgment (8 stations/2 days, >=3 stations/day on track)")

MILESTONE = ("voice-bank 5/7 admitted -> next: BOY/MANCANG sourcing + differentiation station "
             "(<=10-22) + O-0948 window judgment 10-19 ~10:2x + CONTENT-LOOP 10-28 "
             "continuous-run judgment")

ARTIFACT = ("content/drama/voice_bank/manifest.json ref_clips admitted 5/7 (CH/XIONG/RED/XIONGWEI/"
            "FATHER, 音色一致检 v0.1 pass, clip-level F0/RMS/centroid evidence in-file) + "
            "content/drama/outbox/VOICE-BANK-ENTRIES-v0.1.md + results/drama_env/"
            "voice_bank_entries.json + S6 products (REPORT-2026-10-19 + LIVE-2026-10-19 ORANGE cap 50%)")

TASK = ("r1018: ST-008 canon voice-bank entries seeded+executed done (5/7 admitted, 2 honest gaps) "
        "+ S6 41 rc0 + idle --worked clear + push")

SYNC_NOTE = ("r1018 payload = own faces (ST-008 voice-bank station: versioned driver + manifest "
             "ref_clips + receipt + status face + engine runner registration + seed script + drama "
             "queue/claims/round-log/loop-state faces + state/heartbeat/round-report + S6 own "
             "regen/product faces [daily_report/live_usage docs + scorecard_v1/strategy_scorecard "
             "+ daily_scorecard/dashboard_status stale-takeover + update_status + compute_audit x2 "
             "+ regime_state x2 + b_layer + pool_dualrun.bm-b + prospect_promotion 23 + "
             "token_usage.bm-b + collector bm-b status faces + orphan/attrition probe faces]); "
             "shared daemon faces (machine-health/watermark_red/token_usage.json + unsuffixed "
             "lhb/futures/astock/etf status) intentionally NOT added (r982/r1015/r1017 policy); "
             "base = 580a9c6c5c origin tip fresh at S0 (local==origin zero-pull)")

ROW = ("{ts} | r1018 bm-b | dept:媒体产线+工程 | WM verdict: GREEN (red=false @06:13·"
       "py_low_board_clear=板空+bandit 空+无可跑批 合法闲置白名单) | "
       "当前活=ST-008 声银行条目站播种+引擎认领+执行收站 done（5/7 角色入行·音色一致检 v0.1 全 pass·"
       "MANCANG 全旗 CLIPPED/BOY 无素材 两缺口如实不入行）| "
       "最近实物=content/drama/voice_bank/manifest.json ref_clips 入行（CH 3 片/XIONG 3 片/RED 2 片/"
       "XIONGWEI 2 片/FATHER 1 片·clip 级 F0/RMS/谱心证据随件）+ VOICE-BANK-ENTRIES-v0.1.md + "
       "results/drama_env/voice_bank_entries.json + 版本化 driver voice_bank_entries.py（selftest 14/14）| "
       "S0 本地==origin 零拉取（8 daemon 面本地 churn 按 r982 政策不入 commit）；S0.5 orders "
       "105/105 零未回执+D-19 双探针零漂移（DEC 8706acd8/ORD 04050fda）；S1 smoke 49/49；"
       "sat engine alive idle；S6 41 腿 rc0（ZERO-DRIFT streak 51·update_daily 零新行 cutoff 10-16·"
       "新bar=否→live.paper/t35_fill/t24_paper 依法跳过·scorecard+dashboard=bm-a 心跳 stale 69min "
       "合法 stale-takeover O-2100 s2.4·REPORT/LIVE-2026-10-19 重生·COMPUTE_AUDIT 旗 "
       "pool_starvation+supply_floor=候 bm-c W276 prereg 已知态非新故障）；"
       "idle 面=green_idle 9 轮计数经 Tools/idle_trigger.py --worked 清零（本轮实际产出工）| "
       "下轮指针=r1019：O-0948 判决窗 10-19 ~10:2x+BOY/MANCANG 寻源站播种+角色差异化站评估+"
       "BigMoney 席位计划贡献 ≤10-25+supply_floor 候 bm-c W276 prereg 落地即引擎供给腿检查 | "
       "本地未达 origin commit 数=N（收口 push+fetch 自证·r1019 S0 翻 PENDING 标记）| "
       "孤儿面=0/7（06:21 探针）| 回执集=105/105 零未回执 | "
       "登记簿零命中断言=本轮零清扫/归档/删除/恢复类动作（treasure_guard 零触面）")


def rd(p):
    with io.open(p, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def wr(p, obj):
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def main():
    st = rd(STATE)
    for k, v in [('round_no', 1018), ('round', 1018), ('round_no_label', 'r1018'),
                 ('clock_read', now), ('last_seen', now), ('ts', now), ('updated', now),
                 ('updated_at', now), ('last_round_at', now), ('last_round_ts', now),
                 ('last_action_at', now), ('last_decisions_read_at', st.get('last_decisions_read_at')),
                 ('did', DID), ('last_action', DID[:300]), ('task', TASK), ('current_task', TASK),
                 ('verdict', VERDICT), ('current', VERDICT), ('next', NEXT),
                 ('next_milestone', MILESTONE), ('latest_artifact', ARTIFACT),
                 ('last_artifact', ARTIFACT), ('now_active', 'r1018 closed')]:
        st[k] = v
    st['sat_engine'] = {
        'status': ('alive (r1018 S6 status rc0, idle verdict, queue_depth 0; supply floor honest '
                   'starvation 0/3 -- W276 prereg freeze = bm-c r1110 first action, engine supply '
                   'leg check on landing)'),
        'checked_at': now,
    }
    st['orphan_face'] = 0
    st['orphan_faces'] = 7
    st['orphan_face_note'] = 'r1018 S6 chain probe (06:21): 7 py faces / 0 orphans'
    st.setdefault('sync', {})
    st['sync']['r1018_main_push'] = {
        'status': 'PENDING (this commit)', 'pushed_sha': 'pending',
        'consumed_at': 'pending r1019', 'behind_origin_main': 0, 'note': SYNC_NOTE,
    }
    st['sync']['last_push_ts'] = now
    wr(STATE, st)

    hb = rd(HB)
    for k, v in [('last_seen', now), ('ts', now), ('clock_read', now),
                 ('task', TASK), ('current_task', TASK), ('did', DID), ('last_action', DID[:300]),
                 ('last_action_at', now), ('verdict', VERDICT), ('current', VERDICT),
                 ('next', NEXT), ('next_milestone', MILESTONE), ('latest_artifact', ARTIFACT),
                 ('last_artifact', ARTIFACT), ('now_active', 'r1018 closed'),
                 ('cpu_cores', 16), ('free_ram_gb', ram), ('gpu_free_vram_mb', vram),
                 ('cpu_load_pct', load), ('idle_rounds', 0), ('agenda_starved', False),
                 ('heartbeat_epoch_utc', epoch), ('round_no', 1018), ('round', 1018),
                 ('orphan_face', 0)]:
        hb[k] = v
    wr(HB, hb)
    # epoch int self-assert (smoke F7 law)
    assert isinstance(rd(HB)['heartbeat_epoch_utc'], int), 'epoch must be JSON int'

    with io.open(RPT, 'a', encoding='utf-8') as f:
        f.write(ROW.format(ts=now) + '\n')
    print(json.dumps({'verdict': 'closeout-written', 'ts': now, 'epoch': epoch,
                      'ram': ram, 'vram': vram, 'load': load,
                      'state_round': st['round_no'],
                      'heartbeat_epoch_int': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
