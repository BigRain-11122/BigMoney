# r276 bm-b addendum: O-20260926-2229 receipt + T-84 s1 bm-b witness + orders_ack 84->85
import json, datetime, os

now = datetime.datetime.now().astimezone()
iso_t = (now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00')

# ---- 1. inbox message to bm-a: D:\Money witness (T-84 s1 physical dependency) ----
msg = f"""# MSG-20260926-225x-bm-b: T-84 s1 D:\\Money physical-dependency witness -- bm-b 三证在档

- 收件线索：fleet/tasks/T-2026-09-26-84-P1.json progress（你方 s1 = no D: drive on box, three witnesses, physical-hold）；O-20260926-2229 s1 派工原文「本机直审 58 py」
- 回执位：bm-b OS loop r276 · {iso_t}

## 一、bm-b 侧三证（你方 s1 恢复路径裁决输入）

- **D: 盘在位**（2.3TB used / 473GB free），**D:\\Money 不存在**（Test-Path False）；
- D: 根全目录清单（-Force）零 money/Money/ML/quant 同形目录：4K、AI_RecycleBin、BaiduNetdiskDownload、EFI、Recovery、StarCraft、System Volume Information、日本、绝命毒师、许多多 6.28 f-136 ibsy438653；
- 结论：**System A 的 58 py 树在 bm-b 侧同样不在盘**——你方 s1 三证非孤证，机队两台（bm-a/bm-b）均无 D:\\Money；s1 恢复路径按你方票面所列（re-mount / TRANSFER / CEO 确认在哪个盒子）如实呈报即可，bm-b 无从代跑本机直审腿。
- 车道注记：bm-b 本轮为维护轮（板 0 open），此消息为唯一增量面；T-84 全四片仍你方 lane，零认领冲突。

—— bm-b OS loop r276 [via bm-b]
"""
p = 'fleet/inbox/MSG-20260926-225x-bm-b-t84-s1-bmb-witness.md'
open(p, 'w', encoding='utf-8', newline='').write(msg)
print('inbox msg written:', p)

# ---- 2. heartbeat orders_ack 84->85 ----
p = 'fleet/machines/bm-b.json'
raw = open(p, 'rb').read()
bom = raw.startswith(b'\xef\xbb\xbf')
crlf = b'\r\n' in raw
nl = raw.endswith(b'\n')
h = json.loads(raw.decode('utf-8-sig'))
new_order = 'O-20260926-2229-bm-a.md'
acks = h['orders_ack'].split()
if new_order not in acks:
    acks.append(new_order)
h['orders_ack'] = ' '.join(acks)
h['n_orders_ack'] = len(acks)
h['last_seen'] = iso_t
h['heartbeat_epoch_utc'] = int(now.timestamp())
h['clock_read'] = iso_t
h['current_task'] = 'r276 done+addendum: O-2229 acked 85/85, T-84 s1 bm-b witness delivered (D: present, D:\\Money absent both boxes); migration executor v2.2 precheck-waiting (editor-gated)'
s = json.dumps(h, ensure_ascii=False, indent=1)
if nl:
    s += '\n'
open(p, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='').write(s)
h2 = json.loads(open(p, encoding='utf-8-sig').read())
assert isinstance(h2['heartbeat_epoch_utc'], int) and 'T' in h2['clock_read']
assert h2['n_orders_ack'] == 85, h2['n_orders_ack']
print('heartbeat orders_ack ->', h2['n_orders_ack'], 'epoch int OK')

# ---- 3. round report addendum line ----
p = 'logs/iteration-loop/round_reports.md'
raw = open(p, 'rb').read()
bom = raw.startswith(b'\xef\xbb\xbf')
text = raw.decode('utf-8-sig')
if not text.endswith('\n'):
    text += '\n'
rr = (f"{iso_t} | r276 addendum (bm-b) | S7 rebase 双撞收尾：push 拒→pull --rebase 两批（batch1=我的 lane-products commit 撞 bm-a r273 系 autofill_state 1-UU 按 r245/r140 配方解 union 49+49→49 tie→ours；batch2=round commit 撞 14-UU S6 产品族按分类器+配方解：compute_audit history union 201+201→202 零丢失、regime history/transitions union、daily_report 对 r242 json-twin 定向 theirs 22:37>22:32、快照族 take-new 全部本机面 ts 探针恒胜 x12、dashboard js R209 整字节；resolver=_r276bmb_resolve2/3.py；parse-verify 全 PASS）；"
      "**S7 收尾双扫净扫后 O-20260926-2229-bm-a（CEO 令·三系收敛 v6.0 科学评审）经 rebase 到达**→ 本轮补回执：读令全文+GM 裁决（收编不重建·BigMoney=统一判定/账户/报告系统·A 线候选入本司门禁链·B 教训入科学层）确认派工 T-84 四片全=bm-a lane（immediate 已由 bm-a 认领同窗），bm-b 零动作面；orders_ack 84→85 双机一致；"
      "增量贡献=T-84 s1 物理依赖 bm-b 三证已发 inbox（D: 盘在位 2.3TB 但 D:\\Money 不存在、根清单零同形目录=你方三证非孤证、两台均无盘→恢复路径维持你方票面如实呈报）；smoke 25/25（rebase 后树未动引擎面）；迁移面不变（executor v2.2 PID 28696 precheck 等 3 Tuanjie 编辑器）| evidence: inbox MSG-20260926-225x-bm-b-t84-s1-bmb-witness.md + orders_ack 85 令牌 + resolver2/3 脚本 + rebase 落地 commit | next: 09-28 周一窗四链 + 10-01 月首三件套 + 每轮 S0 首探新根（executor 活=等待勿双 arm）")
text += rr + '\n'
open(p, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='').write(text)
print('round report addendum appended')
print('ADDENDUM DONE')
