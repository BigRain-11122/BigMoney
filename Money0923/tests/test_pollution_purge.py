"""污染清除机制测试（用户红线 2026-09-21"错误的训练数据及时清空，发现以后，
不要污染我的模型"）。

覆盖：①校验发现判据（纯函数）②纪元读写 ③缓存键纪元敏感性（发现坏数据后
旧分永不命中+股票/期货分域互不误杀）④陈旧缓存行及时清除（含机制前遗留行）
⑤联赛证据按事件类型清除（校验发现类=证据+认证全清；例行重写类=保留）
⑥全量重拉→纪元联动。隔离铁律：epoch 文件/缓存DB/日线路径全部指向临时目录，
绝不触碰真实 state.json / eval_cache.db / data_epoch.json。
运行: python tests/test_pollution_purge.py
"""
import os
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd  # noqa: E402

import quant.data as qd  # noqa: E402
import quant.evolve as qev  # noqa: E402
from quant import arena as qar  # noqa: E402
from quant import validation as qv  # noqa: E402
from quant.config import AppConfig  # noqa: E402


def _isolate():
    """隔离环境：临时 epoch 文件 + 临时缓存DB + 记忆体复位。"""
    tmp = tempfile.mkdtemp(prefix="pollution_test_")
    qd.DATA_EPOCH_FILE = os.path.join(tmp, "data_epoch.json")
    qev._EVAL_CACHE_DB = os.path.join(tmp, "eval_cache.db")
    qev._EPOCH_MEMO[:] = [0.0, None]
    qev._PURGE_MEMO[:] = [0.0, None]
    return tmp


def test_discovery_diff():
    prev = {"excluded": [{"code": "600000"}], "repaired": ["510300"],
            "inferred_20pct": ["159915"]}
    same = {"excluded": [{"code": "600000", "reason": "x"}], "repaired": ["510300"],
            "inferred_20pct": ["159915"]}
    assert qv._discovery_diff(prev, same) == [], "语义集合未变不得误报发现"
    new = {"excluded": [{"code": "600000"}, {"code": "601999"}],
           "repaired": ["510300", "588170"], "inferred_20pct": ["159915", "159949"]}
    events = qv._discovery_diff(prev, new)
    assert len(events) == 3 and any("601999" in e for e in events), f"三处新发现都要报: {events}"
    print("校验发现判据 OK: 无变化不误报 / 新剔除+新修复+新推断三事件全捕获")


def test_bump_and_epoch_roundtrip():
    _isolate()
    assert qd.data_epoch()["stock"] == 0, "无文件=纪元0"
    qd.bump_data_epoch("stock", "校验发现数据修正：剔除2只")
    qd.bump_data_epoch("futures", "主力连续日更重拼接9品种")
    ep = qd.data_epoch()
    assert ep["stock"] == 1 and ep["futures"] == 1
    assert "校验" in ep["reason_stock"] and "日更" in ep["reason_futures"], "域内原因各自留存"
    qd.bump_data_epoch("stock", "全量重拉204只（qfq基准重写历史）")
    ep = qd.data_epoch()
    assert ep["stock"] == 2 and ep["futures"] == 1, "两域纪元独立计数"
    print("纪元读写 OK: 两域独立计数+域内原因留存")


def test_cache_key_epoch_sensitivity():
    _isolate()
    cfg = AppConfig()
    panel = types.SimpleNamespace(
        dates=[pd.Timestamp("2024-01-02") + pd.Timedelta(days=i) for i in range(30)],
        codes=["600000", "600519", "510300"])
    slices = [(panel.dates[5], panel.dates[20])]
    stock_ind = {"strategy": "momentum", "params": {"lookback": 20}}
    fut_ind = {"strategy": "cta_trend", "params": {"chan_len": 40}}
    k1, e1 = qev._eval_cache_key(stock_ind, panel, slices, cfg)
    assert e1 == "s0", f"股票个体挂股票纪元，实际{e1}"
    kf1, ef1 = qev._eval_cache_key(fut_ind, panel, slices, cfg)
    assert ef1 == "f0", f"cta_trend 挂期货纪元，实际{ef1}"
    # 期货纪元 bump：期货个体键必变，股票个体键不变（分域互不误杀）
    qev._EPOCH_MEMO[:] = [0.0, None]
    qd.bump_data_epoch("futures", "主力连续日更重拼接9品种")
    qev._EPOCH_MEMO[:] = [0.0, None]
    k2, _ = qev._eval_cache_key(stock_ind, panel, slices, cfg)
    kf2, _ = qev._eval_cache_key(fut_ind, panel, slices, cfg)
    assert k1 == k2, "期货日更不得误杀股票缓存"
    assert kf1 != kf2, "期货历史重写后期货旧分必须失效"
    # 股票纪元 bump（校验发现）：股票键变，期货键不变
    qev._EPOCH_MEMO[:] = [0.0, None]
    qd.bump_data_epoch("stock", "校验发现数据修正：剔除2只")
    qev._EPOCH_MEMO[:] = [0.0, None]
    k3, _ = qev._eval_cache_key(stock_ind, panel, slices, cfg)
    kf3, _ = qev._eval_cache_key(fut_ind, panel, slices, cfg)
    assert k1 != k3, "发现坏数据后股票旧分必须永不命中"
    assert kf2 == kf3, "股票域发现不误杀期货缓存"
    # 池成分变化（同数量不同成分）→ 键必变
    panel.codes = ["600000", "600519", "159915"]
    k4, _ = qev._eval_cache_key(stock_ind, panel, slices, cfg)
    assert k3 != k4, "同数量不同成分的池不得吃陈旧分"
    print("缓存键纪元敏感性 OK: 分域互不误杀+发现后旧分永不命中+池成分入键")


