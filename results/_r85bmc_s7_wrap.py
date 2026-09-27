# -*- coding: utf-8 -*-
"""r85 bm-c S7 wrap: CODELY pitlaw append + HANDOVER 5x window bullet + state r85
+ heartbeat (epoch int + clock_read T-sep) + round report line. Byte-faithful per
file EOL face (r325 law: probe before write, assert counts after)."""
import io, json, time, datetime, subprocess

def head_blob(path):
    return subprocess.run(['git', 'show', f'HEAD:{path}'], capture_output=True,
                          check=True).stdout

NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec='seconds')          # 2026-09-27T14:3x:xx+08:00
HMS = NOW.strftime('%H:%M')

# ---------- 1) CODELY.md pitlaw append (blob LF face; worktree smudged CRLF irrelevant) ----------
ENTRY = ('- [2026-09-27 14:3x r85 bm-c] 坑律：**compute_audit 生产者滚动窗截留——union 面'
         '行数回缩≠丢行，判别=以生产者窗口首行 ts 为界做窗内键集差集存活核**——r85 实弹'
         '（第三撞 30-UU 重落窗）：resolver union 208 行落库（207|206·重叠 205 内容恒等）后'
         '同轮 S6 生产者写出 201 行（首行 09-26 08:14:07），行数直看疑丢 7 行；窗内差集='
         '200/200 全存活+1 新增=零丢失实证。正典=①禁按行数直判丢失禁旗标升级②写回面镜像 '
         'base blob 行尾缩进（bm-b 生产者 CRLF+indent2 与 bm-c/bm-a LF+indent1 交替面，'
         'rolling-ledger 配方以 base 为准 r223/r234 律）③配方已同步 SKILL.md rolling-ledger '
         '行（r83 律：律在 CODELY≠配方在 SKILL）。指针=results/_r85bmc_probe.py+'
         '_r85bmc_resolve.py+commit c5d480ac。\n')
b = head_blob('CODELY.md')
assert b.count(b'\r\n') == 0, 'CODELY blob LF face expected'
assert b.endswith(b'\n')
b2 = b + ENTRY.encode('utf-8')
assert len(b2) < 10240, f'CODELY {len(b2)}B over 10KB line'
open('CODELY.md', 'wb').write(b2)
b2.decode('utf-8')
print(f"1 CODELY: +r85 rolling-window pitlaw {len(b)}->{len(b2)}B (<10KB, blob LF face)")

