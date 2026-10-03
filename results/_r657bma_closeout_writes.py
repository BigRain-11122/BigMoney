import json, datetime

now = datetime.datetime.now().astimezone()
stamp = now.strftime('%Y-%m-%d %H:%M')
iso = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')

# --- 1) CODELY.md pit entries (hot layer, CRLF file) ---
p = 'CODELY.md'
b = open(p, 'rb').read()
eol = b'\r\n' if b.count(b'\r\n') > (b.count(b'\n') - b.count(b'\r\n')) else b'\n'
assert b.count(b'\r\n') + (b.count(b'\n') - b.count(b'\r\n')) > 60
if not b.endswith(eol):
    b += eol
e1 = ('- [2026-10-04 04:0x r657 bm-a] PS foreach 循环内 python ("路径")+" 参数" 表达式拼接吞参坑（market_clock_call 假 exit=2 实弹）：'
      'argument-mode 下括号表达式+字符串后缀不并成单 token，子命令参数丢失→脚本打 usage→假「机制故障 exit 2」误诊'
      '（字面直跑 rc0 同轮自愈）。How to apply：PS 循环驱动 python 命令一律字面直写 python scripts\\x.py run 禁中缀拼接构造参数；'
      '见 usage 类报文先查 argv 构造再判机制故障。').encode('utf-8')
e2 = ('- [2026-10-04 04:0x r657 bm-a] git merge 冲突标记 EOL 形态实探律（TREASURE_REGISTRY union 手术两连坑实弹）：'
      'merge 落工作树的冲突标记随 autocrlf 呈 CRLF 形态——字节手术 needle 硬编码 LF=assert count 0 当场炸（良性），'
      '但 ; 链后续 add 照跑=把仍带 marker 的冲突面 staged（pre-commit 钳正确拦截零 origin 伤害）。'
      '正法=①手术前实探 <<<<<<< 邻域字节定 EOL 再定 needle（count==1 断言）②手术步失败后禁带错续 add（分步提交勿 ; 链到底）'
      '③钳拦后修复→重 add→再 commit。与 r630 marker 手术律/r644 --check 律并用。How to apply：一切冲突面字节手术先探 EOL；'
      'add 前置步必须可判成败。').encode('utf-8')
b += e1 + eol + e2 + eol
open(p, 'wb').write(b)
print('CODELY.md +2 entries, size', len(b))

# --- 2) round report line (UTF-8 append) ---
rp = 'round_reports-bm-a.md'
b = open(rp, 'rb').read()
eol = b'\r\n' if b.count(b'\r\n') > (b.count(b'\n') - b.count(b'\r\n')) else b'\n'
if not b.endswith(eol):
    b += eol
line = (
    'watermark: green (red=false; satengine alive rc0 queue 0; pool floor 3/3 no breach -- fund trio NULLS bm-b '
    'canonical in-flight keepalive; probe insufficient_history window n=1 no violation face) | ' + iso +
    ' | r657 | dept:研究 | 当前活: 题材环 R4 判决批 THEME_PERSIST_P1 落地=收养窗（前体 r657 会话冻 prereg 457c37ac0→'
    '烧批 259 行 23.2s→写完 §7/§8 后猝死零提交；本会话同轮收养：验数全对 JSON 恒等后落地）| 交付实物: '
    'scripts/theme_persist_p1.py + results/theme_persist_p1/ 五件 + THEME_PERSIST_P1.md §7/§8 回填 + E25 方法论卡'
    '（幸存者基线律+结构常数敏感性律）+ 宝藏/语法账行 + T-165 票面 | 实测读数（白话）: ①「看前 20 天热度判断题材命」判负'
    '（12/15 检验全灭）；②首波长于复活波 AUC 0.73（唯一过线·簇弱按结构描述采纳）；③机械「破线出+复活进」系统 +632% vs '
    '著名主题持有 +928% 判负——但持有是幸存者基线（vs 随机点火 null p95 +313% 系统为 15.8 倍胜）；④常数敏感性 4 倍摆幅'
    '=[237%,952%]=未定案如实注记 | S0: 三证探测前体已死（进程零+簿记未动）→收养；TREASURE_REGISTRY merge UU=union CRLF '
    '字节手术（钳拦截 marker-staged 一次·修复后过）；_attrition face 对齐 origin blob；merge 586cf56ca push DELIVERED | '
    '验证证据: 收养验数=关键数字全对（631.6/927.9/312.6/16-16/2.23/0.214/0.7325/259/237.4..951.6 逐项 JSON 恒等）；S1 '
    'smoke 47/47；orders 双扫 152/152 零未回执；D-19 fresh read MATCH eb14b510 零新行（desktop 实径 fetch+show）；attrition '
    'CLEAN 4 files；S6 ~37 腿全 rc0（dualrun ZERO-DRIFT streak 32；compute_audit CLEAN flags=[]；CALL ORANGE_COOL sleeves 4 '
    'activated 0；LIVE-20261004 ORANGE cap50；report 面全刷；market_clock 假 exit=2=PS 拼接吞参·直跑 rc0 坑律已入）；S7 4/4 '
    '注册全绿；inbox 零未读 | 记分: 2（可跑脚本+数据实物+判决=CEO 点名 T1 研究线 R4 判决批收养落地）| 记账预算: 4/5 '
    '（state+心跳+轮报+票面）| 本地未达 origin commit 数=1（closeout commit 即推·推后 fetch+rev-parse 自证）| '
    'ceo-visibility: [当前活] 题材环 R4 持续性判决批已落地：folk「看 20 天热度断题材命」判负、首波长于复活波成立（描述级）、'
    '机械破线系统跑不赢著名主题持有但远赢随机 [最近实物] results/theme_persist_p1/theme_persist_p1.json + '
    'research/THEME_PERSIST_P1.md §7/§8，2026-10-04 04:0x，收养+merge 586cf56ca 已推 [下个里程碑] 题材环 R5《题材战法方法论》'
    '章（三句收录：著名题材持有优先/任意时点波骑优于随机/常数未定案）收口 T-165，窗≤10-06；fund 三族 NULLS bm-b 烧完 ETA '
    '10-05..09→judged finalize（预演 ALL-GREEN 就绪）'
).encode('utf-8')
b += line + eol
open(rp, 'wb').write(b)
print('round report +1 line, size', len(b))

# --- 3) heartbeat fleet/machines/bm-a.json ---
hp = 'fleet/machines/bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
epoch = int(datetime.datetime.now().timestamp())
h['last_seen'] = iso
h['current_task'] = 'r657: THEME_PERSIST_P1 R4 judgment adopted+landed; next=R5 methodology chapter to close T-165'
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = iso
json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat written, epoch int', epoch, 'orders_ack', len(chk.get('orders_ack', [])))
