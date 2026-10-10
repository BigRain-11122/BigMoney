# r828 bm-b: append r828 consumption record to explore.md (UTF-8 LF, byte-safe)
p = r"state\queue\explore.md"
raw = open(p, "rb").read().decode("utf-8")
assert "r828 消耗记录" not in raw
rec = (
    "\n> r828 消耗记录（bm-b）：E8 本轮完成出列（**商品期货跨期价差监控面→9/9 品种描述面落地**"
    "：T-18 探针 CLEAR 认领〔commit 3b5b3686b 锁〕；预检 results/_r828bmb_e8_shape_probe.py "
    "四族 5/5 活=同一 per-contract 端点通吃〔键位 d/o/h/l/c/v/p/s·p=持仓 s=结算·CFFEX s=0.000 诚实 None〕"
    "；交付=监控面 scripts/futures_calendar_spread.py〔selftest 14/14 离线密封·48 请求 0 失败·2.5s 限速"
    "·配对=活 20 天+OI 15% floor+far_thin 回退披露〕+证据 results/futures_calendar_spread/"
    "{face.json,spreads.csv}〔791 行序列·panel cutoff 2026-10-09 全对齐〕"
    "+调研件 research/digests/DIGEST-20261010-e8-futures-calendar-spread.md；"
    "判读=股指四族 2610/2612 贴水 -38.6~-127〔分红贴现正向结构〕·国债 2612/2703 [far_thin] "
    "CTD 微贴水 -7~-9bp·RB 2701/2703 z=-2.14 近期翻面·AU 2612/2702 +2.4 升水·SC 2611/2612 "
    "深贴水 -23.3〔ratio 0.968=近月现货紧面最厚信号面〕；basis(near-panel)=0.0×6"
    "+OI 逐位恒等〔RB 1,673,458/SC 23,669/T 377,917〕=主力连续面板三方交叉验证；"
    "上游 latent 键位坑〔update_futures raw fallback OI 读键 o（=开盘价）·真键 p〕登记 tech T20 "
    "归 bm-a lane；零判据零 prereg·judged face 须另开票+PREREG_TEMPLATE 正门）。"
    "P3 队列 5→4（E9 队头=港股通 AH 折溢价均值回归深化）。"
    "附修=r827 记录行界分裂+3 路径缺 r 出生缺陷治愈〔4 行并 1·字节账 3 LF 剔除+3 r 还原·工件存在性先验〕。"
)
open(p, "wb").write((raw + rec + "\n").encode("utf-8"))
print("appended r828 record; new bytes:", len((raw + rec + "\n").encode("utf-8")))
