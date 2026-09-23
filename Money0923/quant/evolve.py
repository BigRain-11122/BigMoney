"""进化引擎：遗传算法 + 多时间片适应度 + 样本外冠军晋升。

防过拟合三道闸：
1. 适应度 = 训练期多个时间片复合分的均值（不偏向单一行情段）
2. holdout（最近18%历史）从不参与适应度，只用于冠军晋升验证
3. 晋升门槛：挑战者样本外分 > 现任×(1+margin) 且 > 绝对分下限

"拿别人成功的模型去推论"：种群初始化注入经典公开模型的标准参数作为种子，
GA 从这些验证过的起点出发继续进化，而非每次从随机噪声起步。
"""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import logging
import os
import random
import sqlite3
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from . import strategies as strat_lib
from .backtest import run_backtest
from .config import DATA_DIR, AppConfig, backtest_fingerprint, ensure_dirs, resolve_workers
from .sizing import SIZING, get_sizing
from .state import load_state, save_state

log = logging.getLogger("quant.evolve")

# ---------------------------------------------------------------- 本地评估缓存（能力累积）
# 每一次适应度回测的结果按（个体基因 + 数据窗口 + 风控/费用/打分口径指纹）落盘 SQLite，
# 重启/换窗口重算时直接复用——机器算过的东西永不重算第二次。
# 口径指纹保证：任何风控/费用/打分参数变化 → 缓存自动整体失效（绝不吃旧口径的脏分）。
# 打分函数或回测引擎结构性改动时，递增 _FITNESS_VERSION 强制全量刷新。

_EVAL_CACHE_DB = os.path.join(DATA_DIR, "eval_cache.db")
_FITNESS_VERSION = "v1"

# 期货域策略（权重含 F.*）：其缓存行挂期货数据纪元，其余挂股票纪元——
# 两域互不误杀（期货日更重拼接不殃及股票缓存行）。
_FUT_STRATS = {"cta_trend"}

_EPOCH_MEMO: list = [0.0, None]   # (取数时间, data_epoch dict)——30s 防每评估读盘
_EPOCH_MEMO_TTL = 30.0
_PURGE_MEMO: list = [0.0, None]   # (检查时间, epoch 元组)——60s 防每评估查 meta


def _current_data_epoch() -> dict:
    """数据纪元（带 30s 进程内记忆，纪元变化最迟 30s 后生效）。"""
    import time as _t
    if _EPOCH_MEMO[1] is None or _t.time() - _EPOCH_MEMO[0] > _EPOCH_MEMO_TTL:
        from .data import data_epoch
        _EPOCH_MEMO[0] = _t.time()
        _EPOCH_MEMO[1] = data_epoch()
    return _EPOCH_MEMO[1]


