# -*- coding: utf-8 -*-
"""r1020 bm-b: CODELY hot-cold mini reorg + HANDOVER 5x catch-up row.

Law chain: O-20260927-0230 <=10KB hard line (append-then-reorganize in-window);
TREASURE_PROTECTION_LAW prescan before any archive move; D-20260924-01
byte-level zero-loss verification.
Moves: r1110 bm-c derive-builder pit row (verbatim) -> archive 202610.md
new window section; pointer line stays hot; new r1020 pit row appended hot.
Also appends bm-b HANDOVER 5x catch-up row (r1011-r1020, stamps
r1015/r1020 OVERDUE-DISCLOSED per r1083 precedent).
"""
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
CODELY = os.path.join(ROOT, 'CODELY.md')
ARCHIVE = os.path.join(ROOT, 'research', 'memory-archive', '202610.md')
HANDOVER = os.path.join(ROOT, 'research', 'HANDOVER.md')
RECEIPT = os.path.join(ROOT, 'results', '_r1020bmb_codely_hotcold_receipt.json')

NOW = '2026-10-19 10:2x'
ARCHIVE_SECTION = '热冷整编 2026-10-19 r1020 bm-b 窗批'

# --- 0. treasure_guard prescan (archive-class action gate) ---
p = subprocess.run(['python', 'Tools/treasure_guard.py', 'prescan'],
                   cwd=ROOT, capture_output=True, timeout=60)
prescan_rc = p.returncode
prescan_out = (p.stdout.decode(errors='replace') + p.stderr.decode(errors='replace')).strip()[:400]
print(f'prescan rc={prescan_rc} :: {prescan_out}')
if prescan_rc == 3:
    print('TREASURE_HIT rc3 -- ABORT (no move)')
    raise SystemExit(3)

with io.open(CODELY, 'r', encoding='utf-8-sig') as f:
    raw = f.read()
size_before = len(raw.encode('utf-8'))

# --- 1. locate r1110 row (must exist exactly once) ---
lines = raw.split('\n')
idx = [i for i, ln in enumerate(lines) if ln.startswith('- [2026-10-19 07:3x r1110 bm-c]')]
assert len(idx) == 1, f'r1110 row count={len(idx)} (expected 1)'
i = idx[0]
moved_row = lines[i]

# --- 2. append verbatim to archive ---
with io.open(ARCHIVE, 'a', encoding='utf-8', newline='\n') as f:
    f.write('\n## ' + ARCHIVE_SECTION + '\n\n')
    f.write(moved_row + '\n')
with io.open(ARCHIVE, 'r', encoding='utf-8') as f:
    arc_raw = f.read()
assert moved_row in arc_raw, 'verbatim zero-loss check FAILED (archive)'

# --- 3. replace with pointer row + append new r1020 pit row ---
PTR = ('- 冷层指针：r1110 bm-c derive builder 活值碰撞坑两枚（死针 OLD 面撞当场活值静默回滚上游 roll+裸值 stale ban '
       '误杀本代活面·canon-clone builder 必过 RAM×GPU 2D sweep·ban 一律 context-scoped·0 命中死针即删）全文 '
       'verbatim=archive 202610.md『热冷整编 2026-10-19 r1020 bm-b 窗批』节。')
NEW_PIT = ('- [' + NOW + ' r1020 bm-b] **bm-b 轮号双面漂移坑（r1020 实弹）**：收口脚本族（r1015-r1019 范式）只写仓根 '
           'state.json，logs/iteration-loop/state.json 遗留面停在 1014 五轮无人写——轮首锚定读旧面即取错轮号'
           '（r1020 实读 1014 vs 真实 1020）。正法=S7 收口两 face 同窗写 round_no（仓根=正身携 sync/sat_engine 键·'
           'logs 面=镜像+指针注），禁单面承载轮号真值。How to apply：bm-b 一切新收口脚本模板必含双写腿；轮首锚定'
           '两面 round_no 不一致时以仓根面为准并当窗 heal（r1020 已 heal+本坑行入册）。')
