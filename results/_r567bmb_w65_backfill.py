# -*- coding: utf-8 -*-
"""r567 bm-b W65 prereg §7/§8 mechanical backfill (post-finalize legal state, r307 two-state law)."""
import io

FP = 'research/PERPETUAL_N1_W65_PREREG.md'
b = open(FP, 'rb').read()
t = b.decode('utf-8')
eol = '\r\n' if t.count('\r\n') * 2 > t.count('\n') else '\n'

S7_OLD = """## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

- （占位·finalize 后机械回填）"""
S7_NEW = """## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

- finalize one-pass 2026-10-02 09:4x（bm-b r567 窗：r566 冻结 c97e04a49〔A 173_004..175_003 算术续带零跳位 / B 49_601..49_800 算术续带零跳位〕→本机 tick 引擎自燃 12/12〔09:34-09:53 全片烧毕·分片 ~60s·workers=8·r535 tick 架构免重启·点火验证=产物增长面 r325 律〕→ ride 918957e0e 尾片 9/10/11 交付 origin 12/12 完备→**bm-a r568 同窗送 W64 finalize〔0e21c860f·head 505,348〕解封本波链序前置**→本窗 finalize one-pass〔r538 一过定稿〕；链序前置=**W64 已落账**〔bm-a r568·零在飞上游席〕·唯一前置=本波自产 12 分片在场 r310 完备性门自证〔shards_consumed 12/12〕）。
- S5 判据 4/4 PASS（**锚=W63 实测面**〔本波 §5 冻结锚·起草窗 W64/W65 在飞·r516 注记条款照准〕——对照面=同设计同窗单波跨度）：
  1. mu 漂移：W65-only **−0.076514** vs 累计池 merged 锚 −0.092648【|Δ|=0.016134<0.02 PASS·冻结判据面】／vs pre-W65 累计（K=138,720）实测 −0.092748【|Δ|=0.016234 PASS】；**诚实披露：单波面 delta vs W64-only（−0.098960）=0.022446（结果件机 derive 键 mu_delta_w65_vs_w64ext）超 0.02 观察带**——单波 mu 波动面（se≈0.0052）罕见偏移如实入册不断裂定性（合并池 mu 影响 +0.00025·−0.092748→−0.092495·链级零异常·W66-only 观察项下波照录）。
  2. sigma 相对变化：W65-only **0.245662** vs W63-only 锚 0.239446【+2.59%<±10% PASS】；merged **0.244775**（pre 0.244753·+0.009%）。
  3. A 族 full_sharpe_p95：**0.3383** vs W63 锚 0.3016【Δ=+0.0367<0.05 PASS】（vs 冻结窗前 W64+ 投影带同域；门校准注记：结果知情校准面·测量面零注册利害）。
  4. K-lift 线移动：**+0.0004【1.1616→1.1620 @n_eff_held 505,348】≤0.02 PASS**（W3..W64 先例族内正负交替——W60 +0.0004 同号先例·加深不必然抬线先例续·如实报正）。
- 账本：prev **505,348**【==W64 finalize 落账头·活链头 derive 禁手抄自证〕＋本波 2,200＝total **507,548**·voids_applied LOWAMP-P1/P2 继承面 ✓；skill_line_v2 消费 n_eff=505,348（W65 合并池 K=140,920==prereg §0 投影 140,920 逐位·se_mu 0.000652 收窄面）。"""

S8_OLD = """## §8 批后复盘【必填·s7-T】

- （占位·finalize 后机械回填）"""
S8_NEW = """## §8 批后复盘【必填·s7-T】

- 设计零偏差：frozen v1 设计逐字复用（run_one 引擎同源），W65-only sigma/分片切片/配对律与先例族【W2..W64】同域；单波 mu 罕见偏移（−0.076514·vs 前波带 [−0.093..−0.101]）如实披露如上——非机器断裂（A-p95/sigma/K-lift 三面全在带内·合并池影响 +0.00025）·观察项移交 W66-only 对照（bm-c 烧录面已 12/12 在场）。
- 波节奏面：W65=bm-b r566 冻结→tick 引擎自燃 12/12（免重启·产物增长面验证）→bm-a r568 W64 落账解封→r567 finalize one-pass 收口（r538 一过定稿）；全窗 W64→W65 链序两波三机接力（bm-a 烧 W64 后半/bm-a finalize W64/bm-b finalize W65）零污染。
- 遥测面披露：本窗 rebase reset 抹过 unpushed 遥测行（shard-4 ledger 行）=r522 孤儿面自愈实证（orphan reconcile 从产物在场重建·buffer 批冲待下 tick 落账）；科学面零影响（finalize 按产物计数 2,200 逐位吻合）。"""

for old, new, tag in ((S7_OLD, S7_NEW, 'S7'), (S8_OLD, S8_NEW, 'S8')):
    oldX = old.replace('\n', eol)
    newX = new.replace('\n', eol)
    assert t.count(oldX) == 1, f'{tag}: anchor not unique ({t.count(oldX)})'
    t = t.replace(oldX, newX)

open(FP, 'wb').write(t.encode('utf-8'))
print('W65 prereg s7/s8 backfill landed (eol preserved:', repr(eol), ')')
