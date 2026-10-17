# -*- coding: utf-8 -*-
# r989 bm-b closeout: round report row + state.json + heartbeat
import json, datetime, io

BASE = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
EPOCH = int(datetime.datetime.now().timestamp())
REPORT = BASE + r'\logs\iteration-loop\round_reports.md'
STATE = BASE + r'\state.json'
HB = BASE + r'\fleet\machines\bm-b.json'

did = ("r989: (a) S0 sync surgery: 29-commit rebase landed, 17 shared-regen-face conflicts resolved origin-side "
       "(newer-wins regen-faces law), rebase-continue deadlock broken via manual commit path (r988 replayed 4237047b3); "
       "stash pop blocked by could-not-write-index -> selective estate recovery instead; "
       "(b) dead-predecessor r989 estate ABSORBED from stuck stash: EPBurn delivery VERIFIED DONE (14:03, 5 files on origin "
       "cph4/fleet/drama-dept-v1/epburn-handover/, receipt results/_r989bmb_epburn_delivery_receipt.json verified=true) + "
       "whisperX venv installed & import-verified (install_rc=0 verify_rc=0) + allin1 broken on missing madmom; "
       "(c) allin1/madmom repair: root-caused (MSVC cl.exe found but Windows SDK io.h include paths absent -> vcvars64 env), "
       "build launched detached via _r989bmb_madmom_install.bat (bat-on-disk law), status at closeout = in-flight, next round reads "
       "madmom-install.log VERIFY_RC; (d) S0.5/D-19 delta consumed: orders 16819a8d->1df82bab (new rows 13:0x-13:5x all "
       "bm-a/bm-c MV domain, zero bm-b legs; O-0100 @bm-b leg = r987 recovery receipt, closed r988), decisions 1d4741e4 unchanged; "
       "(e) round-zero orphan probe 8 py faces 0 orphans; (f) S1 smoke 49/49 PASS; (g) S6 chain 40/40 legs ALL GREEN "
       "(dualrun ZERO-DRIFT streak42, compute_audit FLAG supply_floor known-STARVED, py_watermark insufficient_history legal, "
       "lhb corrupt-status WARN self-healed by leg rewrite 15:24, market_clock ORANGE_COOL, daily_score stale-takeover per "
       "O-2100 s2.4, t35_export 10-16 18 positions, LIVE-2026-10-17 written, token L2 legs 0); "
       "(h) MSG-0910 processed-move completed from estate; (i) local self-drive pool STARVED open=0 honest note, no manufactured work")

verdict = ("GREEN: dead-predecessor estate absorbed with EPBurn delivery verified done + whisperX installed; "
           "allin1 madmom build in-flight (root-caused, vcvars64 path, next-round verify); S6 40/40 green; "
           "honest defers: backlog claimable-line eval kept STARVED-note (pool zero bm-b cpu-sound lines), "
           "spawn-gate defer-log path locate = r990")

next_ = ("r990: 1) madmom VERIFY_RC read (allin1 import gate -> POOL-0018/0019 ignition inner-7-songs first, card window "
         "10-18 17:41) 2) spawn-gate defer-log path locate (E1 receipt-2 addendum) 3) backlog/pool claimable-line eval "
         "4) S6 chain 5) stash@{0} disposition (drop after 7-day-face check or keep; contains only regen faces + estate already recovered)")

# --- round report row ---
row = "%s | r989 | %s | evidence: smoke 49/49, S6 40/40 rc0, EPBurn receipt verified=true 5/5 files on origin, madmom-install.log in-flight, D-19 probe json | next: %s\n" % (NOW, did, next_)
with io.open(REPORT, 'a', encoding='utf-8', newline='') as f:
    f.write(row)

# --- state.json ---
with io.open(STATE, 'r', encoding='utf-8') as f:
    st = json.load(f)