# ---------- 2) HANDOVER 5x bullet append (CRLF face) ----------
BULLET = (
 '- 开发队列增量窗（接续版）**round 85 bm-c（5x 核对本轮），2026-09-27 14:3x 补核；对账区间='
 '增量 bm-c r81-85（基线=round 80 bm-c 行·round 325 bm-b 行已收讫），统一链 286,541 实读'
 '平持（_r295bmb_ledger_scan 复跑链尾全连续 HEAD=DECISION_CHAIN_E2E_P1·本窗 bm-c 零批 '
 'finalize：r81-85=维护/冲突解/治理窗零科学判定批）**：①r81-84 已录前行（r82 S0.5 决策'
 '台账 origin 直读律〔D-06~10 补审〕+r83 SKILL launches 撞键去重配方同步〔r322 律锚〕+'
 'r84 毒提交首重落+council seat-3 让路 F-04+D-09 回执 F-03+S7 二撞 7-UU 典解）；②**r85'
 '（本轮）=第三撞重落窗 30-UU 全解**——S0 pull-rebase 重放 a7f66d3b 撞 bm-b r328 同窗 '
 'S6 面（r84 addendum-2 明令主重落）→探针 _r85bmc_probe/_probe2 双发定性：26 take-ours '
 '新面字节保真（含 autofill 44 复合键集双侧恒等零分歧+last_tick 取新 bm-b 14:00:02）+'
 'compute_audit 复合键 union 207|206→208（重叠 205 内容恒等·生产者后置滚动窗 201 行·窗内 '
 'union 行零丢失实证）+x2 行级并集 708|708→714 零丢失+归档后缀直拼 856,474+2373+3155'
 '（双『十五批』节并存=bm-a r327 索引折叠+r84 条目面·CODELY 头勘注编号撞号后续自十六批'
 '起编）+CODELY 手工并 9036→7338B（r321/r323/r82/r325 四条目 verbatim 外迁在档核）+'
 'resolver _r85bmc_resolve.py 断言全绿；push 拒 1 次（d34810cd bm-b autofill claim 同窗）'
 '→pull-rebase 零冲突→**c5d480ac 落 origin/main** 零强推零 abort；③维护面：S6 32/32 '
 'rc=0（周日合法 no-op 族+lane-guard 诚实 no-op·live_paper OK·t35 PASS 零例·prospect '
 '22/22·export-09-24 幂等·regime ORANGE breadth 0.77·daily_report faces=4）+smoke 25/25+'
 'orders 96/96 双扫零未回执+决策台账尾 D-10 止零新增（C-01 意见窗至 09-29 12:00）+板 0 '
 'open/30 claimed+水位 red=false healthy+audit CLEAN；④观测（非本机车道）：bm-b r328 BOM '
 '修+S6 双产已收讫·censusw2a（T-86 W2-A 因子融合普查 5,920 specs）=bm-b 14:22:44 认领烧'
 '片中·bm-a T-91 完整系统 armed 周一 09:15 自动点火；⑤指针：09-28 周一开市窗=新 bar 全链'
 '接力（update_daily→live.paper REGIME_GUARD v3 enforce 首跑→t35v→t24×2→aggr→grid→'
 'export→scorecard→daily_report）+T-91 s3 自动点火 09:15+T-87 astock 首续拉 15:30 后+'
 '10-01 月度三件套+REGIME_GUARD v3 日期门生效（三重门勿手改）+10-31 六员首检 all-HOLD+'
 'T-34 半档梯 11-01+r90 下次 5x 核对。\r\n')
b = open('research/HANDOVER.md', 'rb').read()
n0 = b.count(b'\r\n')
b2 = b + BULLET.encode('utf-8')
n1 = b2.count(b'\r\n')
assert n1 == n0 + 1, f'crlf {n0}->{n1} (+k assert failed)'
b2.decode('utf-8')
open('research/HANDOVER.md', 'wb').write(b2)
print(f"2 HANDOVER: +round 85 bm-c 5x window bullet ({len(b)}->{len(b2)}B, crlf {n0}->{n1})")

# ---------- 3) state-bm-c.json round bump ----------
st = json.loads(io.open('state-bm-c.json', encoding='utf-8').read())
assert st['round_no'] == 84
st['round_no'] = 85
st['updated'] = NOW.strftime('%Y-%m-%dT%H:%M')
st['last_round_ts'] = TS
st['note'] = ("r85: third-collision re-land window fully resolved -- S0 pull-rebase replayed "
              "r84 a7f66d3b (backup origin/machine/bm-c-r84) onto bm-b r328 face, 30-UU "
              "canon-resolved (26 take-ours newer-face byte-faithful incl autofill 44-keyset "
              "identical + last_tick ours; compute_audit union 207|206->208; x2 line-union 714; "
              "archive suffix-concat dual-15th-batch with numbering note; CODELY manual union "
              "9036->7338B), push-reject x1 (d34810cd) -> zero-conflict rebase -> c5d480ac "
              "landed on origin/main; S6 32/32 rc=0; smoke 25/25; orders 96/96; 5x HANDOVER "
              "window (chain 286,541 flat); compute_audit rolling-window pitlaw + SKILL sync.")