def _cache_conn() -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(_EVAL_CACHE_DB, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")
    conn.execute("CREATE TABLE IF NOT EXISTS eval_cache ("
                 "key TEXT PRIMARY KEY, score REAL, extra TEXT, updated_at TEXT, "
                 "epoch TEXT DEFAULT '')")
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(eval_cache)")]
        if "epoch" not in cols:  # 旧表迁移（机制上线前的行 epoch=''，永不命中）
            conn.execute("ALTER TABLE eval_cache ADD COLUMN epoch TEXT DEFAULT ''")
    except Exception:  # noqa: BLE001
        pass
    return conn


def _purge_stale_cache(conn) -> None:
    """数据纪元变化 → 及时清除对应域陈旧缓存行（用户红线 2026-09-21：
    "错误的训练数据及时清空，发现以后，不要污染我的模型"）。

    行的 epoch 列=写入时的域纪元（"s{n}"股票 / "f{n}"期货）；股票纪元变化
    清 s 开头行，期货纪元变化清含 f 行。纪元已入键所以旧行本就永不命中——
    本清除是"及时清空"字面执行+回收空间。首次运行顺带清空机制前遗留行。
    meta 表记住上次见过的纪元；24 个 worker 并发竞争无害（后者 rowcount=0）。"""
    import time as _t
    now = _t.time()
    if _PURGE_MEMO[1] is not None and now - _PURGE_MEMO[0] < 60.0:
        return
    _PURGE_MEMO[0] = now
    ep_d = _current_data_epoch()
    ep = (int(ep_d.get("stock", 0)), int(ep_d.get("futures", 0)))
    if _PURGE_MEMO[1] == ep:
        return
    _PURGE_MEMO[1] = ep
    conn.execute("CREATE TABLE IF NOT EXISTS cache_meta (k TEXT PRIMARY KEY, v TEXT)")
    row = conn.execute("SELECT v FROM cache_meta WHERE k='epoch'").fetchone()
    prev = tuple(json.loads(row[0])) if row else None
    if prev == ep:
        return
    purged = 0
    if prev is None:
        purged = conn.execute(
            "DELETE FROM eval_cache WHERE epoch IS NULL OR epoch=''").rowcount or 0
        conn.execute("INSERT OR REPLACE INTO cache_meta VALUES ('epoch', ?)",
                     (json.dumps(ep),))
        conn.commit()
        if purged:
            log.warning("【污染清除】评估缓存清理机制前遗留 %d 行（键缺纪元成分，永不命中）", purged)
        return
    if prev[0] != ep[0]:
        purged += conn.execute("DELETE FROM eval_cache WHERE epoch LIKE 's%'").rowcount or 0
    if prev[1] != ep[1]:
        purged += conn.execute("DELETE FROM eval_cache WHERE epoch LIKE '%f%'").rowcount or 0
    conn.execute("INSERT OR REPLACE INTO cache_meta VALUES ('epoch', ?)", (json.dumps(ep),))
    conn.commit()
    if purged:
        log.warning("【污染清除】评估缓存清除 %d 行（纪元 s%d/f%d←s%d/f%d：%s）",
                    purged, ep[0], ep[1], prev[0], prev[1],
                    ep_d.get("reason_stock") or ep_d.get("reason_futures") or "")


def _eval_cache_key(ind: dict, train_panel, slices, cfg: AppConfig):
    """缓存键 + 域纪元标记。返回 (key, epoch_str) 或 None。

    污染清除机制（用户红线 2026-09-21）：数据纪元入键——历史重写/发现坏
    数据后，旧数据上算出的分数永不命中（宁可重算不吃脏分）；股票池成分
    哈希入键——同数量不同成分的池不再吃到陈旧分。"""
    try:
        gene = {"s": ind["strategy"], "p": ind["params"]}
        # 仓位控制基因：非默认时必须入键（等权=无操作，保持同口径命中）
        z = ind.get("sizing") or "equal"
        zp = ind.get("sizing_params") or {}
        if z != "equal" or zp:
            gene["z"] = z
            gene["zp"] = zp
        gene = json.dumps(gene, sort_keys=True)
        window = f"{train_panel.dates[0]}|{train_panel.dates[-1]}|{len(train_panel.dates)}|{len(train_panel.codes)}|" \
                 + "|".join(f"{s[0].date()}~{s[1].date()}" for s in slices)
        ep = _current_data_epoch()
        epoch_str = (f"f{ep['futures']}" if ind.get("strategy") in _FUT_STRATS
                     else f"s{ep['stock']}")
        codes_hash = hashlib.md5(
            "|".join(map(str, train_panel.codes)).encode("utf-8")).hexdigest()[:10]
        raw = "|".join([_FITNESS_VERSION, gene, window, backtest_fingerprint(cfg),
                        epoch_str, codes_hash])
        return hashlib.md5(raw.encode("utf-8")).hexdigest(), epoch_str
    except Exception:  # noqa: BLE001 任何异常都放弃缓存（正确性优先）
        return None


def _cache_get(key: str):
    try:
        with _cache_conn() as conn:
            _purge_stale_cache(conn)
            row = conn.execute("SELECT score, extra FROM eval_cache WHERE key=?", (key,)).fetchone()
        if row and row[0] is not None:
            return float(row[0]), json.loads(row[1])
    except Exception:  # noqa: BLE001
        pass
    return None


def _cache_put(key: str, score: float, extra: dict, epoch_str: str = "") -> None:
    try:
        with _cache_conn() as conn:
            _purge_stale_cache(conn)
            conn.execute("INSERT OR REPLACE INTO eval_cache VALUES (?,?,?,?,?)",
                         (key, float(score), json.dumps(extra, ensure_ascii=False),
                          dt.datetime.now().isoformat(timespec="seconds"), epoch_str))
    except Exception:  # noqa: BLE001 缓存写入失败不影响计算
        pass


# 经典公开模型的标准参数种子（进化起点，出处见各策略 docstring）
# 仓位控制基因一并种子化：等权/波动率倒数/组合波动率目标/均线风险开关
GA_SEEDS: list[dict] = [
    {"strategy": "mean_rev", "params": {"rsi_len": 2, "entry_th": 10, "exit_th": 75,
                                        "trend_ma": 200, "max_hold": 5, "top_k": 5},
     "sizing": "equal", "sizing_params": {}},                              # Connors RSI2
    {"strategy": "donchian", "params": {"entry_len": 20, "exit_len": 10, "top_k": 5},
     "sizing": "inv_vol", "sizing_params": {"vol_win": 20}},              # 海龟 20/10 + 波动率倒数定仓（原文ATR思想）
    {"strategy": "dual_momentum", "params": {"mom_len": 250, "skip_days": 21,
                                             "top_k": 2, "abs_floor": 0.0},
     "sizing": "vol_target", "sizing_params": {"target_vol": 0.15, "vol_win": 20, "min_exp": 0.2}},  # Antonacci 12m-1m
    {"strategy": "rotation_28", "params": {"lookback": 20, "cash_mom": 0.0},
     "sizing": "ma_risk", "sizing_params": {"ma_len": 60, "risk_off": 0.4}},  # 二八轮动 20日
    {"strategy": "low_vol", "params": {"vol_win": 60, "top_k": 6, "rebal_days": 10},
     "sizing": "inv_vol", "sizing_params": {"vol_win": 30}},               # 低波动异象
    {"strategy": "rsrs", "params": {"window": 18, "zscore_win": 300, "buy_z": 0.8,
                                    "exit_z": -0.2, "target": "510300"},
     "sizing": "vol_target", "sizing_params": {"target_vol": 0.20, "vol_win": 30, "min_exp": 0.0}},  # 光大 RSRS
    # GP 基因组种子：Connors式（趋势上超卖+RSI回升离场）与海龟式（突破+通道跌破离场）
    {"strategy": "evolved", "params": {"entry": [{"kind": "cross_up", "n": 50},
                                                  {"kind": "osc_low", "n": 2, "th": 10.0}],
                                        "logic": "all", "exit": [{"kind": "osc_high", "n": 2, "th": 70.0}],
                                        "score": "rev_5", "top_k": 5, "rebal_days": 5,
                                        "ma_filter": 200, "max_hold": 5, "weighting": "equal"},
     "sizing": "equal", "sizing_params": {}},
    {"strategy": "evolved", "params": {"entry": [{"kind": "breakout", "n": 55},
                                                  {"kind": "mom_pos", "n": 60, "th": 0.0}],
                                        "logic": "all", "exit": [{"kind": "breakdown", "n": 20}],
                                        "score": "roc_20", "top_k": 5, "rebal_days": 5,
                                        "ma_filter": 0, "max_hold": 0, "weighting": "equal"},
     "sizing": "inv_vol", "sizing_params": {"vol_win": 20}},
]


def _sample_param(spec: tuple, rng: random.Random):
    kind = spec[0]
    if kind == "int":
        return int(rng.randint(int(spec[1]), int(spec[2])))
    if kind == "float":
        return round(float(rng.uniform(spec[1], spec[2])), 4)
    if kind == "choice":
        return rng.choice(list(spec[1]))
    raise ValueError(f"未知参数类型 {kind}")


def _sample_sizing(rng: random.Random) -> tuple[str, dict]:
    """随机仓位控制基因：类型 + 参数。"""
    name = rng.choice(list(SIZING))
    space = SIZING[name].param_space
    return name, {k: _sample_param(v, rng) for k, v in space.items()}


def _blend_sizing(a: dict, b: dict, rng: random.Random) -> dict:
    """仓位基因交叉：同类型参数级均匀混合，异类型整组取一亲本。"""
    za, zb = a.get("sizing") or "equal", b.get("sizing") or "equal"
    za_pa = dict(a.get("sizing_params") or {})
    zb_pb = dict(b.get("sizing_params") or {})
    if za == zb:
        keys = set(za_pa) | set(zb_pb)
        return {"sizing": za,
                "sizing_params": {k: (za_pa.get(k, zb_pb.get(k)) if rng.random() < 0.5
                                      else zb_pb.get(k, za_pa.get(k))) for k in keys}}
    src = a if rng.random() < 0.5 else b
    return {"sizing": src.get("sizing") or "equal",
            "sizing_params": dict(src.get("sizing_params") or {})}


def _mutate_sizing(ind: dict, rng: random.Random, rate: float, sigma: float) -> None:
    """仓位基因变异：类型重选（换仓位哲学）或参数高斯扰动。"""
    z = ind.get("sizing") or "equal"
    if rng.random() < rate * 0.5:  # 半概率换整套仓位策略
        new_z, new_p = _sample_sizing(rng)
        ind["sizing"], ind["sizing_params"] = new_z, new_p
        return
    space = SIZING.get(z, SIZING["equal"]).param_space
    out = dict(ind.get("sizing_params") or {})
    for k, spec in space.items():
        if rng.random() >= rate:
            continue
        if spec[0] in ("int", "float"):
            lo, hi = float(spec[1]), float(spec[2])
            cur = out.get(k, (lo + hi) / 2)
            new = cur + rng.gauss(0.0, sigma * (hi - lo))
            new = max(lo, min(hi, new))
            out[k] = int(round(new)) if spec[0] == "int" else round(new, 4)
        elif spec[0] == "choice":
            out[k] = rng.choice(list(spec[1]))
    ind["sizing_params"] = out


def sample_individual(rng: random.Random, prefer_family: str | None = None,
                      force_family: bool = False) -> dict:
    """随机个体；风格引擎提示族时 20% 概率偏向（因子专家审查#12：50%是族级追涨杀跌，
    会造成种群多样性周期性坍缩，降到20%且仅作提示不作主导）。
    force_family=True 时确定性生成指定族（移民族覆盖用：每族保底1个活体）。
    GP 基因组策略（evolved）走专用随机基因组生成器——结构级进化。"""
    if prefer_family and prefer_family in strat_lib.STRATEGIES \
            and (force_family or rng.random() < 0.2):
        name = prefer_family
    else:
        name = rng.choice(list(strat_lib.STRATEGIES))
    z, zp = _sample_sizing(rng)
    if name == "evolved":
        return {"strategy": name, "params": strat_lib.Evolved.random_genome(rng),
                "sizing": z, "sizing_params": zp}
    space = strat_lib.get_strategy(name).param_space
    params = {k: _sample_param(v, rng) for k, v in space.items()}
    return {"strategy": name, "params": strat_lib.sanitize_params(name, params),
            "sizing": z, "sizing_params": zp}


def crossover(a: dict, b: dict, rng: random.Random) -> dict:
    """参数级均匀交叉；跨策略不杂交（基因型不兼容），随机取一父本。
    evolved 基因组做原语列表单点交叉（结构级重组）；仓位基因同步交叉。"""
    if a["strategy"] == b["strategy"] == "evolved":
        child = {"strategy": "evolved",
                 "params": strat_lib.Evolved.crossover_genomes(a["params"], b["params"], rng)}
        child.update(_blend_sizing(a, b, rng))
        return child
    if a["strategy"] != b["strategy"]:
        return copy.deepcopy(a if rng.random() < 0.5 else b)  # 整组基因随父本（含仓位）
    child = {"strategy": a["strategy"],
             "params": {k: (a["params"][k] if rng.random() < 0.5 else b["params"][k])
                        for k in a["params"]}}
    child.update(_blend_sizing(a, b, rng))
    return child


def mutate(ind: dict, rng: random.Random, rate: float, sigma: float) -> dict:
    """高斯变异：int/float 在参数空间内做相对步长扰动，choice 随机重选；
    变异后过 sanitize_params 依赖约束（防 fast>slow 等病态区）。
    evolved 基因组走专用变异器（增/删/换原语 + 参数微调，结构级突变）。
    仓位控制基因同样参与变异（换仓位哲学或调仓位参数）。"""
    out = copy.deepcopy(ind)
    if out["strategy"] == "evolved":
        out["params"] = strat_lib.Evolved.mutate_genome(out["params"], rng, rate)
        _mutate_sizing(out, rng, rate, sigma)
        return out
    space = strat_lib.get_strategy(out["strategy"]).param_space
    for k, spec in space.items():
        if rng.random() >= rate:
            continue
        kind = spec[0]
        if kind in ("int", "float"):
            lo, hi = float(spec[1]), float(spec[2])
            new = out["params"][k] + rng.gauss(0.0, sigma * (hi - lo))
            new = max(lo, min(hi, new))
            out["params"][k] = int(round(new)) if kind == "int" else round(new, 4)
        elif kind == "choice":
            out["params"][k] = rng.choice(list(spec[1]))
    out["params"] = strat_lib.sanitize_params(out["strategy"], out["params"])
    _mutate_sizing(out, rng, rate, sigma)
    return out


def composite_score(m: dict, cfg: AppConfig) -> float:
    """复合适应度（因子专家审查#3防躺赢版）：Calmar 0.30 + Sharpe 0.15 + 胜率(拉普拉斯收缩) 0.10
    + 年化目标达成 0.25，再乘暴露系数（平均暴露<50%按比例打折，防低暴露低频躺赢）。

    胜率收缩：(wins+1)/(sells+2)，防小样本全胜虚高；
    低频惩罚按平仓回合数（sell_count≥min_trades）而非成交笔数。
    """
    e = cfg.evolve
    calmar = max(-3.0, min(3.0, m["calmar"]))
    sharpe = max(-2.0, min(2.0, m["sharpe"]))
    wins = int(m.get("wins", 0))
    sells = int(m.get("sell_count", 0))
    win = min(1.0, (wins + 1) / (sells + 2))  # 拉普拉斯收缩
    cagr = max(-1.0, min(1.5, m["cagr"]))
    target = max(0.05, float(getattr(e, "cagr_target", 0.20)))
    hit = max(0.0, min(1.5, cagr / target))
    s = 0.30 * (calmar + 3.0) / 6.0 + 0.15 * (sharpe + 2.0) / 4.0 \
        + 0.10 * win + 0.25 * hit
    # 暴露系数：空仓≈×0.5，暴露≥50%全额（低暴露策略必须靠真alpha取胜）
    expo = max(0.0, min(1.0, float(m.get("exposure", 0.0))))
    s *= 0.5 + 0.5 * min(1.0, expo / 0.5)
    if m["max_dd"] < -e.backtest_max_dd_penalty:
        s *= 0.5
    if sells < max(20, e.min_trades):
        s *= 0.6
    return float(s)


def _round_metrics(m: dict) -> dict:
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}


