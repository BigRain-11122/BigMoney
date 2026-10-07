# -*- coding: utf-8 -*-
"""r670 bm-c 5x HANDOVER row insert (after title line; r665 precedent format).

Byte-level insert: title row + EOL, then new 5x row + EOL, then prior body.
Rerun guard + post count==1 verify."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HO = os.path.join(ROOT, "research", "HANDOVER.md")

ROW = (
 "> bm-c round 670 五倍数核对（2026-10-07 10:5x·增量窗 r666-670 五轮）：增量窗 r666-670=bm-c 面（**金周值守主线+D-06 域件族三连再平衡（pit-git-resolver 超线→pit-lineage 满员→主件增量批）+复市日历勘误律+O-0935 派单双机回执闭口+构造式×方程式双 derive 恒等门立法到实装**——"
 "r666 值守轮〔CODELY r662/r665 两指针行 latin-1 双层 mojibake 治愈（根因=python str \\xNN 转义 byte-as-str 落盘坑→pit-encoding.md 直写 1 条·r447 逆映射律治愈·收据 _r666bmc_codely_mojibake_heal.json）+机活探针裸机名 needle 撞他机 commit 文案假阳性坑（r659 自配族 git-log 变体→pit-lineage-legdiff.md 直写 1 条）〕；"
 "r667 值守轮〔pit-ps.md mini-split（D-06 再平衡·31,449B>30,720B 触发）——零窗包装器调用族 7 条+1 对账行 verbatim 迁出→research/pit-ps-wrapper.md（ArgString 引号吞噬/单串输出/行拆消费/位置绑定/落文件法族）·主件 r662/r665 两指针行随批 verbatim 迁 pit-ps.md 尾·逐行字节+sha16+零丢失断言=receipt _r667bmc_pit_ps_split_receipt.json〕；"
 "r668 值守轮〔**未来日历事实未核验写 CEO 面坑立法**（复市日错报勘误 10-09→10-08：国务院办公厅 2026 节假日通知三源交叉=国庆 10-01~10-07 休·A 股复市首交易日=10-08 周四·bm-a r714 readiness 件+bm-b 心跳本持 10-08=仅 bm-c 面单方错〔r666 close 模板引入〕·正法=未来市场日历事实写入心跳/里程碑前必两源核验）+增量批同窗：r814 水位坑 verbatim 迁 pit-protocol-d19.md（sha16 3598f944144aaa01·收据 _r668bmc_codely_increment.json）〕；"
 "r669 值守+超线修复轮〔**pit-git-resolver sub-split**：实测 30,850B>30,720B 域线（bm-a r817 10:06 增量致·r668 收据面 room-308B 声明=陈旧收据=r653 收据-实测律活案例）→rebase/sequencer 净路族 9 条 verbatim 零丢失迁出→research/pit-git-resolver-rebase.md 新子件 11,569B+主件 r659 坑 994B 迁入母件 append 面（母件 23,579B 回线）·主件 30,719→29,724B·prescan rc3+登记册预登记+--verify 55/55+S4 新坑律 803B 入册〔**拆件脚本列表构成错误=逐行锚点门盲区·构造式×方程式双 derive 恒等门正法**——survivors 误含 3 行头块 19 锚点门全过·唯一拦截=字节方程门·主件终态 30,527B 余 193B〕+close push-race 15-UU 逐面裁定收口〔addendum 留痕〕〕；"
 "r670=本核对轮〔**5x HANDOVER 义务（本行）+pit-lineage 让位 sub-split+主件增量批+派单闭口**：S0 落后 0 零 rebase·S0.5 双扫零 delta+inbox bm-b capability receipt 核收=O-20261007-0935-bm-c 派单正主收口〔JSON cat-file rc0 验达 origin+MSG 转 processed+票面 bm-b 勾选+回执节写入·bm-a r817+bm-b r803 两机回执全收·提前交付 ≤10-09 窗〕；"
 "主产品=pit-lineage.md 30,552B 满员让位（r669 next 指针窗兑现）：收据可复核律族 12 条 verbatim→research/pit-lineage-receipt.md 新子件 15,198B+母件 18,527B〔−12,803B+778B 指针行〕+主件增量批 r653 坑 677B→receipt 子件〔r646 同族归位〕+r669 坑 802B→pit-git.md〔拆件断言层族〕·主件 30,527→30,101B 回线余 619B·**双 derive 恒等门首次实装**（r669 坑正法落地·四文件构造==方程全过·尺寸 gate len() derive）·--verify 93/93；三坑实弹：needle 同轮号异坑撞车（r637 双坑撞 sibling 门拦截→S4 直写 pit-git.md 913B）+r653 第三活例（声明 676/803 vs 实测 677/802 双陈旧）+头部行数假设错（fail-closed probe 后修正）〕〕）。"
 "产物清单漂移=research/pit-git-resolver-rebase.md+research/pit-lineage-receipt.md〔两新子件〕+research/pit-{git-resolver,lineage,ps,ps-wrapper,protocol-d19,pit-encoding,git}.md 增量族+CODELY.md〔主件 30,527→30,101B·r669 坑迁出+r670 指针行〕+knowledge/TREASURE_REGISTRY.md〔r669/r670 预登记行〕+results/_r6{66,67,68,69,70}bmc_* 工件族〔mojibake heal+ps split+increment+resolver split+lineage receipt split 收据〕+Tools/_r6{66,67,68,69,70}bmc_*.py 驱动器族+qa/smoke-r6{6,7,8,9,70}.md+qa/equity-curve-r6{6,7,8,9,70}.png〔QA 证据包族·93 trades·determinism=True·equity 1,017,839 跨轮恒等〕+results/_r6{66..70}bmc_s6_log.txt〔S6 log 五连 38/38 rc0〕+fleet/orders/O-20261007-0935-bm-c.md〔双机回执节全闭〕+fleet/inbox/processed/MSG-2026-10-07-095x-bmb-bmc-capability-receipt.md；零新产品行（值守窗零批 finalize 零判决零新链入=如实注记）；"
 "统一链 **781,612 实读平持**（live head=results/perpetual_faces/n1_w171_results.json science_gates.ledger.total 实测·W171 finalize bm-a r816 落账·W172 预坐席 bm-a r818〔A 393_204..395_203+B 395_204..395_403·E36 阶梯第 31 例〕·bm-c 零引擎波归属面如实注记）；"
 "板面 open=0·job_list 空·satengine 活〔Tools 实例 rc0〕·水位绿〔next_pick=claimed moneyflow IC batch·面板 parked EM 源阻 30min 自愈·金周无 bar 合法 idle〕·DEC/ORD 双扫零 delta（635C3024/B687D867）164/164·attrition CLEAN·post_review ✗0；"
 "指针：**10-08（周四）复市首交易日——数据链 re-arm〔S6 legs 25-28 复活〕+REGIME_GUARD v3 首 bar 激活（t24 门 last_bar≥10-01 当日核验）+纸盘 marks 地板推进+external run-11/run-7（bm-a r714 readiness owns preflight）**；trio finalize 窗观察至 10-09（bm-b 道）；W172 冻结窗（bm-a）；月界首考 10-31；主件余量 619B=下批 direct-write pit 续压面；下一 5x=bm-c r675。"
)

raw = open(HO, "rb").read()
title_end = raw.find(b"\n")
assert title_end > 0, "title line gate"
title = raw[: title_end + 1]
assert title.decode("utf-8").startswith("# Bigmoney"), "title content gate"
guard = "round 670 五倍数核对".encode("utf-8")
assert raw.count(guard) == 0, "rerun guard"
rest = raw[title_end + 1:]
eol = b"\r\n" if title.endswith(b"\r\n") else b"\n"
row_b = ROW.encode("utf-8")
new = title + row_b + eol + rest
open(HO, "wb").write(new)
post = open(HO, "rb").read()
assert post.count(guard) == 1, "post count==1"
assert post[: len(title)] == title, "title preserved"
assert post[len(title): len(title) + len(row_b)] == row_b, "row inserted at pos2"
print("HANDOVER 5x row inserted; file now", len(post), "B; row", len(row_b), "B")
