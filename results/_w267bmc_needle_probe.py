# -*- coding: utf-8 -*-
# _w267bmc_needle_probe.py - r1087 bm-c: measured-count needle probe on the
# W266 frozen template face (T0 = results/_w267bmc_w266_frozen_face.txt) per
# the r1077 measured-counts-not-assumed law + live RAM/VRAM face.
# Read-only; prints one count per needle + live machine face.
import io, sys

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w267bmc_w266_frozen_face.txt"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

NEEDLES = [
    "W266", "W265", "W264", "W263", "W262", "W261", "W260", "W259", "W258",
    "W257", "W256", "W255", "W254", "W267",
    "W267+", "W268+", "W266+",
    "n1_w266", "n1_w265", "n1_w264",
    "_w266bmc", "_w265bmc", "_w264bmc",
    "_w266bmc_20261018", "_w265bmc_20261017", "_w266bmc_20261017",
    "_w265bmc_20261018",
    "A-ext seed=600_501..602_500",
    "B-ext exit seed=602_501..602_700",
    "entry rng=**600_501+j**",
    "entry rng seed=**600_501+j**",
    "exit rng=**602_501+j**",
    "MSG-20261018-0719-bmc-w266-seat",
    "ace19ba85b",
    "席位公示=MSG-20261018-0719-bmc-w266-seat 已推 origin ace19ba85b r565 律（bm-c r1084 席·queue-head seat-first lane）",
    "席位公示 MSG-20261018-0719-bmc-w266-seat 先推 origin ace19ba85b r565 律",
    "波号 266",
    "r1084 席位窗实跑：origin inbox 零 W266 席位外机命中",
    "零 266 行",
    "零 skip-ahead W267/W268 席位声明",
    "池第 264 枚",
    "第 256 波",
    "bm-c 第八十五枚自有波",
    "probe leg0 bmc_rows=84 attempt-continuity face（r1084 窗算法·bm-c own seat+bmc live rows 84 实读）——freeze 时 live derive bmc rows 84+候选=第 85 枚 EXACT",
    "engine_owner==bm-c 84 行注册",
    "engine_owner 行 255 注册在册（表尾",
    "saturation_engine.py status live-read r1085：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1085 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1085 窗实读",
    "本窗 free RAM ~3GB",
    "（nvidia-smi 实读 3%·3.2G VRAM 常驻·零在飞烧批）",
    "--wave 266/finalize --wave 266",
    "§5.5 W267+ 投影承接机证",
    "07:0x",
    "10:2x",
    "1,009,535",
    "585,320",
    "602_701..604_700",
    "604_701..604_900",
    "602_501..604_500",
    "600_501..602_500",
    "602_501..602_700",
    "waits-upstream ARMED",
    "（W265 实测键 **\u22120.09271568**·K=580,920 合并池·W265-only 实测 **\u22120.08956582**）",
    "W2..W265 共二百六十四面实测 mu 稳定先例",
    "W265-only vs merged 实差 0.0031 在带内",
    "键 **0.24504118**=W265 合并池实测",
    "与 W265 A 档 p95（**0.3149** 实测锚）",
    "键 W265 实测 K-lift **0.0000**·line_merged@K580,920 **1.1956**·line_pre_w265 1.1956·n_eff_held_equal 996,335",
    "\u2192W262 **0.000323**\u2192W263 **0.000323**\u2192W264 **0.000322**\u2192W265 **0.000321**\u2192W266 投影 0.000321】",
    "（起草窗实流 W1..W265 已落账 580,920 实测",
    "bm-c r1084 W265 §7 范式",
    "bm-c r1084 W265 §8 范式",
    "·W244 冻结窗 41.9G bm-a 实锚·W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚）",
    "n_eff_held_equal 996,335",
    "580,920 投影",
    "583,120 投影",
    "prev=**届时空窗活链头 derive 禁手抄**",
    "（**A 面=STAIRCASE-AFFECTS-A",
    "（见 §5 item5）。",
    "；p=`BASELINE_P",
    "；p_exit=`P_EXIT=0.05`",
    "probe W267+ 投影 A naive 602_501..604_500 CLEAN hops=0",
    "never transcribe r587**）",
    "5. **W267+ 投影（probe 机证 leg4",
    "verify at W267 prereg，hop 链逐跳在 probe 回执。",
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本",
    "（gate0.5 绿·编辑器 loud abort 兜底）**。",
    "owner per chain-order law）**】】）",
    "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。",
    "第 85 枚",
    "第 257 波",
    "第八十六枚",
    "engine_owner==bm-c 85 行注册",
    "engine_owner 行 256 注册在册",
    "SIXTEENTH consecutive",
    "SEVENTEENTH",
    "第十六次连续 A-hop",
    "第十七次连续 above-own-A",
    "第十五次连续 A-hop",
    "第十六次连续 above-own-A",
    "W266 finalize one-pass bm-c r1086",
    "W265 finalize one-pass bm-c r1084",
]

for n in NEEDLES:
    print("%04d | %s" % (T0.count(n), n))

print("--- live machine face ---")
try:
    import psutil
    vm = psutil.virtual_memory()
    print("ram_free_gb=%.2f ram_free_pct=%.1f" % (vm.available / 2**30, vm.available / vm.total * 100))
except Exception as e:
    print("psutil fail: %r" % e)
print("needle_probe_done")
