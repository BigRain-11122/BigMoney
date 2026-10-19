# r1024 bm-b closeout: dual-face state + heartbeat + round report + inbox moves.
import datetime
import io
import json
import os
import shutil
import time

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
S_MAIN = os.path.join(ROOT, 'state.json')
S_MIRROR = os.path.join(ROOT, 'logs', 'iteration-loop', 'state.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
RR = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
INBOX = os.path.join(ROOT, 'fleet', 'inbox')
PROC = os.path.join(INBOX, 'processed')

NOW = datetime.datetime.now().isoformat(timespec='seconds')
EPOCH = int(time.time())
R = 1024

DID = ("r1024: (a) ST-013 dubbing-sheet preprocessing EP001-003 executed and DONE via lock-held "
       "direct station run (content_loop_step module import, single-writer law kept; loop plan "
       "honest-held at ST-012 gpu-night runner-pending): 52 per-line rows (EP001 19/EP002 16/EP003 17) "
       "with voice-bank mapping + rule-emotion v0.1 + est-sec vs shot-window fit (OK 19 / TIGHT 12 / "
       "OVERFLOW 21 surfaced = pacing-decision list for casting station) + multi-speaker auto-split 2 "
       "(heuristic, flagged) + needs-manual-split 3 + honest GAP 18 rows (NARRATOR no bank entry + "
       "minors gatekeeper/retailer/crowd/broker-VO); products = voice_sheets/EP001-003-VO-SHEET.md + "
       "json twin (origin-blob provenance sha256) + outbox receipt; runner dubbing_sheet_prep.py "
       "selftest 26 asserts PASS + adopted into RUNNERS/RUNNER_ADOPT (loop selftest green, incl. "
       "done-station historical-runner-name assert fix -- r1022 ST-011 label false-negative healed). "
       "Two in-window bugs fixed (needs-manual-split list-vs-dict pass; ep field integer vs EP key "
       "line_id -- empty-table caught by product verify, products regenerated idempotent). "
       "(b) ST-012 sourcing-gate scan receipt delivered (api.github.com anonymous, radar law): "
       "official RVC-Boss/GPT-SoVITS 63,139-star MIT pushed 2026-10-18 = the training wheel (local "
       "clone already in place), zero higher-star third-party trainer in top-15, AGPL/GPL family 4 "
       "explicitly license-blocked; ST-012 station stays open for the 22:0x night LoRA run (8G "
       "profile adaptation = night first action). (c) S0: FF absorb bm-c 3 commits (zero face "
       "intersection, d2667773da lineage) + D-19 fresh probes twice + advance (143d0767 then "
       "c1ed040c window: 9 new group ORD rows 13:26-14:09 all MV/WorkBuddy/bm-a domains, zero "
       "bm-b dispatch, watermark advanced per tool law, mirrors synced). (d) S6 chain 41 legs rc0 "
       "4.1min (smoke 49/49; orphan 0; idle --worked declared idle_rounds=0; pool_dualrun "
       "ZERO-DRIFT streak 51; compute_audit honest flags pool_starvation+supply_floor 0/3 = "
       "W278 N1 feed = bm-c engine next windows; scorecard/paper_export/daily_scorecard/build_status "
       "stale-takeover derives; minute_feed +55 rows; REPORT/LIVE-2026-10-19 regen; market_clock "
       "ORANGE_COOL). (e) inbox processed: bm-c MSG-1334 x2 (cadence-v2/RepoSlim bm-c-leg "
       "confirmations, informational).")
VERDICT = ("GREEN: r1024 ST-013 台本站收口轮——EP001-003 配音台本 52 行全落表（声库映射/情绪 v0.1/预估秒-镜窗配速 "
           "OK19·TIGHT12·OVERFLOW21=生产站逐行决断清单）+GAP18 如实点名（旁白无声银行条目+四配角=选角站必答）+多说话人 "
           "2 自动拆/3 待人工；ST-012 寻源闸回执毕（官方 GPT-SoVITS 63k★MIT=正主轮·本地已克隆·夜窗 22:0x 首训照单）；"
           "D-19 两探两进（9 行全零 bm-b 派工·MV/WorkBuddy 域）；S6 41 腿 rc0·smoke 49/49·孤儿 0·idle --worked 归零；"
           "下窗=r1025 15:30 后 papers 链（新 bar 落地）+ST-012 夜窗 LoRA 首训（22:0x·官方 finetune 8G 档适配）+"
           "supply_floor N1 喂池观察")
NEXT = ("r1025: 1) post-15:30 papers chain (new bar after close -> live.paper family + marks + export) "
        "2) ST-012 night-window 22:0x first character-voice LoRA run (official GPT-SoVITS finetune, "
        "8G VRAM profile adaptation, MANCANG new-base family per ST-009 law; GitHub wheels scan "
        "receipt already delivered r1024) 3) supply_floor: N1 pool feed watch (W278 burn 12/12 on "
        "bm-c -> sixgate -> finalize; bm-b pool feeds after) 4) RepoSlim first daily run tomorrow "
        "09:03 live-anchor verify 5) ST-013 casting-station seed (GAP rows disposition + OVERFLOW "
        "decisions) = next station seed after night lane")
ART = ("content/drama/voice_sheets/EP001-003-VO-SHEET.md + .json (52 rows) + ST-013 receipt + "
       "ST-012-TRAINING-WHEELS-SCAN.md + runner dubbing_sheet_prep.py + queue.json ST-013 done + "
       "S6 products (REPORT/LIVE-2026-10-19 regen + minute_feed +55 rows + DUALARM + market_clock)")


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
        'last_action_at': NOW, 'last_action': 'r1024: ST-013 EP001-003 dubbing sheet done '
        '(52 rows / gap 18 / overflow 21) + ST-012 wheels-scan receipt + D-19 advanced c1ed040c',
        'current_task': 'r1024: ST-013 dubbing-sheet EP001-003 done (52 rows) + ST-012 sourcing scan '
        'receipt + D-19 9 ORD rows + S6 41 rc0',
        'task': 'r1024: ST-013 dubbing-sheet EP001-003 done (52 rows) + ST-012 sourcing scan '
        'receipt + D-19 9 ORD rows + S6 41 rc0',
        'did': DID, 'verdict': VERDICT, 'current': VERDICT,
        'last_artifact': ART, 'latest_artifact': ART,
        'next': NEXT, 'now_active': 'r1024 closed',
        'orphan_face': 0, 'orphan_face_note': 'r1024 S6 chain probe (14:12): 7 py faces / 0 orphans',
        'orphan_faces': 'n/a',
        'state_face_note': 'r1024: mirror-written per r1020 dual-face law. ' + note,
    })
    s.setdefault('sync', {})['r1024_main_push'] = {
        'status': 'PENDING (this commit)', 'pushed_sha': 'pending',
        'consumed_at': 'pending r1025', 'behind_origin_main': 0,
        'note': 'r1024 payload = ST-013 products (sheet md+json + receipt + runner + queue.json done + '
                'CLAIMS rows + loop faces) + ST-012 wheels-scan receipt + content_loop_step st013 '
                'wrapper/selftest fix + D-19 advance faces + S6 own regen/product faces (docs '
                'daily_report/live_usage + bm-b lanes + stale-takeover derives + d19/orphan/attrition '
                'faces) + heartbeat/state/round-report + r1024 work files + inbox processed moves x2; '
                'shared daemon faces (machine-health/token_usage.json + unsuffixed lhb/futures status) '
                'NOT added (r982/r1015/r1020 policy); base = b965e2ecf0 origin tip fresh at FF absorb'}
    s['r1022_post_chain_ord_note'] = ('r1024: ORD bridge consumed through ord=c1ed040c (rows 13:26 '
                                      'WorkBuddy / 13:30 craft-spec / 13:33 anti-AI / 13:36 methodology '
                                      '/ 13:38 kuang-narrative / 13:40 Phase2 / 13:41 SIL4 / 14:02 '
                                      'Phase3 / 14:09 Phase4 -- all MV/WorkBuddy domains via bm-a, '
                                      'zero bm-b dispatch); r1025 FIRST ACTION = fresh d19 probe per law')
    wr(path, s)


