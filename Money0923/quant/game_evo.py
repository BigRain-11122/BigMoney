"""玩法自进化器（用户指令 2026-09-21：每半小时迭代玩法，与时俱进，真实实战
驱动，务必公平；02:40 追加"机制要科学有效！不要自己产生幻觉和作弊！"）。

公平铁律：只调"校准类"参数且对全部选手同规则生效——
  ① 近窗采样偏置 recent_bias：近段联赛成绩相对历史的背离大时，加大"近1/4
     历史窗口"的抽样占比（与时俱进：市场变了，考核就多考新市场）；
  ② 认证门槛 qualify_floor：按认证流量闭环校准（断流降门槛防死寂、通胀升
     门槛防廉价），有界 [0.25, 0.60]、步长 0.02；
绝不触碰用户钦定规则：1年考核窗 / 连续3局认证 / 5风格各20席 / 晋升红线。

科学有效性防线（防自我幻觉与作弊，2026-09-21 02:40 用户红线）：
  S1 每日漂移上限：门槛±0.06/日、偏置±0.10/日——过夜狂奔不可能；
  S2 失效冻结：门槛校准连续3拍未把流量带回目标带 → 冻结该旋钮24小时
     （承认无效、停止伪科学式的反复拧）；
  S3 选才有效性只认独立证据：联赛内战绩对比是"同源证据"——认证本就是
     从这批局里选出来的，用它证明"认证者更强"是循环论证（自我幻觉）。
     独立证据=前瞻轨道（认证后逐日真实推进的成绩，与认证数据不相交）；
     前瞻数据未成熟时诚实显示"数据未成熟"，绝不宣称✅。
"""
from __future__ import annotations

import logging
import time

from .arena import _ind_key

log = logging.getLogger("quant.game_evo")

INTERVAL_S = 1800  # 半小时一拍
FLOOR_MIN, FLOOR_MAX, FLOOR_STEP = 0.25, 0.60, 0.02
FLOOR_DAILY_DRIFT = 0.06   # S1：门槛单日总漂移上限
BIAS_MIN, BIAS_MAX = 0.15, 0.50
BIAS_DAILY_DRIFT = 0.10    # S1：偏置单日总漂移上限
DRIFT_TRIGGER = 0.25       # 近10局均分相对历史背离超25% → 提高近窗采样
FLOOR_FAIL_FREEZE = 3      # S2：连续失效拍数
FREEZE_S = 86400           # S2：冻结24小时
FWD_MIN_DAYS = 5           # S3：前瞻轨道至少有5个交易日推进才算独立证据成熟


def _game(a: dict) -> dict:
    g = a.setdefault("game", {})
    g.setdefault("recent_bias", 0.20)
    g.setdefault("qualify_floor", None)  # None=沿用config，首个节拍起接管
    g.setdefault("history", [])
    g.setdefault("last_evo", 0.0)
    g.setdefault("last_round", 0)
    g.setdefault("floor_fails", 0)
    g.setdefault("floor_frozen_until", 0.0)
    return g


def effective_recent_bias(a: dict) -> float:
    return float((a.get("game") or {}).get("recent_bias", 0.20) or 0.20)


def effective_qualify_floor(a: dict, cfg) -> float:
    g = (a.get("game") or {})
    v = g.get("qualify_floor")
    return float(v) if v else float(cfg.arena.qualify_floor)


def _day_anchor(g: dict) -> None:
    """S1：每日锚点——记录当日开局值，校准不得单日漂移超限。"""
    today = time.strftime("%Y%m%d")
    if g.get("day") != today:
        g["day"] = today
        g["day_floor0"] = g.get("qualify_floor") or 0.40
        g["day_bias0"] = float(g.get("recent_bias", 0.20))
        g["floor_fails"] = 0  # 新的一天，失效计数重置
        g["floor_frozen_until"] = 0.0


