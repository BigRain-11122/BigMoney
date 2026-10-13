# -*- coding: utf-8 -*-
# r916 inc3 (bm-b) closeout: dead-session takeover round 3 -- state + heartbeat + round report + O-0930 receipt
import json, time, os

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
now = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

def load(p):
    with open(os.path.join(ROOT, p), 'r', encoding='utf-8') as f:
        return json.load(f)

def save(p, obj):
    with open(os.path.join(ROOT, p), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write('\n')

# --- 1) state.json ---
st = load('state.json')
st['clock_read'] = now
st['round'] = 916
st['round_no'] = 917
st['round_no_label'] = 'r916'
st['current_task'] = 'r917 = i2v batch deferred-decision window (PSU swap pending / CEO re-order; recipe 160W clause governs) + unity-mcp bridge-level diagnosis (2 probes failed with editor open) + N2U3 chain stays batch-gated + Music3 post-batch + Speech-02 adjudication pending + game-audio batch (O-2245 bm-b face)'
st['task'] = 'r917: batch deferred-decision window + unity bridge diagnosis > at re-ignition/batch-done: remove keepwarm.pause + N2U3 flip (batch-done + RAM>=4GB double gate; RAM now 10.7GB OK) -> autofill burn -> export-topk K=32 -> judged legs > Music3 install post-batch (license PASS r913) > Speech-02 adjudication awaiting committee/CEO (POOL-0002 frozen) > game audio batch (O-2245) > E15 s4 intake legs = monthly boundary'
st['did'] = ('r916 inc3: (1) THIRD dead-session takeover today: inc1 died pre-closeout 04:0x, inc2 watchdog-killed at 25min mark ~22:42 mid-S7 (4 commits rebased 22:27:45 + S6 full chain all-green 22:29-22:36 + heartbeat-restore 22:42:01, no concurrent session -- only own codely PID), inc3=this round with salvage-commit-early discipline: dead estate committed+rebased+pushed FIRST (d604677c7, 64+ files 2026-10-13 data close) before any new work. (2) D-19 double delta consumed: decisions fb378423->b137f331 = 3 group receipt rows (D-20261013-01 receipt-sweep incl bigmoney E1-restart-window verification, D-20261013-02 Phase-0 hand-in, C-20261013-01 cleanup bill) zero BigMoney mechanism rows; orders 3f22ee3e->91d9fad3 = MV-line CEO wave (2200 all-local / 2215 CPU-always-on+meaning-gate / 2230 audience-voice / 2245 full-speed-no-waste; bm-b face = Speech-02/Music3 gates -> game-audio batch + 480P animatic backup, gates standing-blocked) -> watermarks advanced, zero repo action. (3) unity-mcp POC probe #2 22:44: editor-open window live (2 Tuanjie procs) but bridge unconnected (No Unity Editor instances found) -> honest overdue carry, bridge-level diagnosis (plugin/port) queued next editor-open window. (4) O-20261013-0930 CEO full-work receipt: CPU/bookkeeping lanes verified alive (loop=this round parent, SatEngine faces ticking post-22:28, autofill p1d gate ran 22:46, astock full-universe refresh in-flight), GPU i2v re-ignition DEFERRED per power-loss recipe 160W escalation clause (3x unexpected shutdowns today 09:2x/09:5x/22:0x = PSU degraded beyond 180W cap; MODE=pause maintained, ollama/comfy down, CEO evening present), honest non-full-speed declaration ETA=PSU swap or CEO re-ignition order. (5) Task health: loop pin=2 alive, SatEngine alive, claws evidenced (this round commit+push passed both), board open=0. (6) S6 = dead-inc2 chain outputs salvaged (no rerun: idempotent, zero new bars since 22:36).')
st['last_action'] = 'r916 inc3: dead-session salvage landed first (d604677c7: 2026-10-13 data close 64+ files) + D-19 double delta consumed + O-0930 acked with honest GPU-deferral receipt + unity POC probe #2 (bridge unconnected)'
st['last_action_at'] = now
st['last_decisions_at'] = now
st['last_decisions_read_at'] = now
st['last_decisions_sha'] = 'b137f3317b4a76fc8e2d50c4171cdd8fefd7fa2c'
st['last_decisions_sha_method'] = 'r916 inc3 probe via results/_r686bmb_d19_check.py: fresh fetch, decisions fb378423->b137f331 delta consumed (3 group receipt rows, zero BigMoney mechanism rows)'
st['last_orders_at'] = now
st['last_orders_read_at'] = now
st['last_orders_sha'] = '91d9fad36a054a842b366cc5b8844b58a99fd9a8'
st['last_orders_sha_note'] = ('r916 inc3 probe consumed orders delta 3f22ee3e->91d9fad3: MV-line CEO order wave (O-20261013-2200 all-local V3 / 2215 CPU-always-on+meaning-gate / 2230 audience-voice v1.1 / 2245 full-speed-no-waste + bm-b face = Speech-02/Music3 gates -> game audio batch + 480P animatic backup slot) -- all MV-line, bm-b gates standing-blocked (Speech-02 adjudication pending CEO/committee, Music3 gated on batch exit which is PSU-deferred) -> watermarks advanced, zero repo mechanism action')
st['last_round_at'] = now
st['last_round_ts'] = now
st['last_seen'] = now
st['latest_artifact'] = 'salvage commit d604677c7 on origin/main (2026-10-13 data close: 5-ETF daily panels + minute_feed + marks/papers as_of 10-13 + REPORT-2026-10-13 + LIVE-2026-10-13 + market_clock CALL-2026-10-13 + 60+ audit faces, dead-inc2 chain all-green 22:29-22:36) + r916 round report line + O-0930 bm-b receipt line'
st['next'] = ('r917: (a) i2v batch deferred-decision window: re-ignite at 160W escalation ONLY per recipe clause (CEO absent + clause allows), else hold for PSU swap (750W gold ATX3.x pending); (b) unity-mcp bridge diagnosis next editor-open window (plugin presence/port scan; 2 probes failed with editor open); (c) at batch-done: remove keepwarm.pause + N2U3-LEG3-TRAIN flip (batch-done + RAM>=4GB double gate, RAM 10.7GB OK now) -> autofill burn -> export-topk K=32 -> judged legs; (d) Music3 install post-batch (license PASS r913); (e) Speech-02 3-option adjudication awaiting committee/CEO (POOL-0002 frozen); (f) game audio batch per O-2245 bm-b face AFTER gates; (g) E15 s4 intake legs = monthly boundary (explore.md L20 sentiment FDR4D chain)')
st['next_milestone'] = 'honest: GPU line blocked on PSU swap / CEO re-ignition order (3 shutdowns today); CPU+bookkeeping lanes running; next concrete milestones = unity bridge diagnosis (next editor-open window) + 2026-10-14 15:30 data window; N2U3 chain resumes only after batch re-ignition completes 53/53'
st['note'] = 'r916 inc3: takeover + salvage-first delivery + D-19 double-delta + O-0930 honest GPU-deferral receipt (MODE=pause held: ollama/comfy down, GPU 34W idle, RAM recovered 10.7GB)'
st['now_active'] = 'bm-b CPU/bookkeeping lanes alive (loop, SatEngine, autofill, astock daily full-universe refresh in-flight); GPU idle 34W (i2v 27/53 deferred per power-loss recipe, MODE=pause)'
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['orphan_face_note'] = 'r916 inc3 probe 22:44:15: py_faces=6 orphans=0 killed=[] (astock refresh worker + satengine faces = legal lanes); predecessor faces: 3x unexpected shutdowns today (09:2x pre-closeout / ~09:5x mid-batch KN23 / ~22:0x boot-window)'
st['sync'] = {'last_push_ts': now, 'note': 'r916 inc3: salvage commit d604677c7 pushed pre-work (deliver-first discipline); closeout commit+push follows this write; delivery self-proof fetch+rev-list'}
st['ts'] = now
st['updated'] = now
st['updated_at'] = now
st['verdict'] = ('GREEN-with-flags: takeover+delivery round complete (dead-inc2 estate landed 64+ files incl 2026-10-13 full data close, d604677c7); flags = GPU production deferred per power-loss recipe (PSU degraded, 3 shutdowns today, MODE=pause, ETA=PSU swap or CEO re-order) + unity-mcp bridge unconnected (2 probes, editor open, diagnosis queued) + Speech-02 adjudication awaiting CEO/committee + RAM recovered 10.7GB (was 1.0GB morning)')
st['d19_watermark_guard']['round_ref'] = 916
st['d19_watermark_guard']['ts'] = now
st['d19_watermark_guard']['note'] = ('r916 inc3 probe: decisions fb378423->b137f331 consumed (3 group receipt rows: D-20261013-01 receipt-sweep 31+overruled incl bigmoney E1-restart-window verification / D-20261013-02 C-20261012-01 Phase-0 hand-in + ledger merge / C-20261013-01 workspace cleanup bill -- all group-ledger receipts, zero BigMoney mechanism rows); orders 3f22ee3e->91d9fad3 consumed (MV-line CEO wave 2200/2215/2230/2245 + V3 repair/whitelist/lyrics rows; bm-b machine face = Speech-02/Music3 gate-pass -> game audio batch + 480P animatic backup, both gates standing-blocked) -> watermarks advanced, zero repo action')
save('state.json', st)

# --- 2) heartbeat fleet/machines/bm-b.json ---
hb = load('fleet/machines/bm-b.json')
hb['clock_read'] = now
hb['heartbeat_epoch_utc'] = epoch
hb['round'] = 916
hb['round_no'] = 917
hb['round_no_label'] = 'r916'
hb['current_task'] = st['current_task']
hb['task'] = st['task']
hb['did'] = st['did']
hb['last_action'] = st['last_action']
hb['last_action_at'] = now
hb['last_round_at'] = now
hb['last_seen'] = now
hb['latest_artifact'] = st['latest_artifact']
hb['next'] = st['next']
hb['next_milestone'] = st['next_milestone']
hb['note'] = st['note']
hb['now_active'] = st['now_active']
hb['verdict'] = st['verdict']
hb['orphan_face'] = 0
hb['orphan_faces'] = 0
hb['orphan_face_note'] = st['orphan_face_note']
hb['idle_rounds'] = 0
hb['green_idle'] = False
hb['agenda_starved'] = False
hb['ram_free_gb'] = 10.73
hb['ram_free_pct'] = 44.7
hb['free_ram_gb'] = 10.73
hb['vram_free_gb'] = 7.0
hb['gpu_free_vram_gb'] = 7.0
hb['gpu_free_vram_mb'] = 7157
hb['gpu'] = {'util_pct': 3.0, 'mem_used_mb': 1035.0, 'power_w': 34.31, 'face': 'GPU idle 34W -- i2v batch 27/53 deferred per power-loss recipe 160W clause (3x shutdowns today, PSU degraded); MODE=pause, ollama/comfy down'}
hb['sync'] = {'last_push_ts': now, 'note': 'r916 inc3: salvage d604677c7 pushed pre-work; closeout commit+push follows this write'}
hb['ts'] = now
hb['updated'] = now
hb['updated_at'] = now
if 'O-20261013-0930-bm-b.md' not in hb['orders_ack']:
    hb['orders_ack'].append('O-20261013-0930-bm-b.md')
hb['orders_ack_count'] = len(hb['orders_ack'])
hb['orders_ack_notes']['O-20261013-0930-bm-b.md'] = ('r916 inc3 bm-b receipt: CPU/bookkeeping lanes verified alive post-order (loop/SatEngine/autofill + astock refresh in-flight); dead windows today = 3x unexpected shutdowns (09:2x/09:5x/22:0x), salvage of interrupted rounds landed (d604677c7); GPU i2v re-ignition DEFERRED per power-loss recipe 160W escalation clause -- honest non-full-speed declaration, ETA=PSU swap (750W pending) or CEO re-ignition order; standing items: Speech-02 adjudication pending committee/CEO (POOL-0002 frozen), Music3 install gated post-batch (license PASS r913), G23/G26/G28 TJ-line items gated on CEO Tuanjie Hub re-login')
save('fleet/machines/bm-b.json', hb)

# --- 3) round report line ---
rr_line = (now + ' | r916 bm-b inc3 [dept:eng/fleet] | dead-session takeover #3 + salvage-first delivery + O-0930 honest-deferral receipt | watermark: GREEN (red=false since r915 closeout; 22:29-22:36 chain probe no red flag) | orphan-faces=0 (probe 22:44:15: py_faces=6 orphans=0 killed=[]; 3x unexpected shutdowns today = predecessor faces) | currently-active: CPU/bookkeeping lanes (loop parent of this round, SatEngine faces ticking post-22:28, autofill p1d gate ran 22:46, astock full-universe refresh in-flight); GPU idle 34W (i2v 27/53 DEFERRED per power-loss recipe 160W clause, MODE=pause, ollama/comfy down, CEO evening present) | latest-artifact: salvage commit d604677c7 on origin/main = 2026-10-13 full data close (5-ETF daily + minute_feed + marks/papers as_of 10-13 + REPORT-2026-10-13 + LIVE-2026-10-13 + market_clock CALL-2026-10-13, 64+ files, dead-inc2 chain all-green 22:29-22:36) | next-milestone: unity-mcp bridge diagnosis next editor-open window (probe #2 22:44 unconnected with editor live); GPU line ETA = PSU swap (750W pending) or CEO re-ignition order; data window next 10-14 15:30 | did: (1) r916 inc2 forensics: watchdog-killed at 25min mark mid-S7 (4 commits rebased 22:27:45 + S6 chain complete 22:36 + heartbeat-restore 22:42:01 then dead; NO concurrent session -- only own codely PID); inc3 discipline = commit-early: dead estate landed BEFORE any new work (d604677c7 pushed, delivery self-proof 0/0); (2) D-19 double delta consumed: decisions fb378423->b137f331 (3 group receipt rows incl bigmoney E1-restart-window verification; zero BigMoney mechanism rows), orders 3f22ee3e->91d9fad3 (MV-line CEO wave 2200/2215/2230/2245; bm-b face = Speech-02/Music3 gates -> game-audio batch + 480P animatic backup, gates standing-blocked) -> watermarks advanced, zero repo action; (3) unity-mcp POC probe #2: editor-open window live (2 Tuanjie procs) but bridge No-Unity-Editor-instances-found -> honest overdue carry, bridge-level diagnosis queued; (4) O-20261013-0930 receipt: CPU lanes verified alive, GPU deferral declared honestly per recipe (3 shutdowns today 09:2x/09:5x/22:0x = PSU degraded beyond 180W cap; MODE=pause maintained), orders_ack 201->202; (5) task health: loop alive (this round its child), SatEngine alive, claws evidenced by commit+push pass, board open=0, job_list self-only tracking; (6) S6 = dead-inc2 chain outputs salvaged, no rerun (idempotent, zero new bars since 22:36, all legs green) | evidence: d604677c7 push + rev-list 0/0 + _orphan_face_probe.bm-b.json + _r686bmb_d19_check.json + machine-state status output + unity probe #2 error message | unacked_orders=0 (O-20261013-0930 acked this round) | registry-zero-hit: no sweep/archive/delete actions this round | local-unreached-origin-commits: salvage push 0/0 proven; closeout commit carrying this line pushes immediately after | next-pointer r917: batch deferred-decision window (160W only if recipe clause allows + CEO absent) + unity bridge diagnosis > N2U3 chain (batch-gated; flip double-gate RAM leg now 10.7GB OK) > Music3 post-batch (license PASS r913) > Speech-02 adjudication (committee/CEO) > game-audio batch (O-2245 bm-b face) > E15 s4 monthly boundary | [r916 bm-b inc3]')
rr_path = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
with open(rr_path, 'r', encoding='utf-8') as f:
    rr_content = f.read()
rr_content = rr_content.rstrip('\n') + '\n' + rr_line + '\n'
with open(rr_path, 'w', encoding='utf-8') as f:
    f.write(rr_content)

# --- 4) O-0930 bm-b receipt line in order file ---
receipt_line = ('- [x] bm-b 回执（发令机补记账）@r916 inc3 ' + now + '：①CPU/簿记车道自证=本令后存活（loop 本轮即其子·SatEngine faces 22:28 后持续 tick·autofill p1d gate 22:46 实跑·astock 全宇宙 refresh 在飞）；死窗三段=今日 3×意外断电（09:2x/09:5x/22:0x），中断轮收尸已上 origin（d604677c7=10-13 全数据收口 64+ 件）；②无法满速面如实声明：GPU i2v 线（27/53）延后=断电 recipe 160W 升档条款（PSU 超限劣化·CEO 晚间在场），ETA=换 750W 金牌电源后恢复或 CEO 明令重点火；MODE=pause 维持（ollama/comfy 停·安全红线同源适用「速度不得凌驾合规/安全」）；③standing 候窗件如实：Speech-02 三选一裁决待委员会/CEO（POOL-0002 frozen）·Music3 装窗=批后（license PASS r913）·G23/G26/G28/TJ 单据族=待 CEO Tuanjie Hub 重登物理件；④orders_ack 201->202 本令入册。')
op_path = os.path.join(ROOT, 'fleet', 'orders', 'O-20261013-0930-bm-b.md')
with open(op_path, 'r', encoding='utf-8') as f:
    oc = f.read()
oc = oc.rstrip('\n') + '\n' + receipt_line + '\n'
with open(op_path, 'w', encoding='utf-8') as f:
    f.write(oc)

# --- self-proof ---
st2 = load('state.json')
hb2 = load('fleet/machines/bm-b.json')
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert hb2['orders_ack_count'] == len(hb2['orders_ack']) == 202, 'ack count mismatch'
assert 'T' in hb2['clock_read'], 'clock_read must be T-separated ISO8601'
print('CLOSEOUT_OK round_no=%d ack=%d epoch=%d ts=%s' % (st2['round_no'], hb2['orders_ack_count'], hb2['heartbeat_epoch_utc'], now))
