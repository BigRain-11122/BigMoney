"""r82 bm-c S7 wrap: heartbeat + state + round report (asserted, zero-BOM-safe, CRLF-preserving)."""
import io
import json
import time
import glob
import os

NOW = time.strftime('%Y-%m-%dT%H:%M:%S')
HM = NOW[11:19]
EPOCH = int(time.time())


def read_json_raw(p):
    b = open(p, 'rb').read()
    bom = b.startswith(b'\xef\xbb\xbf')
    return json.loads(b.decode('utf-8-sig')), bom


def write_json_raw(p, obj, bom):
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    b = s.encode('utf-8')
    if bom:
        b = b'\xef\xbb\xbf' + b
    open(p, 'wb').write(b)


# --- heartbeat: fleet/machines/bm-c.json (own file only) ---
hb, bom = read_json_raw('fleet/machines/bm-c.json')
ack = sorted(os.path.basename(p) for p in glob.glob('fleet/orders/O-*.md'))
assert len(ack) == 96, 'orders dir count: %d' % len(ack)
hb['orders_ack'] = ack
hb['last_seen'] = NOW + '+08:00'
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = NOW + '+08:00'
hb['cpu_util_pct'] = 30.0
hb['free_ram_gb'] = 0.6
hb['gpu_free_vram_mb'] = 10970
hb['cpu_pct'] = 0.0
hb['current_task'] = ('R82 done: decisions D-06~10 catch-up review (origin direct-read recipe) + D-09 '
                       'execution verified on-tree + CODELY water-line 13th-batch archival (8460B) + S6 32/32; '
                       'R83: watch repull terminal window ~15:0x (bm-a mechanical three-piece -> moneyflow IC '
                       'batch lands -> starvation convergence criterion)')
hb['verdict'] = ('FLAG:pool_starvation honest face continued (audit v2.3 13:10:43, py 0.0%, pool ready=0): '
                 'supply line in-flight on other machines (bm-a sina_mf A1 repull ETA ~15:0x -> moneyflow IC '
                 'reference batch next_pick claimed; bm-b sina-construct prereg gate opens on completion); '
                 'bm-c zero legal feed face (board 0 open, own tickets date/blocked/HOLD, T-87 closed '
                 'zero-survivor, T-86 s2 = bm-a claimed science face no dual-head, 禁造数凑烧恒在律) -- '
                 'red-card disclosure per O-2320, closure expected ~15:0x with repull terminal verdict')
write_json_raw('fleet/machines/bm-c.json', hb, bom)

# post-write self-assertions (F7 discipline)
hb2, _ = read_json_raw('fleet/machines/bm-c.json')
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in hb2['clock_read'] and '+' in hb2['clock_read'], 'clock_read ISO T-separated'
assert hb2['orders_ack'] == ack and len(ack) == 96

# --- state: state-bm-c.json (own file only) ---
st, bom2 = read_json_raw('state-bm-c.json')
assert st['round_no'] == 81, 'unexpected round_no %s' % st['round_no']
st['round_no'] = 82
st['updated'] = NOW[:16]
st['note'] = ('r82: decisions D-06~10 catch-up via origin direct-read (local HQ worktree stale at D-05, origin '
              'aacae41 has noon batch; r80/r81 stale-face miss disclosed; pitlaw in CODELY) + D-09 (conflict-'
              'resolve two-fix) verified on-tree (bm-a r321 executed; classify deep-scan + SKILL suffix-concat '
              'present; no runtime skill copy on bm-c = dual-copy face is bm-a side) + CODELY water-line 13th-'
              'batch archival (r312 fetch-insight + r320 PS-lane-splat -> 202609.md, line-level zero-loss, '
              '8460B<10KB) + self-inflicted glued-tail red fixed + S6 32/32 rc=0.')
st['last_round_ts'] = NOW + '+08:00'
write_json_raw('state-bm-c.json', st, bom2)

