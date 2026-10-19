# -*- coding: utf-8 -*-
# r1020 bm-b closeout: state.json (root primary) + legacy state heal + heartbeat + round report row.
# Fresh-read-modify-write per file (r1006 multi-writer law). ASCII code, UTF-8 data.
import io
import json
import os
import subprocess
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, 'state.json')
LEGACY_STATE = os.path.join(ROOT, 'logs', 'iteration-loop', 'state.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
RR = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')

NOW = datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
EPOCH = int(time.time())

DID = ("r1020: (a) S0 absorb origin 14 commits (bm-c r1112-r1115 W277 seat publish + prereg "
       "derive + 2D sweep + freeze receipts + burn shards 6-of-12 in flight; bm-a r1074-r1076 "
       "closeout/s6chain/postscript + a5_acceptance pack + perpetual_faces_n1.py) via "
       "dirty-tree FF (stash 12 daemon faces -> ff-only be88d72a21..d7b732c9e8 -> stash pop "
       "5 UU law-resolved by versioned resolver results/_r1015bmb_uu_resolve.py: "
       "machine-health origin-wins (stashed side disclosed corrupted qwen3.8:4b-object-as-key "
       "writer face), futures/lhb/token_usage upstream-newer, watermark_red stashed-local-newer "
       "10:03 r1028); stash dropped 775bf616. (b) S0.5 orders 105/105 zero-unacked + D-19 dual "
       "probe UNCHANGED (DEC 8706acd8 / ORD 04050fda, fresh-read via git show origin/main). "
       "(c) FIRST ACTION DUE-NOW: O-20261018-0948 24h died-pre-closeout observation window "
       "judgment rendered CASE CLOSED -- anchor last fleetwide incident 2026-10-18 09:50:02 "
       "(bm-c W266 splice, v1 wall-clock kill) +24h elapsed fully clean; bm-b TIMEOUT census "
       "13 all pre-v2 (last 10-18 08:47:02), 16 v2-carrier firings zero kills, r1006->r1019 "
       "continuous closeouts; bm-c r1087->r1115 + bm-a r1070+ zero death language; honest "
       "residual disclosure: bm-b first-v2-carrier 24h mark completes 10:57 (~40min residual, "
       "covered by standing commitment); products: "
       "fleet/inbox/MSG-20261019-1017-bmb-o0948-window-judgment.md + order receipt section "
       "append + evidence script results/_r1020bmb_s0probe.py (rerunnable). (d) S1 smoke "
       "49/49 + SatEngine alive idle queue0. (e) S6 41 legs rc0 4min: ZERO-DRIFT streak 51, "
       "minute_feed real pull +281 rows (510300 live 10:13), update_daily no new bar (cutoff "
       "10-16 Monday pre-close -> live.paper family legally skipped), REPORT+LIVE-2026-10-19 "
       "regenerated ORANGE cap50% heat COOL, strategy_scorecard+t35_paper_export+"
       "daily_scorecard+build_status stale-takeover (bm-a stale 81-83min, O-2100 s2.4), "
       "DUALARM-2026-09-30 written, CALL-2026-10-16 ORANGE_COOL, compute_audit "
       "pool_starvation+supply_floor honest 0/3 (answered: W277 landed, burn on bm-c lane, "
       "bm-b pool waits W278 seat / trial-labor standing line), attrition historical 2-shrink "
       "healed note. (f) idle --worked rounds->0 (real judgment work). (g) HANDOVER 5x "
       "catch-up row r1011-r1020 (stamps r1015/r1020 OVERDUE-DISCLOSED per r1083 precedent). "
       "(h) state round_no dual-face drift healed: legacy logs/iteration-loop/state.json was "
       "stale at 1014 (r1015-r1019 five rounds wrote root state.json only) -> both faces now "
       "1020 + heal note; CODELY pit row appended.")

VERDICT = ("GREEN: r1020 判决窗收口轮——O-20261018-0948 死窗 24h 观察窗判决 CASE CLOSED（机队末次 died-pre-closeout="
           "10-18 09:50 bm-c v1 墙钟·+24h 满窗全清；bm-b v2 后 16 发火零击杀·TIMEOUT 13 例全在 v2 前；三机轮报告零死窗语言·"
           "bm-b 首承载锚余 40min 诚实披露由常设承诺覆盖）——判决回执 MSG+令档回执节+可复跑证据脚本三件落位；S0 吸收 "
           "bm-c W277 席位链+bm-a 收口 14 提交（脏树 FF+5 UU 依法拆解·machine-health stashed 面=qwen 对象键损坏写入面"
           "披露）；S6 41 rc0（ZERO-DRIFT 51·minute_feed +281 行实拉·REPORT/LIVE 再生 ORANGE cap50%·四 stale-takeover "
           "面依法接管·supply_floor 诚实饿 0/3 已答=W277 落地 burn 在 bm-c）；state round_no 双面漂移 heal（logs 面 "
           "1014→1020+指针注）；HANDOVER 5x 欠账 r1015/r1020 两截补章；下窗=r1021 ST-010 分档试合成站+BOY/MANCANG "
           "寻源站（voice P1 ≤10-22）+BigMoney 席位计划贡献 ≤10-25+周一 15:30 papers 链")

NEXT = ("r1021: 1) ST-010 pitch-tier test-synthesis station seed+exec (XIONG/XIONGWEI/FATHER "
        "1 line each through GPT-SoVITS + tier DSP 0/+3/-1st -> re-measure F0 separation -- "
        "r1019 debt, first action) 2) BOY/MANCANG sourcing station seed (child-voice license "
        "review first / de-clip re-production) 3) BigMoney seat automation plan contribution "
        "<=10-25 (consume bm-a r1069 3762f3dafa no-rebuild) 4) supply_floor watch: W277 burn "
        "(bm-c lane) -> W278 seat / trial-labor standing line draft 5) Monday 15:30 papers "
        "chain (new bar lands after close) 6) ST-002 CEO direction-gate watch (IndexTTS-2)")

MILESTONE = ("O-0948 case closed -> next: voice P1 <=10-22 (ST-010 tier synthesis + "
             "BOY/MANCANG sourcing) + BigMoney seat automation plan <=10-25 + CONTENT-LOOP "
             "10-28 continuous-run judgment (10 stations seeded / 9 done-ish pace) + "
             "month-boundary 10-31")

ARTIFACT = ("fleet/inbox/MSG-20261019-1017-bmb-o0948-window-judgment.md (O-0948 case closure "
            "receipt) + results/_r1020bmb_s0probe.py (rerunnable evidence) + research/HANDOVER.md "
            "5x catch-up row + S6 products (REPORT-2026-10-19 + LIVE-2026-10-19 ORANGE cap 50% "
            "+ minute_feed +281 rows + DUALARM-2026-09-30)")

RR_ROW = (NOW + " | r1020 bm-b | dept:舰队+媒体产线 | WM verdict: GREEN（red=false @10:03 "
          "watermark_red lane=healthy·链腿 py_watermark insufficient_history n=1 合法起步窗·"
          "idle --worked rounds->0 判决实物工作清零）｜当前活=O-20261018-0948 24h 死窗观察窗判决 CASE "
          "CLOSED（判决窗到期当轮执行）｜最近实物=fleet/inbox/MSG-20261019-1017-bmb-o0948-window-judgment.md"
          "（" + NOW[:16] + "·机队末次 died-pre-closeout=10-18 09:50 bm-c v1 墙钟·+24h 满窗全清·bm-b TIMEOUT 13 例"
          "全在 v2 前·v2 后 16 发火零击杀·三机轮报告零死窗语言·bm-b 首承载锚余 40min 诚实披露）+ 令档回执节追加 + "
          "results/_r1020bmb_s0probe.py 可复跑证据脚本｜下个里程碑=voice P1 ≤10-22（ST-010 分档试合成+BOY/MANCANG "
          "寻源·r1021 首动作）+BigMoney 席位计划 ≤10-25+CONTENT-LOOP 10-28 连跑判决｜S0=吸收 origin 14 提交"
          "（bm-c r1112-1115 W277 席位发布+prereg derive+2D sweep+冻结回执+burn 6/12 在飞+bm-a r1074-1076 收口链+"
          "a5 验收包+perpetual_faces_n1.py）脏树 FF+stash pop 5 UU 依法拆解（resolver results/_r1015bmb_uu_resolve.py："
          "machine-health origin-wins=stashed 面系 qwen3.8:4b 对象被字符串化为键的损坏写入面已披露/futures+lhb+"
          "token_usage upstream-newer/watermark_red 本地 10:03 r1028）｜S0.5=orders 105/105 零未回执+D-19 双探零漂移"
          "（DEC 8706acd8/ORD 04050fda·集团树 fresh-read）｜S1 smoke 49/49｜SatEngine alive idle queue0｜S6 41 腿 "
          "rc0 4min（ZERO-DRIFT 51·minute_feed +281 行实拉·update_daily 0 新行 cutoff 10-16 周一盘前 live.paper 族"
          "依法跳过·REPORT+LIVE-2026-10-19 再生 ORANGE cap50% heat COOL·scorecard/paper_export/daily_scorecard/"
          "build_status=bm-a stale 81-83min 合法 stale-takeover O-2100 s2.4·compute_audit pool_starvation+"
          "supply_floor 诚实旗 0/3 已答=W277 落地 burn 在 bm-c 车道·attrition 历史 2 缩行 [healed] 注记照录）｜S7="
          "四件套幂等全绿（loop pin=2 no-op·watchdog S4U 重注册·双爪 LF 归一重装）+state round_no 双面漂移 heal"
          "（logs/iteration-loop/state.json 陈旧 1014→1020+指针注=r1015-r1019 五轮只写仓根面·CODELY 坑行入册）+"
          "HANDOVER 5x 欠账 r1015/r1020 两截一次窗补章（r1083 先例）｜下轮指针=r1021：①ST-010 分档试合成站播种+执行"
          "（r1019 债·首动作）②BOY/MANCANG 寻源站（童声许可先审）③BigMoney 席位自动化计划贡献 ≤10-25④supply_floor "
          "候 W277 burn→W278 席/试用期常设线⑤周一 15:30 papers 链（新bar 收盘后落）⑥ST-002 候 CEO direction-gate"
          "｜本地未达 origin commit 数=0（收尾 push+fetch 互证）｜新账目=0/8（S6 链探针）｜孤儿面=0（8 面 0 孤儿）"
          "｜登记簿判定=无清扫/归档/删除/恢复类动作（treasure_guard 未触发）")


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

# --- root state.json (primary face, r1019 closeout convention) ---
with io.open(STATE, 'r', encoding='utf-8-sig') as f:
    st = json.load(f)
st['round_no'] = 1020
st['round'] = 1020
st['round_no_label'] = 'r1020'
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
st['now_active'] = 'r1020 closed'
st['current_task'] = ('r1020: O-20261018-0948 24h window judgment CASE CLOSED (died-pre-'
                      'closeout zeroed fleetwide) + S6 41 rc0 + state dual-face heal + push')
st['task'] = st['current_task']
st['verdict'] = VERDICT
st['current'] = VERDICT
st['next'] = NEXT
st['next_milestone'] = MILESTONE
st['latest_artifact'] = ARTIFACT
st['last_artifact'] = ARTIFACT
st['orphan_face'] = 0
st['orphan_faces'] = 8
st['orphan_face_note'] = 'r1020 S6 chain probe (10:11): 8 py faces / 0 orphans'
st['last_decisions_read_at'] = NOW
st['last_orders_read_at'] = NOW
st['sat_engine'] = {
    'status': ('alive (r1020 S3+S6 status rc0, idle verdict, queue_depth 0; supply floor '
               'honest starvation 0/3 -- W277 seat published + prereg derived + frozen '
               '(bm-c r1112-r1115 absorbed at S0), burn in-flight on bm-c engine 6-of-12 '
               'shards; bm-b research pool waits W278 seat window / trial-labor standing '
               'line draft)'),
    'checked_at': NOW,
}
st['sync']['r1019_main_push'] = {
    'status': ('PUSHED_VERIFIED (verified at r1020 S0 FF: e3ec062b76 payload + be88d72a21 '
               'postscript both on origin, ancestor of d7b732c9e8 tip)'),
    'pushed_sha': 'be88d72a21',
    'consumed_at': NOW,
    'behind_origin_main': 0,
    'note': 'r1019 payload delivered pre-r1020; state face closed by r1020',
}
st['sync']['r1020_main_push'] = {
    'status': 'PENDING (this commit)',
    'pushed_sha': 'pending',
    'consumed_at': 'pending r1021',
    'behind_origin_main': 0,
    'note': ('r1020 payload = O-20261018-0948 window judgment (MSG + order receipt append + '
             'evidence/probe/resolver scripts) + drama queue/round-log/loop-state sweep + '
             'state/heartbeat/round-report + HANDOVER 5x catch-up + CODELY pit row + legacy '
             'state heal + S6 own regen/product faces (daily_report/live_usage docs + '
             'scorecard/paper_export/daily_scorecard/dashboard stale-takeover regen + '
             'compute_audit/regime_state/b_layer/dualarm/orphan/attrition faces + collector '
             'bm-b-lane status faces + marks-20261019) + r1020 work files; shared daemon '
             'faces (machine-health/watermark_red/token_usage.json + unsuffixed '
             'lhb/futures/astock/etf status) intentionally NOT added (r982/r1015/r1018/'
             'r1019 policy); base = d7b732c9e8 origin tip fresh at S0 FF'),
}
st['sync']['last_push_ts'] = NOW
with io.open(STATE, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write('\n')

# --- legacy logs/iteration-loop/state.json heal (dual-face drift fix) ---
with io.open(LEGACY_STATE, 'r', encoding='utf-8-sig') as f:
    lg = json.load(f)
lg['round_no'] = 1020
lg['round'] = 1020
lg['round_no_label'] = 'r1020'
lg['clock_read'] = NOW
lg['did'] = DID
lg['last_action'] = DID[:300]
lg['last_action_at'] = NOW
lg['last_round_ts'] = NOW
lg['last_seen'] = NOW
lg['ts'] = NOW
lg['updated_at'] = NOW
lg['now_active'] = 'r1020 closed'
lg['current_task'] = st['current_task']
lg['task'] = st['current_task']
lg['verdict'] = VERDICT
lg['current'] = VERDICT
lg['next'] = NEXT
lg['next_milestone'] = MILESTONE
lg['latest_artifact'] = ARTIFACT
lg['last_artifact'] = ARTIFACT
lg['state_face_note'] = ('r1020 heal: this legacy face was stale at round_no=1014 (r1015-'
                         'r1019 five rounds wrote root state.json per r1019 closeout '
                         'convention only). Primary authoritative face = repo-root '
                         'state.json (sync keys + sat_engine live there). This face healed '
                         'to 1020 at r1020 and will be mirror-written each closeout '
                         '(CODELY pit row r1020).')
with io.open(LEGACY_STATE, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(lg, f, ensure_ascii=False, indent=1)
    f.write('\n')

# --- heartbeat ---
with io.open(HB, 'r', encoding='utf-8-sig') as f:
    hb = json.load(f)
hb['last_seen'] = NOW
hb['ts'] = NOW
hb['clock_read'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
hb['round_no'] = 1020
hb['round'] = 1020
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
hb['now_active'] = 'r1020 closed'
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
assert schk['round_no'] == 1020
with io.open(LEGACY_STATE, 'r', encoding='utf-8-sig') as f:
    lchk = json.load(f)
assert lchk['round_no'] == 1020
print(json.dumps({'verdict': 'closed', 'round': 1020, 'epoch': EPOCH,
                  'ram_free_gb': ram, 'cpu_pct': cpu, 'gpu_free_mb': gpu,
                  'clock_read': NOW}, ensure_ascii=False))