# ---------------------------------------------------------------- 并行评估（高频迭代）

_WORKER_CTX: dict = {}


def _worker_init(train_panel, slices, cfg):
    _WORKER_CTX["panel"] = train_panel
    _WORKER_CTX["slices"] = slices
    _WORKER_CTX["cfg"] = cfg


def _worker_fitness(ind: dict) -> tuple[float, dict, dict]:
    try:
        f, extra = evaluate_fitness(ind, _WORKER_CTX["panel"], _WORKER_CTX["slices"], _WORKER_CTX["cfg"])
        return f, ind, extra
    except Exception:  # noqa: BLE001 工人异常按淘汰处理
        return -1.0, ind, {}


def evaluate_fitness(ind: dict, train_panel, slices, cfg) -> tuple[float, dict]:
    """个体适应度（多时间片复合分均值）——纯函数，供串行/并行进程调用。

    本地能力累积：结果按（基因+窗口+口径指纹）写评估缓存；同一窗口/口径下
    重启后的种群恢复、经典种子重评、同类个体复评全部秒回，算力只花在新个体上。
    """
    key_ep = _eval_cache_key(ind, train_panel, slices, cfg)
    if key_ep:
        hit = _cache_get(key_ep[0])
        if hit is not None:
            return hit
    try:
        strat = strat_lib.get_strategy(ind["strategy"])()
        w = strat.target_weights(train_panel, ind["params"])
        sizing = get_sizing(ind.get("sizing") or "equal")()
        w = sizing.apply(w, train_panel, ind.get("sizing_params") or {})
    except Exception:  # noqa: BLE001
        return -1.0, {}
    scores = []
    mdds = []
    for s0, s1 in slices:
        sub = train_panel.window(s0, s1)
        res = run_backtest(sub, w, cfg)
        scores.append(composite_score(res.metrics, cfg))
        mdds.append(float(res.metrics["max_dd"]))
    # train_mdd=各切片最差回撤：晋升配额预筛用（训练期已超5%闸的个体不烧稀缺的
    # 每日样本外尝试）。只作元数据随缓存留存，不入适应度口径（_FITNESS_VERSION 不变）。
    out = (float(np.mean(scores)), {"slice_scores": [round(x, 4) for x in scores],
                                    "train_mdd": round(min(mdds), 4)})
    if key_ep and out[0] > -1.0:
        _cache_put(key_ep[0], out[0], out[1], key_ep[1])
    return out


