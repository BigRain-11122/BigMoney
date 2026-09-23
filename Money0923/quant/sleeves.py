"""多队并行分仓制（用户指令"策略风格要非常差异化和多种多样"，2026-09-21 部署层落地）。

用户模型的真金落地：派 N 个团队各自独立作战，每仓独立 10% 停机线——
队死（停机）→ 冻结 → 次日换下一个合格认证选手（不同族优先），资金留在
仓内继续 PK；仓内毁灭线（capital_start×20%）→ 仓退役。账户级保护不变：
毁灭线 80%（总权益）+ 账户 10% 停机线作最后防线（多仓各自 -10% 时才可能
触发=系统性风险，纵深防御）。15% 单票红线按仓内权益执行（更保守）。

设计裁决（诚实披露）：
- 此前"冠军独享部署"只输出幸存者=单一防御风格（low_vol 结构性买低波
  大盘蓝筹），多样性只活在联赛里——分仓制把"极稳→激进全覆盖"搬进实盘。
- 成员回撤≤10% 硬闸在分仓语境下由各仓自己的停机线执行（隔离使部署
  与风控不再自相矛盾）；激进族可上场，代价是死得快换人快=淘汰机制在跑。
- 仓数量=3：10 万÷3≈3.3 万，15% 仓内上限≈5,000 元仍可整手买多数标的
  （ETF/低价股尤佳）；100 仓在整手数学下不可行（1,000 元/队买不起一手）。
- 同票冲突：一个标的只属于一个仓（他仓已持有 → 本仓跳过留痕），
  防两仓叠加变相超 15% 账户集中度。
- S1=现任冠军团队（跟随 maybe_update_team 的换血；迁移期持仓偏重，
  按纪律自然退出后三仓收敛等分）；S2/S3=认证池多样性选队，全目标暴露
  （无风格引擎缩放——各仓风格本就该互不相干，风险由各仓自己的停机线管）。
"""
from __future__ import annotations

import datetime as dt
import json
import logging

from .config import AppConfig

log = logging.getLogger("quant.sleeves")

# 仓成员族锚（多样性：低波防御 / ETF轮动 / 小市值反转——三个互不相干的宇宙角落）
SLEEVE_FAMILY_ANCHORS = ["low_vol", "etf_trend", "small_reversal"]

# 风险线按风格分级（用户指令 2026-09-21"根据策略来，激进的策略亏 8 成都行，
# 但亏完了就永远出局"）：仓的停机线由该仓风险等级决定，不再全局统一 10%——
# 统一紧线会勒死激进风格（还没等到它的行情就被停机换人）。毁灭线（起点×20%，
# 亏80%需+400%回本=数学实质亏完）对所有仓一律生效：触发即仓退役，永不自动恢复。
SLEEVE_RISK_TIERS = {
    "S1": {"label": "稳健仓", "halt_line": 0.10, "desc": "防御：10%停机换人"},
    "S2": {"label": "进取仓", "halt_line": 0.20, "desc": "进取：20%停机换人"},
    "S3": {"label": "激进仓", "halt_line": None, "desc": "激进：不停机，亏到-80%毁灭线永久退役"},
}


# ---------------------------------------------------------------- 视图与判定

def sleeve_positions(state: dict, sv: dict) -> dict:
    """仓内持仓视图：从总持仓按 sleeve 标签切出。"""
    out: dict = {}
    for c, p in (state.get("account", {}).get("positions") or {}).items():
        if p.get("sleeve") == sv["id"]:
            out[c] = p
    return out


def sleeve_equity(state: dict, sv: dict, prices: dict[str, float]) -> float:
    """仓权益 = 仓内现金 + 仓内持仓市值（期货 lot×乘数×价）。"""
    from .futures import futures_meta
    mv = 0.0
    for c, p in sleeve_positions(state, sv).items():
        if str(c).startswith("F."):
            pr = prices.get(c, 0.0) or p.get("avg_entry", 0.0)
            mv += p.get("lots", 0) * futures_meta(str(c))["mult"] * pr
        else:
            pr = prices.get(c, 0.0) or p.get("cost", 0.0)
            mv += p.get("shares", 0) * pr
    return float(sv.get("cash", 0.0)) + mv


def halted(sv: dict) -> bool:
    return bool((sv.get("risk") or {}).get("halt"))


def deployable(sv: dict) -> bool:
    """可部署：有成员、未停机、未退役。"""
    return bool(sv.get("members")) and not halted(sv) and not sv.get("retired")


def sleeve_label(sv: dict) -> str:
    ms = sv.get("members") or []
    hl = sv.get("halt_line")
    line_txt = f"{float(hl):.0%}线" if hl else "亏完出局"
    if not ms:
        return f"{sv['id']}·空仓({line_txt})" + ("（退役）" if sv.get("retired") else "")
    head = f"{ms[0].get('strategy')}+{ms[0].get('sizing') or 'equal'}"
    extra = f" 等{len(ms)}成员" if len(ms) > 1 else ""
    tag = "（停机）" if halted(sv) else ("（退役）" if sv.get("retired") else "")
    return f"{sv['id']}·{head}{extra}[{line_txt}]{tag}"


