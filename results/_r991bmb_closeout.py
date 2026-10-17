# -*- coding: utf-8 -*-
# r991 bm-b closeout: backlog done marker + state.json + heartbeat + round report.
# Fresh-read-modify-write per multi-writer ledger law; anchor by unique substring.
import json, os, datetime

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec='seconds')
EPOCH = int(NOW.timestamp())
BH_SHA = '3409e53'

def read(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()

def write(p, s):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(s)

# --- 1) backlog line-12 done marker ---
bp = os.path.join(ROOT, 'fleet', 'backlog.md')
txt = read(bp)
lines = txt.splitlines(True)
hits = [i for i, l in enumerate(lines) if '12. 【BigHouse】城市接入件设计' in l]
assert len(hits) == 1, 'backlog anchor not unique: %r' % hits
marker = (' done@bm-b@%s+BigHouse %s（T-2 清偿=r991·设计件 design/city-integration-v1.md'
          '·催办件闭合·AD 对库核验门+§四待核双门前置留档）' % (TS, BH_SHA))
i = hits[0]
lines[i] = lines[i].rstrip('\r\n') + marker + ('\r\n' if lines[i].endswith('\r\n') else '\n')
write(bp, ''.join(lines))
print('backlog marker appended to line', i + 1)

# --- 2) state.json (bm-b uses state.json; preserve unknown keys) ---
sp = os.path.join(ROOT, 'logs', 'iteration-loop', 'state.json')
st = json.loads(read(sp))
st['round_no'] = 991
st['did'] = ('r991: 主产出双线。①POOL-0018 词级锚点批救命修复：whisperX words 批在飞中全首词级对齐失败根因=NLTK '
             'punkt_tab 缺失（GFW 掐断 nltk 官方下载·星晴/可爱女人 words=0 降级件实证）→gh-proxy 镜像下载装入 '
             'C:/Users/Administrator/nltk_data（venv 内 sent_tokenize 验证过）→在飞批次从龙卷风起吃上词级对齐；'
             '降级 2 件已过 treasure_guard prescan（零命中）隔离 results/_quarantine/r991-20261017 逼下一 tick '
             '重烧（batch=输出存在即跳过·续跑安全）。②r990 改写的 anchor_runner_r990.py 引用未定义全局 '
             'VCVARS/MIRROR=每新 tick NameError 崩死于 step A、step B 连带不跑的结构性缺陷→按 r989 bat 真值补 '
             '定义（vcvars64 Community 路径+清华 pip 镜像）py_compile 过。③BigHouse T-2 城市接入件设计清偿'
             '（backlog 行12·逾期两日·bm-c 催办件）：本机稀疏克隆 BigHouse 仓（projects/BigHouse·r631 配方）→'
             '消费 R1 §2.2/§2.3/§2.4/§五+BLUEPRINT v0.4→design/city-integration-v1.md 入仓推送'
             '（BigHouse 3409e53·街区级选样[木渎首件·CEO 意向优先]+构件 9 件+城内选址[西缘望山带+B/C 扩展带]'
             '+AD 槽位 10 组[对库核验门·禁编 AD 号·缺口呈 CEO 填库]）+TASKS.md T-2 翻 done。④r989 遗留 '
             'tmp_index 隔离（prescan 零命中）。S0.5 orders 17:00 后零新令未回执差集=0；D-19 双水位零增量'
             '（decisions 1d4741e4/orders 1df82bab 恒等）。S1 smoke 49/49；孤儿面 11/0；SatEngine ALIVE rc0；'
             'S6 链 37/37 rc0（r946 配方克隆·newbar 门控 4 腿周六合法剔除·ZERO-DRIFT streak43·DUALARM+CALL-'
             '2026-10-16+REPORT/LIVE-2026-10-17 产出·bm-a 心跳 91min 陈旧面按 STALE_MIN 法本机接管 derive）。')
st['verdict'] = ('green: anchor 词级锚点批三缺陷修复（punkt_tab 装入+orchestrator NameError 补定义+降级件隔离'
                 '重烧链路打通）+BigHouse T-2 逾期欠件当窗清偿入仓（3409e53）+S6 37/37；诚实面：POOL-0018 首批'
                 '10/10 词级产出候下一 tick 重烧完成（窗至 10-18 17:41）、POOL-0019 madmom 修复候 tick 验证'
                 '（fuse 3 上限 attempt2 在途）、MSG-1249 bm-a 取件仍未证（其心跳 15:49）')
st['next'] = ('r992: ①anchor 线读进度（words 产出计数 vs 10/重烧 2 件落地/下一 tick madmom env-capture attempt2 '
              'VERIFY_RC/fuse 态/旧 r989 bat 遗留 cmd 进程孤儿面复查）②POOL-0018 首批回执（首批落地后：orders 行+'
              '心跳 orders_ack 更新+词级件 lyric_calibration.py 兼容性验证 1 首）③BigHouse T-3 安家流程（三候选+'
              '三型家宅位参数已备·CEO 意向优先）④MSG-1249 bm-a 取件盯守⑤闲置面照 S8 读 registry')
st['last_round_ts'] = TS
st['last_result'] = 'ok'
st['current_task'] = 'r992: anchor 首批收官+POOL-0018 回执+BigHouse T-3'
st['updated_at'] = TS
st['last_seen'] = TS
st['ts'] = TS
write(sp, json.dumps(st, ensure_ascii=False, indent=1))
print('state.json r991 written, keys preserved:', sorted(st.keys()))

# --- 3) heartbeat fleet/machines/bm-b.json (preserve unknown keys) ---
hp = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
hb = json.loads(read(hp))
hb['machine_id'] = 'bm-b'
hb['last_seen'] = TS
hb['task'] = 'r991: closeout'
hb['round_no'] = 991
hb['round'] = 991
hb['did'] = ('r991: 当前活=POOL-0018 whisperX 词级锚点批烧制中（punkt_tab 修复后剩余曲在飞）；最近实物='
             'BigHouse 仓 design/city-integration-v1.md（17:44·commit 3409e53·T-2 逾期欠件清偿）+nltk '
             'punkt_tab 装入+anchor_runner NameError 修复+S6 37/37（DUALARM/CALL-2026-10-16/REPORT+LIVE-'
             '2026-10-17）；下个里程碑=POOL-0018 首批 10/10 词级锚点+首批回执（窗内 ≤10-18 17:41·预计 '
             'r992-r993）+BigHouse T-3 安家流程（≤10-20）。孤儿面=11/0；watermark green；smoke 49/49。')
hb['cpu_cores'] = 16
hb['free_ram_gb'] = 12.5
hb['gpu_free_vram_mb'] = 3653
hb['cpu_load_pct'] = 14
hb['verdict'] = ('GREEN: anchor 批三缺陷修复（punkt_tab+orchestrator NameError+降级件隔离重烧）+BigHouse T-2 '
                 '清偿入仓+S6 37/37 rc0；honest defers: 首批 words 10/10 候下一 tick、madmom attempt2 候验、'
                 'MSG-1249 bm-a 取件未证')
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = TS
hb['ts'] = TS
hb['orders_ack'] = ('r991: fleet/orders 17:00 后零新令（未回执差集=0·轮首+S7 收尾双扫）；D-19 双水位零增量'
                    '（decisions 1d4741e4/orders 1df82bab 恒等·probe rc0）；backlog 行12 BigHouse T-2 done'
                    '（BigHouse 3409e53）；anchor 线修复回执在首批落地后随 r992 补')
hb['note'] = ('r991: punkt_tab 经 gh-proxy 装入 nltk_data（GFW 掐断官方源的镜像解）；anchor_runner_r990.py '
              '补 VCVARS/MIRROR 定义（r990 重写遗留 NameError 结构缺陷）；降级 words 件+r989 tmp_index 隔离'
              '（prescan 双零命中·results/_quarantine/r991-20261017）')
hb['latest_artifact'] = 'BigHouse design/city-integration-v1.md @3409e53 + punkt_tab install + S6 37/37 (results/_r991bmb_s6_log.txt)'
hb['current_task'] = 'r992: anchor 首批收官+POOL-0018 回执+BigHouse T-3'
hb['next'] = ('r992: 1) anchor progress read (words count vs 10; re-burn of quarantined 2; madmom attempt2 '
              'VERIFY_RC; fuse state) 2) POOL-0018 first-batch receipt + lyric_calibration compatibility 1 song '
              '3) BigHouse T-3 安家流程 4) MSG-1249 bm-a pickup watch 5) S8 registry read if idle')
json_ok = json.loads(json.dumps(hb))  # round-trip sanity
assert isinstance(json_ok['heartbeat_epoch_utc'], int), 'epoch must be int'
write(hp, json.dumps(hb, ensure_ascii=False, indent=1))
print('heartbeat r991 written (epoch int ok):', EPOCH)

# --- 4) round report line (bm-b uses logs/iteration-loop/round_reports.md) ---
rp = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
line = ('%s | r991 | anchor批三缺陷修复（punkt_tab 装入+orchestrator NameError 补定义+降级2件隔离重烧）+'
        'BigHouse T-2 清偿（design/city-integration-v1.md@BigHouse 3409e53）+tmp_index 隔离+S6 37/37 | '
        'evidence: smoke 49/49·孤儿面 11/0·D-19 零增量 probe rc0·S6 log=results/_r991bmb_s6_log.txt·'
        '隔离回执=results/_r991bmb_anchor_cleanup.json·sent_tokenize venv 验证过·py_compile OK·BigHouse push '
        'range 16fda71..3409e53·登记簿零命中断言（prescan 双零）·本地未达 origin commit 数=0（commit 后自证） | '
        'next: r992 anchor 首批收官+POOL-0018 回执+BigHouse T-3+MSG-1249 盯守\n' % TS)
with open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('round report appended')
print('CLOSEOUT FILES DONE @', TS)
