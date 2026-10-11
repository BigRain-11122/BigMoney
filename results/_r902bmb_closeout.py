# -*- coding: utf-8 -*-
"""r902 bm-b closeout writer: HANDOVER 5x (r900 debt) + round report + state.json + heartbeat."""
import json, time, io, datetime

NOW = datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S+08:00')
NOWX = datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S')

# ---- 1. HANDOVER r900 5x row (owed by dead r900, executed r902) ----
h_row = ("> bm-b round 900 五倍数核对（2026-10-12 02:2x r902 补做〔r900 死会话欠账·死因=夜网推送窗挂死 94min〕·增量窗覆盖 r896-r900 五轮·逐轮权威面=logs/iteration-loop/round_reports.md 全行在册）："
 "增量窗 r896-r900=bm-b 面像（**BigHouse 首件+W18 全链烧录起点+i2v CEO 终裁本地化点火三主线**——"
 "①r896=BigHouse 首件〔house/BigHouse 苏州唐仲社区复刻研究件三面 research/wuzhong-replication-r1.md+TASKS.md·commit 16fda71 提前 20h 交付 O-1917 搂2〕+W18 finalize 分离点火〔188/188 checkpoint 完备→PID25060〕+S6 41 腿 rc0；"
 "②r897=前班体异常离场接管定谳+CEO 终裁 O-2126 i2v 本地化当轮受理点火〔53 单 int4 480P animatic 全线起批·ComfyUI 专汤 :8188·keepwarm 释放阀 4520→03MiB〕+D-19 双 delta 消费；"
 "③r898=i2v 53 单夜批守望开张〔首单 XQ_XQ28 1002s/1071KB 落盘·KN_KN16 2/53 在跑零 err〕+W18 finalize detached 在烧〔PID25060 CPU 累计 4040s〕；"
 "④r899=两 CEO 令腿收口〔O-2147 inspector 三腿 heritage verified+-KRoot 重注册 readback green+BigHouse T-1 done/4 open>=3·O-2215 maintain leg〕+G-soft/r895 推送晨窗顺延+watermark ADVANCED；"
 "⑤r900=死亡会话〔00:0x-00:33 挂死于夜网推送窗·pre-pull churn commit 7fbc92f88 落 W18 finalize 产品五件+i2v 守望启动〕→r901 吸收〔3 提交 rebase 13 冲突面+W210 让位回执+O-2333 POC 排窗〕→r902 判决消费收口〔账本分叉重锚+§7/§8 回填+attrition 双行+判词条〕〕。"
 "维护面全窗：smoke 49/49 链·SAT 活 rc0 链·attrition CLEAN 链·水位 red=false 链·D19 双水位消费链（dec 16861a6→d296e83d→358ba69b·ord 三推进）·孤儿面 0-2 合法 detached 链；dualrun streak 49-51。"
 "产物清单漂移=results/trial_labor_w18/{w18_judge,w18_intake,w18_reform_face,w18_paired_deltas,judge_state}.json〔W18 判决面五件·r900 pre-pull 落+r902 重锚件 w18_judge_ledger_reanchor_r902.json〕+research/TRIAL_LABOR_W18_PREREG.md §7/§8 回填态+results/_r897bmb_i2v/ i2v 点火件套〔wf 双汤+manifest+album 脚本+README〕+results/pool_scored/POOL-SCORED-20261012.md+house/BigHouse 首件三件+Tools/fleet-oversight.ps1 族〔O-2147 部署件〕+results/_r901bmb_rebase_resolver{,2,3}.json〔r901 恢复收据〕+results/_r902bmb_w18_reanchor_receipt.json〔r902 分叉治愈收据〕。"
 "指针：**W18 48h CEO 呈报 due 2026-10-14 00:44（判决面落地 00:44 起算）+E15 48h 报 due 10-13 11:2x=合并窗**；i2v 53 单全落 ETA 10-12 午后→unity-mcp POC 回执 ≤10-13 12:00（O-2333）；BigHouse T-2 城市接入件 due ≤10-15；T-184=bm-a courtesy byte-compare 等待态（self-rescue done r882·bm-a 暗 27h+）；trial-labor W4-W17 attrition 缺行+W17 §7 空=GM 裁定建议面（r902 观察）；下一 5x=bm-b r905。\n")
