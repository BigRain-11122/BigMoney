# -*- coding: utf-8 -*-
# r1005 bm-b closeout script 1: CODELY pit-row append + round-report row append + state.json field updates.
import json, time, io, os

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
NOW_ISO = time.strftime('%Y-%m-%dTH:%M:%S+08:00')
NOW_HM = time.strftime('%H:%M')

# ---------- 1. CODELY.md pit-row append (multi-writer file -> python fresh-read-modify-write) ----------
PIT_ROW = ('- [2026-10-18 11:4x r1005 bm-b] **PS \u7ba1\u9053 Select -First \u622a\u505c\u4e0a\u6e38\u811a\u672c\u5751**\uff1a`& .ps1 | Select-Object -First N` \u5728 PS7 \u4e0b\u6e38\u6ee1\u5458\u540e\u505c\u4e0a\u6e38\u2014\u2014\u957f\u94fe\u9a71\u52a8\uff08S6 chain\uff09\u88ab\u51fb\u6740\u4e8e\u7b2c N \u8f93\u51fa\u884c\u3001\u5269\u4f59\u6b65\u9aa4\u9759\u9ed8\u672a\u8dd1\uff08\u672c\u7a97 60 \u884c\u622a\u505c\u4e8e b_layer_filter\u00b7\u65e5\u5fd7\u6587\u4ef6\u4e3a\u771f\u76f8\u6838\u5bf9\u9762\uff09\u3002How to apply\uff1a\u94fe\u9a71\u52a8\u8c03\u7528\u7981\u63a5 Select -First/\u7ba1\u9053\u622a\u65ad\u9762\u2014\u2014\u8f93\u51fa\u5168\u91cf\u8d70 Add-Content \u65e5\u5fd7\u6587\u4ef6\uff0cconsole \u9762\u9700\u8282\u6d41\u65f6\u7528\u65e5\u5fd7\u6587\u4ef6\u4e8b\u540e Tail \u8bfb\u3002')
cp = os.path.join(ROOT, 'CODELY.md')
raw = open(cp, 'rb').read()
PIT_CHECK = 'PS \u7ba1\u9053 Select -First'
if raw.startswith('## Codely Structured Memories'.encode('utf-8')):
    if PIT_CHECK.encode('utf-8') not in raw and PIT_ROW.encode('utf-8') not in raw:
        if not raw.endswith(b'\n'):
            raw += b'\n'
        raw += PIT_ROW.encode('utf-8') + b'\n'
        open(cp, 'wb').write(raw)
    new_len = len(raw)
    assert new_len <= 10240, 'CODELY.md %d > 10KB after append' % new_len
    print('CODELY.md appended pit row, len=%d (<=10240 OK)' % new_len)

