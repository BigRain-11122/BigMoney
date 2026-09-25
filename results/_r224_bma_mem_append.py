# -*- coding: utf-8 -*-
"""R224 bm-a memory append: sina tier-semantics line (one matter, pointer-form)."""
entry = (" - [2026-09-26 06:2x] 数据面/R118 证据升级（bm-a R224·T-72 prereg open-item 批腿·"
         "sina 四档语义官方面）：**sina 行情页官方 JS（utils-hq.js）实证 "
         "r0_in=「主力净流入(元)」/r3_in=「散户净流入(元)」（与 lscjfb r0_net/r3_net 同名族）"
         "——sina 四档叙事=投资主体类非 EM 单笔单量类，「sina 主力」与「EM 主力（超大单+大单聚合）」"
         "同名不同构，跨平台互映射在标签层即伪（R118 禁映射律获直接证据）**；r1/r2 档名+数值阈值"
         "已探面 UNDOCUMENTED 维持（消费页不可定位：xh1.php+realstock 兄弟页 404、API 精确串 "
         "SERP 噪音已证无效禁再烧=换面不换串）；同名族识别=合理归纳禁升格 DOCUMENTED（PARTIAL 口径）。"
         "指针=DIGEST-20260926-r224-t72-sina-tier-doc-probe.md+results/_r224_bma_sina_tier_* 五探针"
         "+SINA_MF_PREREG §5 R224 注记。")
with open("CODELY.md", "a", encoding="utf-8") as f:
    f.write("\n" + entry + "\n")
import os
print("appended, new size:", os.path.getsize("CODELY.md"))
