"""GPU 海选引擎（RTX 4070 SUPER）：万级参数广域筛查。

定位（三层漏斗第一层）：
  GPU 海选（本模块，近似成本模型，~300个体/秒）
    → GA 精修（精确适应度 + 16核并行 + SQLite评估缓存）
      → 样本外/随机取点/联赛闸门（唯一裁决者，GPU 分数不参与任何闸门）

范围：只移植"排名/轮动族"信号（momentum/low_vol/multifactor/dual_momentum/
vol_mom/rotation_28，纯滚动+横截面排名数学）；状态机型族由 CPU GA 探索。

简化口径（仅候选排序用）：换手×双边成本率近似（股票0.45%/ETF0.30%），
不仿真 T+1/涨跌停/止损——所有产出候选必须重过 CPU 精确引擎才能进种群。
GPU 不可用时本模块整体自动跳过，主流程零影响。
"""
from __future__ import annotations

import logging
import random

import numpy as np

from . import strategies as strat_lib
from .config import AppConfig
from .data import PanelData, is_etf

log = logging.getLogger("quant.gpu")

_TORCH_OK: bool | None = None
_DEV = None  # 缓存的 torch.device


def gpu_available() -> bool:
    """torch+CUDA 探测（一次后缓存；任何失败都不影响主流程）。"""
    global _TORCH_OK, _DEV
    if _TORCH_OK is not None:
        return _TORCH_OK
    try:
        import torch  # noqa: PLC0415
        if torch.cuda.is_available():
            _DEV = torch.device("cuda")
            _TORCH_OK = True
            log.info("GPU 海选就绪: %s（%.1f GB）", torch.cuda.get_device_name(0),
                     torch.cuda.get_device_properties(0).total_memory / 1e9)
        else:
            _TORCH_OK = False
            log.info("torch 可导入但无 CUDA 设备：GPU 海选停用（CPU GA 照常）")
    except Exception as e:  # noqa: BLE001
        _TORCH_OK = False
        log.info("GPU 海选不可用（%s）：自动跳过", e)
    return _TORCH_OK


SCREEN_FAMILIES = ["momentum", "low_vol", "multifactor", "dual_momentum", "vol_mom",
                   "rotation_28", "sector_momentum", "small_reversal"]

_HS300_ETFS = ["510300", "510310", "159919"]
_ZZ500_ETFS = ["510500", "512500", "159619", "560010"]


def sample_grid(family: str, n: int, rng: random.Random) -> list[dict]:
    """参数空间均匀采样 n 组（自动去重：小空间如 rotation_28 不会浪费重复采样）。"""
    space = strat_lib.get_strategy(family).param_space
    out: list[dict] = []
    seen: set[str] = set()
    for _ in range(n * 2):
        if len(out) >= n:
            break
        p = {}
        for k, spec in space.items():
            if spec[0] == "int":
                p[k] = int(rng.randint(int(spec[1]), int(spec[2])))
            elif spec[0] == "float":
                p[k] = round(float(rng.uniform(spec[1], spec[2])), 4)
            else:
                p[k] = rng.choice(list(spec[1]))
        key = json_key(p)
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


# ---------------------------------------------------------------- 信号原语（单个体）

def _shift_ratio(C, den_lag: int, num_lag: int):
    """out[t] = C[t-num_lag]/C[t-den_lag] - 1（与 pandas shift(s)/shift(s+lb)-1 同口径）。

    行 t 的分子索引 = t-num_lag → 切片 C[den_lag-num_lag : D-num_lag]
    行 t 的分母索引 = t-den_lag   → 切片 C[0 : D-den_lag]
    """
    import torch
    out = torch.full_like(C, float("nan"))
    D = C.shape[0]
    if den_lag > num_lag >= 0 and den_lag < D:
        out[den_lag:] = C[den_lag - num_lag: D - num_lag] / C[0: D - den_lag] - 1.0
    return out