with io.open(r'research\HANDOVER.md', 'a', encoding='utf-8', newline='') as f:
    f.write(h_row)
print('HANDOVER appended')

# ---- 2. Round report line ----
rr = ("| r902 | 2026-10-12T02:2x | dept:研究（TRIAL_LABOR_W18 judge-finalize 收口单获·TREASURE_PROTECTION_LAW 搂1）+dept:工程（死前序 r902 吸收+S0 rebase+账本分叉推前治愈）| "
 "实况三行：当前活=W18 收口后 i2v 夜批守望（ComfyUI :8188 在烧·VRAM 合法满载）·最近实物=results/trial_labor_w18/w18_judge_ledger_reanchor_r902.json+prereg §7/§8 回填（commit 8725d1de4 推达 origin·02:1x）·下个里程碑=i2v 53 单全落 ETA 10-12 午后→unity-mcp POC 回执 ≤10-13 12:00+W18 48h CEO 报 10-14 00:44 | "
 "did: ①死前序吸收（前序 r902 01:03 churn 164271f91+01:22 S6 41 腿 rc0 落地未收口·二次 churn 77414fd78+rebase 上 origin 3903b0dd0）；②W18 判决消费前 pit-protocol-judge 全读+runner selftest 24/24 前后双跑：judged=188 判腿全 fail·0 onboard·E[FP] 9.4·配对差分四 face 中位≈0=sizing 轴降权活弹（§0 consumer 搂2 兑现）；"
 "③**r807 账本分叉推前捕获**：judge 块 prev=883,589=judge-prep 19:11 陈旧头·W210 23:2x 同 prev 落 885,789→judge 883,777 sub-head 不可见=追加式重锚 885,789+188=**885,977** 上活链（looser-side 判负零翻案·receipt _r902bmb_w18_reanchor_receipt.json）；"
 "④§7/§8 一次定稿回填（预测对账全带内：§5.4 [0,3]→0·n_blocks 47∈[43,75]·§5.2 存活率 4/4 带内）；⑤§6 attrition 双行补账（SCREEN 892+JUDGE 188·MASS_TRIAL W1 schema 先例·死 finalize 未写面）+TREASURE_REGISTRY W18 判词条；"
 "⑥观察披露：W17 §7 空+trial-labor W4-W17 attrition 行系统性缺行=非本窗修复面（GM 裁定建议）；⑦O-2333 unity POC 窗检查=No Unity Editor instances（等待态·post-i2v 窗·due 10-13 12:00 不动）；⑧T-184=done 自 r882 自救（alloc_paper rc0 死前序 S6 实证）·bm-a 暗 27h+=courtesy compare 等待态一行收；"
 "⑨push 撞 pre-push 爪：6 bm-c W211 shard 工作树被后台腿（backfill_ext_slots/satengine 族）删=add -A 误吞删除集→treasure_guard restore rc0 放行+origin-verbatim 恢复+amend（爪正确拦截零外泄·坑例：rebase 后工作树外来件被后台删=closeout add -A 前必 diff-filter=D 扫）；"
 "⑩r900 欠账 HANDOVER 5x 行补做（r896-r900 增量窗） | "
 "证据：smoke 49/49+selftest 24/24 双态+S6 41 腿 rc0（死前序落地吸收）+attrition guard CLEAN+水位 red=false（py 系列尾 8.9/7.7/7.5·next_pick claimed moneyflow IC）+孤儿面 0（round probe 13 faces）+D-19 双水位零 delta+SAT rc0 idle+push 后 fetch rev-list 0/0 送达自证 | "
 "watermark verdict：GREEN（red=false）| 本地未达 origin commit 数=0（push 后 fetch+rev-list 自证）| "
 "下轮指针：r903：i2v 53 单守望（progress 推进·停滞>4h 让渡评估）> unity-mcp POC 执行窗检查（编辑器在位+post-i2v 实弹+截图留证→回执 due 10-13 12:00）> W18+E15 48h CEO 报合并窗（10-13 11:2x/10-14 00:44）> BigHouse T-2（≤10-15）> T-184 bm-a courtesy compare 到件核对 > trial-labor attrition 缺行 GM 裁定建议单 |\n")
