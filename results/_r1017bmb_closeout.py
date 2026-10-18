"""r1017 bm-b closeout: round report row + state.json + heartbeat (three faces)."""
import datetime
import io
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, 'state.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
RLOG = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')  # +08:00 with T sep
epoch = int(time.time())

DID = ("r1017: (a) S0 FF c9f1ab5f8a..c77ee358f5 absorbed 12 commits (bm-c W275 full cycle CLOSED: "
       "prereg->splice->burn 12/12->sixgate 38th->finalize ledger 1,029,335/K 602,920 EXACT->fivekeys 6/6; "
       "bm-a r1071 A2 G4 PnL-attribution daily ledger + r1072 A3 G1+G2 runtime enforcement); "
       "5 intersecting shared faces resolved per-face (machine-health/watermark_red local live-wins, "
       "token_usage per-machine union r1008 law, lhb/futures origin-wins). "
       "(b) S0.5 orders diff 105/105 acked zero-unacked + D-19 dual probe HOLD (DEC 8706acd8 / ORD 04050fda, "
       "zero rows owed). (c) S1 smoke 49/49 + sat engine alive (queue 0, supply floor honest-starved 0/3, "
       "W275 consumed by bm-c self-burn 12/12; W276 seat publish = bm-c r1109 first action). "
       "(d) FIRST ACTION DONE: ST-007 first-synthesis smoke station seeded (lock-held, engine lock protocol "
       "r1015 pattern) + executed -> engine claim claimed@bm-b@05:58:21 -> done (done-early evidence path). "
       "GPT-SoVITS v1 zero-shot chain PASS: in-house r998 audition ref ep002_line04 (speaker=chang, 3.42s, "
       "audition zero hard flags, MANIFEST-r998 exact text) -> clone -> target line -> output.wav 4.42s/32000Hz/"
       "RMS 0.0105/282,924B, inference wall 26.2s CPU (GPT 1500-step autoreg + SoVITS v1 decode); three env gaps "
       "discovered and fixed idempotent in-window (jieba_fast alias shim via sys.modules; torchaudio-2.11 "
       "torchcodec DLL-face missing -> 5 files 9 call-sites _bmb_ta_load try-native/soundfile-fallback, "
       "py_compile all green; resampy pip idempotent ensure) -- recipes versioned in "
       "content/drama/runner_assets/first_synth_smoke.py ensure_* steps; receipt ST-007-FIRST-SYNTHESIS-SMOKE-"
       "RECEIPT.md + status face results/drama_env/first_synthesis_smoke.json state=done. "
       "(e) engine fix: content_loop_step require_ok case blindness (ST-005 dep gate startswith('st') false on "
       "uppercase 'ST-005' -> lower(); 11 days zero live-fire of the gate semantics); post-fix scan CLEAR "
       "claimable, selftest PASS. (f) S6 43 legs rc0 3.6min: ZERO-DRIFT streak 51, py_watermark "
       "insufficient_history n=1 legal window-start (red=false healthy), market_clock CALL-2026-10-16 ORANGE_COOL "
       "idempotent sleeves=4 activated=0, 4-leg stale-takeover guard legal (bm-a heartbeat stale 46-47min, "
       "O-2100 s2.4), daily_report REPORT-2026-10-19 regenerated (faces=5) + ceo_live_usage LIVE-2026-10-19 "
       "(state=ORANGE cap=50%), attrition healed x1, live.paper family honest skip (Monday pre-15:30 no new bar, "
       "cutoff 2026-10-16). (g) S7: 6 Bigmoney tasks present, claws pre-commit/pre-push OK; SatEngine-bm-b "
       "false-MISSING heal signal (r1017 s7check nested-powershell capture bug) fired default-principal register "
       "-> InteractiveToken flip; same-window XML flip back to S4U rc=0 (backup %TEMP%\\bmb-s4u-backup-*.xml); "
       "lesson logged. (h) CODELY hotcold split 10,978B->8,612B (6 pit rows verbatim -> archive 202610.md "
       "r1017 window-batch section; treasure_guard prescan rc3 -> ledger-class 摘录存旁 channel; zero-loss "
       "asserted; receipt _r1017bmb_codely_hotcold_receipt.json) + 2 new pit rows (env 3-gap law + self-heal "
       "false-signal family). (i) idle two-read RED cleared by real product work (idle --worked rounds->0, "
       "agenda_starved=false). Orphan face=0/7.")

