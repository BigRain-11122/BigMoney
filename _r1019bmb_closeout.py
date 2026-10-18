# -*- coding: utf-8 -*-
# r1019 bm-b closeout: state.json + heartbeat + round report row.
# Fresh-read-modify-write per file (r1006 multi-writer law). ASCII code, UTF-8 data.
import io
import json
import os
import subprocess
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, 'state.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
RR = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')

NOW = datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
EPOCH = int(time.time())

DID = ("r1019: (a) S0 origin advanced 7 (bm-c r1110/1111 W276 prereg DERIVED + five-face "
       "FREEZE-SPLICE landed, burn shards 11/12 in-flight; bm-a r1073 WAVE_LOOP_LAW landed "
       "early + MF Monday adjudication FREEZE-RETAIN panel parked) -- dirty-tree FF per "
       "r1015/r1017 law: stash 12 daemon faces -> ff-only -> stash pop 5 UU resolved per laws "
       "(machine-health origin-wins r1015 / futures+lhb origin-newer-wins 07:05 vs 06:22 / "
       "watermark_red local-newer-wins 07:35 r1028 / token_usage origin-base r1008 union); "
       "stash drop sha-recorded baa47cb7; local==origin 0/0. (b) S0.5 orders 105/105 "
       "zero-unacked + D-19 dual probe zero-drift (DEC 8706acd8/ORD 04050fda); S1 smoke 49/49; "
       "sat engine alive idle queue 0. (c) FIRST ACTION: ST-009 character voice "
       "differentiation eval station seeded (engine lock held, r1015/r1018 pattern) + runner "
       "st009 registered in Tools/content_loop_step.py (py_compile OK, engine selftest PASS) "
       "+ engine round 33 claimed + executed done -- measured debt: 3 same-voice-band pairs, "
       "all voice_07 family (XIONG 170.9 / XIONGWEI 171.4 / FATHER 151.0 Hz; XIONG-XIONGWEI "
       "f0_rel 0.3% = acoustically the same voice); deterministic pitch-tier search "
       "(semantic direction constraints, min total shift) -> XIONG 0st / XIONGWEI +3st / "
       "FATHER -1st (total 4st, all family pairs f0_rel >= 0.15 post-shift); method "
       "feasibility: post-synth DSP tiering primary / fine-tune-on-same-base honest NEGATIVE "
       "(cannot separate a shared-base family) / distinct-source root fix rides BOY+MANCANG "
       "sourcing; products: driver runner_assets/voice_differentiation_eval.py (selftest "
       "17/17) + receipt VOICE-DIFFERENTIATION-EVAL-v0.1.md + status face "
       "results/drama_env/voice_differentiation_eval.json. (d) S6 41 legs rc0 2.1min: "
       "ZERO-DRIFT 51, new-bar=no (cutoff 10-16 Monday pre-market -> live.paper family "
       "legally skipped), REPORT+LIVE-2026-10-19 regenerated ORANGE cap50%, "
       "scorecard/daily_scorecard/dashboard = bm-a fresh 19min legal lane-guard skip, "
       "compute_audit flags pool_starvation+supply_floor honest 0/3 = answered-by-chain "
       "(W276 landed 07:2x, burn on bm-c lane; bm-b pool waits W276 finalize -> W277 seat / "
       "trial-labor standing line). (e) idle --worked rounds->0 (real station work).")

VERDICT = ("GREEN: r1019 ST-009 角色音色差异化评估站播种+引擎认领+执行收站 done——共享底嗓债定谳实测：voice_07 "
           "三人组 3 对全落同嗓带（XIONG-XIONGWEI F0 相对差仅 0.3%=声学同一把嗓子）；确定性音高分档=XIONG 0st/"
           "XIONGWEI +3st/FATHER -1st（总移位 4st·组内全对出带 ≥15%）；方法面诚实负发现=同底嗓微调不可分离（根解="
           "换源寻根·随 BOY/MANCANG 寻源站）；driver selftest 17/17；S0 吸收 bm-c W276 冻结+burn 与 bm-a "
           "WAVE_LOOP_LAW 7 提交（脏树 FF+5 UU 依法拆解）；S6 41 rc0（ZERO-DRIFT 51·新bar=否纸盘链依法跳过）；"
           "supply_floor 诚实饿 0/3 已答（W276 已落地·burn 在 bm-c 车道·bm-b 池候 W277 席/试用期常设线）；下窗="
           "r1020 O-20261018-0948 判决窗 10-19 ~10:2x+ST-010 分档试合成站+BOY/MANCANG 寻源站+BigMoney 席位计划贡献 ≤10-25")

NEXT = ("r1020: 1) O-20261018-0948 24h died-pre-closeout window judgment (~10:2x, v2 "
        "liveness-gated launcher observation) 2) ST-010 pitch-tier test-synthesis station "
        "seed (XIONG/XIONGWEI/FATHER 1 line each through GPT-SoVITS + tier DSP -> re-measure "
        "F0 separation) 3) BOY/MANCANG sourcing station seed (child-voice license review "
        "first / de-clip re-production) 4) BigMoney seat automation plan contribution "
        "<=10-25 (bm-a r1069 3762f3dafa consume-no-rebuild) 5) supply_floor watch: W276 "
        "finalize -> W277 seat (bm-c lane) + trial-labor standing line 6) Monday 15:30 "
        "papers chain (new bar lands after close)")