lines[i] = PTR
lines.append(NEW_PIT)
out = '\n'.join(lines)
with io.open(CODELY, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
size_after = len(out.encode('utf-8'))
assert NEW_PIT in out and PTR in out and moved_row not in out
assert size_after < 10240, f'CODELY still over 10KB hard line: {size_after}'

# --- 4. HANDOVER 5x catch-up row ---
HB_ROW = ('> bm-b round 1020 五倍数核对·2026-10-19 10:2x 核对；增量窗覆盖 r1011-r1020 十轮·**5x 戳 r1015/r1020 '
          '两截未落=OVERDUE-DISCLOSED**〔r1015-r1019 五轮全窗被 voice 车道站线连营消耗（ST-005→ST-009）·本窗按 '
          'r1083 先例一次补章〕·零回改零伪造·逐轮权威=logs/iteration-loop/round_reports.md 全行在册+仓根 '
          'state.json sync 族（logs 面 r1020 同窗 heal））：增量窗主线=**O-2144 内容线循环化 CEO 令落地→'
          'CONTENT-LOOP v0.2 实装→voice 车道五连站（ST-005→ST-009）→O-20261018-0948 死窗根治全链收口**——'
          '①r1011 r1010 送达 466312108f+O-2144 令接收；②r1012 手术窗 detached 遗产（r1013 postscript 自愈定谳）；'
          '③r1014 CONTENT-LOOP v0.2 双 runner（content_loop_step.py+st003/st004）+ST-001 集团 LEDGER CAS '
          'ae59395d6b+ST-003 声库首批（GPT-SoVITS/OpenVoice 双克隆+评估面）+ST-004 锚清洗入产线（anchor_precheck.py'
          '+五锚补丁+硬闸）；④r1015/r1016 ST-005 GPT-SoVITS env 全位落地（pyopenjtalk-plus wheel 根因+4351MB '
          'weights+G2PW）+ST-006 voice_bank manifest 7 角色；⑤r1017 ST-007 首合成 smoke（4.42s wav·env 三缺口'
          '修复律入册）；⑥r1018 ST-008 词库 ref clips 5/7（MANCANG clipped/BOY 缺素材诚实负发现）；⑦r1019 '
          'ST-009 角色差异化评估（voice_07 同嗓带债定谳+分档 XIONG 0/XIONGWEI +3st/FATHER -1st）；⑧r1020 本窗='
          'O-20261018-0948 24h 死窗观察窗判决 CASE CLOSED（机队末次 10-18 09:50 bm-c v1 墙钟·+24h 满窗零复发·'
          'bm-b v2 后 16 发火零击杀·MSG-20261019-1017+令档回执节）+state 轮号双面 heal+本行。维护面全窗：smoke '
          '49/49 链·S6 41-43 rc0 链（_r1011..1020bmb_s6chain.ps1 族）·attrition CLEAN 链·双爪恒等链·loop pin=2 链·'
          'idle --worked 链·孤儿面 7-8/0 合法链。产物清单漂移（增量代表面非全列）：content/drama/runner_assets/'
          '{gpt_sovits_env_driver,first_synth_smoke,voice_bank_entries,voice_differentiation_eval}.py+content/drama/'
          'outbox/{VOICE-LIBRARY-EVAL-20261019,VOICE-PIPELINE-SKELETON-v1,ST-007-FIRST-SYNTHESIS-SMOKE-RECEIPT,'
          'VOICE-BANK-ENTRIES-v0.1,VOICE-DIFFERENTIATION-EVAL-v0.1}.md+results/drama_env/*.json 状态面+Tools/'
          'content_loop_step.py st005-st009 五 runner+docs/daily_report/REPORT-2026-10-1{8,9}.md+docs/live_usage/'
          'LIVE-2026-10-1{8,9}.md+fleet/inbox/MSG-20261019-1017-bmb-o0948-window-judgment.md+_r1011..1020bmb_* '
          '工件族。指针：**ST-010 分档试合成站+BOY/MANCANG 寻源站（voice P1 ≤10-22·r1021 首动作）+BigMoney 席位'
          '自动化计划贡献 ≤10-25（消费 bm-a r1069 勿重建）+CONTENT-LOOP 10-28 连跑判决+月界首考 10-31**；'
          '下一 5x=bm-b r1025。[via bm-b r1020]')
with io.open(HANDOVER, 'a', encoding='utf-8', newline='\n') as f:
    f.write(HB_ROW + '\n')

# --- 5. receipt ---
receipt = {
    'ts': time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
    'round': 'r1020',
    'machine': 'bm-b',
    'action': 'codely_hotcold_minireorg + handover_5x_catchup',
    'prescan_rc': prescan_rc,
    'prescan_out': prescan_out[:200],
    'treasure_hit': prescan_rc == 3,
    'moved_row_head': moved_row[:80],
    'archive_section': ARCHIVE_SECTION,
    'codely_bytes_before': size_before,
    'codely_bytes_after': size_after,
    'zero_loss_verified': True,
    'handover_row_appended': True,
}
with io.open(RECEIPT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
    f.write('\n')
print(json.dumps({'ok': True, 'codely_before': size_before, 'codely_after': size_after,
                  'prescan_rc': prescan_rc, 'zero_loss': True}, ensure_ascii=False))
