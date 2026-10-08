# -*- coding: utf-8 -*-
"""r880 bm-a 5x HANDOVER entry insert (fresh-read single-file edit per multi-writer law)."""
import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ENTRY = (
    "> bm-a round 880 五轮数对账（2026-10-08 14:1x·增量窗 r851-r880 三十轮【前锚 r850；5x 锚 r855/860/865/870/875 五截被死腿/收养复合窗吞未落账·如实披露·本窗合并补记】）：增量窗 r851-r880=bm-a 面像（**N1 永续线 W180..W185 六波全生命周期收口主线（freeze→tick 自燃→12/12→finalize→账本）+ r880 W186 席位发布**——W180 finalize 801,905 / W181 804,518（链内 +413 post-freeze 增量随 prereg §5.5 披露）/ W182 806,718 / W183 808,918 / W184 812,128（+1,010 REGIME5-VALIDATION-P1 入链 r518 origin-timing 披露）/ W185 814,328（K=404,920 / skill_line 1.1857 K-lift -0.0001 no-roll / A p95 0.3066 门过 / sec7-8 机械回填）/ r880 W186 pre-seat probe rc0 ADMIT（阶梯第46例：A 424_004..426_003 hops1 被 W185-B 拒起 / B 426_004..426_203 hops1 own-A 预留）+ 席位 MSG published=reserved 推 origin dd362c690 + buildgen facts 落盘（src=origin W185 冻结 blob 直抽 sha256 留痕）；统一链 **793,105→814,328 实读平移**（r850 锚=W179 尾 799,705；W180..W185 六波 ×2,200=13,200 + 两笔链内 post-freeze 增量 +413/+1,010 已披露并账）**；CEO 令面=ORD 水位逐跳消费链 facts-driven（BigStream MV 域派工行零 bm-a 执行面·涉本仓零 delta 双水位 UNCHANGED 照录）；S6 维护链 41 腿连营全绿（dualrun ZERO-DRIFT streak 51）**；smoke 48→49 新腿族（zt_pool gate 等）；四件套幂等绿（loop pin=8+watchdog+双爪 MATCH）；孤儿面=0；attrition CLEAN；marks lane 盘中值守连营（13:39 tick bm-c watch adjudicated r480 <5bp suppression legal）。产物清单迁移：results/perpetual_faces/n1_w18{0..5}_results.json——六波 finalize 合并件；research/PERPETUAL_N1_W18{0..5}_PREREG.md——冻结件+§7/§8 回填；results/p2cal_ext/n1_w18{0..5}/ 分片件族+席位 MSG 族（fleet/inbox/processed/）+band gate/probe/xform/buildgen 回执族（results/_r8*.py/.json）；本行 research/HANDOVER.md（r880 5x 合并补记）。维护面全绿：orders 双扫零未回执；DEC/ORD 双水位 UNCHANGED 照录（ee70cef0/1ce71b36）；SAT 活 rc0（N1_BANDS 注册表至 W185）；idle NOT-GREEN --worked 申报（常驻 llama-server+MiniGame 双任务 CEO 级·既有处置维持）；post_review 零红；月界首考 10-31。指针：**W186 prereg buildgen（r877 血统·facts+src 已落盘）→ freeze 五面插入 → tick 自燃；盘后 15:30+ 新 bar 窗=数据链全 re-arm+REGIME_GUARD v3 enforce+live.paper 族+首 marks 验证；下一 5x=bm-a r885**。"
)

with open('research/HANDOVER.md', 'rb') as f:
    data = f.read()
lines = data.split(b'\n')
assert lines[0].startswith(b'# Bigmoney'), 'title line drift'
entry_b = ENTRY.encode('utf-8') + b'\r'
new = lines[:1] + [entry_b] + lines[1:]
with open('research/HANDOVER.md', 'wb') as f:
    f.write(b'\n'.join(new))
print('INSERTED r880 5x entry; total lines', len(lines), '->', len(new))