def _roll_mean_t(C, w: int, min_periods: int | None = None):
    """NaN 感知滚动均值（默认 min_periods=w；停牌股不得贡献 0 值拉低统计）。"""
    import torch
    D = C.shape[0]
    mp = w if min_periods is None else max(1, min_periods)
    valid = torch.isfinite(C).float()
    x = torch.nan_to_num(C, nan=0.0)
    cs = torch.cumsum(x, dim=0)
    cv = torch.cumsum(valid, dim=0)
    out = torch.full_like(C, float("nan"))
    if w < D:
        s = cs[w:] - cs[:-w]
        v = cv[w:] - cv[:-w]
        out[w:] = torch.where(v >= mp, s / v.clamp_min(1.0),
                              torch.full_like(s, float("nan")))
    return out


def _daily_returns(C):
    """(D,M) 日收益，首行 NaN；价格 NaN 传导为 NaN（停牌不产生假收益）。"""
    import torch
    out = torch.full_like(C, float("nan"))
    out[1:] = C[1:] / C[:-1] - 1.0
    return out


def _ann_vol_t(C, w: int):
    """年化波动率：收益率序列滚动std×√252（与 ind.ann_vol 同口径，非价格std）。"""
    import torch
    return _roll_std_t(_daily_returns(C), w) * (252.0 ** 0.5)


def _roll_std_t(C, w: int):
    """NaN 感知滚动标准差（E[x²]-E[x]²，min_periods=w）。"""
    import torch
    e1 = _roll_mean_t(C, w)
    e2 = _roll_mean_t(C * C, w)
    var = (e2 - e1 * e1).clamp_min(0.0)
    return torch.where(torch.isfinite(var), torch.sqrt(var),
                       torch.full_like(var, float("nan")))


def _topk_mask(score, top_k: int):
    """(D,M) 逐日横截面 top_k 布尔（NaN 不可选）。"""
    import torch
    s = torch.nan_to_num(score, nan=-1e9)
    k = max(1, min(top_k, s.shape[-1]))
    v = torch.topk(s, k, dim=-1).values
    return (s >= v[..., -1:]) & torch.isfinite(score)


_ANCHOR_CACHE: dict = {}


def _rebal_anchors(dates, step: int) -> np.ndarray:
    """ISO 周锚定调仓日（与 strategies._rebalance_series 逐字同口径，结果缓存）。"""
    import pandas as pd
    key = (id(dates), int(step))
    if key in _ANCHOR_CACHE:
        return _ANCHOR_CACHE[key]
    iso = pd.Index(dates).isocalendar()
    wk = np.asarray(iso.week, dtype=np.int64)
    weeks = max(1, int(round(step / 5.0)))
    first_of_week = np.r_[True, np.diff(wk) != 0]
    anchors = np.nonzero(first_of_week & (wk % weeks == 0))[0]
    _ANCHOR_CACHE[key] = anchors
    return anchors


def _rebal_expand_iso(sel, dates, step: int):
    """锚点日选择 → 前向展开到下一锚点（首锚点前为空仓，与 pandas where+ffill 一致）。"""
    import torch
    D = sel.shape[0]
    anchors = _rebal_anchors(dates, step)
    pos = np.searchsorted(anchors, np.arange(D), side="right") - 1
    src = np.where(pos >= 0, anchors[np.clip(pos, 0, None)], 0)
    out = sel[torch.from_numpy(src).to(sel.device)].clone()
    if (pos < 0).any():
        out[torch.from_numpy(np.nonzero(pos < 0)[0]).to(sel.device)] = False
    return out


def _pct_rank(x):
    """逐日横截面百分位排名 (D,M)；平局取平均秩（与 pandas rank(pct=True) 同序）。

    NaN → NaN（与 pandas rank 一致：NaN 分量使合成分 NaN，该标的被排除，而非记 0 分参选）。
    """
    import torch
    valid = torch.isfinite(x)
    s = torch.where(valid, x, torch.full_like(x, -1e9))
    n = valid.sum(dim=-1, keepdim=True).float().clamp_min(1.0)
    b = s.unsqueeze(-2)   # (D, M, 1)：第 j 个值
    a = s.unsqueeze(-1)   # (D, 1, M)：第 i 个值
    less = (b < a).float().sum(dim=-1)          # #{j: s_j < s_i}
    eq = (b == a).float().sum(dim=-1)           # #{j: s_j == s_i}（含自身）
    rank = less + 0.5 * eq                      # 平均秩（同值同秩）
    out = torch.where(valid, rank / n,
                      torch.full_like(rank, float("nan")))
    return out


