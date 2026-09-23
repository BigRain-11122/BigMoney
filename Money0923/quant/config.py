"""全局配置：代码内默认值 + 根目录 config.json 覆盖（敏感项如 QMT 账号写 json，不进代码库）。

风控档位：稳健（用户指定）——单票≤15%、单日亏损>3%熔断、组合回撤≥10%停机。
"""
from __future__ import annotations

import copy
import json
import os
from dataclasses import asdict, dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
DAILY_DIR = os.path.join(DATA_DIR, "daily")
LOGS_DIR = os.path.join(ROOT, "logs")
STATE_DIR = os.path.join(ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "state.json")
CONFIG_FILE = os.path.join(ROOT, "config.json")  # 可选：用户覆盖配置（已 gitignore）
STOP_FILE = os.path.join(ROOT, "STOP")           # 紧急停机开关：手工创建该文件即撤单停机


@dataclass
class FeeModel:
    """A股交易成本：印花税卖出0.05%，佣金万2.5最低5元，过户费0.001%双边，滑点单边0.1%。"""
    commission_rate: float = 0.00025
    min_commission: float = 5.0
    stamp_duty: float = 0.0005      # 仅卖出
    transfer_fee: float = 0.00001   # 双边
    slippage: float = 0.001         # 单边滑点（回测/模拟盘撮合用）


@dataclass
class RiskConfig:
    """稳健档风控红线。小散户定位（用户指定）：10万本金、短线、日频、单笔持股3~15个交易日。"""
    initial_capital: float = 100_000.0   # 10万本金（小散户口径：最小佣金5元的摩擦占比更高，费率建模更重要）
    max_position_pct: float = 0.15       # 单只股票市值占组合上限（用户红线）
    max_etf_position_pct: float = 0.50   # 单只ETF上限：ETF为一篮子股票，轮动类经典模型需要集中度
    max_positions: int = 8               # 最大同时持仓数
    stop_loss_pct: float = 0.08          # 个股硬止损（相对成本价；交易纪律=换股，非账户出局）
    min_hold_days: int = 3               # 最短持股3个交易日：不满3日不因调仓卖出（止损/超时离场不受限）
    max_hold_days: int = 15              # 最高持股15个交易日：超时开盘强制离场（3~15天级别，用户指定）
    daily_loss_limit_pct: float = 0.0    # 日熔断已停用（2026-09-21 用户指令"不能盘中波动就出局"：
                                         # 0=两端一致关闭。旧值0.03为盘中触发当日禁买，正中波动出局禁区）
    drawdown_halt_pct: float = 0.10      # 组合回撤停机线（用户确认红线）：**收盘结算口径判定**，
                                         # 盘中浮动永不触发；停机=暂停+人工复盘后可恢复，非出局
    ruin_loss_pct: float = 0.80          # 毁灭出局线（用户"亏完出局"的科学落地）：收盘结算时
                                         # 权益≤初始本金×20% → 永久出局。亏80%需+400%回本
                                         # =数学实质亏完；留20%残值为重生火种；唯一账户出局
    max_participation: float = 0.05      # 单票成交 ≤ 当日成交量5%
    min_keep_cash_pct: float = 0.02      # 保底现金2%
    target_vol: float = 0.15            # 组合波动率目标（年化）：近20日实现波动超此值自动线性降杠杆
                                         # （下限0.25×），0=关闭。理性仓位：波动大→仓位小。
    vol_scale_floor: float = 0.25        # 波动率目标降杠杆下限（防止清仓式收缩）
    # —— 国债逆回购现金管理（用户指令2026-09-22"现金加入国债逆回购赚隔夜收益"）——
    # 三端一致：paper收盘借出/次日开盘前归还；backtest按204001真实历史利率逐日计息
    repo_enabled: bool = True           # 收盘闲置现金自动借出GC001，风险≈0（交易所质押+中登担保）
    repo_min_lend: float = 1000.0      # 沪市门槛：1000元起、1000整数倍
    repo_fee_rate: float = 0.00001     # 佣金十万分之一（现行规则，一次性收取）
    repo_default_rate: float = 1.8     # 利率数据缺失时的保守默认年化%（诚实下界）
    repo_year_basis: int = 365         # 沪市计息基准：365天