st['round_no'] = 989
st['round'] = 989
st['round_no_label'] = 'r989'
st['clock_read'] = NOW
st['ts'] = NOW
st['updated'] = NOW
st['updated_at'] = NOW
st['last_round_at'] = NOW
st['last_round_ts'] = NOW
st['last_seen'] = NOW
st['last_action'] = 'r989: estate absorption (EPBurn done + whisperX ok) + allin1 madmom repair in-flight + S6 40/40 green'
st['last_action_at'] = NOW
st['current_task'] = 'r989: closeout (state/heartbeat/push)'
st['did'] = did
st['verdict'] = verdict
st['next'] = next_
st['now_active'] = 'r989: allin1 madmom build in-flight (detached), POOL-0018/0019 ignition pending verify; local pool STARVED'
st['next_milestone'] = 'POOL-0018/0019 whisperX ignition inner-7-songs before 10-18 17:41 card window; madmom verify r990'
st['current'] = 'r989: estate absorption + madmom repair + S6 green'
st['orphan_face'] = 8
st['orphan_faces'] = 8
st['orphan_face_note'] = 'r989 round-zero probe (15:1x): 8 py faces, 0 orphans'
st['last_orders_at'] = NOW
st['last_orders_read_at'] = NOW
st['last_orders_probe_at'] = NOW
st['last_orders_sha'] = '1df82bab4faea632fb2593a54fce799680878091aea9184220635e9d43c1dfa7'
st['last_orders_sha_probe_note'] = 'r989: delta 16819a8d->1df82bab consumed (rows 13:0x-13:5x bm-a/bm-c MV domain zero bm-b legs)'
st['orders_delta_pending'] = False
st['last_decisions_at'] = NOW
st['last_decisions_read_at'] = NOW
st['last_decisions_sha'] = '1d4741e4a0d6514519040442182b0679a423d58896a4105861e152108be441f1'
st['decisions_delta_pending'] = False
st['d19_probe_due'] = False
st['d19_watermark_guard']['round_ref'] = 989
st['d19_watermark_guard']['ts'] = NOW
st['sat_engine']['checked_at'] = NOW
st['latest_artifact'] = 'r988 replayed on origin tip 4237047b3 (S0) + EPBurn handover 5 files on origin (14:03 estate) + madmom-install.log in-flight'
st['last_artifact'] = st['latest_artifact']
sync = st.setdefault('sync', {})
sync['r989_main_push'] = {
    'status': 'PUSH_ATTEMPTED_CLOSING',
    'pushed_sha': 'pending',
    'consumed_at': 'pending r990',
    'behind_origin_main': 0,
    'note': 'C-r989 payload = own faces (state/heartbeat/round report + S6 regen diff faces + estate recovered files + MSG-0910 processed move); base = origin tip 20b7f265f (post-rebase); docs faces excluded (anti-regression, r982 policy)'
}
sync['r988_main_push'] = {
    'status': 'PUSHED_VERIFIED',
    'pushed_sha': '4237047b3 (rebase-replay of df8b799ad, conflict faces resolved origin-side)',
    'consumed_at': NOW,
    'behind_origin_main': 0,
    'note': 'r988 commit replayed during r989 S0 rebase; conflict set = 17 shared regen faces taken origin (regen law)'
}
with io.open(STATE, 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat ---
with io.open(HB, 'r', encoding='utf-8') as f:
    hb = json.load(f)
hb['round_no'] = 989
hb['round'] = 989
hb['ts'] = NOW
hb['clock_read'] = NOW
hb['last_seen'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
hb['did'] = did
hb['verdict'] = verdict
hb['next'] = next_
hb['task'] = 'r989: closeout (state/heartbeat/push)'
hb['current_task'] = 'r989: closeout (state/heartbeat/push)'
hb['idle_rounds'] = 0
hb['agenda_starved'] = True
hb['latest_artifact'] = 'EPBurn handover verified on origin (estate) + allin1 madmom build in-flight + S6 40/40 green'
hb['orders_ack'] = ("r989: D-19 orders delta consumed 16819a8d->1df82bab (new rows 13:0x V5.2/V5.3 line + bm-c fill order - "
                    "zero bm-b legs; O-0100 @bm-b leg already closed r988); decisions unchanged 1d4741e4; "
                    "watermarks: orders -> 1df82bab, decisions -> 1d4741e4")
with io.open(HB, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# verify epoch int
with io.open(HB, 'r', encoding='utf-8') as f:
    check = json.load(f)
assert isinstance(check['heartbeat_epoch_utc'], int), 'epoch must be int'
print('CLOSEOUT_OK ts=%s epoch=%d idle_rounds=%d' % (NOW, EPOCH, check['idle_rounds']))
