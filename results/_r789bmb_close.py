# r789 bm-b close-out: state.json (honest jump 786->789 absorbing dead r787/r788 per r714 law)
# + D-19 watermark advance + heartbeat update with ack +1 (O-20261006-2358) + int-epoch self-verify.
import json, time, datetime

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

# ---- state.json ----
sp = 'state.json'
st = json.load(open(sp, encoding='utf-8'))
st['machine_id'] = 'bm-b'
st['round_no'] = 789
st['round_no_label'] = 'r789'
st['note'] = ("r789: dead r787/r788 tails absorbed (r787 S6 chain 38-leg rc0 23:34-23:55 + r788 S0 absorb b5a4c9587 + "
              "O-20261006-2358 bm-b 3-face receipt landed pre-death, absorbed this round fef5d3db0; honest jump 786->789 per r714 law). "
              "Main product: D-06 CODELY.md main-file incremental re-sweep closed the size gate 31,590->29,255B (<=30,720B, 1,465B headroom) "
              "ahead of the D-20261002-06 extension window 10-09 00:00 (per D-20261007-01(3)): 3 newest pit entries verbatim-migrated "
              "(r640 QA round-label race -> pit-protocol-lane.md 867B sha16 b976051eddf6def5 + r642 autostash-pop conflict-death recipe "
              "-> pit-git-resolver.md 1213B sha16 c813e01b7ab44e8f + r787 rebase-continue fake-conflict windowing -> pit-git-resolver.md "
              "1190B sha16 d274a35e61043e23), migration ritual r441/r703/r783 same (prescan rc3 x4 logged, registry in-out row appended, "
              "byte equation exact, all 25 pit files <=30,720B, marker scan clean). QA pack r789 5/5 detached --round 789 explicit "
              "(r758 law), terminal-state polled per r640 law before this close. Q/D trio burns alive via autofill.")
st['last_round_at'] = now
st['ts'] = now
st['updated'] = now
st['last_seen'] = now
st['last_round_ts'] = now
st['clock_read'] = now
st['last_decisions_sha'] = '635C3024A95E4487A08E55BE9DAD3A97E41C73726A9D82D955986D95EF6F6AF6'
st['last_decisions_at'] = now
st['last_decisions_read_at'] = now
st['last_orders_sha'] = '9BE6A74F882866653504717DBAA2E52FAA92D913699BFEE22BB767E0AAF6CE21'
st['last_orders_read_at'] = now
st['last_orders_sha_note'] = ("r789: ord delta consumed via results/_r789bmb_d19_read.py (r770 bm-a recipe lineage, r631 sparse-clone, "
                              "ssh-first dual-URL r677 law): 10-07 ~00:1x token-saving/local-compute row = group-side executed batch "
                              "(ledger split wave-3 + BGM local loop + rmbg queue + spill pool), zero new BigMoney dispatch; "
                              "fleet/orders side: O-20261006-2358 bm-b receipt (executed by dead r788) acked this round 162->163")
st['last_decisions_sha_method'] = ("SHA-256 hex upper of git show origin/main:docs/decisions.md raw bytes (sparse-clone --no-checkout, "
                                   "r631/r770 recipe, D-20261024-02(3)); computed in-script by results/_r789bmb_d19_read.py")
st['next'] = ("(1) trio Q finalize watch ~10-07 morning (Q 1838/2000 @00:35 face, autofill burning), D ~10-07 evening; first-to-2000 "
              "finalize same-window per r668 law, window 10-05..10-09, G4 PENDING r638 fallback armed; "
              "(2) market reopen 10-08: S6 legs 25-28 resume + REGIME_GUARD v3 first new bar enforce; "
              "(3) CODELY.md main 29,255B watch (new pit laws enter main first then re-sweep per law; D-20261002-06 window 10-09 00:00 "
              "criterion met early this round, keep headroom 1,465B); "
              "(4) O-20261006-2358 trio self-claim law: post-trio-close <=1h claim one backlog item")