def deployment_fingerprint(state: dict) -> list:
    """部署指纹（备单→执行之间检测换血）：分仓制=逐仓成员基因；否则回退团队指纹。"""
    sleeves = state.get("sleeves") or []
    if sleeves:
        return [[sv["id"], json.dumps(
            [{"s": m.get("strategy"), "p": m.get("params"),
              "z": m.get("sizing"), "zp": m.get("sizing_params")} for m in (sv.get("members") or [])],
            sort_keys=True, default=str)] for sv in sleeves]
    from .decide import team_fingerprint
    return team_fingerprint(state)


# ---------------------------------------------------------------- 选队（认证池，多样性约束）

def pick_member(state: dict, exclude_families: set[str] | None = None,
                prefer_family: str | None = None,
                exclude_ids: set[str] | None = None) -> dict | None:
    """从联赛认证池选仓成员：偏好族内证据最强者；族均无认证则按证据
    全池最高且不与 exclude 撞族。exclude_ids=刚被淘汰者不给原地满血复活
    （防同基因无限换人循环；同族不同个体允许接力=该族还有新基因在池里）。

    认证=随机 1 年窗连续 3 局多样性前10——真实实战战绩群体，不是训练分。

    选人证据分级（科学审计 2026-09-21 用户红线"所有都要基于科学"）：
    单局认证分=一个随机窗快照，运气成分大；联赛逐局累积的实战盈稳分
    （收益−1.5×|回撤|，用户"只认盈利和稳定"口径，含认证后独立抽取的
    新窗）样本≥30局才够格优先——大样本压制单局运气。证据不足回退认证分。
    返回可直接部署的单成员基因。"""
    q = (state.get("arena") or {}).get("qualified") or []
    exclude = set(exclude_families or [])
    ex_ids = set(exclude_ids or set())
    cands = [x for x in q if x.get("strategy") == prefer_family
             and x.get("id") not in ex_ids] if prefer_family else []
    if not cands:
        cands = [x for x in q if x.get("strategy") not in exclude
                 and x.get("id") not in ex_ids]
    if not cands:
        return None
    from .arena import _ind_key
    ps = (state.get("arena") or {}).get("pstats") or {}

    def _evidence(x: dict) -> tuple:
        s = ps.get(_ind_key(x))
        if s and int(s.get("n") or 0) >= 30:
            return (1, float(s.get("ps_sum") or 0.0) / int(s["n"]))
        return (0, float(x.get("score") or 0.0))

    best = max(cands, key=_evidence)
    s = ps.get(_ind_key(best))
    if s and int(s.get("n") or 0) >= 30:
        basis = f"实战{int(s['n'])}局均盈稳分{float(s['ps_sum']) / int(s['n']):.3f}"
    else:
        basis = f"认证分{float(best.get('score') or 0.0):.3f}（实战样本<30局）"
    return {"strategy": best.get("strategy"), "params": dict(best.get("params") or {}),
            "sizing": best.get("sizing") or "equal",
            "sizing_params": dict(best.get("sizing_params") or {}),
            "_src": {"id": best.get("id"), "score": best.get("score"),
                     "streak": best.get("streak"), "certified_at": best.get("qualified_at"),
                     "basis": basis}}


def new_sleeve(sid: str, label: str, members: list[dict], cash: float,
               capital_start: float, halt_line: float | None = None) -> dict:
    tier = SLEEVE_RISK_TIERS.get(sid, {})
    return {"id": sid, "label": label, "members": members, "cash": float(cash),
            "capital_start": float(capital_start),
            "halt_line": halt_line if halt_line is not None else tier.get("halt_line", 0.10),
            "risk": {"halt": False, "halt_reason": None, "halted_at": None,
                     "equity_high": float(capital_start), "daily_breaker_date": "",
                     "day_key": "", "day_start_equity": float(capital_start), "daily_pnl": 0.0},
            "since": dt.date.today().isoformat(), "history": [], "retired": False,
            "rotations": 0}