@dataclass
class UniverseConfig:
    stock_universe_size: int = 120  # 沪深300权重Top120（剔除ST/科创板）
    small_universe_size: int = 40   # 小市值端：中证1000权重最小40只（小市值策略族标的池）
    etf_universe_size: int = 30     # ETF池：宽基/行业/债券/黄金/跨境，按成交额取Top
    min_market_cap: float = 3e10    # 总市值下限 300 亿（稳健档偏大盘）
    min_price: float = 3.0
    max_price: float = 300.0
    history_years: float = 25.0     # 历史深度（2026-09-21 用户"把历史数据下全"：3.5→25年=2001年起，
                                    # 覆盖2001-05熊/2007泡沫/2015股灾/2018熊/2019-21结构牛全部regime谱；
                                    # 联赛随机窗跨全历史=认证考核广度×7；GA/GPU训练由 evolve.train_years
                                    # 独立控制仍用近年——训练贴当下、考核跨全史）
    enable_futures: bool = False   # 期货通道闸（2026-09-21 全品种指令，架构裁决改自服务）：
                                   # 面板**永不**并入 F.* 列（防股票策略把期货当"低波股"
                                   # 选——权重语义错配=隐形杠杆刷分）；cta_trend 与期货引擎
                                   # 经 futures.futures_window 自取窗口数据，本闸只控
                                   # CTA 是否参与（关=空仓信号）。全链路已接线+冒烟：
                                   # 分流/手数规划/模拟盘撮合/行情源/团队同类别约束。


@dataclass
class EvolveConfig:
    population: int = 96               # 种群48→96（2026-09-21 用户"样本要大"：双倍基因并行测试，
                                       # 吃下认证池200的注入流速；eval缓存下增量成本可控）
    train_years: float = 4.0           # GA/GPU训练面板解耦（2026-09-21 历史扩至25年配套）：
                                       # 面板25年只供联赛跨史随机窗考核；训练仍用近4年——
                                       # 进化探索方向贴当下市场，GPU海选成本可控(~1.2×)
    generations: int = 10               # 每次进化任务的代数预算
    elite: int = 4
    tournament_k: int = 3
    crossover_rate: float = 0.7
    mutate_rate: float = 0.35
    mutate_sigma: float = 0.18          # 变异步长（参数空间的相对扰动）
    n_train_slices: int = 3             # 训练期切3片算适应度，防单段行情过拟合
    holdout_pct: float = 0.18           # 最近18%历史仅用于冠军晋升验证（样本外）
    promotion_margin: float = 0.05      # 团队平均样本外分须比现任高5%才换血
    promote_min_score: float = 0.45     # 单人门槛（防垃圾上位）；团队成员门槛见 meta.team_member_floor
    max_promote_attempts_per_day: int = 12  # 样本外磨刷保护：每日晋升尝试上限（24h进化必须）
    backtest_max_dd_penalty: float = 0.20  # 回测最大回撤>20% 重罚
    min_trades: int = 20                # 训练期成交<20笔 视为运气单降权
    cagr_target: float = 0.20           # 目标年化20%：适应度含达成度项（目标≠承诺，样本外闸门不变）
    # —— 自适应机制（进化引擎的自我更新；用户红线参数不在此列，永不被自动修改）——
    stagnation_gens: int = 8            # 连续N代最优分无提升 → 判定停滞
    immigrant_frac: float = 0.3         # 停滞时注入移民比例（新随机个体替换最差）
    sigma_boost_max: float = 2.5        # 停滞时变异步长放大上限（×基础sigma）
    workers: int = 0                    # 并行评估进程数：0=自动（min(24, 逻辑核-2)，2026-09-21 "疯狂加速"16→24），>1 强制指定
    # —— GPU 广域海选（RTX 4070 SUPER；无CUDA自动跳过不影响主流程）——
    gpu_screen_per_family: int = 20000  # 每族每夜采样参数组数（~390-550组/秒；"疯狂加速"3000→20000，
                                        # GPU 空闲算力释放=广度搜索×6.7）
    gpu_screen_top: int = 24           # 每族注入GA种群的Top候选数（同步扩容12→24）
    # —— Top10 循环迭代（用户指定机制：每轮看前10名选手→围绕它们精修）——
    top_breeders: int = 10              # 每代前N名选手=亲本池（子代全部由Top10繁殖）
    local_refine_frac: float = 0.25    # 子代中Top10邻域小步精修占比（每轮循环迭代）
    max_breed_family: int = 3           # 亲本池同族配额上限（0=禁用）：防高分族霸榜使种群
                                        # 单化稳态（2026-09-20实测etf_trend×48后17族绝迹，
                                        # 移民注入无效、晋升配额全烧注定否决的满仓候选）