with io.open(r'logs\iteration-loop\round_reports.md', 'a', encoding='utf-8', newline='') as f:
    f.write(rr)
print('round report appended')

# ---- 3. state.json ----
with io.open(r'state.json', encoding='utf-8') as f:
    st = json.load(f)
st.update({
 'round': 902, 'round_no': 903, 'round_no_label': 'r902',
 'current_task': 'r902 closeout：W18 judge-finalize 收口（分叉重锚 885,977+§7/§8 回填+attrition 双行+判词条）+死前序吸收+i2v 夜批守望',
 'clock_read': NOW, 'ts': NOW, 'updated': NOW, 'updated_at': NOW,
 'last_seen': NOW, 'last_round_at': NOW, 'last_action_at': NOW, 'last_action': 'r902: W18 finalize 收口全链（重锚+回填+attrition+registry）+ push 8725d1de4',
 'did': ('r902: ①死前序 r902 吸收（churn 164271f91+77414fd78+S6 41 腿 rc0 落地未收口·rebase 上 origin 3903b0dd0）；'
         '②W18 判决消费（pit-judge 全读+selftest 24/24 双跑）：188 全 fail·0 onboard·E[FP] 9.4·sizing 四 face 中位≈0=X 轴降权活弹；'
         '③r807 账本分叉推前捕获治愈：judge prev=883,589 陈旧（W210 同 prev 先落 885,789）→追加式重锚 885,789+188=885,977 上活链（looser-side 零翻案·receipt _r902bmb_w18_reanchor_receipt.json）；'
         '④prereg §7/§8 一次定稿回填（预测对账全带内）；⑤§6 attrition 双行（SCREEN 892/JUDGE 188）+TREASURE_REGISTRY W18 判词条；'
         '⑥观察：W17 §7 空+trial-labor W4-W17 attrition 系统性缺行=GM 裁定建议面；⑦O-2333 窗未开（No Unity Editor·post-i2v 窗内回执 due 10-13 12:00）；'
         '⑧T-184=done r882 自救·bm-a 暗 27h+ courtesy compare 等待；⑨push 撞爪治愈（6 W211 shard 后台删误吞→origin-verbatim 恢复 amend·爪正确拦截）；'
         '⑩r900 欠账 HANDOVER 5x 行补做；smoke 49/49+S6 41 腿 rc0（吸收）+attrition CLEAN+SAT rc0+D19 零 delta'),
 'latest_artifact': ('r902: results/trial_labor_w18/w18_judge_ledger_reanchor_r902.json（分叉治愈 885,977）+research/TRIAL_LABOR_W18_PREREG.md §7/§8 回填态+'
                     'results/_r902bmb_w18_reanchor_receipt.json+results/_r902bmb_w18_attrition_rows.py（SCREEN/JUDGE 双行）+TREASURE_REGISTRY W18 条+HANDOVER r900 5x 行·commit 8725d1de4 推达'),
 'next': ('r903: i2v 53 单守望（progress-bmb 推进·停滞>4h 让渡评估）> unity-mcp POC 执行窗检查（编辑器在位+post-i2v 实弹+截图→回执 O-2333 due 10-13 12:00）> '
          'W18+E15 48h CEO 报合并窗（due 10-13 11:2x / 10-14 00:44）> BigHouse T-2 城市接入件（due ≤10-15）> T-184 bm-a courtesy compare 到件核对 > trial-labor attrition 缺行 GM 裁定建议单'),
 'next_milestone': 'i2v 53 单全落 ETA 10-12 午后 → unity-mcp POC 回执 ≤10-13 12:00；W18 48h CEO 报 10-14 00:44；E15 48h 报 10-13 11:2x；BigHouse T-2 ≤10-15',
 'now_active': 'r902 closeout',
 'note': ('r902：死前序 r902 吸收轮+W18 finalize 收口轮；账本分叉推前捕获（r807 窗）=本防止机队 N_eff 低估；'
          '孤儿面=0（round probe 13 py faces·W18 finalize PID25060 已完退场）；bm-a 心跳 stale 27h+（T-184 courtesy compare 与 IntradayMarks 周一首火观察面）'),
 'orphan_face': 0, 'orphan_faces': 0,
 'orphan_face_note': 'r902 round probe: py_faces=13 orphans=0；W18 finalize PID25060 完成退场（00:44 落五件）；合法 detached=i2v/ComfyUI 族',
 'sync': {'last_push_ts': NOW, 'note': 'r902 closeout push lands with this commit; delivery self-proof = post-push fetch + rev-list 0'},
 'task': ('r902 收口：i2v 53 单夜批守望（progress-bmb 推进·停滞>4h 单按 README 搂4 让渡） > unity-mcp POC 执行窗（编辑器在位+post-i2v→实弹+截图留证·回执 due 10-13 12:00） > '
          'W18 48h CEO 报 due 10-14 00:44（与 E15 10-13 11:2x 合并窗评估）> BigHouse T-2 城市接入件 due ≤10-15 > T-184 bm-a courtesy compare > 48h CEO 报 10-13 11:2x'),
 'verdict': ('GREEN: W18 judge-finalize 收口全链闭环（分叉重锚 885,977+§7/§8+attrition 双行+判词条+push 送达自证 0/0）+ smoke 49/49 + S6 41/41 rc0 + 水位 red=false；'
             '观察面 = unity-mcp POC 执行窗（编辑器未开）+ i2v 夜批 VRAM 满载合法 + bm-a 暗 27h+（T-184 courtesy/IntradayMarks 周一首火）'),
})
with io.open(r'state.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print('state.json updated: round_no ->', st['round_no'])

# ---- 4. heartbeat ----
with io.open(r'fleet\machines\bm-b.json', encoding='utf-8') as f:
    hb = json.load(f)
epoch = int(time.time())
hb.update({
 'clock_read': NOW, 'ts': NOW, 'updated': NOW, 'updated_at': NOW,
 'last_seen': NOW, 'last_round_at': NOW, 'last_action_at': NOW,
 'last_action': 'r902: W18 finalize 收口（分叉重锚 885,977+§7/§8+attrition 双行+判词条）+死前序吸收+HANDOVER 5x 补做',
 'current_task': 'r902 closeout：W18 judge-finalize 收口+i2v 夜批守望',
 'did': st['did'],
 'latest_artifact': 'results/trial_labor_w18/w18_judge_ledger_reanchor_r902.json + prereg §7/§8 回填 + commit 8725d1de4（02:1x 推达 origin）',
 'next': st['next'], 'next_milestone': st['next_milestone'],
 'round': 902, 'round_no': 903, 'round_no_label': 'r902',
 'now_active': 'r902 closeout',
 'heartbeat_epoch_utc': epoch,
 'orphan_face': 0, 'orphan_faces': 0,
 'orphan_face_note': 'r902 round probe: py_faces=13 orphans=0；W18 finalize PID25060 完成退场；合法 detached=i2v/ComfyUI 族',
 'idle_rounds': 0, 'agenda_starved': False, 'green_idle': False,
 'sync': {'last_push_ts': NOW, 'note': 'r902 closeout push lands with this commit; delivery self-proof = post-push fetch + rev-list 0'},
 'note': 'r902：死前序吸收+W18 收口轮；账本分叉推前治愈（885,977）；bm-a 心跳 stale 27h+ 观察',
 'verdict': st['verdict'],
})
with io.open(r'fleet\machines\bm-b.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(r'fleet\machines\bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat updated; epoch int ok:', chk['heartbeat_epoch_utc'])