def main():
    upd_state(S_MAIN, 'authoritative face.')
    upd_state(S_MIRROR, 'mirror face.')
    # heartbeat
    hb = rd(HB)
    hb.update({
        'last_seen': NOW, 'ts': NOW, 'clock_read': NOW,
        'heartbeat_epoch_utc': EPOCH,
        'idle_rounds': 0, 'agenda_starved': False,
        'current_task': 'r1024: ST-013 dubbing sheet done + ST-012 wheels scan receipt',
        'verdict': 'GREEN: r1024 ST-013 done (52 rows sheet) + ST-012 sourcing receipt; idle cleared '
                   '(--worked real product round)',
        'did': 'r1024: ST-013 EP001-003 dubbing sheet (52 rows/gap18/overflow21) + ST-012 wheels scan '
               '+ D-19 advance + S6 41 rc0',
        'last_artifact': 'content/drama/voice_sheets/EP001-003-VO-SHEET.md',
    })
    wr(HB, hb)
    chk = rd(HB)
    assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
    # round report row
    row = ('%s | r%d | %s | %s | %s' % (
        NOW, R,
        'ST-013 EP001-003 dubbing-sheet preprocessing DONE (52 rows: voice-map/emotion v0.1/fit OK19 '
        'TIGHT12 OVERFLOW21; GAP 18 honest; multi-split 2+3) + ST-012 wheels-scan receipt + S0 FF '
        'absorb bm-c x3 + D-19 9 ORD rows consumed (zero bm-b dispatch) + S6 41 legs rc0 + inbox '
        'MSG-1334 x2 processed',
        'runner selftest 26 PASS + loop selftest PASS + CLAIMS.jsonl done row rows=52 + sheet json '
        'per-ep 19/16/17 + smoke 49/49 + chain log rc0 41 legs + d19 advance read-back OK + '
        '未达 origin commit 数=1 (本 commit 在途·push 后归零·r1025 S0 验)',
        NEXT))
    with io.open(RR, 'a', encoding='utf-8') as f:
        f.write(row + '\n')
    # inbox processed moves
    moved = []
    for m in ('MSG-1334-bmc-cadence-v2.md', 'MSG-1334-bmc-repo-slim.md'):
        src = os.path.join(INBOX, m)
        if os.path.exists(src):
            shutil.move(src, os.path.join(PROC, m))
            moved.append(m)
    print(json.dumps({'closed': 'r%d' % R, 'ts': NOW, 'epoch_int': True,
                      'inbox_moved': moved}, ensure_ascii=False))


if __name__ == '__main__':
    main()
