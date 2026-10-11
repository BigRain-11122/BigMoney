# -*- coding: utf-8 -*-
"""r915 bm-c: prepend round-915 5x increment block to research/HANDOVER.md (title-line anchor)."""
import io

PATH = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\HANDOVER.md"
raw = open(PATH, "rb").read()
title = "# Bigmoney 交接与成果收割指南（HANDOVER）"
tb = title.encode("utf-8")
assert raw.startswith(tb), "title anchor missing"
# detect title line ending
eol = b"\r\n" if b"\r\n" in raw[:200] else b"\n"
head_end = len(tb)
# skip the title line's EOL
assert raw[head_end:head_end + len(eol)] == eol, "title line EOL mismatch"
rest = raw[head_end + len(eol):]

block_txt = (
    "> bm-c round 915 五倍数核对（2026-10-12 07:0x·增量窗覆盖 r871-r915 四十五轮·**5x 截 "
    "r875/r880/r885/r890/r895/r900/r905/r910 八截未落 HANDOVER 行如实披露**〔坑-79 族·CEO mv0001 "
    "影片链收割窗+排满夜战窗消耗〕·r871-r915 逐轮权威面=round_reports-bm-c.md 全行在册）：增量窗 "
    "r871-r915=bm-c 面像（**W210→W216 七连引擎波全生命周期收口+never-dry 席位链 W214/W215/W216/W217 "
    "四发布+排满令夜战 absorb 三连**——①引擎波链全落：W210 885,789/K459,920→W211 887,989/K462,120→"
    "W212 890,189/K464,320→W213 892,389/K466,520→W214 894,589/K468,720→W215 896,789/K470,920→W216 "
    "898,989/K473,120（七连 merged mu 稳定 -0.0927 带·se_mu 收窄链 0.000367→0.000356·每波 "
    "pre-finalize 六门探针先于 finalize+W212 债务教训后零复发+五键全过+prereg §7/§8 机读回填·逐波产物="
    "results/perpetual_faces/n1_w2XX_results.json）；②never-dry 席位链：W214 席 r909〔d55a6b58b〕→"
    "W215 席 r911〔37d7adc0a〕→W216 席 r913〔f8b38fa1e〕→W217 席 r915 本窗〔MSG-20261012-0700·A "
    "492_204..494_203/B 494_204..494_403·阶梯 A-hops-prior-B 第七十七例·seed_admit 双带 FREE·origin "
    "vacancy 四查〕——引擎 DRY 常供给零断档·排满令〔CEO 10-10 23:1x RE-ISSUE「机队CPU算力全部用于回测，"
    "排满」〕常设执行中；③absorb 夜战三连：r898-r914 夜窗多会话死于收尾前（GPU/RAM 挤压+5min 零输出"
    "自动杀）·r907 吸收 r898-r906 九窗+r911 吸收 r908-r910 三窗+r915 吸收 r914 一窗〔本窗·r914 遗体="
    "W216 全链 prereg 7d565ee67+freeze 0b3c489f0+engine 12/12 两批 4f998b352/9f99cecf6+finalize 产物"
    " 06:51:45 已推零 closeout〕——账本零双计〔每吸收窗 S0.5 双水位 delta FALSE 实证〕；④治理面："
    "s05_probe 常设组合器〔r871 世代〕+双水位 sha corrupt-face 勘误链〔r894/r902 两犯治愈·现水位 dec "
    "67403afa/ord 33aee170〕+books union 手术〔r913·49 行 root->canon·r855 先例第 3 发〕+attrition "
    "守卫 CLEAN 连窗+孤儿探针连窗〔ComfyUI=CEO MV i2v lane 零-touch 如实注记〕+S6 链 38/38 rc0 连窗；"
    "⑤CEO mv0001 影片链收割=本机 GPU 面让路窗〔i2v 批+KF 收割·交互窗持有·BigMoney 零 lane-touch〕；"
    "下一里程碑=W217 per-wave prereg+五面冻结拼接（下一窗 FIRST ACTION）+周一 15:30 新 bar 链"
    "〔update_daily+live.paper+t35_open_fill_verify+t24 链〕+unity-mcp POC 回执 10-13 12:00〔O-2333〕。"
)
block_b = block_txt.encode("utf-8")
new_raw = tb + eol + block_b + eol + rest
assert len(new_raw) == len(raw) + len(block_b) + len(eol), "length invariant failed"
assert new_raw.endswith(raw[-100:]), "tail preservation failed"
open(PATH, "wb").write(new_raw)
print("inserted r915 5x block; old", len(raw), "new", len(new_raw), "eol", eol)
