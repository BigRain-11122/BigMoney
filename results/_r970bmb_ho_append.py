# r970 bm-b HANDOVER 5x duty: binary append of the r970 compact incremental
# entry (window r966-r970) to research/HANDOVER.md (r962 binary/append law,
# r770/r790 single-window compact coverage discipline). Zero deletion; tail
# verbatim assertion before/after. ASCII script, UTF-8 entry bytes.
BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
PATH = BM + r'\research\HANDOVER.md'

ENTRY = u'''- 【第五节·产物清单核对（新增与删改）】**round 970 bm-b（5x 核对本轮；r965 条目完整性核验=盘/origin 字节恒等 1,087,298B 双面实证；本条目增量窗 r966-r970 五轮）**：2026-10-15 09:1x 核对；对账区间增量 bm-b r966-r970（基准线=round 965 bm-b 紧凑条目）；逐轮权威=logs/iteration-loop/round_reports.md 全行在册。增量窗主线=**恢复线监控拍链（第七~十拍+r970）+CEO 令送达修复与出向 MSG 交付线**：①v5 恢复驱动判活链（pid 3672·05:24 起跑无重启·回执面 done-climb 846→886→966→1006→1026/1804·ok=716 平台期如实披露·GFW 白窗尾+日间死窗散布 fails 130→170→290→310·断路器 300s 探针节律=r960 设计响应·stagnant=False 链）；②主支推送链 C-r967/r968/r969 全 PUSHED_VERIFIED 消费链（9105e251/a159bd5d4f5f/2314c74e·behind=0·merge-base ancestor 验证）+C-r970 本轮收口；③CEO 令 O-20261015-0025 送达修复（r968：origin ABSENT→add-only 外科面送达·r959 送达律）+令件在位核验链（r969/r970 present on origin·零触碰 per MSG-0612 max-merge 律）+出向 MSG-20261015-0825 CPU 后备件池催办送达 origin（r969·r959 送达律·受令面=bm-a 常设轮消费）；④死尝试吸收律执法（r969 吸收 08:10-08:30 前席死会话遗产三件：salvage 分离重跑 pid 2800+MSG 送达+backfill no-touch·反重复开发律）；⑤分离 worker 双活面（salvage pid 2800 tmp_pack 零网络打捞 r955/r958 律+backfill_ext_slots pid 18788 P-1d 数据腿·ext_slots_pull_status 面推进·均 own-lane no-touch）；⑥组面 D-19 双水位真差集探针链（r966-r970 五连 NO_DELTA·ord e2423fef/dec 6910a9ed 恒等·fresh fetch 链）；⑦维护面：车道四件套幂等重装链（loop pin=2/watchdog/precommit 爪/prepush 爪·进程内零窗）+引擎活 idle queue 0 链+水位 red=False 链（08:53/09:05 面）+哨兵 v1.2 NORMAL 无 flag 链+孤儿面=0 链（r959 读数 0/18·v5+salvage+backfill=own-lane 合法体三件判活）。完成状态：origin 侧零损失维持；v5 恢复在飞（1026/1804·remaining 1088·pass2 断路器探针节律）；完成包（smoke 49/49+全 S6 链+orders 全 ack 差集+attrition 重扫+origin 追平+双侧支合并 machine/bm-b-r954 c59c94e7+machine/bm-b-r958 dc0034d7+CODELY union merge+MSG-20261014-2015 撤回搬移）候 ALL_RESTORED 落账。指针：v5 ALL_RESTORED（诚实 ETA ~17:58 死窗锚速率面）→完成包同窗；月界首考 10-31。下一 5x=bm-b r975。[via bm-b r970]'''

d = open(PATH, 'rb').read()
tail = d[-40:]
assert b'[via bm-b r965]' in d[-120:], 'tail anchor missing: %r' % tail
body = ENTRY.encode('utf-8')
sep = b'\n' if not d.endswith(b'\n') else b''
new = d + sep + body + b'\n'
open(PATH, 'wb').write(new)
d2 = open(PATH, 'rb').read()
assert d2 == new, 'rewrite mismatch'
assert d2[:len(d)] == d, 'head not preserved'
print('APPENDED entry_bytes=%d old_size=%d new_size=%d' % (len(body), len(d), len(d2)))
