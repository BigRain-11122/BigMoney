import io, datetime

RP = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports.md"
now = datetime.datetime.now().isoformat(timespec="seconds") + "+08:00"

product = (
    "%s | r672 (bm-b) PRODUCT (dept:研究预finalize证据+数据维护链): [watermark verdict: GREEN "
    "(red=false lane=healthy; probe py_low_with_work_cands=三烧 claimed-burning 合法态点名声明 r671 同款; "
    "audit CLEAN burning-healthy; dualrun ZERO-DRIFT streak 51)] | 当前活: FUND 三族 NULLS 烧录在飞 "
    "V770/Q598/D444 of 2000 @13:1x (38.5/29.9/22.2pct, owners=bm-b keepalive mtime<3min, 速率 24.6/21.0/17.7/h 稳态无降级) "
    "| 最近实物: results/_r672bmb_finalize_rehearsal_summary.json (13:25:22, 三族 finalize 预演 ALL-GREEN——"
    "r633 阻塞② VALUE passive 崩溃修复后全调用链端到端跑通: quality 181.4s / value 229.6s / divlowvol 183.0s, "
    "failed_legs 全空, NOT_A_VERDICT 声明; 阻塞① G-SEG 冻结 insufficient-sample 路径=O-20261004-0808 GM 已裁定维持) "
    "+ results/trio_burn_eta.json 刷新 (ETA VALUE 10-06T15 / QUALITY 10-07T07 / DIVLOWVOL 10-08T05) "
    "| 本轮同窗: S0 merge+push DELIVERED (bm-c r472 收口并入零UU) + orders/D-19 双扫双键 MATCH (153/153, "
    "decisions 4E5BE321 / orders 68947C17, sparse-clone+git-show 原字节 r631/r660 配方) + smoke 48/48 + "
    "S6 38/38 rc0 (golden-week no-new-bar 面: cutoff 2026-09-30, 大多数腿诚实 no-op; bm-a hb 陈旧 25-27min "
    "=其正常轮中节奏非停滞, scorecard/daily_scorecard/build_status/t35 四面 lane_io stale-takeover derive by bm-b "
    "O-2100 s2.4 合法; regime=ORANGE 取守为攻) + bm-a 心跳三证核查 (28min stale=轮中态, T-169 s1 frozen 完好, "
    "零接管零触碰) + p1d_gates 元数据刷新面 (gates 全 PASS 随轮) | 下轮指针: trio 看护续期 + VALUE 烧完 "
    "(~10-06)即 finalize 候选窗开 (10-06..09, GM 裁定窗已闭); finalize 轮必同窗池面双翻 (r668 律) + "
    "方法卡判据: 预演 ALL-GREEN 后无已知代码路径阻塞, 判词面按冻结路径如实出\n" % now
)

with io.open(RP, "a", encoding="utf-8", newline="") as f:
    f.write(product)

# verify append landed exactly once (r453 dedup/marker discipline)
t = io.open(RP, encoding="utf-8", errors="replace").read()
assert t.count("r672 (bm-b) PRODUCT") == 1, "PRODUCT line count != 1"
print("appended r672 PRODUCT line; count==1 OK")