def _weights_one(fam: str, p: dict, C, D, M, etf_cols, hs_idx, zz_idx, is_etf_t, dates=None):
    """单个体权重 (D,M) torch（排名族）。dates 用于 ISO 周锚定调仓（与 pandas 同口径）。"""
    import torch
    if fam == "momentum":
        skip = int(p.get("skip_days", 0))
        mom = _shift_ratio(C, int(p["lookback"]) + skip, skip)
        sel = _topk_mask(mom, int(p["top_k"]))
        sel = _rebal_expand_iso(sel, dates, int(p["rebal_days"]))
        w = sel.float() / float(p["top_k"])
        L = int(p.get("ma_filter_len", 0))
        if 2 < L < D:
            # 等权指数（与 ind.universe_index 同构）：NaN 感知日收益均值累乘
            ret = _daily_returns(C)
            valid = torch.isfinite(ret).float()
            rmean = (torch.nan_to_num(ret, nan=0.0).sum(dim=-1)
                     / valid.sum(dim=-1).clamp_min(1.0))
            eq = torch.zeros(D, device=C.device)
            eq[1:] = rmean[1:]
            eq = torch.cumprod(1.0 + eq, dim=0)
            # pandas 口径：rolling(L, min_periods=1) → 预热期即生效
            ma = _roll_mean_t(eq.unsqueeze(1), L, min_periods=1).squeeze(1)
            gate = torch.nan_to_num((eq > ma), nan=0.0)
            w = w * gate.view(D, 1).float()
        return w
    if fam == "low_vol":
        sel = _topk_mask(-_ann_vol_t(C, int(p["vol_win"])), int(p["top_k"]))
        sel = _rebal_expand_iso(sel, dates, int(p["rebal_days"]))
        return sel.float() / float(p["top_k"])
    if fam == "multifactor":
        mom = _shift_ratio(C, int(p["lookback"]), 0)
        rev = _shift_ratio(C, 5, 0)
        vol = _ann_vol_t(C, 60)
        trend = (C > _roll_mean_t(C, 120)).float()
        comp = (p["w_mom"] * _pct_rank(mom) + p["w_rev"] * _pct_rank(-rev)
                + p["w_lowvol"] * _pct_rank(torch.where(torch.isfinite(vol), -vol,
                                                        torch.full_like(vol, float("nan"))))
                + p["w_trend"] * _pct_rank(trend))
        sel = _topk_mask(comp, int(p["top_k"]))
        sel = _rebal_expand_iso(sel, dates, int(p["rebal_days"]))
        return sel.float() / float(p["top_k"])
    if fam == "dual_momentum":
        if etf_cols is None or len(etf_cols) == 0:
            return None
        skip = int(p.get("skip_days", 0))
        mom = _shift_ratio(C, int(p["mom_len"]) + skip, skip)
        mom = torch.where(is_etf_t, torch.nan_to_num(mom, nan=-1e9),
                          torch.full_like(mom, -1e9))
        hold = mom > float(p["abs_floor"])
        sel = _topk_mask(mom, int(p["top_k"])) & hold
        return sel.float() / float(p["top_k"])
    if fam == "vol_mom":
        mom = _shift_ratio(C, int(p["lookback"]), 0)
        vol = _ann_vol_t(C, int(p["vol_win"]))
        score = torch.where(torch.isfinite(mom) & torch.isfinite(vol) & (vol > 0),
                            mom / vol, torch.full_like(mom, -1e9))
        sel = _topk_mask(score, int(p["top_k"]))
        sel = _rebal_expand_iso(sel, dates, int(p["rebal_days"]))
        if p.get("weighting", "equal") == "inv_vol":
            inv = torch.where(sel & (vol > 0), 1.0 / vol.clamp_min(1e-4),
                              torch.zeros_like(vol))
            rowsum = inv.sum(dim=-1, keepdim=True)
            return torch.where(rowsum > 0, inv / rowsum.clamp_min(1e-9),
                               torch.zeros_like(inv))
        return sel.float() / float(p["top_k"])
    if fam == "sector_momentum":
        if etf_cols is None or len(etf_cols) == 0:
            return None
        mom = _shift_ratio(C, int(p["mom_len"]), 0)
        mom = torch.where(is_etf_t, torch.nan_to_num(mom, nan=-1e9),
                          torch.full_like(mom, -1e9))
        sel = _topk_mask(mom, int(p["top_k"])) & (mom > float(p["mom_floor"]))
        sel = _rebal_expand_iso(sel, dates, int(p["rebal_days"]))
        return sel.float() / float(p["top_k"])
    if fam == "small_reversal":
        rev = -_shift_ratio(C, int(p["rev_len"]), 0)
        mw = int(p.get("mom_win", 0))
        if mw > 0:
            gate = _shift_ratio(C, mw, 0) >= float(p["mom_filter"])
            rev = torch.where(torch.nan_to_num(gate, nan=0.0) > 0, rev,
                              torch.full_like(rev, -1e9))
        sel = _topk_mask(rev, int(p["top_k"]))
        sel = _rebal_expand_iso(sel, dates, int(p["rebal_days"]))
        return sel.float() / float(p["top_k"])
    if fam == "rotation_28":
        if hs_idx is None or zz_idx is None:
            return None
        mom = _shift_ratio(C, int(p["lookback"]), 0)
        m_h, m_z = mom[:, hs_idx], mom[:, zz_idx]
        w = torch.zeros(D, M, device=C.device)
        w[:, hs_idx] = torch.nan_to_num((m_h >= m_z) & (m_h > p["cash_mom"]), nan=0.0).float()
        w[:, zz_idx] = torch.nan_to_num((m_z > m_h) & (m_z > p["cash_mom"]), nan=0.0).float()
        return w
    return None


