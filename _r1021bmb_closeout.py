# -*- coding: utf-8 -*-
# r1021 bm-b closeout: state.json (root primary) + legacy mirror + heartbeat + round report row.
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

DID = ("r1021: (a) S0 absorb origin 3 commits (bm-c r1115-continuation window: W277 CYCLE "
       "COMPLETE sixgate 40th ALL PASS + finalize 1,033,735/607,320 EXACT + fivekeys 6/6 + "
       "W278 SEAT PUBLISHED probe ADMIT first-try + closeout) via stash 6 own dirty faces -> "
       "ff-only 78af6c9ca..efc4a1c1b -> pop 1 UU watermark_red newer-wins (local 10:46:04 > "
       "origin 10:39:03) -> stash dropped; W278 seat MSG @ALL consumed (informational: bm-c "
       "next window derives prereg; bm-b zero action) -> processed/ move. (b) S0.5 orders "
       "O-*.md 105/105 zero-unacked (fleet/orders/README.md = folder readme non-order face, "
       "disclosed); D-19 dual probe DEC 8706acd8 UNCHANGED / ORD 04050fda->a14c3693 CHANGED "
       "mid-round -> consumed row 10-19 10:53 CEO jman LoRA young-tier order (dispatched "
       "@bm-c GPU training lane, bm-b zero-action row; voice-lane bm-b face already carried "
       "by ST-008/010 stations per 10-18 20:17/20:20 character-bank orders) -> watermark "
       "advanced d19_watermark.py update --advance (ord=a14c3693, mirrors synced 3). "
       "(c) FIRST ACTION: ST-010 pitch-tier test-synthesis station seeded+executed (r1019 "
       "debt): seeded ST-010 (runner st010_pitch_tier_test_synth, require ST-009) + ST-011 "
       "(BOY/MANCANG sourcing, v0.2-pending) lock-held; loop selftest PASS (11 stations); "
       "runner registered in Tools/content_loop_step.py + versioned driver "
       "pitch_tier_test_synth.py + venv DSP helper st010_dsp_helper.py (librosa 0.10.x "
       "effects-namespace pitch_shift face fixed in-window; GPT-SoVITS 3-10s ref gate vs "
       "FATHER 2.31s single admitted clip -> deterministic tail-silence pad 3.05s "
       "disclosed); execution saga: loop round 46 first full chain = frozen-face gate FAIL "
       "(honest) -> same-window v2 two-stage driver: stage1 frozen ST-009 offsets "
       "{0,+3,-1} on synth outputs FAIL (X-F 6.6%); KEY FINDING = zero-shot same-text "
       "synthesis homogenizes F0 register (raw 173.5/172.0/177.8Hz despite ref "
       "165.8/162.8/151.0Hz) -> ref-derived offsets do not transfer; stage2 deterministic "
       "re-tier ON synth F0s (ST-009 tier_search law reuse) {0,+3,-4} measured X-F 14.99% "
       "miss (nominal -4st -> measured ~-3.5st) -> bounded verify-adjust loop iter1 "
       "FATHER -4->-5 -> ALL PASS: X-XW 15.41% / X-F 19.65% / XW-F 32.03% (all out of "
       "same-voice band); FATHER -5st = search edge + outside +/-3st DSP safe zone (honest "
       "limits, ear-check weight up, root fix = distinct-source re-supply ST-011); "
       "products: 3x{raw, tier_frozen, tier} wavs (media area) + status face "
       "results/drama_env/pitch_tier_test_synth.json + receipt "
       "ST-010-PITCH-TIER-TEST-SYNTH-RECEIPT.md (two-stage + adjust trace + honest "
       "limits) + batch-station method prototype (per-line verify-adjust loop). "
       "(d) S1 smoke 49/49 + SatEngine alive idle queue0 rc0. (e) S6 41 legs rc0 3.9min: "
       "ZERO-DRIFT streak 51, minute_feed 510300 +50 rows, update_daily no new bar "
       "(Monday pre-close -> live.paper family legally skipped), REPORT+LIVE-2026-10-19 "
       "regenerated ORANGE cap50% heat COOL, 4 stale-takeover faces (scorecard/"
       "paper_export/daily_scorecard/build_status -- bm-a stale 131-133min daytime-paused "
       "per CEO 10-15 law), DUALARM-2026-09-30, CALL-2026-10-16 ORANGE_COOL idempotent, "
       "compute_audit pool_starvation+supply_floor honest 0/3 (answered: W278 prereg "
       "derive = bm-c next window; bm-b pool feeds after), attrition bm-a shrink-2 "
       "[healed] note. (f) idle --worked rounds->0 (real product work). (g) S7 quad "
       "registrations green (loop pin=2 no-op, watchdog S4U re-registered, both claws "
       "LF-normalized reinstalled). (h) DEFERRED: CODELY.md pit row (nominal != measured "
       "semitone + verify-adjust loop lesson) -- file at 10,231B just under 10,240B hard "
       "line; append would trigger mandatory in-window hot-cold split; scheduled r1022 "
       "first action WITH the split; lesson already versioned in receipt/driver/status "
       "face (three git faces).")

