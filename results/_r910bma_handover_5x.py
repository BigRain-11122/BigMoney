# -*- coding: utf-8 -*-
# r910 bm-a 5x HANDOVER entry append (bm-a round 900 append-style, end-of-file, CRLF)
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
P = 'research/HANDOVER.md'

entry = """> bm-a round 910 五倍数核对（2026-10-09 10:1x·增量窗 r901-r910·逐轮权威=round_reports-bm-a.md 全量在册·r905 5x 义务死窗顺延至本窗双倍面如实注记）：增量窗主线=**N1 常供给链 W193→W195 三波全生命周期收口+W196 席位占位（bm-a 109th/110th/111th owned·185th/186th wave engine-derive）**——r901 W193 五面冻结 LANDED（死会话双段窗：05:38 prereg 9c0c089b8+06:12 takeover 五面 5cf0d6175·A 439_404..441_403/B 441_404..441_603 阶梯 FIFTY-THIRD·状态三写失=r902 遗产承接）→r902 W194 席位链（seat MSG-0627 push 5cca13637·184th·A 441_604..443_603 FIFTY-FOURTH/B 443_604..443_803 own-A 保留）+r901 遗产收口→r903 死尾 W193 烧录 12/12+finalize one-pass（n1_w193_results.json ledger 836,745+2,200=838,945 EXACT·r904 收口 origin 1316ab9e7）→r904 r903 遗产吸收+W194 prereg build（e85717ec9·锚滚 r590 至 W193 实数·pool proj 424,720）→r905 W194 五面冻结（82670b0ba/cc0b4ba94/bafcafb04·死窗 pre-closeout·引擎自燃烧录 12/12 08:00-08:02·5x 义务未落=顺延 r910 如实）→r906 r905 遗产吸收+W194 finalize one-pass（bd1f515f2·ledger 838,945+2,200=841,145 EXACT·K 424,720·四预键 PASS·materializer 自动 finalize 未复现坑律入 pit-engine-finalize）+六门 probe 13/13→r907 W195 席位链（seat MSG-0844 push eb81c0878·185th·A 443_804..445_803 FIFTY-FIFTH/B 445_804..446_003·claw-block 解法披露 addendum）→r908 W195 prereg build（buildgen 干净窗 154ad3275·proj ledger 843,345/K 426,920·DRY 40/40·banned gate rc0）→r909 W195 五面冻结 LANDED（pf row 195+n1 cfg195+materializer face·冻结回执在案·视觉转录坑律入 pit-engine-freeze-editor·死窗 pre-closeout·引擎自燃 2-tick 12/12）→r910 本窗：r909 遗产吸收（33-UU rebase canon 解：7 ALL_FACES merge_lane_views resolve 正典工具+26 面孪生同侧/深探 take-new/行级 union r907 血统·push 0/0 自证）+W195 finalize one-pass（a0b16d1d8·ledger 841,145+2,200=843,345 EXACT 零偏离·K 426,920·四预键 PASS·merged mu -0.0929/w-only -0.0970/sigma 0.245069 rel -0.0119%/se_mu 0.000375 收窄/skill_line 1.1874→1.1873 K-lift -0.0001·A p95 0.3078·sec7/sec8 机械回填+n1 selftest PASS）+W196 席位链（probe rc0 ADMIT·A 446_004..448_003 阶梯 FIFTY-SIXTH 被 W195 B 带恰拒/B 448_004..448_203 own-A 互斥保留 hops 1/1·seat MSG-1007 push 01992cd42·186th engine wave bm-a 111th owned·W197+ 投影 B-inside-A 预披露）+本 5x 落账（r905 顺延面双倍清偿）。产品清单漂移=scripts/perpetual_faces.py rows 193/194/195 + scripts/perpetual_faces_n1.py cfg193/194/195+materializer faces + results/perpetual_faces/n1_w193/194/195_results.json 族 + results/p2cal_ext/n1_w193/194/195/ 12-shard 族×3 + research/PERPETUAL_N1_W19(3,4,5)_PREREG.md（W195 含 sec7/§8 回填）+ results/_r90x_ bma 探针/回执/冻结/回填家族 + fleet/inbox/(processed/) W194/W195/W196 seat MSG 族 + research/pit-engine-finalize.md r906 行 + research/pit-engine-freeze-editor.md W195 视觉转录行。维护面=smoke 49/49 链 + S6 39-40 腿 rc0 链 + attrition CLEAN 链 + orders 双扫零未回执链 + 四件套幂等链（pin=8）+ DEC/ORD 水位 83813196/861949ca python-raw UNCHANGED 链 + compute_audit reconcile drift 观察相记录（r910 冲突窗 state-take 面·T-116 观察相数据非故障）。指针：**W196 prereg build+五面冻结（下一轮·锚=W195 实数 843,345/426,920 r590 零前滚）+10-09 15:30 复市 bar 落地→晚间 marks 全家链（REGIME_GUARD enforce+live.paper+t35/t24 族）+池补货 bm-c 车道窗 10-10 00:00+月界首考 10-31**；下一 5x=bm-a r915。 [via bm-a r910]
"""

raw = open(P, 'rb').read()
assert raw.endswith(b'\r\n'), 'HANDOVER.md must end CRLF'
assert b'> bm-a round 910' not in raw, 'r910 entry already present (double-write guard)'
assert raw.count(b' bm-a round 900 ') >= 1, 'r900 entry expected in place'
block = ('\r\n' + entry).encode('utf-8')
with open(P, 'ab') as f:
    f.write(block)
raw2 = open(P, 'rb').read()
assert raw2 == raw + block, 'append not byte-exact'
print('r910 5x entry appended: %d -> %d bytes (+%d), CRLF preserved, double-write guarded' % (len(raw), len(raw2), len(block)))