def _score_one(w, R, cost_rate, cfg: AppConfig):
    """近似适应分：组合日收益（决策滞后+换手成本）→ 复合分同构。"""
    import torch
    if w is None or not torch.isfinite(w).any():
        return -1.0
    D = w.shape[0]
    gross = torch.einsum("dm,dm->d", torch.nan_to_num(w[:-1]), R[1:])
    dw = torch.nan_to_num(w[1:] - w[:-1]).abs().sum(-1) * 0.5
    ret = torch.zeros(D, device=w.device)
    ret[1:] = gross - dw * cost_rate
    eq = torch.cumprod(1.0 + ret, dim=0).clamp_min(1e-9)
    years = max(D / 252.0, 1e-9)
    cagr = float(eq[-1] ** (1.0 / years) - 1.0)
    std = ret.std().clamp_min(1e-9)
    sharpe = float(ret.mean() / std * (252.0 ** 0.5))
    dd = float((eq / torch.cummax(eq, dim=0).values - 1.0).min())
    calmar = cagr / max(0.05, -dd) if dd < 0 else (cagr if cagr > 0 else 0.0)
    calmar = max(-3.0, min(3.0, calmar))
    sharpe_c = max(-2.0, min(2.0, sharpe))
    active = (ret.abs() > 1e-9).sum().clamp_min(1)
    win = float((ret > 1e-9).sum() / active)
    s = 0.5 * (calmar + 3.0) / 6.0 + 0.3 * (sharpe_c + 2.0) / 4.0 + 0.2 * win
    if dd < -cfg.evolve.backtest_max_dd_penalty:
        s *= 0.5
    return float(s)


# ---------------------------------------------------------------- 主入口