VERDICT = ("GREEN: r1021 产品轮——ST-010 分档试合成站播种+执行收官 gate PASS（二段法：stage1 冻结面 "
           "{0,+3,-1} 在合成面 FAIL=同句零样本合成把 F0 拉平 173.5/172.0/177.8Hz·参考音面分档不迁移→"
           "stage2 合成面重分档 {0,+3,-4} 实测 X–F 14.99% 差 0.01%→校验-调整环 FATHER -4→-5→全对出同嗓带 "
           "15.41%/19.65%/32.03%；FATHER -5st=搜索域边界+超±3 安全区诚实披露·根解=换源寻根 ST-011）；"
           "关键发现=名义半音≠实测半音（-4st 名义→-3.5st 实测）→分离门必须在实测面上校验=批产站逐行"
           "校验-调整环方法原型；ST-011 寻源站同窗播种（BOY 童声许可先审/MANCANG 去削波）；S0 吸收 "
           "bm-c W277 完成+W278 席位链 3 提交（watermark_red UU newer-wins）；D-19 ORD 增量消费"
           "（10:53 jman LoRA 年轻档令 @bm-c·bm-b 零动作行·水位已推进）；S6 41 rc0（REPORT/LIVE 再生 "
           "ORANGE cap50%·四 stale-takeover 面接管·supply_floor 诚实饿 0/3 已答=W278 prereg 派生在 "
           "bm-c 下窗）；下窗=r1022 周一 15:30 papers 链+CODELY 坑行+热冷整编（10,231B 贴线）+ST-011 "
           "执行+BigMoney 席位计划 ≤10-25")

NEXT = ("r1022: 1) Monday 15:30 papers chain (new bar lands after close -> live.paper + "
        "t35_open_fill + t24 prospect + export family) 2) CODELY.md pit row append "
        "(nominal!=measured semitone verify-adjust lesson) + in-window hot-cold split "
        "(file at 10,231B just under 10,240B hard line -- append triggers the split) "
        "3) ST-011 BOY/MANCANG sourcing station exec (child-voice license review FIRST) "
        "4) BigMoney seat automation plan contribution <=10-25 (consume bm-a r1069 "
        "3762f3dafa no-rebuild) 5) supply_floor watch: W278 prereg derive (bm-c r1115) -> "
        "bm-b N1 pool feed 6) batch-station spec: per-line verify-adjust tier loop "
        "(ST-010 method prototype)")

MILESTONE = ("voice P1 <=10-22 (ST-010 gate PASS delivered + ST-011 sourcing + batch station "
             "per-line verify-adjust spec) + BigMoney seat automation plan <=10-25 + "
             "CONTENT-LOOP 10-28 continuous-run judgment (11 stations seeded / 10 done pace) "
             "+ month-boundary 10-31")

ARTIFACT = ("content/drama/outbox/ST-010-PITCH-TIER-TEST-SYNTH-RECEIPT.md + "
            "results/drama_env/pitch_tier_test_synth.json (gate PASS, two-stage+adjust "
            "trace) + runner trio (pitch_tier_test_synth.py + st010_dsp_helper.py + "
            "content_loop_step.py registration) + media wavs "
            "media/drama-tools/voice_smoke/st010/<CID>/{tier.wav,tier_frozen.wav} + "
            "S6 products (REPORT-2026-10-19 + LIVE-2026-10-19 ORANGE cap 50% + "
            "minute_feed +50 rows + DUALARM-2026-09-30)")

