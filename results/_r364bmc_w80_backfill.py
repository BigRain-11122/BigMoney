"""r364 bm-c W80 prereg §7/§8 mechanical backfill (post-finalize, r307
two-state law; bytes-in-bytes-out per r530; placeholders only)."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(REPO, "research", "PERPETUAL_N1_W80_PREREG.md")

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
    "- **finalize 实烧=one-pass r364 bm-c**（r538 一过例·2026-10-02 12:1x·12 分片 shards_consumed 12/12·r310 完备性门 origin 12/12 ls-tree 过〔appender 三批 4+4+4·末批 4 片由 r364 收尾 commit 送达〕）：N=2,200（A 2,000＋B 200）。" + eol +
    "- **S5 四门全过（§5 预测 4/4）**：① W80-only mu **−0.088862** 与 merged mu **−0.092353**（K=173,920）漂移 |Δ|=**0.003491**<0.02（对锚 W78 merged −0.092267 漂 0.000086）✓；② sigma 相对变化 **−0.06%**<±10%（W80-only **0.244885** vs 锚 0.245029=W78-only 实测）✓；③ A 族 full_sharpe_p95 **0.3253** vs 锚 0.3245 |Δ|=**0.0008**<0.05 ✓；④ K-lift **+0.0001**≤0.02（1.1653→**1.1654** @n_eff_held 538,348·se_mu **0.000587** 收窄中〔W77 0.000598→W78 0.000594→W79 0.000591→W80 0.000587〕·正负交替律如实：W76 +0.0001→W77 −0.0001→W78 +0.0000→W79 +0.0000→W80 +0.0001）✓。mu_delta_w80_vs_w79ext=**+0.013549**。")

SEC8_NEW = (
    "## §8 批后复盘【必填·s7-T】" + eol + eol +
    "- **全生命周期单窗闭环（r364 一窗三产）**：席位公示 MSG-20261002-1204-bmc 先推 origin（r565 律·commit 31db49798·12:04）→带闸+banned 闸双 ADMIT→冻结五面 commit 7fbeadb2e（12:07 工作树落成·12:12 推 origin 一次过）→常驻引擎 v0.4 per-tick 自燃 12/12 烧毕（12:07..12:10·appender 三批 commit）→finalize r364 one-pass（12:1x·同窗 W78 finalize 落账解锁链序后）。" + eol +
    "- **链序面**：W78 bm-c r364 落账（536,148）→W79 bm-b r574 落账（538,348）→本波 W80 落账（**540,548**·K=173,920·voids_applied=LOWAMP-P1/LOWAMP-P2）→**链序 W1..W80 全落账**·W81（bm-a r574 冻·在飞席）finalize 链序待位。" + eol +
    "- **撞面实证**：bm-b 同窗发布 W80 席位（MSG-20261002-1210-bmb·12:11）→本机冻结 first-land（r511 commit 时序律）→bm-b 让路回执在案（MSG-20261002-1220-bmb·零成本让路·带位逐位同=r530 族确定性交叉验证；bm-b 披露近失误=其起草窗曾覆写本机 W80 prereg·当场 checkout 恢复零推送〔r560 族·本机无损〕）；bm-a 同窗 W81 席位（MSG-20261002-1210-bma）——W81 竞位归 bm-a/bm-b 裁定非本机列。无重跑（r538 一过例）·无判据触碰（回填限 §7/§8）。" + eol +
    "- **遗产收口链**：r363 猝死会话〔state 停 362·死于 S7 簿记前夜〕→r364 按 r529 律收养：W78 finalize（536,148）+W80 全生命周期（冻结→烧毕→finalize 540,548）同窗双波收口。")

t = t.replace(SEC7_ANCHOR, SEC7_NEW)
t = t.replace(SEC8_ANCHOR, SEC8_NEW)
assert "（占位·finalize 后机械回填）" not in t, "placeholder residue"
open(FP, "wb").write(t.encode("utf-8"))
print("BACKFILL_OK 80")