VERDICT = ("GREEN: r1017 ST-007 首合成冒烟站播种+执行收站 done（r1016 升格首动作闭环：GPT-SoVITS 零样本链实弹 "
           "PASS——r998 自产参考音 3.42s→克隆→目标句→4.42s wav·CPU 26.2s；三处环境缺口同窗幂等修复且配方版本化"
           "可复跑；CONTENT-LOOP 站点 7 done/1 gated）；引擎依赖闸大小写盲区修（require_ok lower()）；S6 43 rc0"
           "（D-19 双零·四腿接管合法·supply_floor 诚实旗候 bm-c W276 prereg）；S7 SatEngine S4U 复位（假 MISSING "
           "信号教训入册）；CODELY 热冷整编 10,978→8,612B 零丢失；下窗=r1018 O-0948 判决窗 10-19 ~10:2x+正典声银行"
           "入行站播种（7 角色 r998 自产素材对齐+音色一致检）+BigMoney 席位自动化计划贡献 ≤10-25")

NEXT = ("r1018: 1) O-0948 window close judgment 10-19 ~10:2x (v1 wall-clock census order) "
        "2) voice lane next station seed: canon voice-bank entries (7 chars x 1-3 ref clips from r998 "
        "in-house assets role-aligned + 音色一致检 gate; voice P1 <=10-22) "
        "3) ST-002 watch CEO direction-gate receipt (IndexTTS-2 stays gated) "
        "4) BigMoney seat automation plan contribution <=10-25 (bm-a r1069 3762f3dafa consume-no-rebuild) "
        "5) supply_floor: on bm-c W276 prereg freeze landing -> engine supply leg check "
        "6) CONTENT-LOOP 10-28 continuous-run judgment (7 stations/2 days, >=3 stations/day on track)")

MILE = ("ST-007 smoke complete -> voice P1 next: canon voice-bank entry station + TTS batch runner (<=10-22) "
        "+ O-0948 window judgment 10-19 ~10:2x + CONTENT-LOOP 10-28 continuous-run judgment")

ART = ("results/drama_env/first_synthesis_smoke.json state=done (GPT-SoVITS first-synthesis smoke PASS: "
       "output.wav 4.42s/32kHz/RMS 0.0105/282,924B, inference 26.2s CPU, ref=r998 ep002_line04 in-house) "
       "+ content/drama/outbox/ST-007-FIRST-SYNTHESIS-SMOKE-RECEIPT.md + S6 products (REPORT-2026-10-19 + "
       "LIVE-2026-10-19 ORANGE cap 50%)")

RROW = (now + " | r1017 bm-b | dept:媒体产线+数据 | WM verdict: GREEN (red=false @06:00 py_watermark "
        "insufficient_history n=1 合法采样窗刚起·idle --worked rounds->0) | 当前活=ST-007 首合成冒烟站"
        "播种+执行收站 done（engine claim claimed@bm-b@05:58:21→done-early 证据路径） | 最近实物="
        "media/drama-tools/voice_smoke/st007/out/output.wav（GPT-SoVITS 零样本链 PASS：4.42s/32000Hz/"
        "RMS 0.0105/282,924B·推理 26.2s CPU·参考音=r998 自产 ep002_line04 3.42s 零硬旗）+ 状态面 "
        "results/drama_env/first_synthesis_smoke.json + 回执 content/drama/outbox/"
        "ST-007-FIRST-SYNTHESIS-SMOKE-RECEIPT.md；三处环境缺口同窗幂等修复（jieba_fast alias shim / "
        "torchaudio-2.11 torchcodec DLL 缺面→5 文件 9 调用位 sf-回退 py_compile 绿 / resampy pip ensure·"
        "配方版本化 runner_assets/first_synth_smoke.py）+ 引擎依赖闸 require_ok 大小写盲区修（lower()）| "
        "S0 FF 吸收 12 提交（bm-c W275 全周期闭合+bm-a r1071/r1072 A2/A3）·S6 43 腿 rc0 3.6min"
        "（ZERO-DRIFT 51 连绿·D-19 双零 DEC 8706acd8/ORD 04050fda·四腿 stale-takeover 合法·"
        "supply_floor 诚实旗 0/3 候 bm-c W276 prereg）·S7 六任务全在+爪钳 OK+SatEngine 假 MISSING 触发"
        " principal 翻转→当窗 XML 翻回 S4U（备份 %TEMP%·教训入册）·CODELY 热冷整编 10,978→8,612B"
        "（6 行 verbatim→archive 202610 r1017 窗批·prescan rc3 摘录存旁通道·零丢失断言·回执"
        " _r1017bmb_codely_hotcold_receipt.json）| 下轮指针=r1018：①O-0948 判决窗 10-19 ~10:2x "
        "②正典声银行入行站播种（7 角色 r998 自产素材对齐+音色一致检·voice P1 ≤10-22）③ST-002 watch "
        "CEO direction-gate（IndexTTS-2 保持门）④BigMoney 席位自动化计划贡献 ≤10-25 ⑤supply_floor 候 "
        "bm-c W276 prereg 落地后引擎供给腿检查 | 本地未达 origin commit 数=N（收口 push+fetch 验证后"
        "回填 postscript）| 孤儿面=0/7（S6 探针 05:59）| 令集=105/105 全回执 | 登记簿零命中断言=本轮无"
        "清扫动作·CODELY 整编走 prescan rc3 摘录存旁通道+零丢失回执")


