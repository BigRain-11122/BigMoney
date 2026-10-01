import json, datetime, subprocess

ts = datetime.datetime.now().astimezone().isoformat(timespec='minutes')[:16] + '+08:00'

# --- round report line (round_reports-bm-a.md) ---
rr = (ts + ' | r527 | dept:策略+工程 | WM=py_low_with_work_cands（@17:39 py 0.2%·n=2 窗）合法治理持面定谳：四供给面全法内阻塞'
      '（W14 线=entry 层治理停泊待 GM/§四闸·N2-W15=本机自持待同语法族裁定〔MSG-173x§四〕·引擎波=W16 bm-b 在飞+W17 bm-c 槽在前本机=W18〔法典 §4 轮值律〕'
      '·T-126=10-03 RW-5 外审解冻门·P1 数据票 T-131/134=GM 署名门）——唯一 work cand=T-141（引擎已活·设计面非可烧件）｜ '
      '**主产品=W14-GENERATE 收割+治理冲突诚实披露**：①r526 分离烧录 17:28:17 完成（raw 10,000→dedup 293·fp 386+corr 331·零引擎格·试验账本未动 N=0 实质面仍守）'
      '→w14_candidates.json+TRIAL_GRAMMAR_LEDGER 行（a231bf10940e7878·consumed·rerun 禁 sec.4）按「已消费语法存量」入册（删除=伪造实况·r525 宣称-实况律）'
      '②池 shard 翻 done（W2 r138 收割先例形状·entry 停泊保留=r504 shared-verdict authority 面）③**本机错误面认账**：r526 点火只读 shard 层（r493 再武装记录）'
      '未复核 entry 层 park_note（r494 段已明书 re-arm lacked self-proof）=判断面错序——shard/entry 两层矛盾时 entry 治理面优先，错误已入 CODELY r527 律'
      '④MSG-20261001-173x（bma→bmb+GM）：完成事实+错误面+293 候选存量处置请求双裁+bm-a 单方承诺（裁定前零触碰 W14 任何腿+N2-W15 自持）'
      '⑤origin 新况收编：bm-c r326 治愈（r526 收尾 stale-sweep 第三犯→N1-W14 引擎波 finalize 复原·K=30,920·ledger 397,548）+bm-b r515 W16 冻结（波号 15=本机 N2-W15 草案持有·N1 跳号）'
      '｜ S0.5 双扫=orders 139/139 零未回执+D-19 sha 753F99E8 MATCH 零新决策 | S6=33 腿 rc0（dualrun ZERO-DRIFT 306 entries streak 5/3·update_daily 0 新行 cutoff 09-30 假日合法'
      '·regime ORANGE 双触发·scorecard 6S/28T/7P 18.3s·CALL-09-30 ORANGE_COOL sleeves4 幂等·采集器假日 no-op 全合法〔lhb 节流/heat 同日/futures/repo/options cutoff 覆盖/mf spawn'
      '/sinamf/ths 同日·astock/etf/revosc/minfeed/alloc/fundprem=车道守卫诚实 no-op〕·AH spawn 分离·fundamental 5.1h fresh·b_layer 过·marks 幂等 no-op×4'
      '·t35e export-09-30 再生·dscore 6 员·dreport REPORT-2026-10-01 faces5/ceo_live LIVE-2026-10-01〔ORANGE cap50 COOL 6 员〕/build_status 10-432-0-6-5/7 全再生=host bm-a 执笔·token L2 0'
      '·无新 bar=live.paper 触发组假日合法跳过·月首三件套已交零重跑） | verify: smoke 47/47+池 diff 7 行外科断言+json.loads 双证+attrition CLEAN（4 台账 healed 注记）'
      '+自愈三件套（loop pin=8 Running 17:48 班·watchdog Ready·claw MATCH）+心跳 epoch int 1790847727 自证 | 计分：2 分（293 候选件+grammar 行=能看实物·池翻面+MSG=文件改动）'
      '·记账 4 处（state/心跳/轮报告/CODELY 一行） | 本地未达 origin commit 数=commit 后自证 | 当前活=治理三线待 GM（T-142 LOWAMP-P2 处置/W14 语法族裁定=PERPETUAL_FACES v1.1 线/CODELY 阈值整编）'
      '；最近实物=results/trial_labor_w14/w14_candidates.json（293 面·17:28 烧毕·58b70c25d 送达）+MSG-20261001-173x；'
      '下里程碑=W14 裁定落地→293 候选去向（screen 升格 or 隔离封存·窗随 GM 裁）+10-03 RW-5 解冻→T-126 REEVAL18 prereg（窗≤48h）+W17=bm-c 冻结后本机 W18 引擎波冻结窗 '
      '| next: r528 治理裁定守望（禁重扫同一等待对象·一行声明收轮型）+W17/bm-c 冻结观察+W18 波门自查 [via bm-a]\n')
with open('round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(rr)
print('round report line appended', len(rr))

# --- CODELY.md lesson line ---
cl = ('- [2026-10-01 17:4x r527 bm-a] 点火前必读 entry 层治理三字段坑（W14-GENERATE 实弹定谳·r504 shared-verdict authority 的执行面缺口）：'
      'WM-red 根治动作（点火我名下泊位分片）只读 shard 层（owner+再武装记录）即点火=错序——entry 层 park_note/parked_per/unfreeze_gate 才是治理权威面；'
      '本例 shard 层 r493 再武装记录（「park was dead-session hold」）与 entry 层 r494 段（「re-arm lacked the self-proof」）互相矛盾=两层各执一词，'
      '单机无权裁=GM/双裁面禁单方动作；烧录完成于 kill 窗外=零损失窗已破（语法消费不可逆·幸零引擎格=试验量闸实质面 N=0 仍守）。'
      'How to apply：任何点火/认领/解除动作前必读 entry 层 park_note 全文+parked_per+unfreeze_gate 三字段（shard 层记录非治理面）；'
      '两层冲突=停手送裁；产物已生成时按「已消费语法存量」入册勿删（删除=伪造实况·r525 宣称-实况背离律）；同语法族下游线（N2-W15 消费同一 18-tuple 语法）连带自持至裁定落定。\n')
with open('CODELY.md', 'a', encoding='utf-8') as f:
    f.write(cl)
print('CODELY lesson appended', len(cl))
