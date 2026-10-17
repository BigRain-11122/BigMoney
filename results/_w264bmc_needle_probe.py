# -*- coding: utf-8 -*-
# r1076 bm-c: W264 derive needle-count pre-flight (measure all floor candidates on T0, one pass).
import io, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0 = io.open(os.path.join(REPO, "results", "_w264bmc_w263_frozen_face.txt"), encoding="utf-8", newline="").read()

KEYS = [
    "W263", "W262", "W261", "W260", "W259", "W258", "W257", "W256", "W255",
    "n1_w263", "n1_w261", "n1_w262", "_w263bma", "_w262bmc",
    "A-ext seed=593_901..595_900", "B-ext exit seed=595_901..596_100",
    "entry rng seed=**593_901+j**", "entry rng=**593_901+j**", "exit rng=**595_901+j**",
    "席位公示=MSG-20261017-1740-bma-w263-seat", "席位公示 MSG-20261017-1740-bma-w263-seat",
    "波号 263", "零 263 行", "零 skip-ahead W264/W265 席位声明", "池第 261 枚",
    "第 253 波", "bm-a 第一百三十枚自有波", "probe leg0 bma_rows=129",
    "engine_owner==bm-a 129 行注册", "engine_owner==bm-a 波的未烧分片",
    "saturation_engine.py status live-read r1037", "本机 bm-a 实例·heartbeat 新鲜实读 r1037 窗",
    "本机 bm-a 实例·heartbeat 新鲜实读", "引擎实况注记（本机 bm-a 实例",
    "bm-a 实例=engine ledger", "本窗 free RAM ~26GB",
    "--wave 263/finalize --wave 263", "§5.5 W264+ 投影承接机证",
    "engine_owner 行 252 注册在册（表尾", "prev=**届时空窗活链头 derive 禁手抄**",
    "（**A 面=STAIRCASE-AFFECTS-A", "probe W264+ 投影 A naive 595_901..597_900 CLEAN hops=0",
    "5. **W264+ 投影（probe 机证 leg4", "本件=席位窗冻结件；五面冻结拼接脚本",
    "（见 §5 item5）。", "；p=`BASELINE_P", "；p_exit=`P_EXIT=0.05`",
    "never transcribe r587**）", "verify at W264 prereg，hop 链逐跳在 probe 回执。",
    "（gate0.5 未绿前禁 splice·编辑器 loud abort 兜底）**。",
    "后下窗归属=W263）**】）", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。",
    "（W262 finalize PENDING·分片 12/12 已烧）", "14:1x", "17:4x", "15:5x",
    "W206/W211..W262 低 RAM 实烧先例", "键 W261 实测 K-lift", "line_pre_w261",
    "→W260 **0.000325**→W261 **0.000325**", "n_eff_held_equal 996,335",
]
out = []
for k in KEYS:
    out.append("%s = %d" % (k, T0.count(k)))
txt = "\n".join(out)
print(txt)
io.open(os.path.join(REPO, "results", "_w264bmc_needle_counts.txt"), "w", encoding="utf-8", newline="").write(txt + "\n")
print("\nwritten results/_w264bmc_needle_counts.txt")