io.open('state-bm-c.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(st, ensure_ascii=False, indent=1) + '\n')
json.loads(io.open('state-bm-c.json', encoding='utf-8').read())
print(f"3 state-bm-c: round_no 84->85, updated {st['updated']}")

# ---------- 4) heartbeat fleet/machines/bm-c.json ----------
hb = json.loads(io.open('fleet/machines/bm-c.json', encoding='utf-8').read())
epoch = int(time.time())
assert isinstance(epoch, int)
hb['last_seen'] = TS
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = TS
hb['verdict'] = ('legal idle: board 0 open (30 claimed by other lanes), pool CENSUS-FUS-S2-W2A '
                 'claimed+burning bm-b 14:22:44 (T-86 W2-A census 5,920 specs), wm red=false '
                 '14:10:03 healthy, audit CLEAN 14:29:28')
hb['current_task'] = ('R85 done: third-collision re-land 30-UU canon-resolved -> c5d480ac on '
                      'origin/main (26 take-ours + audit/x2 unions + archive concat + CODELY '
                      'manual union) + S6 32/32 + 5x HANDOVER r85 window (chain 286,541 flat) + '
                      'rolling-window pitlaw + SKILL rolling-ledger sync')
io.open('fleet/machines/bm-c.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(hb, ensure_ascii=False, indent=1) + '\n')
d = json.loads(io.open('fleet/machines/bm-c.json', encoding='utf-8').read())
assert isinstance(d['heartbeat_epoch_utc'], int) and 'T' in d['clock_read']
print(f"4 heartbeat: last_seen {TS}, epoch={epoch} (int), clock_read T-sep verified, "
      f"orders_ack {len(hb.get('orders_ack', []))} kept")

# ---------- 5) round report line ----------
LINE = (
 f"{TS}｜R85｜bm-c watermark verdict=绿（wm red=false 14:10:03 lane healthy·probe 14:29:35 rc0；"
 f"板 0 open、30 票全 claimed 他人线、job_list 0·censusw2a bm-b 14:22:44 认领烧片中=供线在飞）"
 f"｜S0 第三撞重落窗全解：r84 addendum-2 明令主重落 a7f66d3b（备份 origin/machine/bm-c-r84）→"
 f"rebase 重放撞 bm-b r328 同窗 S6 面 30-UU→probe 双发定性+resolver 正典解=26 take-ours 新面"
 f"字节保真（autofill 44 复合键集双侧恒等零分歧+last_tick 取新 bm-b 14:00:02）+compute_audit "
 f"union 207|206→208（重叠 205 内容恒等·同轮 S6 生产者后置滚动窗 201 行·窗内键集差集 200/200 "
 f"存活零丢失实证）+x2 行并集 708|708→714+归档后缀直拼（双十五批节并存=bm-a 索引折叠+r84 "
 f"条目面·编号撞号勘注后续自十六批起编）+CODELY 手工并 9036→7338B（r321/r323/r82/r325 四条目 "
 f"verbatim 外迁在档核）→push 拒 1 次（d34810cd bm-b autofill claim 同窗）→二次 rebase 零冲突"
 f"→c5d480ac 落 origin/main 零强推零 abort｜S0.5 orders 96/96 双扫零未回执+决策台账尾=D-10 止"
 f"零新增（C-20260927-01 意见窗至 09-29 12:00）+inbox 零本机未读｜S1 smoke 25/25 绿｜S6 32/32 "
 f"rc=0（周日合法 no-op 族+lane-guard 诚实 no-op·live_paper OK·t35 open_fill PASS 零例·"
 f"prospect 22/22·paper_export/scorecard/daily_report/build_status/token_meter 全 rc0）｜"
 f"5x=HANDOVER r85 增量窗补核（统一链 286,541 实读平持·零 finalize）+坑律入册（compute_audit "
 f"滚动窗截留判别）+SKILL rolling-ledger 行同步（r83 律·selftest rc0）｜证据=results/"
 f"_r85bmc_probe.py+_r85bmc_probe2.py+_r85bmc_resolve.py+commit c5d480ac｜下轮指针：09-28 周一"
 f"开市窗=新 bar 全链接力（update_daily→live.paper REGIME_GUARD v3 enforce 首跑→t35v→t24×2→"
 f"aggr→grid→export→scorecard→daily_report）+T-91 s3 自动点火 09:15 首队列入场+T-87 astock "
 f"首续拉 15:30 后；r90 下次 5x 核对。 [via bm-c]\n")
b = head_blob('logs/iteration-loop/round_reports-bm-c.md')
assert b.count(b'\r\n') == 0, 'round report blob LF face expected'
b2 = b + LINE.encode('utf-8')
b2.decode('utf-8')
open('logs/iteration-loop/round_reports-bm-c.md', 'wb').write(b2)
print(f"5 round report: R85 line appended ({len(LINE.encode('utf-8'))}B, blob LF face)")

print('S7 WRAP COMPLETE')
