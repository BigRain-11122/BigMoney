# -*- coding: utf-8 -*-
# r588 bm-a wrap: pit-git lesson + state/heartbeat/report + commit + push
import subprocess, sys, os, json, time, datetime, psutil
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREAT = 0x08000000

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', creationflags=CREAT)
    if check and r.returncode != 0:
        print('FAIL rc=%d: %s' % (r.returncode, ' '.join(cmd[:4])))
        print((r.stdout or r.stderr)[-400:]); sys.exit(1)
    return r

now_iso = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# 1. pit-git.md lesson (bytes-level, EOL-safe)
P = 'research/pit-git.md'
raw = open(P, 'rb').read()
eol = b'\r\n' if raw.count(b'\r\n') * 2 > raw.count(b'\n') else b'\n'
lesson = ("- [2026-10-02 18:5x r588 bm-a] \u5916\u79d1 reset --mixed \u540e M \u9762\u524d\u7f00\u5206\u7c7b\u9a71\u52a8\u5751"
          "\uff08W109 \u540c\u7a97\u5b9e\u5f39\u00b7stale \u4ed6\u673a\u6b63\u5178\u9762\u81ea\u6d4b\u5047\u7eff\u969c\u788d\u9762\u81ea\u67e5\u6293\u56de\uff09\uff1a"
          "\u5916\u79d1 push+update-ref+reset --mixed \u5e8f\u5217\u540e\u7684 ' M' \u6001\u6587\u4ef6\u6df7\u4e24\u7c7b"
          "\u2014\u2014\u2460\u672c\u673a\u6d3b\u5199/\u672c\u673a\u4ea7\u51fa\uff08\u4fdd\u7559\uff09\u2461\u4ed6\u673a canonical \u6587\u4ef6\u672c\u5730\u65e7\u7248"
          "\uff08worktree==\u65e7\u57fa blob=stale\uff0c\u987b checkout \u6062\u590d HEAD\uff09\uff1b\u672c\u8f6e\u53ea\u6062\u590d ' D' \u9762\u6f0f ' M' \u9762"
          "\u2192 n1 selftest \u5728 stale bm-b \u4ee3\u7801\u4e0a\u8dd1\uff08W109 materializer leg \u7f3a\u5e2d\u4ecd PASS"
          "\uff1d\u5047\u7eff\u969c\u788d\u9762\u975e\u5047\u7eff\u5224\u636e\u2014\u2014W104 leg \u5728\u573a\u4e14\u8fc7\uff0c\u5e78\u96f6\u5bb3\uff09\u3002"
          "\u6b63\u6cd5=reset \u540e\u5bf9 M \u9762\u9010\u4ef6\u5206\u7c7b\uff1aworktree blob==\u65e7\u57fa blob\u2192checkout -- \u6062\u590d\uff1b"
          "\u6062\u590d\u9762\u5fc5\u987b\u5206\u7c7b\u9a71\u52a8\u7981\u524d\u7f00\u9a71\u52a8\uff08r578 \u5f8b\u7684\u6267\u884c\u9762\u7ec6\u5219\uff09\u3002").encode('utf-8')
if b'r588 bm-a' not in raw:
    if not raw.endswith(eol):
        raw += eol
    raw += lesson + eol
    open(P, 'wb').write(raw)
    print('pit-git lesson appended')

# 2. state
s = json.load(open('state-bm-a.json', encoding='utf-8'))
s["round_no"] = 588
s["did"] = ("r588: W107 burn products 12/12 delivered to origin (254b9d3f0, K=2,200, ledger rides 24 rows append-only) "
            "+ W104 FINALIZE landed one-pass first-run (prev 591,148 W103 bm-b + 2,200 = 593,348, K=226,720, "
            "merged mu=-0.09276131 sigma=0.24486278, skill_line 1.1697->1.1696 K-lift -0.0001, S5 four gates ALL PASS "
            "on W99 frozen anchor, 0abbaa458) + W110 seat published (MSG-20261002-1829-bma, f457e1c4f) + W110 band gate "
            "ADMIT rc0 (A 263_004..265_003 / B 61_201..61_400, 100th engine wave by machine-derive, bm-a 31st owned) "
            "+ S6 36 legs green + D-19 10-02 batch consumed (D-20261002-05 receipt=executed r575; D-06 engine domain "
            "split landed r585, data/protocol by 10-07; D-07/08/09 non-BigMoney zero-action)")