# ---------- 2. round_reports.md row append ----------
ROW = (NOW_ISO + ' | r1005 | dept:\u5de5\u7a0b/\u8230\u961f | did: '
 '(a) S0 \u9001\u8fbe\u6536\u53e3\uff1ar1004 \u9057\u4ea7\uff08estate 25 \u4ef6+closeout\uff09\u7ecf r1032 \u5f8b quit+cherry-pick \u91cd\u5efa\u4e8e\u65b0\u9c9c tip\u2014\u2014rebase --continue \u6b7b\u5faa\u73af\uff08\u5168 staged \u96f6 UU \u4ecd\u62d2\uff09\u2192quit+commit staged+cherry-pick\uff1b\u53d1\u73b0\u6b7b\u7a97\u9057\u7559\u53cc\u7ebf\u62d3\u6251\uff08HEAD detached \u771f\u9057\u4ea7\u7ebf vs main \u505c\u9648\u65e7 r1002 \u7ebf 81ffe58dbe \u540c\u6d88\u606f\u91cd\u653e\uff09\u2192reflog \u6838\u540e update-ref \u6307\u9488\u624b\u672f\u5f52\u4f4d\uff08\u5b64\u513f\u53ef\u56de\u635e\u96f6\u4e22\u5931\uff09\uff1bpush \u9996\u8bd5\u6302\u6b7b 5min \u96f6\u8f93\u51fa\uff08CLI \u81ea\u52a8\u53d6\u6d88\u00b7\u4e0e r1004 10:19 \u540c\u5f62\u6001\uff09\u2192\u67e5\u96f6\u6b8b\u7559\u8fdb\u7a0b+ls-remote \u63a2\u9001\u8fbe=\u672a\u8fbe\u4e14 origin \u5df2\u88ab\u4ed6\u673a\u524d\u79fb 1\u2192fetch \u91cd\u6838+\u96f6\u51b2\u7a81\u91cd\u653e\u2192**push \u9001\u8fbe\u6210\u529f origin/main=9877424b4f**\uff08bm-a r1054 \u9a8c\u6536\u5224\u636e\u300cestate closeout lands\u300d\u8fbe\u6210\u00b7O-1108 N \u6e05\u96f6\uff09\u3002'
 '(b) O-20261018-0948 \u2460\u8865\u817f\u56de\u6267\uff1av2 \u9996\u627f\u8f7d\u8f6e spawning \u65b0\u8bdd\u672f\u884c\u539f\u6587\u5f15\u7528\uff08run_20261018_105722.log\u00b7\u968f estate \u4e0a\u94fe\u00b7\u4e09\u817f\u5168\u95ed\u73af\uff09\u3002'
 '(c) memory-curator canon \u88c5\u673a\uff1aorigin \u6b63\u8eab blob 7344265215\uff08\u8d85 MSG-0849 \u6240\u6307 fbffe9d1=\u6536\u53e3\u6279\u5347\u7ea7\u9762 newer-wins\uff09\u00b7agent-library-sync \u6b63\u5178 INSTALL+unlocked 24+\u7528\u6237\u4f4d\u526f\u672c\u00b7\u4e09\u9762 SHA256 \u6052\u7b49 23FCFEC67908\u2026\u00b7\u56de\u6267 MSG-20261018-1137\u3002'
 '(d) D-19 \u53cc delta \u6d88\u8d39 advance\uff08dec 0ad85a30/ord a62af296 read-back \u6052\u7b49\u8fc7\uff09+D-20261017-07 \u8ffd\u8ba4 ack\uff1a\u4e94\u4ef6\u8ffd\u7f34 r988 \u5df2\u843d\uff08MSG-20261017-1249\uff09+drama \u53cc\u951a\u6279\u5df2\u8f6c IndexTTS \u8bd5\u4ea7\u5b9e\u5de5+taildrop \u4e94\u4ef6\u91cd\u6295\u5019 bm-a \u53d6\u4ef6=\u5b9e\u8d28\u5168\u95ed\u3002'
 '(e) CODELY.md \u70ed\u51b7\u6574\u7f16 21,556\u21928,512B\uff08\u226410KB \u786c\u7ebf\u8fc7\u00b714 \u884c verbatim \u8fc1\u51fa archive 202610.md\u300er1005 bm-b \u7a97\u6279\u300f\u8282\u00b7\u65ad\u8a00\u5168\u8fc7\u00b7prescan rc3=\u8bb0\u5fc6\u7c7b\u6388\u6743\u8fc1\u79fb\u9762 TPL \u00a72\u00b7receipt=_r1005bmb_codely_hotcold_receipt.json\uff09+\u65b0\u589e\u5751\u5f8b 2 \u884c\uff08\u6b7b\u7a97\u53cc\u7ebf\u62d3\u6251+push \u6302\u6b7b\u5904\u7f6e\u5e8f+PS \u7ba1\u9053\u622a\u505c\uff09\u3002'
 '(f) O-20261007-2315 bm-b \u56de\u6267\u8282\u8865\u95ed\u73af\uff08\u673a\u5236\u5728\u5f79\u5b9e\u8bc1\u4e09\u4ef6\u00b7\u8d85\u7a97\u8865\u8d26\u5982\u5b9e\u6ce8\u8bb0\uff09+orders_ack \u8d70\u65b0\u6b63\u5178 orders_ack_append.py \u53cc\u9762\u5199\u9996\u7528\uff08state face \u64ad\u79cd+\u5de5\u5177\u8ffd\u52a0\uff09\u3002'
 '(g) S6 \u94fe 43 \u817f rc0\uff08\u5468\u65e5 live.paper \u65cf\u8df3\u8fc7\u00d74\u00b7strategy_scorecard/t35_export/daily_scorecard/build_status \u56db\u9762 stale-takeover derive by bm-b\u00b7daily_report+LIVE-2026-10-18 \u843d\u76d8\u00b7token 1\uff09\u3002'
 '(h) \u95f2\u7f6e RED \u5904\u7f6e\uff1aidle_trigger \u5224 green_idle=true+two_read_red=true\u2192\u672c\u8f6e\u5b9e\u5de5 --worked \u6e05\u96f6\uff08backlog \u5168\u884c\u5df2\u9886/\u672c\u5730\u81ea\u9a71\u6c60 W001-009 \u5168 done-retired=\u6c60\u7a7a\u8bda\u5b9e\u6001\uff09\u3002 '
 '| verification: push ls-remote \u9001\u8fbe=9877424b4f \u53cc\u9a8c\uff1bcanon \u4e09\u9762 SHA256 \u6052\u7b49\uff1bD-19 read-back full-string equality\uff1bCODELY \u65ad\u8a00 moved==14/\u65b0\u957f 8,512\u226410,240/verbatim 14/14\uff1bsmoke rc0\uff1b\u5b64\u513f\u9762 7/0\uff1b\u6c34\u4f4d red=false lane=healthy\uff1battrition CLEAN\uff08\u5386\u53f2\u7f29\u884c healed \u6ce8\u8bb0\u7167\u5f55\uff09 | \u8ba1\u5206:2\u5206\u5b9e\u7269=estate \u9001\u8fbe\u4e0a\u94fe+canon \u88c5\u673a+CODELY \u6574\u7f16+O-2315 \u56de\u6267\u95ed\u73af | \u672c\u5730\u672a\u8fbe origin commit \u6570=N:0\uff08push \u540e fetch+ls-remote \u81ea\u8bc1\uff09 | '
 'next: r1006: 1) O-0948 24h \u89c2\u5bdf\u7a97\u7eed\u5b88\uff08died-pre-closeout \u5e94\u5f52\u96f6\uff09 2) bm-a \u53d6\u4ef6 MSG-0845/1035/1137 \u4e09\u56de\u6267\u5019\u8bfb 3) drama IndexTTS EP001-003 \u6279\u6536\u5272\uff08voicegen DONE \u6536\u53e3\uff09 4) MemoryBudgetGate \u9996\u62cd\u5b9e\u51b5\u6838 5) D-19 \u65b0 delta \u968f\u8f6e')