RR_ROW = (NOW + " | r1021 bm-b | dept:媒体产线+舰队 | WM verdict: GREEN（red=false @10:46 "
          "watermark_red lane=healthy·ORD 水位已推进 a14c3693·py_watermark "
          "insufficient_history n=1 合法起步窗·idle --worked rounds->0 实物工作清零）｜"
          "当前活=ST-010 分档试合成站收官（gate PASS·二段法+校验-调整环全链落证）｜"
          "最近实物=content/drama/outbox/ST-010-PITCH-TIER-TEST-SYNTH-RECEIPT.md（" + NOW[:16] +
          "·门判 PASS：重分档 {XIONG 0, XIONGWEI +3, FATHER -5} 实测对 15.41%/19.65%/32.03% 全出同嗓带·"
          "关键发现=同句零样本合成 F0 拉平+名义半音≠实测半音→分离门必须实测面校验=批产站逐行校验-调整环"
          "方法原型·FATHER -5st 超±3 安全区诚实披露·根解=ST-011 换源）+ 状态面 "
          "results/drama_env/pitch_tier_test_synth.json + 三件 runner（驱动/DSP 助手/队列注册）+ "
          "media 分档 wav×3｜下个里程碑=voice P1 ≤10-22（ST-010 已交+ST-011 寻源+批产站规格）+BigMoney "
          "席位计划 ≤10-25+CONTENT-LOOP 10-28 连跑判决｜S0=吸收 origin 3 提交（bm-c r1115 续窗：W277 "
          "完成 sixgate 40th+finalize EXACT+fivekeys 6/6+W278 席位发布探针 ADMIT）脏树 FF+stash pop 1 UU "
          "watermark_red newer-wins（本地 10:46>origin 10:39）｜S0.5=orders O-*.md 105/105 零未回执"
          "（README.md=目录说明件非令件如实披露）+D-19 双探：DEC 8706acd8 持平/ORD 04050fda→a14c3693 "
          "轮中变更→消费 10-19 10:53 jman LoRA 年轻档令（dispatched @bm-c 视觉车道·bm-b 零动作行·声音"
          "车道 bm-b 面已由 ST-008/010 承接）→d19 update --advance 推进（mirrors synced 3）｜S1 smoke "
          "49/49｜SatEngine alive idle queue0｜S6 41 腿 rc0 3.9min（ZERO-DRIFT 51·minute_feed 510300 "
          "+50 行·update_daily 0 新行=周一盘前 cutoff 10-16·live.paper 族依法跳过·REPORT+LIVE 再生 "
          "ORANGE cap50% heat COOL·scorecard/paper_export/daily_scorecard/build_status=bm-a stale "
          "131-133min 白天让路态合法 stale-takeover O-2100 s2.4·compute_audit pool_starvation+"
          "supply_floor 诚实旗 0/3 已答=W278 prereg 派生在 bm-c 下窗·attrition bm-a 缩 2 行 [healed] "
          "注记照录）｜S7=四件套幂等全绿（loop pin=2 no-op·watchdog S4U 重注册 first fire 11:07·双爪 "
          "LF 归一重装）+W278 席位 MSG processed move｜DEFERRED=CODELY.md 坑行（名义≠实测半音+校验-调整环"
          "教训）——文件 10,231B 贴 10,240B 硬线·追加即触发当窗热冷整编·排 r1022 首动作随整编落（坑已在"
          "回执/驱动/状态面三处版本化）｜下轮指针=r1022：①周一 15:30 papers 链（新 bar 收盘后落）②CODELY "
          "坑行+热冷整编③ST-011 寻源站执行（童声许可先审）④BigMoney 席位计划 ≤10-25⑤supply_floor 候 "
          "W278 prereg→bm-b 池喂料⑥批产站规格=逐行校验-调整环｜本地未达 origin commit 数=0（收尾 "
          "push+fetch 互证）｜新账目=0/8（S6 链探针）｜孤儿面=0（7 面 0 孤儿）｜登记簿判定=无清扫/归档/"
          "删除/恢复类动作（treasure_guard 未触发·CODELY 整编为 r1022 排期件非本轮动作）")


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
st['round_no'] = 1021
st['round'] = 1021
st['round_no_label'] = 'r1021'
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
st['now_active'] = 'r1021 closed'
st['current_task'] = ('r1021: ST-010 pitch-tier test-synthesis gate PASS (two-stage '
                      're-tier {0,+3,-5} + verify-adjust loop) + ST-011 seeded + S6 41 '
                      'rc0 + ORD delta consumed + push')