s["verify"] = ("smoke 47/47; n1 selftest PASS (W109 leg live post-M-face restore); pf 9/9; attrition guard CLEAN; "
               "dualrun ZERO-DRIFT streak 51/3; WM py_low_board_clear legal idle (holiday board-clear + engine lane "
               "supply gap closing via W110 freeze next round)")
s["next"] = ("W110 five-face freeze = r589 primary (prereg gen from W109 prereg copy-adapt family + freeze edits "
             "r587/r588 pattern + engine ignition within 2 ticks; anchors roll to W104 landed values 593,348/226,720 "
             "per r576); W105 bm-c finalize unblocked by my W104; W107 own finalize awaits W105/W106 chain order; "
             "D-20261001-03 wording ack due 10-03 12:00; D-20261002-06 remaining domains data/protocol + flow-sinking due 10-07")
s["last_round_at"] = now_iso
s["last_round_ts"] = now_iso
s["last_round"] = "r588"
s["updated"] = now_iso
s["last_decisions_sha"] = "13DCB81ABCF2670F139C5603BEB18A487B291DC8A9F463709ED2AD87D1E264A8"
s["last_decisions_at"] = now_iso
s["current_task"] = ("r588 bm-a: W104 FINALIZE landed (593,348/K=226,720, 0abbaa458) + W107 products delivered "
                     "(254b9d3f0) + W110 seat+gate ADMIT (A 263_004..265_003/B 61_201..61_400); next = W110 five-face freeze")