def gpu_screen(cfg: AppConfig, panel: PanelData, families: list[str] | None = None,
               per_family: int = 3000, top_k_out: int = 12,
               progress: bool = True) -> list[dict]:
    """GPU 广域海选：每族采样 per_family 组参数批量近似评估，每族取 Top 候选。

    ⚠ 必须传入与 GA 目标函数同窗的面板（Evolver.train_panel，训练期不含样本外）。
      实测教训：全历史打分与训练切片适应度在行情切换下呈负相关（ρ=-0.6），
      会给 GA 喂反信号——海选窗口错位 = 系统性反向过滤器。

    返回 [{"strategy","params","gpu_score"}]（按 gpu_score 降序），供注入 GA 种群当移民。
    """
    if not gpu_available():
        return []
    import torch

    fams = [f for f in (families or SCREEN_FAMILIES)
             if f in strat_lib.STRATEGIES]
    device = _DEV
    rng = random.Random()

    C_np = panel.close.to_numpy(dtype=np.float32).copy()
    R_np = np.nan_to_num(np.divide(C_np[1:], C_np[:-1],
                                   out=np.zeros_like(C_np[1:]),
                                   where=C_np[:-1] > 0) - 1.0, nan=0.0)
    R_full = np.vstack([np.zeros((1, C_np.shape[1]), dtype=np.float32), R_np])
    C = torch.from_numpy(C_np).to(device)
    R = torch.from_numpy(R_full).to(device)
    D, M = C.shape

    codes = list(panel.codes)
    etf_cols = torch.tensor([i for i, c in enumerate(codes) if is_etf(c)],
                             device=device, dtype=torch.long)
    is_etf_t = torch.tensor([is_etf(c) for c in codes],
                            device=device, dtype=torch.bool)
    hs_idx = next((codes.index(c) for c in _HS300_ETFS if c in codes), None)
    zz_idx = next((codes.index(c) for c in _ZZ500_ETFS if c in codes), None)

    # 与精确引擎同口径的仓位截断（股票15%/ETF50%）
    cap = torch.tensor([cfg.risk.max_etf_position_pct if is_etf(c)
                        else cfg.risk.max_position_pct for c in codes],
                       device=device).view(1, -1)
    # 双边成本率近似（股票0.45% / ETF0.30%，含滑点佣金印花过户）
    cost_rate = float(np.mean([0.0030 if is_etf(c) else 0.0045 for c in codes]))

    all_candidates: list[dict] = []
    for fam in fams:
        grid = sample_grid(fam, per_family, rng)
        scored: list[tuple[float, dict]] = []
        t_start = __import__("time").time()
        for p in grid:
            try:
                w = _weights_one(fam, p, C, D, M, etf_cols, hs_idx, zz_idx, is_etf_t,
                                 dates=panel.dates)
                if w is None:
                    continue
                w = w.to(device).clamp(0.0, 1.0).minimum(cap)
                if not torch.isfinite(w).any():
                    continue
                s = _score_one(w, R, cost_rate, cfg)
                if s > 0:
                    scored.append((s, p))
            except Exception:  # noqa: BLE001 个别参数组异常跳过
                continue
        scored.sort(key=lambda t: t[0], reverse=True)
        for s, p in scored[: top_k_out]:
            all_candidates.append({"strategy": fam, "params": p, "gpu_score": round(s, 4)})
        if progress and scored:
            log.info("【GPU海选】%s: %d组 → 有效%2d → Top%d=%.3f（%.0f组/秒）",
                     fam, len(grid), len(scored), min(top_k_out, len(scored)),
                     scored[0][0], len(grid) / max(0.001, __import__("time").time() - t_start))
    all_candidates.sort(key=lambda x: x["gpu_score"], reverse=True)
    return all_candidates


def inject_to_population(state: dict, candidates: list[dict],
                          cap: int | None = None) -> int:
    """海选候选注入 GA 种群（当移民；是否上位由精确适应度决定）。

    cap 不给时跟随 config.evolve.population——此前默认硬编码 48，今日池扩容
    96 后每夜 GPU 注入都会把种群偷偷截回 48（撤销"样本要大"扩容，2026-09-21
    科学审计抓出的配置漂移）；调用方（run.py 两处）显式传 cfg 值。"""
    if not candidates:
        return 0
    if cap is None:
        try:
            from .config import AppConfig
            cap = int(AppConfig().evolve.population)
        except Exception:  # noqa: BLE001
            cap = 48
    pop = state["evolution"].setdefault("population", [])
    existing = {(ind.get("strategy"), json_key(ind.get("params", {}))) for ind in pop}
    added = 0
    for c in candidates:
        key = (c["strategy"], json_key(c["params"]))
        if key in existing:
            continue
        pop.append({"strategy": c["strategy"], "params": dict(c["params"])})
        existing.add(key)
        added += 1
    state["evolution"]["population"] = pop[-cap:]
    return added


def json_key(p: dict) -> str:
    import json
    return json.dumps(p, sort_keys=True, ensure_ascii=False)