# --- round report: line append (CRLF-preserving) ---
rp = 'logs/iteration-loop/round_reports-bm-c.md'
raw = open(rp, 'rb').read()
eol = b'\r\n' if b'\r\n' in raw[-200:] else b'\n'
line = (
    HM + '｜R82｜bm-c watermark verdict=绿（wm probe 13:10 rc=0 verdict=insufficient_history n=2 span 12.2min 窗累积如实·red=false 12:40:03 lane healthy；'
    'audit v2.3 13:10:43 FLAG:pool_starvation 供线缺口如实续报：py 0.0%/pool ready=0·合法收敛面不变=bm-a sina_mf A1 repull 在飞 ETA ~15:0x→moneyflow IC reference batch next_pick claimed·'
    'bm-b sina-construct prereg gate 随开·本机零合法喂弹面（板 0 open+本机票 T-16 周一窗/T-17 AH EM 阻断待窗/T-19 毕）·禁造数凑烧恒在律）｜'
    '决策审核补审回执（新读法=集团仓 git fetch+git show origin/main:docs/decisions.md 直读 origin 零工作树触碰——本机集团仓工作树 mtime 09:08 止 D-05·origin aacae41 已含决策轮午批 D-20260927-06~10·'
    'r80/r81 按陈面漏审如实披露+坑律入 CODELY）：D-09 涉本仓=冲突解两修法（嵌套 ts 深扫+memory-union 后缀直拼）bm-a r321 已同轮执行·本机树验证在场（classify_conflicts.py L46 deep-scans+SKILL.md L34 后缀直拼·'
    '本机 .codely-cli 无运行时 skill 副本=双副本同步面在 bm-a 侧零动作）+回执确认收口；D-06/07/10=HQ 收取面零动作（D-07 本机窗 0025ea7 P-07 双落在案）；D-08 委员会 C-20260927-01=非本司域零动作；D-01~05 r81 已回执维持｜'
    'S0 pull already-up-to-date（零冲突）+round-start 树干净｜S0.5 orders 全扫 96/96 ack 差集零（本机心跳对账）+inbox 0 未读｜S1 smoke 25/25｜S2 板 0 open·job_list 0·next_pick=claimed（moneyflow IC 车道）｜'
    'S3 主活（dept:工程+治理）＝决策台账读面修法+CODELY 水位整编：①轮首身份自证=先误读根目录 state-bm-a.json 为本机（多机 state 件并存）·sina_mf 探针 #6 尝试即遭 FileNotFound 零产出零残留（车道护栏结构性兜底）·'
    '身份以 fleet\\machine.json 实读自证=bm-c 转正——教训=轮首必先实读 machine.json 再读任何 state 件；②本轮自伤修红=append 碎片段锚定（old_string 截断条目头）致 r323 bm-b 条目体粘连 r82 新行尾（10601B 超线）→'
    'results/_r82bmc_codely_archive.py 程序化修复（combo 锚定切除+在场断言+r323 正条目唯一在场断言）；③水位律十三批当窗外迁=r312 bm-a 轮内烧片 fetch 洞察+r320 bm-b PS lane 嵌套 splat 两行级零丢失入 '
    'research/memory-archive/202609.md 十三批节+CODELY 索引行（归档侧回流查零重复先行）·CODELY 8460B<10KB 线·二进制 CRLF 校验；④坑律 r82 入册（决策台账 origin 直读法·一条一事）｜'
    'S6 32/32 rc=0（_r82bmc_s6_chain.ps1=r81 谱系 Copy-Item 头部差异律 per r298·difflib delta=header 1 行验证：audit FLAG 上述/wm probe rc0/daily 周日 0 新行 cutoff 09-24/regime ORANGE shadow breadth 0.77/'
    'scorecard 6-28-7/clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0/lhb <30min/heat 周末/fut 本地覆盖 no-op/车道护栏诚实 no-op 9 道（opt/mf/smf/astk/rev_osc/ths/ah/alloc/sysv1）/fp 我车道周末 NAV no-op/'
    'fund fresh 3.7h/blf pass/live paper OK+t35 open-fill PASS 0/0/0/t24 22/22 drift0+promo 0/22 诚实腿败/aggr+grid 幂等 no-op/t35exp 再生 export-09-24/dsc 6 员/drep REPORT-20260927 faces=4 token=1/bs 432combos/'
    'token L2 1 腿 ~6450 crash-fuse refusals=1）｜S7 心跳簿记（epoch int 1790485844 类自证+clock ISO T 分隔+orders_ack 目录再生 96 全枚举）+schtasks 双任务在役+push 回执见 commit｜'
    '证据=results/_r82bmc_codely_archive.py+归档 202609.md 十三批节（852707B·CRLF 844 行）+CODELY 8460B 二进制校验+S6 32 rc=0 stdout+smoke 25/25+git show origin/main:docs/decisions.md D-06~10 实读｜'
    '下轮 r83：盯 repull 终局窗 ~15:0x（bm-a 机械三件套→moneyflow IC 批落池=starvation 收敛判据）；T-16 P-A2 LOF 现货面周一 09-28 重试；10-01 月三件套 standing；next 5x HANDOVER=R85 [via bm-c]'
)
if not raw.endswith(b'\n'):
    raw += eol
open(rp, 'wb').write(raw + line.encode('utf-8') + eol)
chk = open(rp, 'rb').read()
assert chk.endswith(eol) and line.encode('utf-8') in chk
print('wrap OK: hb epoch=%d clock=%s ack=%d state=82 report-line=%dB' % (EPOCH, hb2['clock_read'], len(ack), len(line.encode('utf-8'))))