MILESTONE = ("differentiation eval done -> next: ST-010 tier test synthesis + BOY/MANCANG "
             "sourcing (<=10-22 voice P1) + O-20261018-0948 window judgment 10-19 ~10:2x + "
             "CONTENT-LOOP 10-28 continuous-run judgment (9 stations seeded / 8 done-ish pace)")

ARTIFACT = ("content/drama/outbox/VOICE-DIFFERENTIATION-EVAL-v0.1.md (10-pair debt matrix + "
            "pitch tier XIONG 0/XIONGWEI +3st/FATHER -1st + method feasibility) + "
            "results/drama_env/voice_differentiation_eval.json + driver "
            "runner_assets/voice_differentiation_eval.py (selftest 17/17) + S6 products "
            "(REPORT-2026-10-19 + LIVE-2026-10-19 ORANGE cap 50%)")

RR_ROW = (NOW + " | r1019 bm-b | dept:媒体产线+引擎 | WM verdict: GREEN（red=false @07:46 "
          "py_watermark insufficient_history n=1 合法起步窗·idle --worked rounds->0 实物工作清零）"
          "｜当前活=ST-009 角色差异化评估站播种+注册+引擎认领+执行收站 done（引擎 round 33·ensure-done "
          "done-early 证据链全）｜最近实物=content/drama/outbox/VOICE-DIFFERENTIATION-EVAL-v0.1.md（共享底嗓债定谳："
          "voice_07 三人组 3 对全同嗓带·XIONG-XIONGWEI F0 相对差 0.3%=同一把嗓子；分档=XIONG 0st/XIONGWEI +3st/"
          "FATHER -1st 总移位 4st 全对出带；诚实负发现=同底嗓微调不可分离）+ results/drama_env/"
          "voice_differentiation_eval.json + driver runner_assets/voice_differentiation_eval.py（selftest 17/17）+ "
          "Tools/content_loop_step.py st009 runner 注册（py_compile 绿+引擎 selftest PASS）｜S0=吸收 origin 7 提交"
          "（bm-c r1110/1111 W276 prereg DERIVED+FREEZE-SPLICE 落地·burn 11/12 在飞 + bm-a r1073 WAVE_LOOP_LAW "
          "提前落地+MF 周一裁定 FREEZE-RETAIN 面板冻结）脏树 FF+stash pop 5 UU 依法拆解（machine-health origin-wins "
          "r1015/futures+lhb origin-newer 07:05/watermark_red 本地 07:35 r1028/token_usage origin 底 r1008 union）"
          "｜S0.5=orders 105/105 零未回执+D-19 双探零漂移（DEC 8706acd8/ORD 04050fda）｜S1 smoke 49/49｜SatEngine "
          "alive idle queue0｜S6 41 腿 rc0 2.1min（ZERO-DRIFT 51·update_daily 0 新行 cutoff 10-16 周一盘前·"
          "live.paper 族依法跳过·REPORT+LIVE-2026-10-19 再生 ORANGE cap50%·scorecard/daily_scorecard/dashboard="
          "bm-a fresh 19min 合法 lane-guard 跳过·compute_audit pool_starvation+supply_floor 诚实旗 0/3 已答="
          "W276 已落地 burn 在 bm-c 车道 bm-b 池候 W277 席/试用期常设线）｜S7=四任务全 S4U 实证（IterationLoop/"
          "LoopWatchdog/ContentLoop/SatEngine）+双爪重装+loop pin=2 no-op+孤儿面=0（07:46 探针 7 面 0 孤儿）"
          "｜下轮指针=r1020：①O-20261018-0948 24h died-pre-closeout 判决窗 10-19 ~10:2x ②ST-010 分档试合成站播种 "
          "③BOY/MANCANG 寻源站播种（童声许可先审）④BigMoney 席位自动化计划贡献 ≤10-25 ⑤supply_floor 候 W276 "
          "finalize→W277 席 ⑥周一 15:30 papers 链（新bar 收盘后落）｜本地未达 origin commit 数=0（收尾 push+fetch "
          "互证）｜新账目=0/7（07:46 探针）｜孤儿面=0｜登记簿判定=无清扫/归档/删除/恢复类动作（treasure_guard 未触发）")


def sample():
    ram, cpu, gpu = None, None, None
    try:
        import psutil
        ram = round(psutil.virtual_memory().available / 1024 ** 3, 1)
        cpu = round(psutil.cpu_percent(interval=1.0), 1)
    except Exception:
        pass
    try:
        r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free',
                            '--format=csv,noheader,nounits'],
                           capture_output=True, creationflags=0x08000000, timeout=15)
        gpu = int(float(r.stdout.decode().strip().splitlines()[0]))
    except Exception:
        pass
    return ram, cpu, gpu


