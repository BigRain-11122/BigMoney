# -*- coding: utf-8 -*-
"""r682 bm-a S7 bookkeeping: state round_no 681->682 (procedural json write +
json.loads self-verify per r645 law) + heartbeat update (epoch int via
int(time.time()), clock T-format per R170/R178/R262 laws)."""
import json, time, datetime, sys, io, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- state face ----
fp = os.path.join(REPO, 'state-bm-a.json')
s = json.load(open(fp, encoding='utf-8'))
assert s.get('round_no') == 681, f"round_no anchor drift: {s.get('round_no')}"
s['round_no'] = 682
s['current_task'] = ("r682 done: W116 pre-seat probe ADMIT-derive receipt (yielded to bm-b per sec.4 "
                     "commit-time order, evidence kept) + N4-B4 no-timepoint gap-finder landmine "
                     "finding (CODELY pit + MSG-ALL) + S6 37/37; next: W117 post-bm-b-W116 + G2 stage-2 prereg candidate")
s['did'] = ("r682: S0 daemon lane absorb + merge origin zero-UU DELIVERED + S0.5 orders 154/154 "
            "dual-scan zero-unacked + D-19 decisions sha MATCH (sparse-clone git-show) + S1 smoke "
            "48/48 + W116 probe rc0 A 275_004..277_003/B 62_701..62_900 CLEAN (yield bm-b 14:52:52 "
            "claim) + N4-B4 gap-finder scan (first-clean=275_004..276_500=N1 A-ladder active path "
            "landmine; B3 sec.5 no-B4-timepoint + O-1901 meaning gate = line stays complete at "
            "K_eff=499) + MSG-2026-10-04-1600-bma-ALL (yield receipt + N4 evidence + bm-a engine "
            "honest supply state) + CODELY pit line + S6 37/37 rc0 85.4s + self-heal 4/4")
with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(s, fh, ensure_ascii=False, indent=1)
chk = json.load(open(fp, encoding='utf-8'))
assert chk['round_no'] == 682, "state reparse drift"
print("state round_no 681->682 OK (reparse verified)")

# ---- heartbeat face ----
hp = os.path.join(REPO, 'fleet', 'machines', 'bm-a.json')
h = json.load(open(hp, encoding='utf-8'))
epoch = int(time.time())
clock = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec='seconds')
h['last_seen'] = clock
h['current_task'] = ("r682: W116 pre-seat probe ADMIT-derive A 275_004..277_003/B 62_701..62_900 CLEAN "
                     "rc0 -> seat YIELDED to bm-b (sec.4 commit-time order, bm-b r676 addendum 14:52:52 "
                     "origin-first; probe receipt = second-machine convergence evidence for bm-b freeze); "
                     "N4-B4 no-timepoint: B3 sec.5 frozen clause + O-1901 meaning gate + gap-finder "
                     "landmine (first-clean-above-family = N1 A-ladder active W116 path) -> N4 line "
                     "stays complete K_eff=499; engine queue 0 honest (trio=bm-b lane, N2=bm-b slice-2, "
                     "W117 awaits bm-b W116 registration)")
h['verdict'] = "healthy supply-yield round"
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = clock
if 'orders_ack' in h:
    assert len(h['orders_ack']) == 154, f"orders_ack count drift {len(h['orders_ack'])}"
with open(hp, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)
chk2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int) and not isinstance(chk2['heartbeat_epoch_utc'], bool), \
    "epoch must be JSON int"
assert 'T' in chk2['clock_read'] and '+' in chk2['clock_read'], "clock must be T-format ISO8601"
print("heartbeat updated: epoch", epoch, "clock", clock, "(int+T-format verified)")
