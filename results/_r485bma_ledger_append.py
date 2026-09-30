"""r485 bm-a one-shot: round report + CODELY appends (ledger append laws:
tail-newline check, pipes gate, byte-range verify after)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REPORT = (
 "2026-09-30T18:2x+08:00 | r485 | dept:数据+工程 | WM=py_low_board_clear 绿"
 "（板 open=0·RW-5 冻结待 10-03 外审+D-41 轨道切换窗=合法 idle 白名单·"
 "red=False）| 做了什么: ①S0.5 双扫=orders 127/127 零未回执（首扫 BaseName "
 "比较假阳当场核正=.md 全名制·r136 坑律复证）+decisions mtime 17:22 零新增行"
 "（D-35~41 已 r479~r483 逐行回执在册）②**主产品件：r484 钦点 09-30 bar "
 "包装器端点观察项诊断闭环**=results/_r485bma_sina_wrapper_probe.{py,json} "
 "四腿探针——akshare 包装器尾 09-29（3487 行）≡原始 klc_kl.js 同尾同行数"
 "（update_etf_daily fetch_member 正典配方复用零重实现）=**包装器无罪**；"
 "scope 腿：股票面 sh600519 已有 09-30 bar·ETF 面双市（sh510300/sz159915）"
 "均缺=**sina ETF 日线面节前发布滞后**；tencent 校验腿已有（与 r483 "
 "fallback_events upstream_has_newer_bar 交叉一致）；hq 实时面活=非宕机→"
 "update_daily 契约（禁 tencent 写 bar）下诚实 no-op 等后续轮自动挂钩=正解；"
 "futures/repo/options 期望完整 bar 日=09-29 系 ETF 日历主源下游面自洽 ③"
 "S6 36+ 腿全 rc0（dualrun ZERO-DRIFT 51/3·audit 旗=pool_starvation+"
 "supply_floor RW-5 合法 idle 同 r484 态·regime ORANGE 双触发面持·scorecard "
 "6/28/7·CALL-2026-09-30 ORANGE_COOL·lhb rc0 cutoff 09-30 检疫态终·采集族"
 "全合法 no-op/spawn（heat 已采·futures/repo/options/sina_mf cutoff 覆盖·"
 "moneyflow 节流·ths 09-29 已采·ah spawn 节流在途·fundamental 6.8h 新鲜）·"
 "车道守卫 x5 诚实 no-op·b_layer 全门过·paper 锚 OK·t35 PASS 0 例·t24 "
 "22/22·promotion 0/22 诚实·aggr/grid/sysv1 marks 幂等 no-op·t35e export-"
 "09-29 再生·dscore/dreport faces5/ceo_live ORANGE cap50 COOL/build/token "
 "全 rc0）④HANDOVER 485 五倍数核对条目入册（增量窗 r481-485 产物清单漂移+"
 "指针·r480 条目后置锚）⑤自愈三件绿（loop pin=8 no-op·watchdog Ready·"
 "claw in sync）⑥attrition CLEAN（4 ledgers·healed 2 注记照录）| 验证"
 "证据: smoke 47/47+S6 全 rc0+probe JSON 四腿+心跳 epoch int 自证"
 "（1790764141）+orders 127/127 收尾复扫 | 当前活: 09-30 bar 落地观察（sina "
 "ETF 面发布即全链自动挂钩）+10-01 月首轮三件套; 最近实物: results/_"
 "r485bma_sina_wrapper_probe.py/.json（18:2x 本窗·四腿诊断证据）+HANDOVER "
 "r485 条目; 下里程碑: 10-01 月首轮三件套+REGIME_GUARD v3 日期门自动激活"
 "（10-01 后首轮 hands-off）+RW-5 外审 10-03，窗≤48h | next: r486=10-01 "
 "月首三件套+09-30 bar 观察续+bm-b r472/473 rebase 并合收口（本窗进行中）"
 " [via bm-a]\n")

CODELY = (
 "- [2026-09-30 18:2x r485 bm-a] sina ETF 日线面节前发布滞后坑（09-30 实弹·"
 "r484 观察项闭环）：update_daily 0 新行+tencent fallback 报 "
 "upstream_has_newer_bar≠包装器 bug——四腿探针定谳（akshare 包装器尾≡原始"
 "klc_kl.js 尾〔update_etf_daily fetch_member 配方〕；股票面 sh600519 已有"
 "当日 bar 而 ETF 面双市缺=面级滞后非全局宕机；hq 实时面活）→正解=契约内"
 "诚实 no-op 等源发布自动挂钩（禁 tencent 写 bar 律不动）·最坏窗=下一交易"
 "日 10-09。探针件 results/_r485bma_sina_wrapper_probe.py 可复跑。How：未来"
 "节前/源端零新行时先跑四腿探针定责（包装器 vs 源面 vs 宕机）再动手，勿空转"
 "重查包装器怀疑圈；futures/repo/options 期望 bar 日随 ETF 日历主源联动="
 "同滞后的下游自洽面非独立故障。\n")

def append_ledger(path, text, pipes_gate=None):
    with io.open(path, "r", encoding="utf-8-sig", newline="") as fh:
        old = fh.read()
    if old and not old.endswith("\n"):
        old += "\n"           # law 1: tail newline
    if pipes_gate is not None:
        assert text.count("|") >= pipes_gate, "pipes gate"
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(old + text)  # law 3: byte-range verified via git diff later
    return len(old + text)

rp = os.path.join(ROOT, "round_reports-bm-a.md")
n1 = append_ledger(rp, REPORT, pipes_gate=7)  # 7 pipes = one line (14+=merged bug)
cp = os.path.join(ROOT, "CODELY.md")
n2 = append_ledger(cp, CODELY)
print("report_bytes=%d codely_bytes=%d (<10240: %s)"
      % (n1, n2, n2 < 10240))