ram, cpu, gpu = sample()

# --- state.json ---
with io.open(STATE, 'r', encoding='utf-8-sig') as f:
    st = json.load(f)
st['round_no'] = 1019
st['round'] = 1019
st['round_no_label'] = 'r1019'
st['clock_read'] = NOW
st['did'] = DID
st['last_action'] = DID[:300]
st['last_action_at'] = NOW
st['last_round_at'] = NOW
st['last_round_ts'] = NOW
st['last_seen'] = NOW
st['ts'] = NOW
st['updated'] = NOW
st['updated_at'] = NOW
st['now_active'] = 'r1019 closed'
st['current_task'] = ('r1019: ST-009 voice differentiation eval seeded+registered+engine-'
                      'claimed+done (debt 3 pairs + tier 0/+3/-1st) + S6 41 rc0 + push')
st['task'] = st['current_task']
st['verdict'] = VERDICT
st['current'] = VERDICT
st['next'] = NEXT
st['next_milestone'] = MILESTONE
st['latest_artifact'] = ARTIFACT
st['last_artifact'] = ARTIFACT
st['orphan_face'] = 0
st['orphan_faces'] = 7
st['orphan_face_note'] = 'r1019 S6 chain probe (07:46): 7 py faces / 0 orphans'
st['last_decisions_read_at'] = NOW
st['last_orders_read_at'] = NOW
st['sat_engine'] = {
    'status': ('alive (r1019 S6 status rc0, idle verdict, queue_depth 0; supply floor '
               'honest starvation 0/3 -- W276 prereg+freeze LANDED 07:2x (bm-c r1110/r1111), '
               'burn in-flight on bm-c engine 11/12 shards; bm-b research pool waits W276 '
               'finalize -> W277 seat window / trial-labor standing line)'),
    'checked_at': NOW,
}
st['sync']['r1018_main_push'] = {
    'status': 'PUSHED_VERIFIED (verified at r1019 S0: a2a6ad5659 ancestor of origin/main, behind=0 after ff)',
    'pushed_sha': 'a2a6ad5659dd4f6bdf49810059840e5639b3cab3',
    'consumed_at': NOW,
    'behind_origin_main': 0,
    'note': 'r1018 payload delivered pre-r1019; state face had stayed PENDING, closed by r1019',
}
st['sync']['r1019_main_push'] = {
    'status': 'PENDING (this commit)',
    'pushed_sha': 'pending',
    'consumed_at': 'pending r1020',
    'behind_origin_main': 0,
    'note': ('r1019 payload = ST-009 differentiation station (versioned driver + receipt + '
             'status face + engine runner registration + seed script) + drama queue/claims/'
             'round-log/loop-state faces + state/heartbeat/round-report + S6 own regen/'
             'product faces (daily_report/live_usage docs + compute_audit/regime_state/'
             'b_layer/dualarm/orphan/attrition faces + collector bm-b-lane status faces) + '
             'r1019 work files; shared daemon faces (machine-health/watermark_red/'
             'token_usage.json + unsuffixed lhb/futures/astock/etf status) intentionally '
             'NOT added (r982/r1015/r1018 policy); base = 627c4e10f2 origin tip fresh at S0 FF'),
}
st['sync']['last_push_ts'] = NOW
with io.open(STATE, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write('\n')

# --- heartbeat ---
with io.open(HB, 'r', encoding='utf-8-sig') as f:
    hb = json.load(f)
hb['last_seen'] = NOW
hb['ts'] = NOW
hb['clock_read'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
hb['round_no'] = 1019
hb['round'] = 1019
hb['task'] = st['current_task']
hb['current_task'] = st['current_task']
hb['did'] = DID
hb['last_action'] = DID[:300]
hb['last_action_at'] = NOW
hb['verdict'] = VERDICT
hb['current'] = VERDICT
hb['next'] = NEXT
hb['next_milestone'] = MILESTONE
hb['latest_artifact'] = ARTIFACT
hb['last_artifact'] = ARTIFACT
hb['now_active'] = 'r1019 closed'
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['last_decisions_read_at'] = NOW
hb['last_orders_read_at'] = NOW
if ram is not None:
    hb['free_ram_gb'] = ram
if cpu is not None:
    hb['cpu_load_pct'] = cpu
if gpu is not None:
    hb['gpu_free_vram_mb'] = gpu
with io.open(HB, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')

# --- round report row ---
with io.open(RR, 'a', encoding='utf-8', newline='\n') as f:
    f.write(RR_ROW + '\n')

# --- verify ---
with io.open(HB, 'r', encoding='utf-8-sig') as f:
    chk = json.load(f)
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read must be T-format'
with io.open(STATE, 'r', encoding='utf-8-sig') as f:
    schk = json.load(f)
assert schk['round_no'] == 1019
print(json.dumps({'verdict': 'closed', 'round': 1019, 'epoch': EPOCH,
                  'ram_free_gb': ram, 'cpu_pct': cpu, 'gpu_free_mb': gpu,
                  'clock_read': NOW}, ensure_ascii=False))
