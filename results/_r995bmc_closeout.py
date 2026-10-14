# -*- coding: utf-8 -*-
"""r995 bm-c wait-state window #10 one-line closeout (S5/S7 writes)."""
import json, time, datetime

ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
now_iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

# ---- fresh probe numbers (this round's own canonical probe outputs) ----
it = json.load(open(ROOT + r'\results\idle_trigger.bm-c.json', encoding='utf-8'))
au = json.load(open(ROOT + r'\results\compute_audit.bm-c.json', encoding='utf-8'))
cpu_pct = au.get('cpu_total_pct', 0)
ram_free_pct = it.get('ram_free_pct', 0)
free_ram_gb = round(23.9 * ram_free_pct / 100.0, 1)
gpu_used = au.get('gpu', {}).get('mem_used_mb', 0)
gpu_free = max(0, 16384 - int(gpu_used))

verdict = ("green: wait-state window #10 one-line law -- W238 bm-a chain pre-splice (prereg derive script landed origin 10:06, "
           "splice/burn/finalize pending; bm-a quiet = CEO daytime zero-dispatch law compliant) -> W239 freeze-prep waits-upstream physical; "
           "bars pre-15:30; MF parked source-blocked; W19 SCREEN bm-b-lane pinned + RAM gate zero bm-c face; backlog#12 BigHouse=bm-b seat lane "
           "no-claim (no clone/no creds/green_idle=false) -- smoke 49/49 + S6 light green + S7 quad green + dualrun streak 51")

did = ("r995: (1) S0-1 anchor bm-c + round-zero probe py_faces=9 orphans=2 zero-kill (ComfyUI 8188=MV-lane protected resident kept + "
       "album_serve/Doubao other-session faces); (2) S0 pull --rebase rc128 FETCH_HEAD multi-branch race (r586 KNOWN pit, zero new memory) -> "
       "canonical two-step fetch + rebase --autostash origin/main rc0 clean autostash-applied; (3) S0.5 dual-delta FALSE x2 (dec 86187eff / "
       "ord 348eaf34 both hold) + filename diff unacked=0 (88 top-level all acked); (4) smoke 49/49; (5) S3 checks: WM red=False + satengine "
       "rc0 ALIVE + idle_trigger green_idle=false (RAM 12.7pct MV-lane protected, vram gate disclosure-only T-183) + jobs=0 + fleet-tasks 0 "
       "open + inbox 0 + P2/P3 queues all consumed + backlog#12 NOT claimed (BigHouse seat=bm-b lane C-20261011-01 D2, bm-c no clone/no "
       "credentials, green_idle=false idle-claim channel does not fire -- wrong-lane grab + infra rebuild avoided); W238 watch=prereg derive "
       "script landed 10:06 splice/burn/finalize ABSENT, bm-a heartbeat 09:48=daytime law compliant; (6) S6 light: dualrun ZERO-DRIFT streak "
       "51 (455) + audit FLAG supply_gap+ignition_sla (W19 bm-b-lane structural + RAM gate) + wmprobe py_low_board_clear honest + daily no-op "
       "cutoff 10-13 + regime breadth-trigger shadow + clock ORANGE_COOL + fund_premium no-op pre-15:30 + fundamental 14.7h skip + blayer rc0 + "
       "daily_report faces=5 + liveusage ORANGE/COOL cap50 + token delta=0; (7) S7 quad: attrition 4 CLEAN + pin=5 no-op + watchdog registered + "
       "claws x2 idempotent")

next_ptr = ("r996: (1) W238 finalize watch -> W239 freeze-prep SAME-WINDOW on landing (prereg derive R33-clone from committed lineage + five-face "
            "splice + six-gate PRE-FINALIZE; gate0.5 selfcheck W238 row + queue_head probe at claim); (2) 15:30 bars -> papers full chain when "
            "10-14 bar lands (debt=0); (3) MF panel recheck (source-blocked -- unpark on bm-a panel completion); (4) W19 pool: bm-b-lane pinned, "
            "zero bm-c face; (5) backlog#12 BigHouse due 10-15 = bm-b seat lane")