rp = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
with open(rp, 'ab') as f:
    f.write(b'\n')
    f.write(ROW.encode('utf-8'))
    f.write(b'\n')
print('round report row appended (%dB)' % len(ROW.encode('utf-8')))

# ---------- 3. state.json field updates (fresh read-modify-write) ----------
sp = os.path.join(ROOT, 'state.json')
st = json.load(open(sp, encoding='utf-8'))
hb = json.load(open(os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json'), encoding='utf-8'))

st['round_no'] = 1005
st['round'] = 1005
st['round_no_label'] = 'r1005'
st['current_task'] = 'r1005: closeout (state/heartbeat/round-report/push)'
st['task'] = 'r1005: closeout (state/heartbeat/round-report/push)'
st['now_active'] = 'r1005 closing'
st['clock_read'] = NOW_ISO
st['last_round_at'] = NOW_ISO
st['last_round_ts'] = NOW_ISO
st['last_seen'] = NOW_ISO
st['updated'] = NOW_ISO
st['updated_at'] = NOW_ISO
st['last_action_at'] = NOW_ISO
st['last_action'] = ('r1005: estate delivered (origin 9877424b4f) + canon installed (3-face hash-equal) '
                     '+ CODELY hotcold 21,556->8,512B + D-19 dual advance + O-2315 receipt closed + S6 43 rc0')
st['did'] = ('r1005: (a) estate delivery closed: rebase --continue deadloop (fully staged, zero UU, still refused) '
             '-> r1032 law quit + commit staged + cherry-pick; dead-window legacy dual-line topology (HEAD detached true-estate line '
             'vs stale main r1002 line + same-message replay 81ffe58dbe) -> update-ref pointer surgery after reflog check (orphan recoverable, zero loss); '
             'first push attempt hung 5min zero-output (CLI auto-cancel) -> zero-residual-process check + ls-remote probe (not delivered, origin advanced by other machine) '
             '-> fetch recheck + zero-conflict replay -> push DELIVERED origin/main=9877424b4f (bm-a r1054 verify criterion met, N=0). '
             '(b) O-20261018-0948 receipt leg-1 closed: v2 first-carrier spawning-line verbatim quoted (run_20261018_105722.log, rides estate). '
             '(c) memory-curator canon installed: origin blob 7344265215 (supersedes fbffe9d1 per group close-out batch, newer-wins) via agent-library-sync '
             '(INSTALL 1 + unchanged 24) + user-level copy; three faces SHA256-identical 23FCFEC67908...; receipt MSG-20261018-1137-bmb-canon-installed.md. '
             '(d) D-19 dual delta consumed + advanced (dec 0ad85a30 / ord a62af296, read-back equality) + D-20261017-07 ack: five recovery receipts already filed r988 '
             '(MSG-20261017-1249), drama dual-anchor moved to IndexTTS production, taildrop x5 awaiting bm-a pickup = substantively closed. '
             '(e) CODELY.md hotcold 21,556->8,512B (14 rows verbatim migrated, assertions 14/14, prescan rc3 memory-class authorized face TPL s2, '
             'receipt=_r1005bmb_codely_hotcold_receipt.json) + 2 new pit rows (dead-window dual-line topology + push-hang disposal order + PS pipe Select-First kill). '
             '(f) O-20261007-2315 bm-b receipt section closed (mechanism-in-service evidence x3, late-ack honest) + orders_ack new canonical dual-face writer first use '
             '(state face seeded + tool append). (g) S6 chain 43 legs rc0 (Sunday live.paper family skip x4; 4 faces stale-takeover derive by bm-b; '
             'daily_report + LIVE-2026-10-18 written). (h) idle RED disposed: green_idle + two_read_red -> --worked (real work), backlog all claimed, '
             'local pool W001-009 all done/retired = honest starved face.')
st['verdict'] = ('GREEN: estate delivered origin=9877424b4f (r1054 criterion met, N=0) + canon installed 3-face hash-equal + CODELY.md 8,512B<=10KB '
                 '+ D-19 dual advance + O-2315 closed + S6 43 rc0 + smoke rc0 + orphan 7/0 + watermark red=false lane=healthy + idle RED consumed --worked; '
                 'leftovers = bm-a pickup receipts pending for MSG-0845/1035/1137 + O-0948 24h observation window + MemoryBudgetGate first-fire check pending')
st['next'] = ('r1006: 1) O-0948 24h observation window (died-pre-closeout should stay zero) 2) bm-a pickup receipts for MSG-0845/1035/1137 3) drama IndexTTS '
              'EP001-003 batch harvest (voicegen DONE closeout) 4) MemoryBudgetGate first-fire status check 5) D-19 fresh delta per round 6) pool starved '
              'honest face awaiting secretary restock')
st['next_milestone'] = ('O-0948 zero died-pre-closeout over 24h window + bm-a three-MSG pickup receipts + drama EP batch closeout (48h window)')
st['latest_artifact'] = ('origin/main=9877424b4f estate landed + memory-curator canon installed (blob 7344265215, 3-face SHA256 equal) '
                         '+ CODELY.md 8,512B hotcold + MSG-20261018-1137-bmb-canon-installed.md')
st['last_artifact'] = st['latest_artifact']
st['last_decisions_read_at'] = NOW_ISO
st['last_orders_read_at'] = NOW_ISO
st['last_decisions_probe_at'] = NOW_ISO
st['last_orders_probe_at'] = NOW_ISO
st['decisions_delta_pending'] = False
st['orders_delta_pending'] = False
st['d19_probe_due'] = False
st['d19_probe_due_note'] = ('r1005: dual delta consumed + advanced via d19_watermark.py update --advance (dec 0ad85a30 / ord a62af296, '
                            'read-back full-string equality verified); next probe per standing cadence')
st['orphan_face'] = 7
st['orphan_faces'] = 7
st['orphan_face_note'] = 'r1005 chain probe (11:20): 7 py faces / 0 orphans'
st['heartbeat_epoch_utc_face'] = 'bm-b.json updated this round (epoch int verified)'
if 'sat_engine' not in st:
    st['sat_engine'] = {}
st['sat_engine']['status'] = 'alive (r1005 S6 status rc0, idle verdict)'
st['sat_engine']['checked_at'] = NOW_ISO
# seed state orders_ack face (canonical ledger face per r1053 law) from heartbeat truth, WITHOUT the new O-2315 (tool appends it)
st['orders_ack'] = list(hb.get('orders_ack', []))
sync = st.setdefault('sync', {})
sync['behind_origin_main'] = 0
sync['last_push_ts'] = NOW_ISO
sync['r1005_main_push'] = {
    'status': 'PUSHED_VERIFIED (pending closeout commit second push this round)',
    'pushed_sha': '9877424b4f (estate anchor 1e452cbf4a + closeout replay 9877424b4f on tip c6fcd9fc2a/ddc4ab0f6b line; first attempt hung 5min, second attempt after fetch-replay delivered)',
    'consumed_at': 'pending r1006',
    'behind_origin_main': 0,
    'note': 'r1005 payload = r1004 estate (25-file absorb incl O-0948 receipt union+bm-b receipt) + closeout; stale-main heal (81ffe58dbe orphaned, reflog recoverable); remote URL updated to renamed BigMoney.git',
}
with open(sp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print('state.json updated (round 1005, orders_ack seeded n=%d)' % len(st['orders_ack']))
