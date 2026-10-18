# r1016 bm-b closeout: state.json + heartbeat + round report row (UTF-8).
import json, time, io, psutil

now_iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())
ram = psutil.virtual_memory()
free_ram = round(ram.available / 1e9, 1)
cpu_pct = psutil.cpu_percent(interval=0.5)

did = ("r1016: (a) S0 tree green (HEAD attach verified, origin 0/0, dirty faces = daemon live-writers only per r982 policy). "
       "(b) S0.5 orders diff 105/105 acked zero-unacked + D-19 probe dual-hold (DEC 8706acd8 / ORD 04050fda). "
       "(c) S1 smoke 49/49 + T-18 queue-head probe CLEAR (T22/E14 both done-rows). "
       "(d) r1015 leftovers consumed: ST-006 products verified already-committed by r1015 closeout 71bdc4f572 (voice_bank/manifest.json 7 canon entries + outbox VOICE-BANK-MANIFEST-v0.1.md, zero re-work); env driver poll x3 = deps phase PASSED (pyopenjtalk-plus wheel fallback confirmed), weights main pack 4351MB DL done 04:09:34 + G2PWModel 68%+ in flight, driver pid 7652 live (ignition-5 04:00) -- cross-round poll to r1017. "
       "(e) W275 seat receipt processed (@ALL from bm-c r1106: A band 620_301..622_300 / B band 622_301..622_500, prereg derive = bm-c next-window first action; bm-b zero direct obligation, engine supply floor stays honest-starved until prereg freeze lands) -> moved to processed. "
       "(f) S6 43 legs rc0 3.9min: orphan 0/8, idle --worked rounds->0, ZERO-DRIFT streak 51, py_watermark py_low_board_clear legal-whitelist, supply_floor honest flag (pool ready 0/floor 3, W275 prereg pending), market_clock CALL-2026-10-16 ORANGE_COOL, daily_report REPORT-2026-10-19 + ceo_live_usage LIVE-2026-10-19 (state=ORANGE cap=50%), scorecard/paper_export/daily_scorecard/build_status 4-leg stale-takeover guard legal (bm-a heartbeat stale 106-108min, O-2100 s2.4 STALE_MIN law), attrition healed x2. "
       "(g) S7 self-heal 5/5 green: loop task pin=2 phase-ok + watchdog S4U + pre-commit/pre-push claws + satengine task. Local self-drive pool 9/0 open (agenda honest).")

verdict = ("GREEN: r1016 收口轮——r1015 遗留双消费（ST-006 产物已由 r1015 提交零重做·env 驱动器 deps 相位绿=pyopenjtalk-plus wheel 兜底实证）+ weights 主包 4351MB 落地（04:09:34）+ G2PW 模型在飞（68%+·pid 7652 live·跨轮 poll 交 r1017）+ W275 席位回执消费（A 带 620_301..622_300·prereg=bm-c 下窗首动作·bm-b 零直接义务）+ S6 43 rc0 3.9min（ORANGE_COOL 时钟·LIVE-2026-10-19·四腿 stale-takeover 守卫合法接管）+ smoke 49/49 + 自愈 5/5；leftovers=env weights/extras/smoke 相位在飞（r1017 poll）+ 首合成 smoke 站候 env 完成播种 + O-0948 判决窗 10-19 ~10:2x + supply_floor 诚实旗（候 bm-c W275 prereg 冻结）")

next_r1017 = ("r1017: 1) poll results/drama_env/gpt_sovits_env_status.json -- weights(G2PW tail)/extras/smoke phases (driver pid 7652 live; on failed phase root-cause + fix + re-ignite idempotent per r1015 pattern) 2) env all-phases complete -> first synthesis smoke station seed (ST-007: ref-clip sourcing per manifest shortlist, content_loop_step.py new runner) 3) O-0948 window close judgment 10-19 ~10:2x (v1 wall-clock census order) 4) ST-002 watch CEO direction-gate receipt (IndexTTS-2 stays gated) 5) BigMoney seat automation plan contribution <=10-25 (bm-a r1069 3762f3dafa consume-no-rebuild) 6) supply_floor: on bm-c W275 prereg freeze landing -> engine supply leg check")