class Evolver:
    def __init__(self, cfg: AppConfig, panel, state: dict | None = None, persist: bool = True):
        self.cfg = cfg
        self.panel = panel
        self.state = state if state is not None else load_state()
        self.persist = persist  # False=离线验证模式（walk-forward），不写线上 state.json
        e = cfg.evolve
        # 训练面板解耦（2026-09-21 用户"历史数据下全"配套）：面板已扩至25年，
        # GA/GPU 训练只用近 train_years 年——训练贴当下市场（进化探索方向），
        # 跨全历史广度考核由联赛随机窗承担。WF 传入的本来就是窗口末段切片，
        # 此切片保持其"用该段实盘前最近数据训练"的语义不变。
        ty = float(getattr(e, "train_years", 0) or 0)
        if ty > 0 and len(panel.dates) > int(ty * 252) + 120:
            _n = len(panel.dates)
            panel = panel.window(panel.dates[_n - max(260, int(ty * 252))],
                                 panel.dates[-1])
            self.panel = panel
        n = len(panel.dates)
        if n < 260:
            raise ValueError(f"历史数据过短（{n} 个交易日），无法切分训练/验证")
        hold_n = max(20, int(n * e.holdout_pct))
        self.holdout_dates = panel.dates[n - hold_n:]
        train_dates = panel.dates[: n - hold_n]
        # 预热段（因子专家审查#4）：指标预热全部落在切片前——权重在全训练段计算，
        # 但适应度只在预热之后的切片上打分，防"切片1必死拖垮均值/经典种子被结构性淘汰"
        warmup = min(300, max(0, len(train_dates) - 120))
        self.train_panel = panel.window(train_dates[0], train_dates[-1])  # 全量历史供指标预热
        usable = np.arange(warmup, len(train_dates))
        splits = np.array_split(usable, max(1, e.n_train_slices))
        self.slices = [(train_dates[s[0]], train_dates[s[-1]]) for s in splits if len(s) >= 60]
        if not self.slices:  # 极短历史兜底
            self.slices = [(train_dates[warmup // 2], train_dates[-1])]
        self.rng = random.Random()
        # 自适应机制状态（变异步长倍数、待注入移民数）与并行池
        self._sigma_boost = 1.0
        self._immigrants_pending = 0
        self._seat_genes: list[tuple[float, dict, dict]] = []  # 认证族保底席位代表
        self._pool = None
        self._pool_failed = False

    def _eval_many(self, inds: list[dict]) -> list[tuple[float, dict, dict]]:
        """批量适应度评估：多进程并行（0=自动按CPU核数拉满），失败自动回退串行。"""
        workers = resolve_workers(self.cfg)
        if (not self._pool_failed and self._pool is None and workers > 1
                and len(inds) >= max(2, workers)):
            try:
                self._pool = ProcessPoolExecutor(
                    max_workers=workers, initializer=_worker_init,
                    initargs=(self.train_panel, self.slices, self.cfg))
                log.info("【机制更新】并行评估已启动：%d 进程（32核机器自动拉满策略见 config.resolve_workers）", workers)
            except Exception as ex:  # noqa: BLE001
                log.warning("并行评估不可用，回退串行: %s", ex)
                self._pool_failed = True
        if self._pool is not None and not self._pool_failed and inds:
            try:
                return list(self._pool.map(_worker_fitness, inds))
            except Exception as ex:  # noqa: BLE001
                log.warning("并行评估异常，回退串行: %s", ex)
                self._pool_failed = True
                try:
                    self._pool.shutdown(wait=False)
                except Exception:  # noqa: BLE001
                    pass
                self._pool = None
        # 串行回退：统一输出 (score, ind, extra) 三元组（与并行口径一致）
        out: list[tuple[float, dict, dict]] = []
        for ind in inds:
            f, extra = self.fitness(ind)
            out.append((f, ind, extra))
        return out

    # -------------------------------------------------- 评估

    def _weights(self, ind: dict):
        strat = strat_lib.get_strategy(ind["strategy"])()
        return strat.target_weights(self.train_panel, ind["params"])

    def fitness(self, ind: dict) -> tuple[float, dict]:
        """多时间片复合分均值（每片独立起算）。异常个体记 -1 分自然淘汰。（走本地缓存）"""
        return evaluate_fitness(ind, self.train_panel, self.slices, self.cfg)

    def holdout_eval(self, ind: dict) -> tuple[float, dict]:
        """样本外评估：只用于晋升，绝不参与适应度。仓位基因与适应度口径一致。"""
        strat = strat_lib.get_strategy(ind["strategy"])()
        w_full = strat.target_weights(self.panel, ind["params"])
        sizing = get_sizing(ind.get("sizing") or "equal")()
        w_full = sizing.apply(w_full, self.panel, ind.get("sizing_params") or {})
        sub = self.panel.window(self.holdout_dates[0], self.holdout_dates[-1])
        res = run_backtest(sub, w_full, self.cfg)
        return composite_score(res.metrics, self.cfg), res.metrics

    # -------------------------------------------------- 主循环

    def run(self, generations: int | None = None, time_budget_s: float = 3600.0) -> dict:
        e = self.cfg.evolve
        gens = generations or e.generations
        st = self.state

        # 冠军衰退信号 → 大规模移民重启搜索（周度复盘置位，消费后清零）
        if st.get("meta", {}).get("champion_decay"):
            self._immigrants_pending = max(self._immigrants_pending, e.population // 2)
            st["meta"]["champion_decay"] = False
            log.warning("【机制更新】冠军衰退信号确认：本代注入 50%% 移民重启搜索")

        # 恢复精英池（无分数则重评）+ 经典模型种子注入（站在成功模型的起点上进化）
        hint = st.get("regime", {}).get("hint_family")  # 风格引擎提示：向当前最适族收敛
        evaluated: list[tuple[float, dict, dict]] = []
        restored = list(st["evolution"].get("population") or [])
        seeds = [copy.deepcopy(s) for s in GA_SEEDS]
        for f, ind, extra in self._eval_many(restored + seeds):
            evaluated.append((f, ind, extra))
        while len(evaluated) < e.population:
            ind = sample_individual(self.rng, prefer_family=hint)
            f, extra = self.fitness(ind)
            evaluated.append((f, ind, extra))
        evaluated.sort(key=lambda t: t[0], reverse=True)
        evaluated = evaluated[: e.population]

        # 认证族保底席位（2026-09-20 修复）：认证基因注入种群后按训练分竞争必然被
        # Top48 截尾淘汰（训练分口径≠部署样本外口径，防御族永远竞争不过强趋势族），
        # maybe_update_team 的 fam_best 因此永远看不到认证族 → 联赛认证→晋升管道断裂。
        # 每个有认证战绩的策略族保底 1 席，代表=该族联赛认证分最高的基因（随机窗
        # 战绩，非部署holdout分——不磨刷部署闸）；席位换掉最差个体，不挤占精英席。
        fam_seat: dict[str, dict] = {}
        for q in (st.get("arena") or {}).get("qualified") or []:
            fam = q.get("strategy")
            if not fam or fam not in strat_lib.STRATEGIES:
                continue
            cur = fam_seat.get(fam)
            if cur is None or float(q.get("score") or 0.0) > float(cur.get("score") or 0.0):
                fam_seat[fam] = {"strategy": fam, "params": dict(q.get("params") or {}),
                                 "sizing": q.get("sizing") or "equal",
                                 "sizing_params": dict(q.get("sizing_params") or {}),
                                 "score": q.get("score") or 0.0}
        self._seat_genes = []
        # 认证代表一律入池（修复#2）：联赛认证=随机窗实战战绩，是该族最强的晋升
        # 候选证据；不能因"族已有成员"（往往只是训练分高的种子/旧基因）而拒之门外。
        in_pool = [(ind["strategy"], ind.get("sizing") or "equal",
                    ind.get("params") or {}, ind.get("sizing_params") or {})
                   for _, ind, _ in evaluated]
        seat_need = [g for f, g in sorted(fam_seat.items())
                     if (g["strategy"], g.get("sizing") or "equal",
                         g.get("params") or {}, g.get("sizing_params") or {}) not in in_pool]
        if seat_need:
            for tup in self._eval_many(seat_need):
                if len(evaluated) >= e.population:
                    evaluated = evaluated[:max(e.elite, len(evaluated) - 1)]
                evaluated.append(tup)
                self._seat_genes.append(tup)
            evaluated.sort(key=lambda t: t[0], reverse=True)
            log.info("【机制更新】认证族保底席位 +%d：%s", len(seat_need),
                     ",".join(g["strategy"] for g in seat_need))

        t0 = time.time()
        for _ in range(gens):
            if time.time() - t0 > time_budget_s:
                log.info("达到时间预算，本批进化结束（累计第%d代）", st["evolution"]["generation"])
                break

            # —— 自适应机制①：移民注入（停滞/衰退时用新随机个体替换最差；风格提示族优先）——
            if self._immigrants_pending > 0:
                n_inj = min(self._immigrants_pending, max(0, e.population - e.elite))
                # 族覆盖式移民：首批每族各1个保证全体策略族都有活体进入种群评估
                # （随机移民在Top10单族化+分数悬殊下一代内即被淘汰，族覆盖+亲本池族配额
                #   才能真正恢复搜索空间——2026-09-20死锁修复）
                fams_all = list(strat_lib.STRATEGIES)
                fresh_inds = [sample_individual(self.rng, prefer_family=f, force_family=True)
                              for f in fams_all[:n_inj]]
                while len(fresh_inds) < n_inj:
                    fresh_inds.append(sample_individual(self.rng, prefer_family=hint))
                fresh = self._eval_many(fresh_inds)
                if n_inj >= len(evaluated):
                    evaluated = fresh
                else:
                    evaluated = evaluated[:-n_inj] + fresh
                evaluated.sort(key=lambda t: t[0], reverse=True)
                log.info("【机制更新】注入移民 %d 个（变异步长×%.1f）", n_inj, self._sigma_boost)
                self._immigrants_pending = 0
                st.setdefault("meta", {})["immigrants_total"] = \
                    int(st.get("meta", {}).get("immigrants_total", 0)) + int(n_inj)

            sigma_now = e.mutate_sigma * self._sigma_boost  # —— 自适应机制②：变异步长随停滞放大 ——
            # —— Top10 循环迭代：每代先选出前N名选手，看策略，再围绕它们繁殖精修 ——
            # 亲本池族配额（同族≤max_breed_family）：单族霸榜=搜索空间塌缩的稳态源头
            n_breed = min(e.top_breeders, len(evaluated))
            if e.max_breed_family > 0:
                breeders: list = []
                _fam_n: dict[str, int] = {}
                for t in evaluated:
                    if len(breeders) >= n_breed:
                        break
                    _fam = t[1]["strategy"]
                    if _fam_n.get(_fam, 0) >= e.max_breed_family:
                        continue
                    _fam_n[_fam] = _fam_n.get(_fam, 0) + 1
                    breeders.append(t)
            else:
                breeders = evaluated[:n_breed]  # 本轮前10名
            children: list[dict] = [copy.deepcopy(evaluated[i][1]) for i in range(e.elite)]
            n_slots = e.population - e.elite
            n_local = int(n_slots * e.local_refine_frac)  # Top10 邻域小步精修（循环迭代赢家）
            for _ in range(n_local):
                parent = copy.deepcopy(self.rng.choice(breeders)[1])
                children.append(mutate(parent, self.rng, e.mutate_rate,
                                       sigma_now * 0.4))  # 精修步长=常规40%
            while len(children) < e.population:
                a = self._tournament(breeders)   # 亲本只从前10名选手中抽（选择压力集中）
                b = self._tournament(breeders)
                child = crossover(a, b, self.rng) if self.rng.random() < e.crossover_rate else copy.deepcopy(a)
                children.append(mutate(child, self.rng, e.mutate_rate, sigma_now))
            new_eval = list(evaluated[: e.elite])
            new_eval += self._eval_many(children[e.elite:])  # 并行评估子代（迭代频率核心）
            new_eval.sort(key=lambda t: t[0], reverse=True)
            evaluated = new_eval[: e.population]

            # —— 看策略（自我观察留痕）：Top10 快照按(策略+参数)去重，用后续个体补位——
            # （GA 收敛时种群全是克隆，不去重会让可视化擂台显示一排相同小人）
            top10_snap: list[dict] = []
            _seen: set = set()
            for _f, _ind, _ in evaluated:
                if len(top10_snap) >= e.top_breeders:
                    break
                _key = (_ind["strategy"], json.dumps(_ind["params"], sort_keys=True, default=str))
                if _key in _seen:
                    continue
                _seen.add(_key)
                top10_snap.append({"strategy": _ind["strategy"], "score": round(_f, 4),
                                   "params": _ind["params"]})
            st["evolution"]["top10"] = top10_snap
            if st["evolution"]["generation"] % 10 == 0:
                fams: dict[str, int] = {}
                for t in top10_snap:
                    fams[t["strategy"]] = fams.get(t["strategy"], 0) + 1
                log.info("【Top10】%s", " ".join(f"{k}×{v}" for k, v in
                        sorted(fams.items(), key=lambda kv: -kv[1])))

            st["evolution"]["generation"] += 1
            best_f, best, best_extra = evaluated[0]
            rec = {"gen": st["evolution"]["generation"],
                   "time": dt.datetime.now().isoformat(timespec="seconds"),
                   "best_score": round(best_f, 4), "mean_score": round(float(np.mean([x[0] for x in evaluated])), 4),
                   "sigma_boost": round(self._sigma_boost, 2),
                   "best": {"strategy": best["strategy"], "params": best["params"]},
                   **best_extra}
            st["evolution"]["history"].append(rec)
            st["evolution"]["history"] = st["evolution"]["history"][-200:]
            log.info("第%d代 best=%.4f mean=%.4f [σ×%.1f] [%s]", rec["gen"], rec["best_score"],
                     rec["mean_score"], self._sigma_boost, best["strategy"])

            # —— 自适应机制③：停滞检测（近N代最优分无提升→放大变异+排队移民；突破→回落）——
            hist = [h["best_score"] for h in st["evolution"]["history"][-e.stagnation_gens:]]
            if len(hist) >= e.stagnation_gens:
                if max(hist) - min(hist) < 0.002:
                    self._sigma_boost = min(self._sigma_boost * 1.5, e.sigma_boost_max)
                    self._immigrants_pending = max(
                        self._immigrants_pending, int(e.population * e.immigrant_frac))
                    st.setdefault("meta", {})["stagnations_total"] = \
                        int(st.get("meta", {}).get("stagnations_total", 0)) + 1
                    log.info("【机制更新】进化停滞%d代：变异步长→×%.1f，下代注入移民",
                             e.stagnation_gens, self._sigma_boost)
                elif hist[-1] >= max(hist[:-1]) + 0.002:
                    self._sigma_boost = max(1.0, self._sigma_boost / 1.2)

            # 认证族席位巡检：席位基因被代内选择淘汰时，团队重组点前补位（换最差个体）
            if self._seat_genes:
                fams_now = {ind["strategy"] for _, ind, _ in evaluated}
                missing = [t for t in self._seat_genes
                           if t[1]["strategy"] not in fams_now]
                if missing:
                    for tup in missing:
                        if len(evaluated) >= e.population:
                            evaluated = evaluated[:max(e.elite, len(evaluated) - 1)]
                        evaluated.append(tup)
                    evaluated.sort(key=lambda t: t[0], reverse=True)
                    log.info("【机制更新】认证族席位补位 %d 个（团队重组前）", len(missing))

            if st["evolution"]["generation"] % self.cfg.meta.team_update_gens == 0:
                self.maybe_update_team(evaluated)

            st["evolution"]["population"] = [copy.deepcopy(ind) for _, ind, _ in evaluated]
            st["evolution"]["last_run"] = rec["time"]
            if self.persist:
                save_state(st)

        best_f, best, _ = evaluated[0]
        return {"score": best_f, "individual": best}

    def _tournament(self, pool) -> dict:
        """锦标赛选择：只从传入池（Top10 亲本池）中抽 k 个取最优。"""
        e = self.cfg.evolve
        cands = self.rng.sample(pool, min(e.tournament_k, len(pool)))
        return copy.deepcopy(max(cands, key=lambda t: t[0])[1])

    def close(self) -> None:
        """释放并行评估进程池。"""
        if self._pool is not None:
            try:
                self._pool.shutdown(wait=True)
            except Exception:  # noqa: BLE001
                pass
            self._pool = None

    # -------------------------------------------------- 冠军团队（资产组合）

    def _ind_asset_class(self, ind: dict) -> str:
        """候选资产类别：末行权重含非零 F.* → 'fut'；含非零股票/ETF → 'stock'；
        两者同持 → 'mixed'（团队组建禁入——联合回测分流层对混合按空仓计，防错撮合）。"""
        try:
            from .futures import is_futures
            w = strat_lib.get_strategy(ind["strategy"])().target_weights(
                self.train_panel, ind["params"]).astype(float)
            sizer = get_sizing(ind.get("sizing") or "equal")()
            w = sizer.apply(w, self.train_panel, ind.get("sizing_params") or {})
            last = w.iloc[-1]
            has_fut = any(is_futures(c) and float(v) != 0.0 for c, v in last.items())
            has_stk = any((not is_futures(c)) and float(v) != 0.0 for c, v in last.items())
            if has_fut and has_stk:
                return "mixed"
            return "fut" if has_fut else "stock"
        except Exception:  # noqa: BLE001 评估失败按股票类（最保守默认）
            return "stock"

    def maybe_update_team(self, evaluated) -> list | None:
        """冠军团队 = 资产组合：各族最优个体做样本外验证，前 team_size 个不同族组队，
        资金均分。换队条件：新团队平均样本外分 > 现任平均×(1+margin)。

        样本外磨刷保护：holdout 每天只允许被"尝试"N次（各族各一次）。
        每成员须过 team_member_floor 绝对门槛——过不了该族宁缺毋滥。
        """
        st = self.state
        e = self.cfg.evolve
        mc = self.cfg.meta
        evo = st["evolution"]
        today_key = dt.date.today().strftime("%Y%m%d")
        if evo.get("promote_date") != today_key:
            evo["promote_date"] = today_key
            evo["promote_count"] = 0

        # 各策略族代表（配额预筛版）：训练期最差回撤已超部署闸的个体不再送样本外
        # ——每日晋升尝试上限是稀缺资源，不烧给注定撞5%闸的满仓型候选。
        # 达标个体族内最高分优先；无 train_mdd 数据（旧评估缓存）的个体作兼容兜底；
        # 全族仅见超标个体 → 跳过该族（省配额）并留痕。
        dd_gate = float(mc.team_member_max_dd or 0.0)
        fam_fit: dict[str, tuple] = {}   # 训练期回撤达标（或闸禁用）
        fam_lax: dict[str, tuple] = {}   # 无 train_mdd 数据（旧缓存兼容）
        fam_worst: dict[str, float] = {}  # 各族被预筛拦下的最差回撤（留痕）
        for f, ind, extra in evaluated:
            fam = ind["strategy"]
            mdd = (extra or {}).get("train_mdd")
            mdd = float(mdd) if mdd is not None else None
            if mdd is not None and dd_gate > 0 and mdd < -dd_gate:
                fam_worst[fam] = min(fam_worst.get(fam, 0.0), mdd)
                continue
            tgt = fam_fit if (mdd is not None or dd_gate <= 0) else fam_lax
            cur = tgt.get(fam)
            if cur is None or f > cur[0]:
                tgt[fam] = (f, ind)
        fam_best: dict[str, tuple] = {**fam_lax, **fam_fit}  # 达标个体优先覆盖兜底
        skipped = sorted(f for f in fam_worst if f not in fam_best)
        if skipped:
            log.info("族级预筛跳过 %d/%d 族（训练期回撤全超%.0f%%闸，省配额不送样本外）：%s",
                     len(skipped), len(skipped) + len(fam_best), dd_gate * 100,
                     ", ".join(f"{k}({fam_worst[k] * 100:.0f}%)" for k in skipped[:10]))
        # 认证代表优先参选（修复#2）：认证=随机窗实战战绩，晋升候选按实战证据优先于
        # 训练分（训练分口径与部署闸背离，认证基因屡在族内训练分竞争中被埋没）。
        # 席位代表的 train_mdd 仍受上面预筛约束（超闸族照旧不烧配额）。
        if self._seat_genes:
            for _t in self._seat_genes:
                _fam = _t[1]["strategy"]
                if _fam not in fam_best:
                    continue
                _mdd_s = (_t[2] or {}).get("train_mdd")
                if _mdd_s is not None and dd_gate > 0 and float(_mdd_s) < -dd_gate:
                    continue
                fam_best[_fam] = (_t[0], _t[1])
        if not fam_best:
            return None

        scored: list[tuple[float, dict, dict]] = []
        _attempted = 0
        for fam, (_f, ind) in fam_best.items():
            if evo.get("promote_count", 0) >= e.max_promote_attempts_per_day:
                if _attempted:
                    log.info("【晋升】今日配额用尽（%d/%d），其余家族明日再试",
                             evo["promote_count"], e.max_promote_attempts_per_day)
                break
            evo["promote_count"] = int(evo.get("promote_count", 0)) + 1
            _attempted += 1
            try:
                score, metrics = self.holdout_eval(ind)
                scored.append((score, ind, metrics))
            except Exception:  # noqa: BLE001
                log.exception("候选成员 %s 样本外评估异常（按落选处理）", ind["strategy"])
                continue
        scored.sort(key=lambda t: t[0], reverse=True)

        # 成员遴选：样本外分门槛 + 随机取点压力闸（历史任意窗口均分达标且过半跑赢持币；
        # 防止"恰好适配固定切分"的成员上位；多备2人过闸补位，宁缺毋滥）
        members = []
        team_class: str | None = None
        for score, ind, metrics in scored[: mc.team_size + 2]:
            # 团队同资产类别约束（2026-09-21 全品种指令）：一队要么纯股票/ETF、
            # 要么纯期货——混合权重的联合体检/回测按空仓计（backtest 分流层），
            # 混合候选禁入；跨类别整体换队（股票队↔期货队）合法。
            cls = self._ind_asset_class(ind)
            if cls == "mixed":
                log.info("候选 %s 为混合权重（股票+期货同持）→ 联合回测不支持，禁入团队",
                         ind["strategy"])
                continue
            if team_class is not None and cls != team_class:
                log.info("候选 %s 资产类别(%s)≠团队(%s) → 同类别约束跳过",
                         ind["strategy"], cls, team_class)
                continue
            if score < mc.team_member_floor:
                log.info("【晋升】候选 %s 样本外分 %.3f < 门槛 %.2f → 落选",
                         ind["strategy"], score, mc.team_member_floor)
                continue
            # 回撤硬约束（用户确认）：成员样本外最大回撤 ≤ 停机线一半，否则否决。
            # 防止选出"会被自己的实盘风控枪毙"的冠军。
            mdd = float(metrics.get("max_dd", 0.0) or 0.0)
            if mc.team_member_max_dd > 0 and mdd < -mc.team_member_max_dd:
                log.info("候选成员 %s 样本外回撤 %.1f%% 超硬约束 %.1f%% → 否决",
                         ind["strategy"], mdd * 100, mc.team_member_max_dd * 100)
                continue
            try:
                ok, ss = _member_stress_gate(ind, self.train_panel, self.cfg)
            except Exception as ex:  # noqa: BLE001 闸异常按不过处理，但必须留痕可审计
                log.exception("候选成员 %s 随机取点闸异常（按不过处理）: %s", ind["strategy"], ex)
                ok, ss = False, {}
            if not ok:
                log.info("候选成员 %s 未过随机取点闸: %s", ind["strategy"], ss)
                continue
            members.append({"strategy": ind["strategy"], "params": ind["params"],
                            "sizing": ind.get("sizing") or "equal",
                            "sizing_params": dict(ind.get("sizing_params") or {}),
                            "holdout": {"score": round(score, 4), "metrics": _round_metrics(metrics)},
                            "stress": ss})
            team_class = team_class or cls
            if len(members) >= mc.team_size:
                break
        if not members:
            if scored:
                log.info("【晋升】第%d代重组无成员过全部门检：候选%d人 最高分 %.3f(%s) → 宁缺毋滥保持现状",
                         st["evolution"]["generation"], len(scored), scored[0][0],
                         scored[0][1]["strategy"])
            return None
        new_avg = sum(m["holdout"]["score"] for m in members) / len(members)

        old = st.get("team") or []
        # 红线一致性复检（用户确认的硬约束）：现任成员样本外回撤超停机线一半即清退；
        # 全员违规 → 团队整体退休、空仓等待新合规团队（宁缺毋滥）。
        if old and mc.team_member_max_dd > 0:
            kept = []
            for m in old:
                mdd = float((m.get("holdout") or {}).get("metrics", {}).get("max_dd", 0.0) or 0.0)
                if mdd < -mc.team_member_max_dd:
                    log.warning("现任成员 %s 样本外回撤 %.1f%% 超硬约束 %.1f%% → 清退",
                                m.get("strategy"), mdd * 100, mc.team_member_max_dd * 100)
                else:
                    kept.append(m)
            if len(kept) != len(old):
                if kept:
                    st["team"] = kept
                    if st.get("champion") and st["champion"].get("strategy") not in \
                            [k.get("strategy") for k in kept]:
                        st["champion"] = {**kept[0],
                                          "team_avg": round(sum(float((k.get("holdout") or {}).get("score", 0) or 0)
                                                                for k in kept) / len(kept), 4),
                                          "promoted_at": dt.datetime.now().isoformat(timespec="seconds"),
                                          "gen": st["evolution"]["generation"]}
                else:
                    st["champion_retired"].append({
                        "leader": old[0].get("strategy"),
                        "members": [m.get("strategy") for m in old],
                        "retired_at": dt.datetime.now().isoformat(timespec="seconds"),
                        "reason": f"样本外回撤超硬约束{mc.team_member_max_dd:.0%}（用户确认的红线一致性）"})
                    st["team"] = []
                    st["champion"] = None
                    log.warning("现任团队全员违反回撤硬约束 → 整体退休，空仓等待新合规团队")
                if self.persist:
                    save_state(st)
                old = st.get("team") or []
        if old:
            # 现任团队先在当前 holdout 窗口重评（因子专家审查#5：
            # 陈值跨行情窗口不可比——牛市窗口轻松换掉熊市窗口上任是系统性偏置）
            # 防降级换血（2026-09-21 实战首日取证修复）：重评需要配额，配额不足时
            # 必须整轮放弃——绝不能让 old_scores 落空归零把闸门砸开（凌晨实测：
            # 配额烧尽后 old_avg=0 → 任何新团队都"优于"现任 → 9分钟6次降级换血，
            # 0.871 团队被 0.399 垃圾顶掉）；重评异常同理用原分，不让异常放行换血。
            quota_left = e.max_promote_attempts_per_day - int(evo.get("promote_count", 0) or 0)
            if quota_left < len(old):
                log.info("【晋升】配额余 %d 不足以重评现任 %d 人 → 本轮放弃（防降级换血，明日再战）",
                         quota_left, len(old))
                return None
            old_scores: list[float] = []
            for m in old:
                evo["promote_count"] = int(evo.get("promote_count", 0)) + 1
                try:
                    s, _ = self.holdout_eval({"strategy": m["strategy"], "params": m["params"],
                                              "sizing": m.get("sizing") or "equal",
                                              "sizing_params": m.get("sizing_params") or {}})
                    m.setdefault("holdout", {})["score"] = round(s, 4)  # 刷新为当前窗口口径
                    old_scores.append(s)
                except Exception:  # noqa: BLE001 异常用原分——绝不让异常把闸门砸开
                    log.exception("现任成员 %s 样本外重评异常（用原分 %.4f 防闸门失效）",
                                  m.get("strategy"),
                                  float((m.get("holdout") or {}).get("score", 0) or 0.0))
                    old_scores.append(float((m.get("holdout") or {}).get("score", 0) or 0.0))
            old_avg = sum(old_scores) / len(old_scores) if old_scores else 0.0
            if new_avg < max(old_avg * (1.0 + e.promotion_margin), old_avg + 0.02):
                log.info("【晋升】新团队均分 %.4f 未超现任 %.4f → 现任留任", new_avg, old_avg)
                return None
            st["champion_retired"].append({
                "leader": old[0].get("strategy"), "team_avg": round(old_avg, 4),
                "members": [m.get("strategy") for m in old],
                "retired_at": dt.datetime.now().isoformat(timespec="seconds")})
            st["champion_retired"] = st["champion_retired"][-20:]

        st["team"] = members
        st["champion"] = {**members[0], "team_avg": round(new_avg, 4),
                          "promoted_at": dt.datetime.now().isoformat(timespec="seconds"),
                          "gen": st["evolution"]["generation"]}
        st.setdefault("meta", {})["promotions_total"] = \
            int(st.get("meta", {}).get("promotions_total", 0)) + 1
        # 新团队通过全部门检上位 → 解除随机取点防御态（次日照常体检复核）
        st.setdefault("meta", {})["stress_defense"] = False
        log.info("★ 冠军团队组建/换血: %s 平均样本外分 %.4f",
                 [m["strategy"] for m in members], new_avg)
        if self.persist:
            save_state(st)
        return members


# ---------------------------------------------------------------- 随机取点验证

def _random_window_scores_for_weights(w, panel, cfg, rng,
                                      n_windows: int, min_len: int, max_len: int) -> list[float]:
    """给定权重矩阵，在历史随机(起点,长度)窗口逐一全规则撮合打分。"""
    dates = list(panel.dates)
    n = len(dates)
    max_len = min(max_len, n - 2)
    min_len = max(10, min(min_len, max_len))
    scores = []
    for _ in range(n_windows):
        length = rng.randint(min_len, max_len)
        start = rng.randint(0, n - length - 1)
        sub = panel.window(dates[start], dates[start + length - 1])
        res = run_backtest(sub, w, cfg)
        scores.append(composite_score(res.metrics, cfg))
    return scores


def _member_stress_gate(ind: dict, panel, cfg, seed: int | None = None) -> tuple[bool, dict]:
    """晋升闸·随机取点：成员须在历史随机窗口上均分达标且过半窗口跑赢持币。
    仓位基因同样叠加（与适应度/样本外/实盘口径一致）。"""
    import random as _random
    mc = cfg.meta
    strat = strat_lib.get_strategy(ind["strategy"])()
    w = strat.target_weights(panel, ind["params"]).astype(float)
    sizing = get_sizing(ind.get("sizing") or "equal")()
    w = sizing.apply(w, panel, ind.get("sizing_params") or {}).astype(float)
    rng = _random.Random(seed)
    scores = _random_window_scores_for_weights(
        w, panel, cfg, rng,
        n_windows=int(getattr(mc, "team_stress_windows", 16)),
        min_len=int(getattr(mc, "stress_min_len", 20)),
        max_len=int(getattr(mc, "stress_max_len", 60)))
    arr = np.array(scores)
    beat = float((arr > float(getattr(mc, "stress_beat_cash", 0.15))).mean())
    summary = {"mean": round(float(arr.mean()), 4), "beat_cash_pct": round(beat, 4),
               "worst": round(float(arr.min()), 4), "windows": len(scores)}
    ok = (summary["mean"] >= float(getattr(mc, "stress_min_mean", 0.25))
          and beat >= float(getattr(mc, "stress_min_beat_pct", 0.5)))
    return bool(ok), summary


def random_point_test(cfg: AppConfig, state: dict, panel, n_windows: int | None = None,
                      seed: int | None = None) -> dict:
    """历史数据随机取点验证模型（团队每日体检 + CLI 手动验证）。

    随机抽取 (起点, 长度) 窗口，用当前冠军团队合成权重做全规则撮合，
    与持币基线、股票池等权基准对比——模型必须经受任意行情段的检验。
    纯只读函数：不写 state。
    """
    import random as _random

    from .backtest import equal_weight_benchmark
    from .decide import team_members, team_target_weights

    mc = cfg.meta
    n_windows = int(n_windows or getattr(mc, "stress_windows", 24))
    members = team_members(state)
    if not members:
        raise RuntimeError("暂无冠军团队，无法随机取点验证")
    w = team_target_weights(cfg, state, panel).astype(float)
    rng = _random.Random(seed)

    dates = list(panel.dates)
    n = len(dates)
    max_len = min(int(getattr(mc, "stress_max_len", 60)), n - 2)
    min_len = max(10, min(int(getattr(mc, "stress_min_len", 20)), max_len))
    beat_line = float(getattr(mc, "stress_beat_cash", 0.15))

    scores, details = [], []
    for _ in range(n_windows):
        length = rng.randint(min_len, max_len)
        start = rng.randint(0, n - length - 1)
        sub = panel.window(dates[start], dates[start + length - 1])
        res = run_backtest(sub, w, cfg)
        bench = equal_weight_benchmark(sub, cfg.risk.initial_capital)
        s = composite_score(res.metrics, cfg)
        scores.append(s)
        details.append({
            "window": f"{dates[start].date()}~{dates[start + length - 1].date()}",
            "score": round(float(s), 4),
            "ret": round(float(res.metrics["total_return"]), 4),
            "bench": round(float(bench.iloc[-1] / bench.iloc[0] - 1.0), 4),
            "max_dd": round(float(res.metrics["max_dd"]), 4),
        })
    arr = np.array(scores)
    summary = {
        "mean": round(float(arr.mean()), 4),
        "std": round(float(arr.std()), 4),
        "beat_cash_pct": round(float((arr > beat_line).mean()), 4),
        "beat_bench_pct": round(sum(1 for d in details if d["ret"] > d["bench"]) / len(details), 4),
        "worst": round(float(arr.min()), 4),
        "best": round(float(arr.max()), 4),
        "windows": n_windows,
    }
    return {"scores": scores, "details": details, "summary": summary,
            "members": [m.get("strategy") for m in members]}


# ---------------------------------------------------------------- walk-forward 链式验证

def walk_forward(cfg: AppConfig, n_windows: int | None = None, gens: int | None = None,
                 live_days: int = 42) -> dict:
    """链式滚动验证——把历史数据当实盘。

    每个窗口严格时序：只用窗口前数据进化 → 各族组队（在训练段内部holdout验证）
    → 下一段约2个月当实盘全规则撮合（T+1/涨跌停/费用/2周上限/滑点分档全生效）
    → 权益滚动衔接下一段。全程无未来数据；进化用临时状态，不污染线上 state。
    """
    import os as _os

    import pandas as pd

    from . import data as qdata
    from .backtest import equal_weight_benchmark, run_backtest
    from .config import LOGS_DIR
    from .state import DEFAULT_STATE

    mc = cfg.meta
    n_windows = n_windows or mc.wf_windows
    gens = gens or mc.wf_gens
    _, panel = qdata.full_panel(cfg)
    dates = list(panel.dates)
    n = len(dates)

    windows = []
    end = n
    for _ in range(n_windows):
        if end - live_days < 500 + 60:  # 训练数据不足则停止
            break
        windows.append((end - live_days, end))
        end -= live_days
    windows.reverse()
    if not windows:
        raise RuntimeError("历史数据不足以切分 walk-forward 窗口")

    equity = float(cfg.risk.initial_capital)
    segs = []
    equity_curve = []
    for live_start, live_end in windows:
        train_panel = panel.window(dates[0], dates[live_start - 1])
        tmp = copy.deepcopy(DEFAULT_STATE)  # 临时状态：进化/组队不写盘
        ev = Evolver(cfg, train_panel, tmp, persist=False)
        try:
            ev.run(generations=gens, time_budget_s=900)
            # 用最终种群按族组队（保留extra供族级回撤预筛——WF空仓与线上同病灶）
            evaluated = []
            for ind in tmp["evolution"]["population"]:
                f, extra = ev.fitness(ind)
                evaluated.append((f, ind, extra or {}))
            evaluated.sort(key=lambda t: t[0], reverse=True)
            # 最终组队无果时保留窗内中期已组建的团队：`or []` 会把真实团队清成
            # 空仓，导致 WF 报告系统性低估（2026-09-21 修复）
            team = ev.maybe_update_team(evaluated) or (tmp.get("team") or [])
        finally:
            ev.close()

        live_panel = panel.window(dates[live_start], dates[live_end - 1])
        start_eq, end_eq, strat_names = equity, equity, ["空仓(无合格团队)"]
        if team:
            calc_panel = panel.window(dates[0], dates[live_end - 1])
            wsum = None
            for m in team:
                w_m = strat_lib.get_strategy(m["strategy"])().target_weights(calc_panel, m["params"]).astype(float)
                wsum = w_m if wsum is None else wsum + w_m
            wsum = wsum / len(team)
            res = run_backtest(live_panel, wsum, cfg, start_cash=equity)
            end_eq = float(res.equity.iloc[-1])
            strat_names = [m["strategy"] for m in team]
            equity_curve.append(res.equity)
        else:
            equity_curve.append(pd.Series(equity, index=live_panel.dates))
        segs.append({"window": f"{dates[live_start].date()}~{dates[live_end - 1].date()}",
                     "team": strat_names, "start": round(start_eq, 0), "end": round(end_eq, 0),
                     "ret": end_eq / start_eq - 1.0})
        equity = end_eq
        log.info("[WF] %s 团队=%s 段收益 %+.2f%%（权益 %.0f）",
                 segs[-1]["window"], strat_names, segs[-1]["ret"] * 100, equity)

    total_ret = equity / cfg.risk.initial_capital - 1.0
    years = (len(windows) * live_days) / 252.0
    cagr = (equity / cfg.risk.initial_capital) ** (1.0 / years) - 1.0 if years > 0 else 0.0

    bench_seg = equal_weight_benchmark(panel.window(dates[windows[0][0]], dates[-1]),
                                       cfg.risk.initial_capital)
    bench_ret = float(bench_seg.iloc[-1] / bench_seg.iloc[0] - 1.0)

    lines = ["# Walk-Forward 链式验证报告（历史当实盘，无未来数据）",
             f"- 生成: {dt.datetime.now():%Y-%m-%d %H:%M} | 窗口 {len(windows)} 段 × {live_days} 交易日",
             f"- 每窗进化 {gens} 代（只用窗口前数据）→ 按族组队 → 下一段当实盘全规则撮合",
             "",
             "| 窗口 | 团队 | 段收益 | 期末权益 |", "|---|---|---|---|"]
    for s in segs:
        lines.append(f"| {s['window']} | {'+'.join(s['team'])} | {s['ret']*100:+.2f}% | {s['end']:,.0f} |")
    lines += ["",
              f"**链式总收益 {total_ret*100:+.2f}% | 年化 {cagr*100:+.2f}% | "
              f"等权基准同期 {bench_ret*100:+.2f}%**",
              "",
              "口径说明：段与段之间权益衔接；团队在每段开始前定型；样本外闸门/风控/费用/滑点分档全部生效。",
              "该结果是历史模拟，不构成未来收益承诺。"]
    _os.makedirs(LOGS_DIR, exist_ok=True)
    path = _os.path.join(LOGS_DIR, f"walkforward_{dt.date.today().strftime('%Y%m%d')}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    log.info("walk-forward 完成 → %s", path)
    return {"segments": segs, "total_return": total_ret, "cagr": cagr, "report": path}
