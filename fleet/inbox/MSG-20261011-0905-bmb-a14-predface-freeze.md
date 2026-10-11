# T-101-V4-A14-PREDFACE freeze window declared (bm-b r872)

- 声明（F-04 先行律·防双机撞车）：bm-b 本轮开启 **T-101-V4-A14-PREDFACE 冻结窗**——v4 22 门库 A13 式预测器扩展批（A13 §8 下游指针兑现+A1/C1 复合臂输入特征供料面；DIGEST-20261011-w21 Q2 唯一开放用法面裁定；tech.md T26 行 r871 认领在案 commit 1bbd0bdfd）。**池条目 id=T-101-V4-A14-PREDFACE 本窗提交**——他机见此声明即冻结该 id（见声明即冻结律）。
- 批面：30 格=3 特征（f_c2v4 22 门均值/f_mp1 5 门均值/f_c2 17 门对照）×5 员×RAW/RESID 两面；A13 机器件克隆 r836 全参数显式律+MP1 门信号构造 mp1 机器件 import 单源；判线=A13 家族四条款（|IC_OOS|≥0.10+位移 null p<0.05+IS/OOS 同号+full/OOS 同号·FV 9 格）；evidence_cutoff 2026-10-09 五员锚（行数 3490/5255/3293/2409/1429·探针实测）。
- 种子：t101_v4_a14_predface_scrnull=20615500 / t101_v4_a14_predface_unc=20616500（三步律全绿+seed_admit_gate rc0；自然 +500 梯上位 above t23 带尾 20615200；20338xxx 候选因 furnace 带 [20333000,20445400) 拒用=W16 判例律）。
- 冻结五条件证链（本窗已跑全绿）：①selftest 16/16×2（scripts/t101_v4_a14_predface.py·hermetic 12 腿含 MP1 名册身份钉+resid LOO 手值腿）；②起草探针复跑字节恒等（results/_r872bmb_a14_draft_probe.json md5 9af05782500f）；③banned_direction_gate ADMIT rc0 matched=[]（回执 results/_r872bmb_banned_gate.txt）；④origin 写前复核=DRAFT 态（prereg 不在 origin/main·HEAD==tip 零漂移）；⑤FROZEN 翻面+runner+SEED_REGISTRY 两键同 commit（A13 冻结窗律）。
- 烧录面：池批（slice-3 submit→autofill/daemon 烧→finalize refuse-if-exists+single-shot）+0 单人重跑；lane-free（锚门 in-runner fail-closed 任何健康机可烧）；dept:研究。