def ensure_sleeves(state: dict, cfg: AppConfig) -> list[dict]:
    """初始化/迁移分仓（幂等）。迁移规则：现有持仓全部归 S1（现任冠军的
    仓位不动，超仓部分按纪律自然退出）；现金向 S2/S3 倾斜使三仓权益趋衡。"""
    if state.get("sleeves"):
        return state["sleeves"]
    acc = state["account"]
    total_cash = float(acc.get("cash", 0.0) or 0.0)
    for p in (acc.get("positions") or {}).values():
        p["sleeve"] = "S1"
    team = state.get("team") or ([state["champion"]] if state.get("champion") else [])
    s1_pos_val = sum(p.get("shares", 0) * p.get("cost", 0.0)
                     for p in (acc.get("positions") or {}).values())
    total_eq = total_cash + s1_pos_val
    target = total_eq / 3.0
    s1_cash = max(target - s1_pos_val, 0.08 * total_cash)
    rest = max(total_cash - s1_cash, 0.0)
    sleeves: list[dict] = [new_sleeve("S1", SLEEVE_RISK_TIERS["S1"]["label"],
                                      [dict(m) for m in team],
                                      s1_cash, s1_cash + s1_pos_val)]
    used = {m["strategy"] for m in team if m.get("strategy")}
    for i, fam in enumerate(SLEEVE_FAMILY_ANCHORS[1:], start=2):
        member = pick_member(state, exclude_families=used, prefer_family=fam)
        if member:
            used.add(member["strategy"])
        sid = f"S{i}"
        sleeves.append(new_sleeve(sid, SLEEVE_RISK_TIERS.get(sid, {}).get("label", f"风格仓{i}"),
                                  [member] if member else [], rest / 2.0, rest / 2.0))
    # 已在场名单：初始成员入册（换人时不得回锅）
    for sv in sleeves:
        for m in (sv.get("members") or []):
            _id = m.get("_src", {}).get("id")
            if _id:
                sv.setdefault("fielded_ids", []).append(_id)
    state["sleeves"] = sleeves
    tier_txt = " | ".join(
        f"{sv['id']}:{('%.0f%%停机' % (sv['halt_line'] * 100)) if sv.get('halt_line') else '亏完出局'}"
        for sv in sleeves)
    log.info("【分仓制】初始化：S1=%s(迁移%d持仓,权益%.0f) S2=%s(%.0f) S3=%s(%.0f) | 风险线 %s",
             sleeve_label(sleeves[0]), len(acc.get("positions") or {}),
             sleeves[0]["capital_start"],
             sleeve_label(sleeves[1]) if len(sleeves) > 1 else "空", sleeves[1]["cash"],
             sleeve_label(sleeves[2]) if len(sleeves) > 2 else "空", sleeves[2]["cash"],
             tier_txt)
    return sleeves


def sync_champion_sleeve(state: dict) -> None:
    """S1 跟随现任冠军团队（maybe_update_team 换血后自动同步；幂等）。"""
    sleeves = state.get("sleeves") or []
    if not sleeves:
        return
    team = state.get("team") or []
    s1 = sleeves[0]
    if not team:
        return
    fp = json.dumps([{k: m.get(k) for k in ("strategy", "params", "sizing", "sizing_params")}
                     for m in team], sort_keys=True, default=str)
    cur = json.dumps([{k: m.get(k) for k in ("strategy", "params", "sizing", "sizing_params")}
                      for m in (s1.get("members") or [])], sort_keys=True, default=str)
    if fp != cur and not halted(s1) and not s1.get("retired"):
        s1["members"] = [dict(m) for m in team]
        log.info("【分仓制】冠军换血 → S1 跟随新团队: %s", sleeve_label(s1))


# ---------------------------------------------------------------- 停机换人

def rotate_sleeve(state: dict, sv: dict, equity: float | None = None) -> bool:
    """停机仓换人：从认证池选下一个挑战者（排除其他在位族），保留资金，
    风控基线按当前仓权益重置（新队新基线=人工复盘语义的自动化）。"""
    sleeves = state.get("sleeves") or []
    used = {m.get("strategy") for s in sleeves if s is not sv
            for m in (s.get("members") or [])}
    # 已在场名单：本仓历任选手一律不得回锅（防 Q2→Q4→Q2 隔代循环复活）
    out_ids = set(sv.get("fielded_ids") or [])
    member = pick_member(state, exclude_families=used, exclude_ids=out_ids)
    if not member:
        log.warning("【分仓制】%s 停机但认证池无可用新挑战者（排除在位族%s 与历任%s）"
                    "→ 仓休战等新认证",
                    sv["id"], sorted(used), sorted(x for x in out_ids if x))
        return False
    sv.setdefault("fielded_ids", []).append(member.get("_src", {}).get("id"))
    sv["members"] = [member]
    sv["rotations"] = int(sv.get("rotations", 0)) + 1
    r = sv["risk"]
    r["halt"] = False
    r["halt_reason"] = None
    r["halted_at"] = None
    r["daily_breaker_date"] = ""
    if equity is not None and equity > 0:
        r["equity_high"] = float(equity)  # 新挑战者的停机线从当前仓权益起算
    sv["since"] = dt.date.today().isoformat()
    log.info("【分仓制】%s 换人第%d次：新挑战者 %s（来自认证池 %s，资金保留继续PK）",
             sv["id"], sv["rotations"], sleeve_label(sv),
             member.get("_src", {}).get("id"))
    return True