@dataclass
class MetaConfig:
    """机制复盘与市场风格引擎（总结→学习当下→反哺进化）参数。"""
    weekly_review_weekday: int = 5   # 周度复盘日（0=周一…5=周六，6=周日）
    decay_min_days: int = 15         # 冠军衰退检测所需最少轨道交易日数
    decay_ratio: float = 0.33        # 实际年化 < 冠军样本外年化×该比例 → 判定衰退
    review_keep: int = 30            # 复盘记录保留条数
    # —— 冠军团队（资产组合：不同策略族各出一人，资金均分）——
    team_size: int = 3               # 团队成员数（每成员一个策略族）
    team_member_floor: float = 0.35  # 成员样本外分绝对门槛
    team_member_max_dd: float = 0.10  # 成员样本外最大回撤硬约束＝停机线本体（2026-09-20 23:15
                                      # 用户指令"放开手脚/亏完了出局"：从停机线一半5%放宽到停机线10%，
                                      # 预审不提前枪毙，上场后由实盘停机线按战绩裁决）；
                                      # 超此回撤的成员不得晋升，现任成员复检违规即清退
    team_update_gens: int = 10      # 每进化N代尝试一次团队重组（受每日尝试上限约束）
    # —— 市场风格引擎（每晚备单前运行）——
    regime_lookback: int = 60        # 风格识别回看窗口（交易日）
    recent_days: int = 40            # 冠军/族 近段模型验证窗口（交易日）
    mismatch_scale: float = 0.6     # 风格错配时曝光系数（目标权重×此值）
    hostile_scale: float = 0.5      # 敌对风格（震荡+高波+冠军近亏）曝光系数
    # —— walk-forward 链式验证（历史当实盘）——
    wf_windows: int = 6              # 默认滚动窗口数（每窗约2个月实盘段）
    wf_gens: int = 250               # 每窗进化代数预算（50代出不了合格团队→全程空仓，实测教训）
    # —— 随机取点验证（历史任意起点任意长度窗口的模型压力检验）——
    stress_windows: int = 24         # 团队每日体检的随机窗口数
    stress_min_len: int = 20         # 窗口最短（交易日）
    stress_max_len: int = 60         # 窗口最长（交易日）
    stress_beat_cash: float = 0.15   # "跑赢持币"分数线（持币基线约0.14）
    stress_min_mean: float = 0.25    # 随机窗口均分下限（体检/晋升闸）
    stress_min_beat_pct: float = 0.50  # 跑赢持币的窗口占比下限
    team_stress_windows: int = 16   # 晋升闸每成员随机窗口数（少以控成本）
    # —— 风控事件告警 ——
    alert_webhook: str = ""          # 停机/熔断/极端行情触发时POST {"text": msg}；留空仅记日志


@dataclass
class FundamentalConfig:
    """基本面负面清单（用户四条规则：亏损/暴雷/共识衰亡行业/舆论负面 → 不做）。

    自动规则（业绩报表，含净利润/同比/所处行业，全市场单请求）：
    - 亏损不做：最新报告期净利润 ≤ min_net_profit
    - 暴雷代理：净利润同比 < profit_yoy_floor（默认-60%，大票罕见量级）
    - 衰亡行业：blacklist.industries 关键词匹配"所处行业"（预置房地产，用户可改）
    手动规则（舆论负面无法可靠自动化——判断由人，执行由系统）：
    - blacklist.codes：run.py blacklist add 编号 "原因" 即永久拉黑
    """
    enabled: bool = True
    min_net_profit: float = 0.0        # 最新报告期净利润 ≤ 此值 → 剔除（单位：元）
    profit_yoy_floor: float = -0.60    # 净利润同比低于此比例 → 剔除（暴雷代理）
    earnings_cache_days: int = 7       # 业绩缓存刷新周期（同报告期内补披露）
    exit_on_negative: bool = True      # 持仓中新触发负面 → 会话内强制离场（"不做"含持货）