line = ("{ts} | r995 | bm-c | WAIT-STATE window #10 per one-line law -- wait-faces VERIFIED not rescanned: "
        "(1) W238 still pre-splice (bm-a prereg derive script landed origin 10:06; splice/burn/finalize artifacts ABSENT; bm-a heartbeat 09:48 "
        "quiet = CEO daytime zero-dispatch law compliant -> W239 freeze-prep waits-upstream physical, prereg derive asserts need W238 finalize "
        "numbers r587 never-transcribe); (2) 10-14 bars pre-15:30 (papers debt=0, chain at 15:30 bar); (3) MF-IC-P1 parked source-blocked (bm-a "
        "panel lane); (4) W19 SCREEN 2 unclaimed shards = bm-b lane-pinned r429 + bm-c RAM gate 12.7pct free honest refuse | boards: jobs=0 + "
        "tasks 0 open + inbox 0 + P2/P3 consumed + backlog#12 BigHouse NOT claimed (bm-b seat lane C-20261011-01 D2 + no clone/no creds + "
        "green_idle=false) | WM-VERDICT: green red=false py_low_board_clear LEGAL-wait (upstream=physical chain dep not stall-by-omission; W239 "
        "seat armed first-action-on-landing) | S6 light: dualrun ZERO-DRIFT streak 51 (455) + audit FLAG supply_gap+ignition_sla structural "
        "bm-b-lane + daily no-op cutoff 10-13 + regime breadth shadow + clock ORANGE_COOL + fund_premium no-op + fundamental 14.7h skip + blayer "
        "rc0 + daily_report faces=5 + liveusage ORANGE/COOL + token delta=0 | body: S0 pull --rebase rc128 r586 known FETCH_HEAD race -> "
        "canonical fetch+rebase --autostash rc0; S0.5 dual FALSE x2; smoke 49/49; satengine rc0 ALIVE; orphan face=2 zero-kill (ComfyUI "
        "8188=MV-lane resident kept) | S7 quad: attrition 4 CLEAN + pin=5 no-op + watchdog + claws x2 | next r996: W238 finalize watch -> W239 "
        "freeze-prep SAME-WINDOW + 15:30 bars papers chain + MF unpark on bm-a panel | watermark: GREEN | local-not-at-origin=N (closeout push "
        "rides this window)").format(ts=now_iso)

with open(ROOT + r'\round_reports-bm-c.md', 'a', encoding='utf-8') as f:
    f.write(line + '\n')

# ---- state bump 995->996 ----
sp = ROOT + r'\state-bm-c.json'
st = json.load(open(sp, encoding='utf-8'))
assert st['round_no'] == 995, st['round_no']
st['round_no'] = 996
st['activity_now'] = "{0} | r995 | bm-c: wait-state window #10 one-line closeout (S6 light+S7 quad green, zero new CEO rows, W238 pre-splice watch) | counter 995->996".format(now_iso[:16])
st['current_task'] = ("r995 wait-state window #10 one-line (W238 bm-a pre-splice: prereg derive script landed 10:06, splice/burn/finalize pending, "
                      "bm-a daytime law compliant -> W239 freeze-prep waits-upstream; bars pre-15:30; MF parked source-blocked; W19 SCREEN bm-b-lane)")