st['task'] = st['current_task']
st['verdict'] = VERDICT
st['current'] = VERDICT
st['next'] = NEXT
st['next_milestone'] = MILESTONE
st['latest_artifact'] = ARTIFACT
st['last_artifact'] = ARTIFACT
st['orphan_face'] = 0
st['orphan_faces'] = 7
st['orphan_face_note'] = 'r1021 S6 chain probe (11:00): 7 py faces / 0 orphans'
st['sat_engine'] = {
    'status': ('alive (r1021 S3+S6 status rc0, idle verdict, queue_depth 0; supply floor '
               'honest starvation 0/3 -- W277 complete + W278 seat published (bm-c '
               'r1115-continuation absorbed at S0), W278 prereg derive = bm-c next '
               'window FIRST ACTION; bm-b N1 pool feeds after prereg lands)'),
    'checked_at': NOW,
}
st['sync']['r1020_main_push'] = {
    'status': ('PUSHED_VERIFIED (verified at r1021 S0: fetch behind=3 ahead=0 -> r1020 '
               'payload commit 78af6c9ca on origin, bm-c 3 continuation commits on top)'),
    'pushed_sha': '78af6c9ca',
    'consumed_at': NOW,
    'behind_origin_main': 0,
    'note': 'r1020 payload delivered pre-r1021; state face closed by r1021',
}
st['sync']['r1021_main_push'] = {
    'status': 'PENDING (this commit)',
    'pushed_sha': 'pending',
    'consumed_at': 'pending r1022',
    'behind_origin_main': 0,
    'note': ('r1021 payload = ST-010 station products (receipt + status face + runner '
             'trio: driver/DSP helper/content_loop_step registration + seed script) + '
             'queue/claims/round-log/loop-state + ST-011 seed + state/heartbeat/'
             'round-report + W278 MSG processed move + S6 own regen/product faces '
             '(daily_report/live_usage docs + scorecard/paper_export/daily_scorecard/'
             'dashboard stale-takeover regen + compute_audit/regime_state/b_layer/'
             'dualarm/orphan/attrition/d19 faces + collector bm-b-lane status faces + '
             'marks-20261019 + minute_feed rows) + r1021 work files; shared daemon faces '
             '(watermark_red/token_usage.json + unsuffixed lhb/futures/astock/etf status) '
             'intentionally NOT added (r982/r1015/r1020 policy); base = efc4a1c1b origin '
             'tip fresh at S0 FF'),
}
st['sync']['last_push_ts'] = NOW
with io.open(STATE, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write('\n')

# --- legacy logs/iteration-loop/state.json mirror (r1020 dual-face law) ---
with io.open(LEGACY_STATE, 'r', encoding='utf-8-sig') as f:
    lg = json.load(f)
lg['round_no'] = 1021
lg['round'] = 1021
lg['round_no_label'] = 'r1021'
lg['clock_read'] = NOW
lg['did'] = DID
lg['last_action'] = DID[:300]
lg['last_action_at'] = NOW
lg['last_round_ts'] = NOW
lg['last_seen'] = NOW
lg['ts'] = NOW
lg['updated_at'] = NOW
lg['now_active'] = 'r1021 closed'
lg['current_task'] = st['current_task']
lg['task'] = st['current_task']
lg['verdict'] = VERDICT
lg['current'] = VERDICT
lg['next'] = NEXT
lg['next_milestone'] = MILESTONE
lg['latest_artifact'] = ARTIFACT
lg['last_artifact'] = ARTIFACT
lg['state_face_note'] = ('r1021: mirror-written per r1020 dual-face law (repo-root '
                        'state.json = primary authoritative face).')
with io.open(LEGACY_STATE, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(lg, f, ensure_ascii=False, indent=1)
    f.write('\n')

# --- heartbeat (fresh read: d19 advance already updated watermark mirrors) ---
with io.open(HB, 'r', encoding='utf-8-sig') as f:
    hb = json.load(f)
hb['last_seen'] = NOW
hb['ts'] = NOW
hb['clock_read'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
hb['round_no'] = 1021
hb['round'] = 1021
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
hb['now_active'] = 'r1021 closed'
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
assert schk['round_no'] == 1021
with io.open(LEGACY_STATE, 'r', encoding='utf-8-sig') as f:
    lchk = json.load(f)
assert lchk['round_no'] == 1021
print(json.dumps({'verdict': 'closed', 'round': 1021, 'epoch': EPOCH,
                  'ram_free_gb': ram, 'cpu_pct': cpu, 'gpu_free_mb': gpu,
                  'clock_read': NOW}, ensure_ascii=False))