@dataclass
class ArenaConfig:
    """百团锦标赛（2026-09-20 赛制升级）：每支团队=一名选手，各携 100 万同台竞技。

    - 资金：每队 100 万（用户指定，此前 10 万）
    - 周期：联赛一局考核窗口 = 1 年（round_days 交易日），起点随机（2026-09-20 最新指令）
    - 风格谱系（用户指定"从极度保守到极度激进都要有"）：5 档风格各占 1/5 席位
      ——极稳/保守/均衡/进取/激进，各档独立风控参数与曝光缩放（TEAM_STYLES in arena.py）
    - 循环迭代不变：一局全员同赛 → 多样性前10晋级 → 连续N局稳定前10认证进GA种群
    """
    size: int = 200             # 团队数（2026-09-21 用户"队伍策略模式要足够多/样本太少"→100→200）
    capital: float = 1_000_000.0  # 每支团队本金（用户指定100万）
    period_days: int = 20       # 周度报告的分段长度（交易日/段）
    feed_top: int = 10          # 总榜前N名的基因注入GA种群（机制回馈）
    mutate_rate: float = 0.6     # 微调选手的变异率（相对经典种子/种群基因）
    mutate_sigma: float = 0.25  # 微调选手的变异步长
    style_spectrum: bool = True  # 风格谱系开关：每队独立风控参数（极稳→激进5档）
    # —— 联赛制：随机1年窗口循环赛（2026-09-20 23:15 用户最新指令"1年为期限"，覆盖此前3年）——
    round_days: int = 252        # 一局考核周期=1年（252交易日），起点随机
    qualify_streak: int = 3      # 连续N局前10 → 稳定前10认证
    qualify_floor: float = 0.40  # 认证所需的最后一局最低分（防全体垃圾局幸存）
    max_family_top: int = 3      # 前10中同策略族人数上限（多样性）
    max_sel_corr: float = 0.85   # 前10中两两持仓权重相关性上限（"选股要不一样"）


@dataclass
class QmtConfig:
    """miniQMT 实盘参数。QMT 客户端（极简模式）需保持登录，账户需开通程序化权限。"""
    account_id: str = ""         # 资金账号
    qmt_path: str = ""           # QMT 安装目录下 userdata_mini 路径
    xtquant_path: str = ""       # 可选：QMT 自带 xtquant 目录（pip 装不了时用）
    session_id: int = 20260919
    dry_run: bool = True         # True=只生成委托不真实报单；联调通过后手动置 false


@dataclass
class AppConfig:
    mode: str = "paper"  # paper | live
    fee: FeeModel = field(default_factory=FeeModel)
    risk: RiskConfig = field(default_factory=RiskConfig)
    universe: UniverseConfig = field(default_factory=UniverseConfig)
    evolve: EvolveConfig = field(default_factory=EvolveConfig)
    meta: MetaConfig = field(default_factory=MetaConfig)
    fundamental: FundamentalConfig = field(default_factory=FundamentalConfig)
    arena: ArenaConfig = field(default_factory=ArenaConfig)
    qmt: QmtConfig = field(default_factory=QmtConfig)


_DATACLASS_MAP = {
    "fee": FeeModel, "risk": RiskConfig, "universe": UniverseConfig,
    "evolve": EvolveConfig, "meta": MetaConfig, "fundamental": FundamentalConfig,
    "arena": ArenaConfig, "qmt": QmtConfig,
}


def load_config() -> AppConfig:
    cfg = AppConfig()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as f:
            user = json.load(f)
        for key, val in user.items():
            if key == "mode":
                cfg.mode = val
            elif key in _DATACLASS_MAP and isinstance(val, dict):
                sub = getattr(cfg, key)
                for k2, v2 in val.items():
                    if hasattr(sub, k2):
                        setattr(sub, k2, v2)
    return cfg