def test_cache_purge_domains():
    tmp = _isolate()
    conn = qev._cache_conn()
    conn.execute("INSERT OR REPLACE INTO eval_cache VALUES (?,?,?,?,?)",
                 ("k_s1", 0.5, "{}", "t", "s0"))
    conn.execute("INSERT OR REPLACE INTO eval_cache VALUES (?,?,?,?,?)",
                 ("k_f1", 0.6, "{}", "t", "f0"))
    conn.execute("INSERT OR REPLACE INTO eval_cache VALUES (?,?,?,?,?)",
                 ("k_legacy", 0.7, "{}", "t", ""))  # 机制前遗留行
    conn.commit()
    # 首次检查：登记纪元 + 清空遗留行
    qev._purge_stale_cache(conn)
    rows = {r[0] for r in conn.execute("SELECT key FROM eval_cache")}
    assert rows == {"k_s1", "k_f1"}, f"机制前遗留行应清除，实际{rows}"
    # 期货纪元 bump → 只清期货行
    qev._EPOCH_MEMO[:] = [0.0, None]
    qev._PURGE_MEMO[:] = [0.0, None]
    qd.bump_data_epoch("futures", "主力连续日更重拼接9品种")
    qev._EPOCH_MEMO[:] = [0.0, None]
    qev._purge_stale_cache(conn)
    rows = {r[0] for r in conn.execute("SELECT key FROM eval_cache")}
    assert rows == {"k_s1"}, f"期货 bump 只清期货行，实际{rows}"
    # 股票纪元 bump（校验发现）→ 股票行也清
    qev._EPOCH_MEMO[:] = [0.0, None]
    qev._PURGE_MEMO[:] = [0.0, None]
    qd.bump_data_epoch("stock", "校验发现数据修正：剔除2只")
    qev._EPOCH_MEMO[:] = [0.0, None]
    qev._purge_stale_cache(conn)
    rows = {r[0] for r in conn.execute("SELECT key FROM eval_cache")}
    assert rows == set(), f"股票 bump 后股票行应清除，实际{rows}"
    conn.close()
    print(f"陈旧行及时清除 OK: 遗留行清理+分域清除（tmp={os.path.basename(tmp)}）")


def test_arena_evidence_reset():
    _isolate()
    cfg = AppConfig()

    def mk_state():
        return {"arena": {"pstats": {"g1": {"n": 40}}, "qualified": [
            {"id": "Q1", "strategy": "etf_trend", "params": {}, "sizing": "equal",
             "sizing_params": {}, "score": 0.6}]}}

    # 校验发现类 → 证据+认证全清（错误数据上挣的证据不可留）
    st = mk_state()
    qd.bump_data_epoch("stock", "校验发现数据修正：剔除2只")
    qar._purge_polluted_evidence(cfg, st)
    assert st["arena"]["pstats"] == {} and st["arena"]["qualified"] == []
    assert st["arena"]["data_epoch_stock"] == 1
    print("联赛证据清除 OK: 校验发现类→pstats+认证池全清重练")

    # 例行重写类（周重拉/期货日更）→ 证据保留（过度清除=毁灭好证据，反而不科学）
    st = mk_state()
    qd.bump_data_epoch("stock", "全量重拉204只（qfq基准重写历史）")
    qar._purge_polluted_evidence(cfg, st)
    assert st["arena"]["pstats"] and st["arena"]["qualified"], "例行重写不得清联赛证据"
    # 幂等：纪元未变不再动作
    qar._purge_polluted_evidence(cfg, st)
    assert st["arena"]["pstats"] and st["arena"]["qualified"]
    print("联赛证据保留 OK: 例行重写类只清缓存分不动证据+幂等")