st['current_task_at'] = now_iso
st['did'] = did
st['verdict'] = verdict
st['next'] = next_ptr
st['last_round_summary'] = "r995: wait-state window #10 one-line closeout -- W238 pre-splice watch + zero new CEO rows + S6 light + S7 quad green; counter 995->996"
st['sync'] = {"origin_tip": "post-r994 9b7159629 at open; closeout commit+push rides this window",
              "ts": now_iso, "ahead_behind": "0/0 pre-closeout (closeout commit+push rides)",
              "note": "r995: fetch + explicit rebase --autostash origin/main rc0 (pull --rebase rc128 = r586 known FETCH_HEAD race face)"}
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- heartbeat ----
hp = ROOT + r'\fleet\machines\bm-c.json'
hb = json.load(open(hp, encoding='utf-8'))
hb['last_seen'] = now_iso
hb['clock_read'] = now_iso
hb['ts'] = now_iso
hb['heartbeat_epoch_utc'] = epoch
assert isinstance(hb['heartbeat_epoch_utc'], int)
hb['round_no'] = 996
hb['last_round'] = 'r995'
hb['last_round_at'] = now_iso
hb['last_round_ts'] = epoch
hb['last_round_closed'] = now_iso
hb['current_task'] = st['current_task']
hb['current_task_at'] = now_iso
hb['current_task_ts'] = epoch
hb['now_active'] = "{0} | r995 | bm-c: wait-state window #10 one-line closeout (S6 light+S7 quad green, zero new CEO rows) | counter 995->996".format(now_iso[:16])
hb['activity_now'] = hb['now_active']
hb['did'] = did
hb['verdict'] = verdict
hb['next'] = next_ptr
hb['next_pointer'] = next_ptr
hb['last_round_summary'] = st['last_round_summary']
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['orphan_face'] = 2
hb['orphan_faces'] = 2
hb['cpu_pct'] = cpu_pct
hb['cpu_util_pct'] = cpu_pct
hb['cpu_idle_pct'] = round(100 - cpu_pct, 1)
hb['free_ram_gb'] = free_ram_gb
hb['idle_ram_gb'] = free_ram_gb
hb['ram_free_gb'] = free_ram_gb
hb['gpu_free_vram_mb'] = gpu_free
hb['gpu_free_mb'] = gpu_free
hb['gpu_idle_mb'] = gpu_free
hb['gpu_free_mib'] = gpu_free
hb['gpu_idle_vram_mib'] = gpu_free
hb['gpu_free_vram_mib'] = gpu_free
hb['gpu_used_vram_mib'] = int(gpu_used)
hb['gpu_mem_used_mib'] = int(gpu_used)
hb['prod_lanes'] = ("CPU=N1 W237 CLOSED (r990 finalized 945,189/K=519,320); W238=bm-a chain pre-splice (prereg derive script landed 10:06, "
                    "splice/burn/finalize pending, bm-a daytime zero-dispatch law compliant); W239=bm-c SEATED 09:14 (freeze waits-upstream W238 "
                    "finalize, prereg derive = first action on landing per seat-first law); MF-IC-P1: parked, bm-a panel rebuild watch; "
                    "GPU=MV V3: burn window protected per O-20261014-0312 sec.2 zero touch")
hb['next_milestone'] = ("10-14 15:30 bars -> papers chain; W238 finalize (bm-a) -> W239 freeze-prep bm-c same-window; MF-IC-P1 unpark on bm-a panel; "
                        "backlog#12 BigHouse due 10-15 = bm-b seat lane")
hb['verify'] = ("receipts: smoke 49/49 + S0.5 dual-delta FALSE x2 (dec 86187eff/ord 348eaf34) + unacked=0 + dualrun streak 51 ZERO-DRIFT + attrition "
                "4 CLEAN + satengine rc0 ALIVE + orphan face=2 zero-kill + wmprobe py_low_board_clear honest; closeout push rides this window")
hb['full_load_selfproof'] = {
    "占用一行": "GPU=MV V3 车道保护烧窗（O-20261014-0312 §2 零碰）+ollama serve 在役+ComfyUI 8188 常驻+双 llama-server；RAM=12.7% free（MV lane 保护态如实）",
    "当前活": "r995 wait-state 窗 #10（W239 席候 W238 finalize 物理解锁〔bm-a 白日零排班律在案〕+bars 15:30 到点 papers 全链）",
    "下一交付物": "W238 finalize 落地即同窗 W239 freeze-prep（prereg derive R33-clone+五面 splice+六门 PRE-FINALIZE）；bars 15:30 papers 全链",
    "队列水位": "N1 引擎 0 在烧（W239 席占·候上游）·W19 SCREEN 池 2 unclaimed=bm-b lane pinned·P2/P3 净·bars 15:30·GPU=MV V3"
}
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# self-proof: reload and assert types
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'] and ' ' not in chk['clock_read'].split('+')[0], 'clock_read must be T-separated'
print('CLOSEOUT WRITES OK', now_iso, 'epoch', epoch, 'round_no->996', 'cpu', cpu_pct, 'ram_free_gb', free_ram_gb, 'gpu_free', gpu_free)
