# -*- coding: utf-8 -*-
"""r464 bm-a: CODELY.md hot-cold reorg (pointer-merge only, zero verbatim
loss) + new r464 pit entry append.  10,234B + new entry > 10,240B hard line
-> in-window reorg per O-20260927-0230 law.  Merges follow the 指针合并归档
r444 范式 (r255/r259 merged-pointer precedents)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "CODELY.md"
src = open(P, encoding="utf-8").read()
orig_len = len(src.encode("utf-8"))


def subn(s, old, new, n, what):
    c = s.count(old)
    if c != n:
        print("REORG-FAIL: %s count=%d expected %d" % (what, c, n))
        sys.exit(2)
    return s.replace(old, new)


# 1. Feedback pointer merge: r458 + r445hang
src = subn(src,
           "- 冷层指针：r458 泊位族选双面核验坑（zoo 行状态面滞后于 results 判决面）"
           "全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r459 bm-a 窗批二』节"
           "（法面=防重核双面序：rg results 判决面先行·zoo/登记行状态只作线索）。\n"
           "- [2026-09-30 r459 bm-a]",
           "- 冷层指针（合并）：r458 泊位族选双面核验坑（rg results 判决面先行·"
           "zoo/登记行状态只作线索）=『热冷整编 2026-09-30 r459 bm-a 窗批二』节+"
           "r445 采集器无超时挂死盲区坑（fetch_one 45s 死限+TimeoutError 走 "
           "CONN_MARKERS fuse 路·探针 _r445bmb_hang_shield_probe.py 承载）="
           "『热冷整编 2026-09-30 r457 bm-a 窗批』节，全文 verbatim=archive "
           "202609.md。\n- [2026-09-30 r459 bm-a]", 1, "feedback r458+r445 merge")

# drop the now-merged r445hang standalone line
src = subn(src,
           "- 冷层指针：r445 采集器无超时挂死盲区坑（conn-fuse 对 hang 失明） "
           "全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r457 bm-a 窗批』节"
           "（法面=fetch_one daemon-worker 45s 死限+TimeoutError 走 CONN_MARKERS "
           "fuse 路+探针 _r445bmb_hang_shield_probe.py 承载）。\n\n### Project",
           "\n### Project", 1, "r445hang standalone drop")

# 2. Project pointer merge: r440撞批 + r440bm-b + r242 -> one line
src = subn(src,
           "- 冷层指针：r440 撞批三查律+r449 风暴 union 复活去重律全文 verbatim="
           "archive 202609.md『热冷整编 2026-09-30 r245 bm-c 窗批』节。\n"
           "- 冷层指针：r440 bm-b 初筛富集面≠注册级增量律全文 verbatim="
           "archive 202609.md『热冷整编 2026-09-29 r449 bm-a 窗批』节"
           "（法面已由 TRIAL_LABOR_W10_PREREG §7/8+CEO-REPORT-WAVE10+attrition 承载）。\n"
           "- 冷层指针：r242 bm-c runner 外科手术四连坑族全文 verbatim="
           "archive 202609.md『热冷整编 2026-09-29 r449 bm-a 窗批』节"
           "（W11 runner 已建毕 selftest 47/47·坑律由 _r242bmc_w11_surgeon 系列工件承载）。",
           "- 冷层指针（r464 合并·指针合并归档 r444 范式）：r440 撞批三查律+r449 "
           "风暴 union 复活去重律（『热冷整编 2026-09-30 r245 bm-c 窗批』节）+"
           "r440 bm-b 初筛富集面≠注册级增量律（法面已由 TRIAL_LABOR_W10_PREREG "
           "§7/8+CEO-REPORT-WAVE10+attrition 承载）+r242 runner 外科手术四连坑族"
           "（W11 runner 已建毕 selftest 47/47·坑律由 _r242bmc_w11_surgeon 系列工件"
           "承载）（两律=『热冷整编 2026-09-29 r449 bm-a 窗批』节），全文 verbatim="
           "archive 202609.md。",
           1, "project 3-pointer merge")

# 3. Reference merge: r456 + r457 + r446bm-b + r252 -> one line
src = subn(src,
           "- 冷层指针：r456 a158 冻结面抽位点对账 eps 分母坑（W13 探针首跑实弹） "
           "全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r459 bm-a 窗批』节"
           "（法面=a158_tsgate_probe 参考式同款 eps 分母+镜像孪生族构造恒等自检承载）。\n"
           "- 冷层指针：r457 风暴 resolver 非幂等追加坑全文 verbatim=archive 202609.md"
           "『热冷整编 2026-09-30 r253 bm-c 窗批』节"
           "（法面=append 型收口脚本 add 前幂等守卫惯例+半途失败 git checkout -- "
           "恢复惯例承载）。\n"
           "- 冷层指针：r446 bm-b 手术过继残漏三连坑（tlN→tlN+1 过继必带真数据 "
           "identity face 三命令实弹首跑收口步）全文 verbatim=archive 202609.md"
           "『热冷整编 2026-09-30 r459 bm-a 窗批三』节"
           "（W13 过继者=bm-a berth·r459 state next 指针直引本条）。\n"
           "- 冷层指针：r252 bm-c 泊位/冻结步开工前 inbox 零未读腿坑全文 verbatim="
           "archive 202609.md『热冷整编 2026-09-30 r459 bm-a 窗批二』节"
           "（法面=供给类开工前置检查单三查扩四查：job_list+tasks+fetch 标题扫+"
           "inbox 未读清零）。",
           "- 冷层指针（r464 合并）：r456 a158 冻结面抽位点对账 eps 分母坑"
           "（a158_tsgate_probe 参考式同款 eps 分母+镜像孪生族构造恒等自检承载="
           "『r459 bm-a 窗批』节）+r457 风暴 resolver 非幂等追加坑（append 型收口"
           "脚本 add 前幂等守卫+半途失败 git checkout -- 恢复惯例=『r253 bm-c 窗批』"
           "节）+r446 bm-b 手术过继残漏三连坑（tlN→tlN+1 过继必带真数据 identity "
           "face 三命令实弹首跑收口步·W13 过继者=bm-a berth=『r459 bm-a 窗批三』节）+"
           "r252 泊位/冻结步开工前 inbox 零未读腿坑（供给类开工前置检查单三查扩四查="
           "『r459 bm-a 窗批二』节），全文 verbatim=archive 202609.md。",
           1, "reference 4-pointer merge")

# 4. Reference merge: r445dual-nulls + r441 -> one line
src = subn(src,
           "- 冷层指针：r445 dual-nulls seed 声明≠实跑基坑全文 verbatim=archive "
           "202609.md『热冷整编 2026-09-30 r455 bm-a 窗批』节"
           "（法面=冻结清单 ⑤ seeds 三步律面+runner rebind fv.UNC_BASE 惯例承载）。\n\n"
           "- 冷层指针：r441 泊位种子撞带竞态活处理律全文 verbatim=archive 202609.md"
           "『热冷整编 2026-09-29 r448 bm-a 窗批』节"
           "（法面双载=T-123 spec+W12 draft ⑤收编清单）。",
           "- 冷层指针（r464 合并）：r445 dual-nulls seed 声明≠实跑基坑"
           "（冻结清单 ⑤ seeds 三步律面+runner rebind fv.UNC_BASE 惯例承载="
           "『热冷整编 2026-09-30 r455 bm-a 窗批』节）+r441 泊位种子撞带竞态活处理律"
           "（法面双载=T-123 spec+W12 draft ⑤收编清单=『热冷整编 2026-09-29 r448 "
           "bm-a 窗批』节），全文 verbatim=archive 202609.md。",
           1, "r445+r441 merge")

# 5. Reference merge: r255poolworker + r449replay -> one line
src = subn(src,
           "- 冷层指针：r255 bm-c pool worker stale-tree claim 假失败坑"
           "（worker 秒级 rc=2 先查 runner 在树性再判机制故障·正法=claim 前置在树核验="
           "O-2210 待单写者窗）全文 verbatim=archive 202609.md"
           "『热冷整编 2026-09-30 r258 bm-c 窗批』节。\n"
           "- 冷层指针：r449 bm-b 冻结面 replay 漂移三源定谳律+W8 构造事实"
           "（对照员字节恒等=机制身份隔离定谳法·λ 中位 0.131·16/66 奇异窗·退化窗"
           "配对差分剔除禁 pinv）全文 verbatim=archive 202609.md"
           "『热冷整编 2026-09-30 r258 bm-c 窗批』节"
           "（正典面=research/INNOVATION_QUOTA_W8_PREREG_DRAFT.md §C1+"
           "results/_r449bmb_w8_probe.json）。",
           "- 冷层指针（r464 合并）：r255 pool worker stale-tree claim 假失败坑"
           "（worker 秒级 rc=2 先查 runner 在树性再判机制故障·正法=claim 前置在树"
           "核验=O-2210 待单写者窗）+r449 冻结面 replay 漂移三源定谳律+W8 构造事实"
           "（对照员字节恒等=机制身份隔离定谳法·λ 中位 0.131·16/66 奇异窗·退化窗"
           "配对差分剔除禁 pinv·正典面=research/INNOVATION_QUOTA_W8_PREREG_DRAFT.md "
           "§C1+results/_r449bmb_w8_probe.json），两条全文 verbatim=archive 202609.md"
           "『热冷整编 2026-09-30 r258 bm-c 窗批』节。",
           1, "r255+r449 merge")

# 6. append new r464 entry (after the r462 entry, before the r259 merged pointer)
src = subn(src,
           "（25min 预算装不下链+主活串行）。\n- 冷层指针（r259 合并）",
           "（25min 预算装不下链+主活串行）。\n"
           "- [2026-09-30 r464 bm-a] surgeon 锚面取自实跑文件律（W13 Slice-A1 三连"
           "实弹）：tlN→tlN+1 过继手术 sub1 锚必须逐条从在树 SRC 实跑文件现取，"
           "禁从前代 surgeon payload 文本复制——三实证：①import 行注释实跑="
           "fifteen-tuple 而 payload=残文 mismatch；②face 标签行换行点/续行缩进"
           "实跑与 payload 不同=0 hits 硬弹（正解=取唯一内串短锚）；③段界 banner"
           "（exclusion N real-reads）归上一段 end marker 所有，下一段段内 sub1 "
           "0 hits——正法=段界改动置段重组装后的 src 层。镜像命名注记：W12 冻结面"
           "最新源标签 w12_*读 tl11=残漏改名痕（W11 实跑=源波命名 w10_*读 tl10 "
           "实证），W13 按消费波镜像（w13_*读 tl12）随冻如实注记。工程件="
           "results/_r464bma_w13_surgeon.py（sections 1-10 一遍全绿+py_compile "
           "PASS）+21 点接线自验 _r464bma_w13_draft_verify.py 全 OK。\n"
           "- 冷层指针（r259 合并）",
           1, "r464 entry append")

open(P, "w", encoding="utf-8", newline="\n").write(src)
new_len = len(src.encode("utf-8"))
print("REORG-OK: %d -> %d bytes (line=%d, %s)" % (
    orig_len, new_len, 10240, "UNDER" if new_len <= 10240 else "OVER!!"))
print("lines: %d -> %d" % (orig_len, src.count("\n")))