def test_update_daily_full_pull_bumps_epoch():
    tmp = _isolate()
    daily_dir = os.path.join(tmp, "daily")
    meta_dir = os.path.join(tmp, "daily_meta")
    os.makedirs(daily_dir, exist_ok=True)
    os.makedirs(meta_dir, exist_ok=True)
    qd._daily_path = lambda code: os.path.join(daily_dir, f"{code}.csv")
    qd._META_DIR = meta_dir
    qd.load_universe = lambda: pd.DataFrame({"code": ["600000"]})
    qd.clock.last_trade_date = lambda d: d - pd.Timedelta(days=1)

    def bars(closes, open0=None):
        n = len(closes)
        return pd.DataFrame({
            "date": [f"2026-01-{i + 1:02d}" for i in range(n)],
            "open": [open0 if (open0 is not None and i == 0) else c for i, c in enumerate(closes)],
            "high": [c * 1.01 for c in closes], "low": [c * 0.99 for c in closes],
            "close": list(closes), "volume": [1000.0] * n, "amount": [c * 1000 for c in closes]})

    bumps = []
    real_bump = qd.bump_data_epoch
    qd.bump_data_epoch = lambda domain, reason: bumps.append((domain, reason)) or real_bump(domain, reason)
    saved_sleep = qd.time.sleep
    qd.time.sleep = lambda s: None
    import logging as _lg
    h = []
    class _H(_lg.Handler):
        def emit(self, r):
            h.append(r.getMessage())
    hh = _H()
    qd.log.addHandler(hh)
    try:
        cfg = AppConfig()
        # ① 首拉落盘（无旧缓存）= 池成分新增：由缓存键成分哈希覆盖，不升纪元
        qd._fetch_hist = lambda code, start, end: bars([10.0, 10.2])
        qd._full_pull_due = lambda code, today: True
        qd.update_daily(cfg)
        assert bumps == [], f"首拉不应升纪元，实际{bumps}"
        assert os.path.exists(qd._daily_path("600000")), "首拉应落盘"

        # ② 周期到点全量重拉且内容改写（收盘价变）→ 升股票纪元
        qd._fetch_hist = lambda code, start, end: bars([10.0, 10.9])
        qd.update_daily(cfg)
        assert len(bumps) == 1 and bumps[0][0] == "stock" and "改写历史" in bumps[0][1], \
            f"内容改写必须升纪元，实际{bumps}"

        # ③ 周期到点但内容与缓存完全一致（源冻结反复重拉同数据）→ 不升纪元
        qd._fetch_hist = lambda code, start, end: bars([10.0, 10.9])
        qd.update_daily(cfg)
        assert len(bumps) == 1, f"同内容重拉不得升纪元（源冻结时防每次重启清缓存），实际{bumps}"

        # ④ 接缝守卫：源忽略 start 返回全史，首根K线 open 与昨日收盘比出假接缝
        #    （-8%跳变）→ 守卫必须跳过接缝检测，去重合并安全处理，不触发全量重拉
        qd._full_pull_due = lambda code, today: False
        qd._fetch_hist = lambda code, start, end: bars([10.0, 10.9, 11.0], open0=10.0)
        n_before = len(pd.read_csv(qd._daily_path("600000"), dtype={"date": str}))
        qd.update_daily(cfg)
        df = pd.read_csv(qd._daily_path("600000"), dtype={"date": str})
        assert len(df) == n_before + 1, "增量新K线应被安全合并"
        assert len(bumps) == 1, f"全史返回不得触发假接缝全量重拉，实际{bumps}"
        assert not any("拼接缝异常" in m for m in h), "守卫必须拦下全史首K假接缝"

        # ⑤ 数据新鲜度告警：合并后仍滞后于 end_date → 必须可见可审计
        assert any("数据新鲜度" in m for m in h), "尾部滞后必须告警留痕"
    finally:
        qd.log.removeHandler(hh)
        qd.time.sleep = saved_sleep
        qd.bump_data_epoch = real_bump
    print("更新链路 OK: 首拉不升纪元/改写才升/同内容重拉不升/全史假接缝被守卫拦下/停更告警留痕")


def test_horizon_pending_mechanism():
    tmp = _isolate()
    qd._META_DIR = os.path.join(tmp, "daily_meta")
    os.makedirs(qd._META_DIR, exist_ok=True)
    p1 = qd._horizon_pending(["A", "B"], "20010401")
    assert p1 == {"A", "B"}, "口径变更→全量待重拉"
    qd._save_horizon_pending("20010401", {"B"})
    p2 = qd._horizon_pending(["A", "B"], "20010401")
    assert p2 == {"B"}, "同口径→保留自愈进度"
    p3 = qd._horizon_pending(["A", "B"], "20100101")
    assert p3 == {"A", "B"}, "口径再变→重新全量"
    print("下载口径机制 OK: 口径变更强制整段重拉/自愈进度保留/再变重置")


if __name__ == "__main__":
    test_discovery_diff()
    test_bump_and_epoch_roundtrip()
    test_cache_key_epoch_sensitivity()
    test_cache_purge_domains()
    test_arena_evidence_reset()
    test_update_daily_full_pull_bumps_epoch()
    test_cache_purge_domains()
    test_arena_evidence_reset()
    test_update_daily_full_pull_bumps_epoch()
    test_horizon_pending_mechanism()
    print("ALL PASS")