def maybe_evolve_game(cfg, state: dict) -> dict | None:
    """玩法半小时节拍：真实实战信号 → 有界校准 + 公平审计 + 台账留痕。"""
    a = state.setdefault("arena", {})
    g = _game(a)
    now = time.time()
    if now - float(g["last_evo"]) < INTERVAL_S:
        return None
    g["last_evo"] = now
    _day_anchor(g)
    changes: list[str] = []

    hist = a.get("round_history") or []
    last_r = int(g.get("last_round", 0))
    new_rounds = [h for h in hist if int(h.get("round", 0)) > last_r]
    if hist:
        g["last_round"] = max(int(h.get("round", 0)) for h in hist)

    # —— ① 与时俱进：近段实战均分 vs 历史均分的背离 → 调近窗采样偏置（S1 限幅）——
    if len(hist) >= 40:
        recent = [float(h.get("mean_score") or 0.0) for h in hist[-10:]]
        older = [float(h.get("mean_score") or 0.0) for h in hist[-40:-10]]
        m_old = sum(older) / len(older) if older else 0.0
        m_new = sum(recent) / len(recent) if recent else 0.0
        drift = abs(m_new - m_old) / (abs(m_old) + 1e-9)
        old_bias = float(g["recent_bias"])
        want = (min(BIAS_MAX, old_bias + 0.05) if drift > DRIFT_TRIGGER
                else max(BIAS_MIN, old_bias - 0.02))
        want = max(float(g.get("day_bias0", old_bias)) - BIAS_DAILY_DRIFT,
                   min(float(g.get("day_bias0", old_bias)) + BIAS_DAILY_DRIFT, want))
        if abs(want - old_bias) > 1e-9:
            g["recent_bias"] = want
            changes.append(f"近窗采样偏置 {old_bias:.2f}→{want:.2f}"
                           f"（近10局均分背离 {drift * 100:.0f}%，日限幅±{BIAS_DAILY_DRIFT}）")

    # —— ② 认证门槛闭环：流量落点带 [0.02, 0.12]人/局 —— S1 限幅 + S2 失效冻结 ——
    rate = None
    if new_rounds:
        certs = sum(len(h.get("qualified") or []) for h in new_rounds)
        rate = certs / len(new_rounds)
        g["last_cert_rate"] = round(rate, 4)
        frozen = float(g.get("floor_frozen_until", 0.0)) > now
        floor = float(g["qualify_floor"] or cfg.arena.qualify_floor)
        in_band = 0.02 <= rate <= 0.12
        if in_band:
            g["floor_fails"] = 0  # 回带=上次校准起效
        elif not frozen:
            new_floor = (max(FLOOR_MIN, floor - FLOOR_STEP) if rate < 0.02
                         else min(FLOOR_MAX, floor + FLOOR_STEP))
            day0 = float(g.get("day_floor0", floor))
            new_floor = max(day0 - FLOOR_DAILY_DRIFT, min(day0 + FLOOR_DAILY_DRIFT, new_floor))
            new_floor = max(FLOOR_MIN, min(FLOOR_MAX, new_floor))
            g["floor_fails"] = int(g.get("floor_fails", 0)) + 1
            if g["floor_fails"] >= FLOOR_FAIL_FREEZE:
                g["floor_frozen_until"] = now + FREEZE_S
                changes.append(f"门槛校准连续{g['floor_fails']}拍未把流量带回目标带"
                               f"→冻结24h（S2：承认无效，停止伪科学反复拧）")
            if abs(new_floor - floor) > 1e-9:
                g["qualify_floor"] = new_floor
                changes.append(f"认证门槛 {floor:.2f}→{new_floor:.2f}"
                               f"（近{len(new_rounds)}局认证{certs}人={rate:.2f}人/局）")

    # —— ③ 公平审计（每拍）：风格席位均衡 ——
    players = a.get("players") or []
    fair_notes: list[str] = []
    ok = True
    if players and len(players) == cfg.arena.size:
        counts: dict[str, int] = {}
        for p in players:
            counts[p.get("style") or "均衡"] = counts.get(p.get("style") or "均衡", 0) + 1
        bad = {k: v for k, v in counts.items() if v < 15 or v > 25}
        if bad:
            ok = False
            fair_notes.append(f"风格席位漂移 {bad}（公平底线20/席）")
    else:
        ok = False
        fair_notes.append(f"阵容人数 {len(players)}≠{cfg.arena.size}")

    # —— S3 选才有效性：同源证据仅作参考，独立证据=前瞻轨道 ——
    # 同源（有选择偏差，仅参考）：认证者本就是从这批局里选出来的，用它证明
    # "认证者更强"是循环论证——绝不据此宣称✅。
    ps = a.get("pstats") or {}
    cert_keys = {_ind_key(q) for q in (a.get("qualified") or [])}
    same_c = [s["ps_sum"] / s["n"] for k, s in ps.items()
              if k in cert_keys and s["n"] >= 30]
    same_r = [s["ps_sum"] / s["n"] for k, s in ps.items()
              if k not in cert_keys and s["n"] >= 30]
    same_c_mean = sum(same_c) / len(same_c) if same_c else 0.0
    same_r_mean = sum(same_r) / len(same_r) if same_r else 0.0
    # 独立证据：认证后逐日真实推进的前瞻轨道（与认证局数据不相交）
    cap = float(cfg.arena.capital)
    cert_ids = {q["id"] for q in (a.get("qualified") or [])}
    fwd_c, fwd_r, fwd_days = [], [], 0
    for p in players:
        tr = p.get("track") or []
        if not tr:
            continue
        fwd_days = max(fwd_days, len(tr))
        r = float(p.get("equity", cap)) / float(p.get("capital", cap)) - 1.0
        (fwd_c if p["id"] in cert_ids else fwd_r).append(r)
    mature = fwd_days >= FWD_MIN_DAYS and (fwd_c or fwd_r)
    fc_mean = sum(fwd_c) / len(fwd_c) if fwd_c else 0.0
    fr_mean = sum(fwd_r) / len(fwd_r) if fwd_r else 0.0
    if mature:
        g["cert_effective"] = bool(fwd_c and (not fwd_r or fc_mean > fr_mean))
        g["cert_evidence"] = (f"独立证据（前瞻{fwd_days}日）：认证者{fc_mean * 100:+.1f}%"
                              f" vs 非认证{fr_mean * 100:+.1f}%（n={len(fwd_c)}/{len(fwd_r)}）")
        if fwd_c and fwd_r and fc_mean <= fr_mean:
            ok = False
            fair_notes.append(f"选才告警（独立证据）：认证者前瞻{fc_mean * 100:+.1f}%"
                              f"≤非认证{fr_mean * 100:+.1f}%——玩法选才需进化")
    else:
        g["cert_effective"] = None  # 数据未成熟——诚实显示，不宣称
        g["cert_evidence"] = (f"前瞻轨道推进{fwd_days}日（需≥{FWD_MIN_DAYS}日才有独立证据）；"
                              f"同源参考（选择偏差）：认证者盈稳分{same_c_mean * 100:+.1f}"
                              f" vs 非认证{same_r_mean * 100:+.1f}——仅参考不作结论")

    rec = {"t": time.strftime("%Y-%m-%d %H:%M:%S"),
           "rounds": len(new_rounds),
           "changes": changes, "fair": ok,
           "fair_notes": fair_notes,
           "recent_bias": float(g["recent_bias"]),
           "qualify_floor": float(g["qualify_floor"] or cfg.arena.qualify_floor),
           "cert_rate": g.get("last_cert_rate"),
           "cert_effective": g.get("cert_effective")}
    g["history"] = (g.get("history") or [])[-49:] + [rec]

    log.info("【玩法进化】节拍完成：%s | 公平审计%s | 近窗偏置%.2f 认证门槛%.2f | %s",
             "；".join(changes) or "本拍无调整（信号在目标带内）",
             "✅" if ok else "⚠️ " + "；".join(fair_notes),
             float(g["recent_bias"]),
             float(g["qualify_floor"] or cfg.arena.qualify_floor),
             g.get("cert_evidence", ""))
    return rec


def game_status(state: dict) -> list[str]:
    g = (state.get("arena") or {}).get("game") or {}
    eff = g.get("cert_effective")
    eff_txt = "数据未成熟（诚实口径，不宣称）" if eff is None else ("✅有效" if eff else "⚠️无效")
    lines = [f"玩法参数：近窗采样偏置={g.get('recent_bias', 0.2)}"
             f" | 认证门槛={g.get('qualify_floor') or 'config默认'}"
             f" | 上拍认证率={g.get('last_cert_rate', '—')}人/局"
             f" | 选才有效={eff_txt}（只认独立前瞻证据）",
             f"选才证据：{g.get('cert_evidence', '—')}"]
    for rec in (g.get("history") or [])[-8:]:
        ch = "；".join(rec.get("changes") or []) or "无调整"
        fair = "✅" if rec.get("fair") else "⚠️ " + "；".join(rec.get("fair_notes") or [])
        lines.append(f"  {rec.get('t')} | {ch} | 公平{fair}")
    return lines