def update_qmt_fields(qmt_path: str, account_id: str) -> bool:
    """自动发现结果写回 config.json：只改 qmt.qmt_path/qmt.account_id 两键，
    用户其他配置原样保留（原子替换写入；文件不存在时以默认+说明打底）。"""
    data: dict = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return False
        except (OSError, json.JSONDecodeError):
            return False
    else:
        data = {
            "_使用说明": ["config.json 由系统自动生成（QMT 自动发现写入）；"
                          "qmt.dry_run=true 只生成委托不真实报单，联调通过后改 false"],
            **default_config_json(),
        }
    qmt = data.get("qmt")
    if not isinstance(qmt, dict):
        qmt = dict(asdict(QmtConfig()))
    if qmt_path:
        qmt["qmt_path"] = qmt_path
    if account_id:
        qmt["account_id"] = str(account_id)
    data["qmt"] = qmt
    tmp = CONFIG_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CONFIG_FILE)
        return True
    except OSError:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        return False


def ensure_dirs() -> None:
    for d in (DATA_DIR, DAILY_DIR, LOGS_DIR, STATE_DIR):
        os.makedirs(d, exist_ok=True)


def default_config_json() -> dict:
    cfg = AppConfig()
    out = {"mode": cfg.mode}
    for k in _DATACLASS_MAP:
        out[k] = asdict(getattr(cfg, k))
    return out


def write_example_config() -> str:
    """生成 config.example.json（合法 JSON，含使用说明键；复制为 config.json 后按需修改）。"""
    example = os.path.join(ROOT, "config.example.json")
    data = default_config_json()
    data = {
        "_使用说明": [
            "复制本文件为 config.json 后按需修改（config.json 已被 gitignore，不会泄露账号）",
            "mode: paper=模拟盘 | live=实盘（需 QMT 配置齐全 + 券商程序化报备）",
            "qmt.account_id: 资金账号; qmt.qmt_path: QMT 安装目录下 userdata_mini 路径",
            "qmt.xtquant_path: pip 装不了 xtquant 时填 QMT 自带库目录，留空则用 pip 安装版",
            "qmt.dry_run: true 时实盘只生成委托不真实报单，联调通过后改 false",
            "风控参数改动会让回测与实盘口径不一致，建议保持默认稳健档",
        ],
        **data,
    }
    with open(example, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return example


def resolve_workers(cfg: "AppConfig") -> int:
    """解析并行进程数：evolve.workers=0 → 自动=min(24, 逻辑核-2)（留2核给系统/守护主进程；
    2026-09-21 用户"疯狂加速"16→24）。"""
    w = int(getattr(cfg.evolve, "workers", 0))
    if w > 1:
        return w
    if w == 1:
        return 1
    cores = os.cpu_count() or 4
    return max(2, min(24, cores - 2))


def backtest_fingerprint(cfg: "AppConfig") -> str:
    """影响回测/适应度结果的全部配置指纹——任一参数变化，本地评估缓存自动整体失效。"""
    import hashlib
    r, f, e = cfg.risk, cfg.fee, cfg.evolve
    payload = json.dumps({
        "capital": r.initial_capital, "stock_cap": r.max_position_pct,
        "etf_cap": r.max_etf_position_pct, "max_pos": r.max_positions,
        "stop": r.stop_loss_pct, "min_hold": r.min_hold_days, "max_hold": r.max_hold_days,
        "target_vol": getattr(r, "target_vol", 0.0), "vol_floor": getattr(r, "vol_scale_floor", 1.0),
        "daily_halt": r.daily_loss_limit_pct, "dd_halt": r.drawdown_halt_pct,
        "part": r.max_participation, "keep_cash": r.min_keep_cash_pct,
        "repo": [r.repo_enabled, r.repo_min_lend, r.repo_fee_rate,
                 r.repo_default_rate, r.repo_year_basis],
        "comm": f.commission_rate, "min_comm": f.min_commission, "stamp": f.stamp_duty,
        "transfer": f.transfer_fee, "slip": f.slippage,
        "dd_pen": e.backtest_max_dd_penalty, "min_trades": e.min_trades,
        "cagr_target": e.cagr_target, "holdout": e.holdout_pct, "slices": e.n_train_slices,
    }, sort_keys=True)
    return hashlib.md5(payload.encode("utf-8")).hexdigest()