artifact = ("results/drama_env/gpt_sovits_env_status.json (deps green, weights main 4351MB done 04:09:34, G2PW in-flight, pid 7652) + "
           "S6 products (docs/daily_report/REPORT-2026-10-19.md + docs/live_usage/LIVE-2026-10-19.md + results/market_clock/CALL-2026-10-16.md) + "
           "_r1016bmb_s6chain.ps1")

task = "r1016: closeout (r1015 leftovers consumed + W275 receipt + env poll x3 + S6 43 + self-heal 5 + state/heartbeat/round-report/push)"

# ---- state.json ----
with io.open('state.json', encoding='utf-8') as f:
    st = json.load(f)
st['round_no'] = 1016
st['round'] = 1016
st['round_no_label'] = 'r1016'
st['clock_read'] = now_iso
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['last_round_at'] = now_iso
st['last_round_ts'] = now_iso
st['last_seen'] = now_iso
st['last_action_at'] = now_iso
st['now_active'] = 'r1016 closing'
st['task'] = task
st['current_task'] = task
st['did'] = did
st['last_action'] = did[:600]
st['verdict'] = verdict
st['current'] = verdict
st['next'] = next_r1017
st['latest_artifact'] = artifact
st['last_artifact'] = artifact
st['orphan_face'] = 0
st['orphan_face_note'] = 'r1016 S6 chain probe (04:05): 8 py faces / 0 orphans'
st['last_orders_read_at'] = now_iso
st['last_decisions_read_at'] = now_iso
st['sat_engine'] = {
    'status': 'alive (r1016 S6 status rc0, idle verdict, queue_depth 0; supply floor honest starvation, W275 seat published this round, prereg freeze = bm-c next-window first action)',
    'checked_at': now_iso,
}
st['sync']['r1016_main_push'] = {
    'status': 'PENDING (this commit)',
    'pushed_sha': 'pending',
    'consumed_at': 'pending r1017',
    'behind_origin_main': 0,
    'note': 'r1016 payload = own faces (state/heartbeat/round-report + _r1016bmb_s6chain.ps1 + s6 log + W275 MSG processed move + own regen/product faces [daily_report/live_usage docs + scorecard/paper_export/daily_scorecard/update_status/market_clock/regime_state/dualarm/compute_audit/b_layer/idle/orphan/attrition drama_env status face]); shared daemon faces (machine-health/watermark_red/token_usage + unsuffixed lhb/futures status) intentionally NOT added (r982/r1012 policy)',
}
with io.open('state.json', 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- heartbeat ----
with io.open('fleet/machines/bm-b.json', encoding='utf-8') as f:
    hb = json.load(f)
hb['last_seen'] = now_iso
hb['task'] = task
hb['did'] = did
hb['cpu_cores'] = 16
hb['free_ram_gb'] = free_ram
hb['gpu_free_vram_mb'] = 3871
hb['cpu_load_pct'] = cpu_pct
hb['verdict'] = verdict
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now_iso
hb['ts'] = now_iso
hb['round_no'] = 1016
hb['round'] = 1016
hb['current_task'] = task
hb['next'] = next_r1017
hb['last_action'] = did[:600]
hb['last_action_at'] = now_iso
hb['latest_artifact'] = artifact
hb['last_artifact'] = artifact
hb['now_active'] = 'r1016 closing'
hb['orphan_face'] = 0
hb['next_milestone'] = ("GPT-SoVITS env all-phases complete + first synthesis smoke (voice P1 <=10-22) + O-0948 window judgment 10-19 ~10:2x + CONTENT-LOOP 10-28 continuous-run judgment (72h >=3 stations/day)")
with io.open('fleet/machines/bm-b.json', 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')

assert isinstance(epoch, int), 'epoch must be int'
print('closeout written', now_iso, 'epoch', epoch, 'ram', free_ram, 'cpu', cpu_pct)
