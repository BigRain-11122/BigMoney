"""r364 bm-c W78 prereg §7/§8 mechanical backfill (post-finalize, r307
two-state law; bytes-in-bytes-out per r530 CRLF law; placeholders only,
no criterion text touched)."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(REPO, "research", "PERPETUAL_N1_W78_PREREG.md")

b = open(FP, "rb").read()
t = b.decode("utf-8")
eol = "\r\n" if t.count("\r\n") * 2 > t.count("\n") else "\n"

SEC7_ANCHOR = ("## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】"
               + eol + eol + "- （占位·finalize 后机械回填）")
SEC8_ANCHOR = ("## §8 批后复盘【必填·s7-T】"
               + eol + eol + "- （占位·finalize 后机械回填）")
assert t.count(SEC7_ANCHOR) == 1, f"S7 anchor count={t.count(SEC7_ANCHOR)}"
assert t.count(SEC8_ANCHOR) == 1, f"S8 anchor count={t.count(SEC8_ANCHOR)}"

SEC7_NEW = (
    "## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】" + eol + eol +
    "- **finalize 实烧=one-pass r364 bm-c**（r538 一过例·2026-10-02 12:0x·12 分片 shards_consumed 12/12·r310 完备性门 origin 12/12 ls-tree 过〔引擎 appender 两批 6+6 分片已全量 origin 在案〕）：N=2,200（A 2,000＋B 200）。" + eol +
    "- **S5 四门全过（§5 预测 4/4）**：① W78-only mu **−0.091233** 与 merged mu **−0.092267**（K=169,520）漂移 |Δ|=**0.001034**<0.02（对锚 W75 merged −0.092271 漂 0.000004）✓；② sigma 相对变化 **−0.34%**<±10%（W78-only **0.245029** vs 锚 0.245868=W75-only 实测）✓；③ A 族 full_sharpe_p95 **0.3245** vs 锚 0.3088 |Δ|=**0.0157**<0.05 ✓；④ K-lift **+0.0000**≤0.02（1.1649→**1.1649** @n_eff_held 533,948·se_mu **0.000594** 收窄中〔W67 0.000642→W69 0.000633→W71 0.000624→W77 0.000598→W78 0.000594〕·正负交替律如实：W74 +0.0002→W75 −0.0001→W76 +0.0001→W77 −0.0001→W78 +0.0000）✓。mu_delta_w78_vs_w77ext=**+0.002319**。")

SEC8_NEW = (
    "## §8 批后复盘【必填·s7-T】" + eol + eol +
    "- **全生命周期三窗闭环（猝死会话遗产跨轮收口）**：冻结 r363（席位 MSG-20261002-1150-bmc·published=reserved r518-①·B 面带位修正回执 MSG-20261002-1155-bmc）→烧录 12/12（r363 窗常驻引擎 v0.4 per-tick 自燃 11:47:37..11:48:30·appender 两批 ledger append 已推 origin）→finalize r364 one-pass（r363 会话死于 S7 簿记前夜〔state 停 362〕·r364 收养续收口·r529 律号位 363 烧毁）。" + eol +
    "- **链序面**：W76 bm-b r573 落账（531,748）→W77 bm-a r573 落账（533,948）→本波 W78 落账（**536,148**·K=169,520·voids_applied=LOWAMP-P1/LOWAMP-P2）→**W79（bm-b·r573 冻结·烧录在飞 4/12+）finalize 解锁**（bm-b 下一 one-pass）。" + eol +
    "- **带位面**：A-ext seed **199_004..201_003**＋B-ext exit seed **53_201..53_400**（gate ADMIT 回执=results/_r363bmc_w78_band_gate.py·A 算术顺延零跳位＋B 双点链跳位 W63-B 族〔j13v2_mill_ic1=53_000+j13v2_mill_ic2=53_100 双撞·分叉 53_101..53_300 披露不采 r566 面〕）。" + eol +
    "- **撞面实证**：起草窗连环让路 W76（bm-b r572）→W77（bm-a r572）后二度再占位（r565 律第二次执行·双让路双逐位交叉验证 #11/#12）；无重跑（r538 一过例）·无判据触碰（回填限 §7/§8）。")

t = t.replace(SEC7_ANCHOR, SEC7_NEW)
t = t.replace(SEC8_ANCHOR, SEC8_NEW)
assert "（占位·finalize 后机械回填）" not in t, "placeholder residue"
open(FP, "wb").write(t.encode("utf-8"))
print("BACKFILL_OK 78")