s["last_seen"] = now_iso[:19]
json.dump(s, open('state-bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state round_no ->', s["round_no"])

# 3. heartbeat (r583 law: load existing -> update dynamic fields only)
h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
vm = psutil.virtual_memory()
h["last_seen"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["current_task"] = s["current_task"]
h["cpu_util_pct"] = psutil.cpu_percent(interval=0.5)
h["free_ram_gb"] = round(vm.available / 1e9, 1)
h["round_no"] = 588
h["verdict"] = ("W104 FINALIZE landed 593,348 K=226,720 (S5 4/4 on W99 anchor); W107 12/12 delivered; "
                "W110 seat+gate ADMIT; next round = W110 five-face freeze + ignition")
assert isinstance(h.get("orders_ack"), list) and len(h["orders_ack"]) == 143, "orders_ack must survive 143"
json.dump(h, open('fleet/machines/bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
re_h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(re_h["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print('heartbeat epoch int ok:', re_h["heartbeat_epoch_utc"])

# 4. round report line
rp = 'round_reports-bm-a.md'
raw3 = open(rp, 'rb').read()
eolr = b'\r\n' if raw3.endswith(b'\r\n') else b'\n'
line = ("{ts} | r588 bm-a: W107\u4ea4\u4ed8+W104 FINALIZE \u843d\u8d26+W110 \u5e2d\u4f4d/\u5e26\u95f8 ADMIT -- "
        "\u5f53\u524d\u6d3b=W110 \u4e94\u9762\u51bb\u7ed3\u5f85\u4e0b\u8f6e\uff08\u5f15\u64ce\u961f\u5217\u7a7a=\u4f9b\u7ed9\u5f8b\u89e6\u53d1\u9762\u5df2\u7533\u5e2d\u5e26\u95f8\uff09 | "
        "\u6700\u8fd1\u5b9e\u7269=results/perpetual_faces/n1_w104_results.json\uff08\u94fe\u5934 593,348\u00b7K=226,720\u00b718:2x\uff09"
        "+ n1_w107/ 12 \u5206\u7247\u4ea4\u4ed8\uff08254b9d3f0\uff09+ W110 \u5e2d\u4f4d MSG-20261002-1829-bma\uff08f457e1c4f\uff09 | "
        "\u4e0b\u4e2a\u91cc\u7a0b\u78d1=W110 \u4e94\u9762\u51bb\u7ed3+\u70b9\u706b\uff08r589 \u7a97\u5185\uff09\u2192\u5f15\u64ce\u7eed\u71c3\u00b7W105 bm-c finalize \u968f\u6211 W104 \u89e3\u5c01 | "
        "\u505a\u4e86\u4ec0\u4e48=\u2460S0 \u7eaf FF \u96c6\u6210\uff08behind 4\u00b7\u96f6\u91cd\u53e0\uff09\u2461W107 \u70e7\u5f55 12/12 \u4ea4\u4ed8"
        "\uff08\u5916\u79d1 push \u4e00\u6b21\u649e\u62d2 r374 \u5206\u53c9\u4f2a\u5f71\u2192r523 \u5916\u79d1 254b9d3f0\uff09\u2462W104 finalize one-pass"
        "\uff08r538 \u9996\u8dd1\u552f\u4e00\u4e00\u8dd1\u00b7prev=591,148+2,200=593,348 \u94fe\u6027\u9a8c\u00b7\u00a75 \u56db\u95e8 W99 \u951a\u5168\u8fc7"
        "\uff08|\u0394\u03bc| 0.0136<0.02\u00b7\u03c3 \u22120.025%<\u00b110%\u00b7A p95 \u5dee 0.0165<0.05\u00b7K-lift \u22120.0001\u2265\u22120.02\uff09"
        "\u00b7\u00a77/\u00a78 \u673a\u68b0\u56de\u586b\uff08\u5b57\u8282\u9762\uff09\u2463W110 \u5e2d\u4f4d\u516c\u793a+\u5e26\u95f8 ADMIT rc0"
        "\uff08\u7b2c\u4e00\u767e\u679a\u5f15\u64ce\u6ce2\u00b7bm-a \u7b2c\u4e09\u5341\u4e00\u679a\u81ea\u6709\u6ce2\u00b7hops 0/0\u00b7W111+ \u6295\u5f71 CLEAN CLEAN\uff09"
        "\u2464\u5916\u79d1\u540e M \u9762\u5206\u7c7b\u4fee\u590d\uff08stale bm-b W109 \u4ee3\u7801\u9762 checkout \u6062\u590d\u00b7\u6559\u8bad\u5165 pit-git\uff09"
        "\u2465S6 36 \u817f\u5168\u7eff\u2466D-19 10-02 \u65b0\u6279\u6d88\u8d39\uff08D-05 \u56de\u6267=r575 \u5df2\u6267\u00b7D-06 \u5f15\u64ce\u57df\u5df2\u62c6 r585"
        "\u00b7\u4f59\u57df 10-07\u00b7D-07/08/09 \u975e\u672c\u53f8\u96f6\u52a8\u4f5c\uff09 | "
        "\u9a8c\u8bc1=finalize stdout \u673a\u51fa\u6570+results JSON \u9876\u5c42\u952e+n1/pf selftest \u53cc\u7eff+attrition CLEAN"
        "+dualrun ZERO-DRIFT 51/3+WM=py_low_board_clear \u5408\u6cd5\u95f2\uff08\u5047\u671f\u677f\u6e05+\u5f15\u64ce\u4f9b\u7ed9\u7f3a\u53e3\u4e0b\u8f6e\u95ed\u5408\uff09 | "
        "\u6c34\u4f4d verdict=\u7eff\uff08red=false\uff09 | \u672c\u5730\u672a\u8fbe origin commit \u6570=0\uff08\u63a8\u9001\u540e\u590d\u6838\uff09 | "
        "\u4e0b\u8f6e\u6307\u9488=W110 \u4e94\u9762\u51bb\u7ed3\uff08prereg gen W109 \u62f7\u9002+freeze edits \u5bb6\u65cf\uff09\u2192\u70b9\u706b\u2192W105 bm-c finalize \u76d1\u6d4b"
        "\uff1bD-20261001-03 \u63aa\u8f9e ack 10-03 12:00\uff1bD-06 \u6570\u636e/\u534f\u8bae\u57df\u62c6\u4ef6 10-07").format(ts=now_iso)
with open(rp, 'ab') as f:
    f.write(line.encode('utf-8') + eolr)
print('report line appended')

# 5. commit + push
PAYLOAD = [
    'state-bm-a.json', 'fleet/machines/bm-a.json', 'round_reports-bm-a.md',
    'research/pit-git.md', 'results/_r588bma_w110_band_gate.py',
    'results/_r588bma_s0_ff.py', 'results/_r588bma_orders_scan.py',
    'results/_r588bma_surgical_push.py', 'results/_r588bma_w104_s78_backfill.py',
    'results/_r588bma_extract_refs.py', 'results/_r588bma_extract_refs2.py',
    'docs/daily_report/REPORT-2026-10-02.md', 'docs/daily_report/REPORT-2026-10-02.json',
    'docs/live_usage/LIVE-2026-10-02.md', 'docs/live_usage/LIVE-2026-10-02.json',
    'docs/live_usage/LIVE-latest.md', 'docs/live_usage/LIVE-latest.json',
    'results/update_status.json', 'results/update_status.bm-a.json',
    'results/compute_audit.json', 'results/compute_audit.bm-a.json',
    'results/regime_state.json', 'results/regime_state.bm-a.json',
    'results/strategy_scorecard.json', 'results/scorecard_v1.json',
    'results/dashboard_status.json', 'results/dashboard_status.js',
    'results/t35_open_fill_verify.json', 'results/token_usage.json', 'results/token_usage.bm-a.json',
    'results/fundamental_b_layer_filter.json', 'results/_attrition_guard_scan.json',
    'results/heat_update_status.json', 'results/heat_update_status.bm-a.json',
    'results/lhb_update_status.json', 'results/lhb_update_status.bm-a.json',
    'results/futures_update_status.json', 'results/futures_update_status.bm-a.json',
    'results/options_update_status.json', 'results/moneyflow_update_status.json',
    'results/sina_mf_update_status.json', 'results/repo_update_status.json',
    'results/ah_panel_status.json', 'results/autofill_state.bm-a.json',
    'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
    'results/pool_dualrun.bm-a.jsonl', 'results/pool_core_samples.jsonl',
    'results/saturation_engine/face_bm-a.json', 'results/saturation_engine/history_bm-a.jsonl',
    'results/saturation_engine/ledger_bm-a.jsonl', 'results/saturation_engine/state_bm-a.json',
]
existing = [p for p in PAYLOAD if os.path.exists(p)]
run(['git', 'add', '--'] + existing)
MSG = ("round 588 bm-a close: W104 FINALIZE landed one-pass (593,348/K=226,720, S5 4/4 on W99 anchor) + W107 products "
       "delivered (254b9d3f0) + W110 seat published + band gate ADMIT (A 263_004..265_003 / B 61_201..61_400, 100th "
       "engine wave, bm-a 31st owned) + S6 36 legs green (ZERO-DRIFT 51/3, WM py_low_board_clear legal idle) + "
       "surgical post-reset M-face classifier lesson -> pit-git.md + state/heartbeat/report r588. Five-face W110 freeze "
       "= next-round primary. [via bm-a r588]")
mp = os.path.join('.codely-cli', 'scratch', 'r588bma_msg.txt')
os.makedirs(os.path.dirname(mp), exist_ok=True)
open(mp, 'w', encoding='utf-8', newline='\n').write(MSG)
r = run(['git', 'commit', '-F', mp], check=False)
print('commit rc=', r.returncode, (r.stdout or r.stderr)[:180])
if r.returncode != 0 and 'nothing to commit' not in (r.stdout or '') + (r.stderr or ''):
    sys.exit(1)
r = run(['git', 'push'], check=False)
print('push rc=', r.returncode)
print(((r.stdout or '') + (r.stderr or ''))[:220])
if r.returncode != 0:
    print('PUSH-REJECT: wrap push needs follow-up (surgical per r523)')
# delivery verification (O-20261001-1108)
run(['git', 'fetch', 'origin'])
n = run(['git', 'rev-list', '--count', 'main..origin/main'], check=False).stdout.strip()
ahead = run(['git', 'rev-list', '--count', 'origin/main..main'], check=False).stdout.strip()
print('behind=%s ahead(local-unpushed)=%s' % (n, ahead))