def rd(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return json.load(f)


def wr(p, obj):
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


st = rd(STATE)
st.update({
    'clock_read': now, 'ts': now, 'updated': now, 'updated_at': now,
    'last_seen': now, 'last_round_at': now, 'last_round_ts': now,
    'last_action_at': now,
    'round_no': 1017, 'round': 1017, 'round_no_label': 'r1017',
    'now_active': 'r1017 closed (postscript pending push-verify)',
    'current_task': 'r1017: ST-007 first-synthesis smoke seeded+executed done (3 env gaps fixed in-window, recipes versioned) + S6 43 rc0 + CODELY hotcold + push',
    'task': 'r1017: ST-007 first-synthesis smoke seeded+executed done (3 env gaps fixed in-window, recipes versioned) + S6 43 rc0 + CODELY hotcold + push',
    'did': DID, 'last_action': DID[:400],
    'verdict': VERDICT, 'current': VERDICT,
    'latest_artifact': ART, 'last_artifact': ART,
    'next': NEXT, 'next_milestone': MILE,
    'orphan_face': 0,
    'orphan_face_note': 'r1017 S6 chain probe (05:59): 7 py faces / 0 orphans',
    'heartbeat_epoch_utc_face': 'bm-b.json updated this round (epoch int verified)',
})
st['sat_engine'] = {
    'status': 'alive (r1017 S6 status rc0, idle verdict, queue_depth 0; supply floor honest starvation '
              '0/3 -- W275 fully consumed by bm-c 12/12 self-burn, W276 seat publish = bm-c r1109 first action)',
    'checked_at': now,
}
st.setdefault('sync', {})['r1017_main_push'] = {
    'status': 'PENDING (this commit)',
    'pushed_sha': 'pending',
    'consumed_at': 'pending r1018',
    'behind_origin_main': 0,
    'note': 'r1017 payload = own faces (state/heartbeat/round-report + ST-007 smoke kit x4 [runner_assets '
            'driver + outbox receipt + status face + content_loop runner/fix] + drama loop faces x5 + '
            'CODELY hotcold 4 [md+archive+script+receipt] + r1017 work files x6 + own regen/product faces '
            '[daily_report/live_usage docs + scorecard/paper_export/daily_scorecard/dashboard/update_status/'
            'market_clock-family/compute_audit/b_layer/regime_state/dualrun/attrition/orphan/d19 + collector '
            'bm-b status faces]); shared daemon faces (machine-health/watermark_red/token_usage.json + '
            'unsuffixed lhb/futures status) intentionally NOT added (r982/r1012 policy)',
}
wr(STATE, st)

hb = rd(HB)
hb.update({
    'last_seen': now, 'ts': now, 'clock_read': now,
    'round_no': 1017, 'round': 1017,
    'now_active': 'r1017 closed (postscript pending push-verify)',
    'current_task': st['current_task'], 'task': st['current_task'],
    'did': DID, 'last_action': DID[:400], 'last_action_at': now,
    'verdict': VERDICT, 'current': VERDICT,
    'latest_artifact': ART, 'last_artifact': ART,
    'next': NEXT, 'next_milestone': MILE,
    'idle_rounds': 0, 'agenda_starved': False,
    'heartbeat_epoch_utc': epoch,  # JSON int (R170/R178 law)
    'orphan_face': 0,
})
wr(HB, hb)

with io.open(RLOG, 'a', encoding='utf-8') as f:
    f.write(RROW + '\n')

# post-write assertions
st2 = rd(STATE)
hb2 = rd(HB)
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in hb2['clock_read'] and '+' in hb2['clock_read'], 'clock_read must be ISO8601 T-sep'
assert st2['round_no'] == 1017 and hb2['round_no'] == 1017
print(json.dumps({'ok': True, 'round': 1017, 'epoch': hb2['heartbeat_epoch_utc'],
                 'clock': hb2['clock_read'], 'rrow_bytes': len(RROW.encode('utf-8'))},
                 ensure_ascii=False))