st['did'] = ("r789: dead r787/r788 absorb + S0 churn-absorb fef5d3db0 (r788 order receipt uncommitted tail) + D-19 dual consumed "
             "(dec A44C39E0->635C3024 3 new rows 10-07 batch: D-20261007-01 receipt-batch 20 + D-07-02 ledger-close + D-07-03 stamp-writer "
             "dispatch [zero BigMoney action, bigmoney-relevant face = D-20261002-06 extension to 10-09 with measured 31,320B -> closed by "
             "this round's sweep]; ord 9A273ECA->9BE6A74F 1 row token-saving batch zero BM action) + smoke 48/48 + QA pack r789 5/5 "
             "detached + D-06 main-file sweep 31,590->29,255B + S6 face = r787 chain 38/38 rc0 fresh (white-run law, no re-run) + "
             "S7 quartet 4/4 + attrition guard 4 ledgers CLEAN")
st['verdict'] = ("green: D-06 size gate closed early (31,590->29,255B, window 10-09); Q/D burns alive (1838/1518 of 2000 @00:35); "
                 "orders 163/163; smoke 48/48; QA r789 5/5; satengine alive rc0 idle")
st['current_task'] = ("r789 closed; next = trio Q finalize ~10-07 morning / D ~10-07 evening + market reopen 10-08 "
                      "(S6 legs 25-28 + REGIME_GUARD v3 first new bar)")
with open(sp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- heartbeat fleet/machines/bm-b.json ----
hp = 'fleet/machines/bm-b.json'
hb = json.load(open(hp, encoding='utf-8'))
hb['last_seen'] = now
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now
hb['ts'] = now
hb['updated'] = now
hb['last_round_at'] = now
hb['round_no'] = 789
hb['round'] = 789
hb['last_action'] = ("r789 closed: dead r787/r788 absorb + D-06 CODELY main-file sweep 31,590->29,255B (gate closed early, window 10-09) "
                     "+ D-19 dual consumed (dec +3 rows / ord +1 row, zero BM action) + smoke 48/48 + QA pack r789 5/5 detached "
                     "+ O-20261006-2358 ack 162->163")
hb['now_active'] = ("FUND trio NULLS judgment batch: V COMPLETE 2000/2000; Q/D burns alive via autofill keepalive "
                    "(Q 1838/2000 @00:35 eta ~10-07 morning, D 1518/2000 eta ~10-07 evening); finalize window 10-05..10-09, "
                    "G1 pending Q+D, G4 governance pending r638 fallback armed; post-close <=1h self-claim law armed")
hb['latest_artifact'] = ("results/_r789bmb_codely_increment.json (D-06 migration receipt: 3 pit entries verbatim, byte equation exact, "
                         "all 25 pit files <=30,720B) + qa/smoke-r789.md 5/5 (93 trades determinism=True, golden-week no-op data face) "
                         "@00:4x-00:5x")
hb['next_milestone'] = ("trio Q finalize ~10-07 morning / D ~10-07 evening (first-to-2000 same-window finalize per r668 law) + "
                        "market reopen 10-08 (S6 legs 25-28 + REGIME_GUARD v3 first new bar enforce) + D-06 window verify 10-09 00:00")
hb['verdict'] = hb['verdict'] if False else ("green: r789 closed (D-06 gate 29,255B early + QA 5/5 + dead-session absorb); "
                                             "Q/D burns alive; orders 163/163; smoke 48/48")
hb['task'] = "r789 done; trio Q/D burn watch + market reopen 10-08 prep"
ack = hb.get('orders_ack', [])
new_ord = 'O-20261006-2358-bm-c.md'
if new_ord not in ack:
    ack.append(new_ord)
    ack.sort()
hb['orders_ack'] = ack
hb['orders_ack_count'] = len(ack)
with open(hp, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- self-verify: epoch int + ack count + round ----
chk = json.loads(open(hp, encoding='utf-8').read())
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert chk['orders_ack_count'] == 163 and 'O-20261006-2358-bm-c.md' in chk['orders_ack'], 'ack must be 163 with 2358'
assert chk['clock_read'] == chk['ts'] and 'T' in chk['clock_read'], 'clock_read must equal ts with T separator'
st2 = json.loads(open(sp, encoding='utf-8').read())
assert st2['round_no'] == 789
print('state.json round 789 + heartbeat epoch %d int + ack 163 self-verified @%s' % (chk['heartbeat_epoch_utc'], now))
