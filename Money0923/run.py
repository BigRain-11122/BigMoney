#!/usr/bin/env python
"""Money 自进化量化交易系统 · 主入口

核心命令：
  python run.py init                       初始化：配置示例/日历/股票池/历史数据
  python run.py evolve [-g 代数] [-m 分钟] 进化迭代（GA + 冠军晋升）
  python run.py status                    状态总览
  python run.py backtest                  现任冠军全历史回测
  python run.py prep                      手动生成次日订单
  python run.py paper [--replay N]        模拟盘：--replay N 历史回放验证；无参=盘中实时
  python run.py live [--force]            QMT 实盘会话（需 config.json 配置齐全）
  python run.py auto [-m 每轮分钟]        全自动守护：开市交易，闭市24小时连续进化+周度复盘
  python run.py review                   手动触发周度机制复盘（总结/衰退检测/机制调整）
  python run.py dashboard                重生成可视化仪表盘 dashboard.html（30秒自动刷新）
  python run.py blacklist show|add|refresh   负面清单（亏损/暴雷/衰亡行业/舆论负面）
  python run.py halt | resume             风控停机 | 人工复盘后恢复
  python run.py reset-account             模拟账户重置为100万（保留进化进度）
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging
import os
import sys
import time

import numpy as np

from quant import arena
from quant import clock
from quant.broker_qmt import discover_qmt
from quant.audit import run_audit_suite
from quant import data as qdata
from quant import minute_store
from quant import strategies as strat_lib
from quant.backtest import equal_weight_benchmark, run_backtest
from quant.config import LOGS_DIR, ROOT, STOP_FILE, ensure_dirs, load_config, write_example_config
from quant.decide import prepare_orders, team_members, team_target_weights
from quant.evolve import Evolver, random_point_test, walk_forward
from quant.futures import update_futures_daily
from quant.handoff import context_blob, write_handoff
from quant.gpu_screen import gpu_available, gpu_screen, inject_to_population
from quant.live import LiveSession
from quant.paper import PaperSession, run_replay
from quant.regime import regime_step
from quant.report import metrics_line, print_status, weekly_review
from quant.state import halt_now, load_state, reset_account, resume, save_state
from quant.viz import render_dashboard
from quant.verify import verify_execution

log = logging.getLogger("run")


def _setup_logging() -> None:
    ensure_dirs()
    fmt_short = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%m-%d %H:%M:%S")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt_short)
    root.addHandler(sh)
    fh = logging.FileHandler(os.path.join(LOGS_DIR, "auto.log"), encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(fh)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# ---------------------------------------------------------------- 命令实现

def cmd_init(args) -> None:
    cfg, state = load_config(), load_state()
    ensure_dirs()
    path = write_example_config()
    clock.trade_dates()  # 拉取交易日历
    uni, panel = qdata.full_panel(cfg, refresh=True)
    print(f"初始化完成。配置示例: {path}")
    print(f"股票池: {len(uni)} 只 | 行情面板: {panel.dates[0].date()} ~ {panel.dates[-1].date()}"
          f"（{len(panel.dates)} 个交易日 × {len(panel.codes)} 标的）")
    print("下一步: python run.py evolve   （开始进化迭代）")
    print_status(cfg, state)


def cmd_evolve(args) -> None:
    cfg, state = load_config(), load_state()
    print("加载数据（增量更新）...")
    _, panel = qdata.full_panel(cfg)
    ev = Evolver(cfg, panel, state)
    print(f"进化开始: 种群{cfg.evolve.population} | 计划{args.gens}代 | 时间盒{args.minutes}分钟 | "
          f"训练切片{cfg.evolve.n_train_slices}段 | 样本外保留{cfg.evolve.holdout_pct:.0%}")
    ev.run(generations=args.gens, time_budget_s=args.minutes * 60)
    save_state(state)
    print_status(cfg, state)


def cmd_status(args) -> None:
    cfg, state = load_config(), load_state()
    print_status(cfg, state)
    for line in arena.arena_status(state):
        print(line)


def cmd_stats(args) -> None:
    """统计中心：好的坏的全量统计（控制台 + HTML可视化面板）。"""
    from quant.stats import refresh_dashboard, render_text
    cfg, state = load_config(), load_state()
    print(render_text(cfg, state))
    path = refresh_dashboard(cfg, state)
    print(f"\n可视化面板 → {path}（浏览器直接打开，红=亏 绿=赚，❌未过的体检也照登）")


def cmd_backtest(args) -> None:
    cfg, state = load_config(), load_state()
    members = team_members(state)
    if not members:
        sys.exit("暂无冠军团队（先 run.py evolve）")
    _, panel = qdata.full_panel(cfg)
    w = team_target_weights(cfg, state, panel)
    res = run_backtest(panel, w, cfg)
    bench = equal_weight_benchmark(panel, cfg.risk.initial_capital)
    b = bench.iloc[-1] / bench.iloc[0] - 1
    print(f"冠军团队全历史回测（{panel.dates[0].date()} ~ {panel.dates[-1].date()}）")
    print("  团队:", " + ".join(m["strategy"] for m in members))
    print("  组合:", metrics_line(res.metrics))
    print(f"  等权基准: 区间收益 {b * 100:+.2f}%")
    eq_path = os.path.join(LOGS_DIR, "champion_equity.csv")
    res.equity.to_csv(eq_path)
    if res.trades:
        import pandas as pd
        pd.DataFrame(res.trades).to_csv(os.path.join(LOGS_DIR, "champion_trades.csv"), index=False)
    print(f"  净值曲线→{eq_path}")


def cmd_walkforward(args) -> None:
    cfg, state = load_config(), load_state()
    print("Walk-Forward 链式验证：把历史当实盘（每窗：进化→组队→下段实盘化撮合）...")
    walk_forward(cfg, n_windows=args.windows, gens=args.gens)


def cmd_prep(args) -> None:
    cfg, state = load_config(), load_state()
    orders, info = prepare_orders(cfg, state)
    if not orders:
        print("无订单（无冠军/停机/已达标不需调仓）:", info)
        return
    print(f"次日订单 {len(orders)} 笔:")
    for o in orders:
        print(f"  {o['side']:4s} {o['code']} {o['shares']}股 [{o.get('reason')}]")
    save_state(state)


def cmd_paper(args) -> None:
    cfg, state = load_config(), load_state()
    if args.replay:
        run_replay(cfg, state, days=args.replay)
    else:
        ok = PaperSession(cfg, state, force=args.force).run()
        if not ok:
            print("（提示：盘中运行；闭市请用 --replay N 做历史回放验证）")


def cmd_live(args) -> None:
    cfg, state = load_config(), load_state()
    if cfg.mode != "live" and not args.force:
        sys.exit("config.json 的 mode 不是 live。确认无误后使用 --force，或先把 mode 改为 live")
    LiveSession(cfg, state, force=args.force).run()


def cmd_qmt_scan(args) -> None:
    """QMT 自动发现（全自动化接入入口）：扫 userdata_mini → 写回 config.json。"""
    try:
        import xtquant  # noqa: F401
        print("xtquant: 已安装")
    except ImportError:
        print("xtquant: 未安装（pip install xtquant，或把 QMT 自带库目录填 qmt.xtquant_path）")
    hit = discover_qmt()
    if hit is None:
        print("未发现 QMT 安装（userdata_mini 未检出）。")
        print("装好 QMT（极简模式）后重跑本命令，或等守护下次启动自动接入。")
        return
    from quant.config import update_qmt_fields
    if update_qmt_fields(hit[0], hit[1]):
        print(f"已写入 config.json：qmt_path={hit[0]}")
        print(f"account_id={hit[1] or '(未从目录提取到——在QMT客户端查看资金账号后补填此一项)'}")
    else:
        print("发现 QMT 但写回 config.json 失败（检查文件占用/权限）。")


def cmd_auto(args) -> None:
    cfg, state = load_config(), load_state()
    # 全自动化接入（用户指令 2026-09-20：决策自主，不人工填值）：
    # 本机装好 QMT 后，守护启动时自动发现 userdata_mini 并写回配置，下次启动生效。
    if not cfg.qmt.qmt_path:
        try:
            hit = discover_qmt()
            if hit is not None:
                from quant.config import update_qmt_fields
                if update_qmt_fields(hit[0], hit[1]):
                    cfg.qmt.qmt_path, cfg.qmt.account_id = hit
                    log.info("QMT 自动发现成功，已写入 config.json：%s | 账号 %s（下次启动按新配置连接）",
                             hit[0], hit[1] or "未提取到")
            else:
                log.info("QMT 自动发现：本机未检出（未安装/未装好）；装好后守护重启即自动接入")
        except Exception as ex:  # noqa: BLE001 发现失败不阻塞模拟盘/进化
            log.warning("QMT 自动发现异常（不影响运行）: %s", ex)
    log.info("auto 全自动守护启动（24小时进化模式）：mode=%s | 每轮进化上限=%d分钟",
             cfg.mode, args.round_minutes)
    # 代码版本快照（HANDOFF.md 每周期对比磁盘现值→新会话立刻看出"有无待重启载入的改动"）
    try:
        from quant.handoff import code_fingerprint, write_handoff
        state["auto"]["code_files"] = code_fingerprint()
        state["auto"]["code_loaded_at"] = dt.datetime.now().isoformat(timespec="seconds")
        save_state(state)
        write_handoff(cfg, state, reason="守护启动")
    except Exception:
        log.exception("代码快照/HANDOFF 生成失败（不阻塞守护）")
    while True:
        try:
            if os.path.exists(STOP_FILE):
                log.warning("STOP 文件存在：守护挂起（恢复请删除 STOP 并 run.py resume）")
                time.sleep(60)
                state = load_state()
                continue
            now = dt.datetime.now()
            today = now.date()
            today_key = today.strftime("%Y%m%d")
            t = now.time()
            trading = clock.is_trade_date(today)

            if trading and dt.time(9, 25) <= t <= dt.time(15, 6):
                if state["auto"].get("session_date") != today_key:
                    log.info("交易日盘中：启动 %s 会话", "实盘" if cfg.mode == "live" else "模拟盘")
                    if cfg.mode == "live":
                        LiveSession(cfg, state).run()
                    else:
                        PaperSession(cfg, state).run()
                    state = load_state()
                else:
                    time.sleep(60)
            elif trading and t < dt.time(9, 25):
                _prep_once(cfg, state, today_key)
                state = load_state()
                # 盘前空窗进化（2026-09-21 用户指令"放开手脚/实战检验"）：交易日凌晨
                # 00:00→09:20 不再整夜沉睡——进化照常跑（每轮结束自动刷新备单），
                # 新晋团队当晚上位、当日开盘即可执行。时间不足一轮时等待，09:20 末次备单。
                while True:
                    _now2 = dt.datetime.now()
                    if _now2.time() >= dt.time(9, 20):
                        break
                    _remain = (dt.datetime.combine(today, dt.time(9, 20)) - _now2).total_seconds()
                    if _remain > max((args.round_minutes + 6) * 60, 45 * 60):
                        # 实测单次调用≈30-40分钟（联赛13+GA15+日常块），
                        # 最后一轮须预留≥45分钟，确保09:20末次备单不冲过开盘线
                        _off_hours_evolve(cfg, state, today_key, args.round_minutes)
                        state = load_state()
                    else:
                        time.sleep(min(300, max(1, _remain - 60)))
                try:
                    state["auto"]["last_prep_date"] = None  # 清除按日守卫：允许用最新团队重备单
                    _prep_once(cfg, state, today_key)
                except Exception:
                    log.exception("盘前末次备单失败（沿用上一轮备单）")
                state = load_state()
                _sleep_until(dt.datetime.combine(today, dt.time(9, 25)))
            elif trading and t <= dt.time(15, 30):
                # 收盘后立即恢复历史虚拟实战（用户指令2026-09-21：非实盘时间用
                # 历史时间点数据建虚拟盘去测、不浪费算力）——联赛跑历史随机窗，
                # 无需等收盘数据落定；盘中会话收盘结算已完成数据与轨道写入。
                _off_hours_evolve(cfg, state, today_key, args.round_minutes)
                state = load_state()
                _sleep_until_next_open()
            else:
                # 闭市时段（盘后/夜盘/周末/节假日）：24小时连续进化直到下一开市
                _off_hours_evolve(cfg, state, today_key, args.round_minutes)
                state = load_state()
                _sleep_until_next_open()
        except KeyboardInterrupt:
            log.info("收到中断，auto 退出")
            break
        except Exception:
            log.exception("auto 循环异常，60秒后重试")
            time.sleep(60)


def _next_open_dt(now: dt.datetime) -> dt.datetime:
    day = now.date()
    if clock.is_trade_date(day) and now.time() < dt.time(9, 25):
        return dt.datetime.combine(day, dt.time(9, 25))
    d = day
    for _ in range(60):
        d += dt.timedelta(days=1)
        if clock.is_trade_date(d):
            return dt.datetime.combine(d, dt.time(9, 25))
    return dt.datetime.combine(day + dt.timedelta(days=1), dt.time(9, 25))


def _off_hours_evolve(cfg, state, today_key: str, round_minutes: int) -> None:
    """闭市时段：增量数据一次 → 24小时连续进化（精英池跨轮续跑）→ 开市前备单。

    说明：同一批数据上无限进化的边际收益会衰减且有过拟合倾向，因此
    ① 样本外晋升尝试有每日上限（evolve.max_promote_attempts_per_day）
    ② 每轮之间短暂歇息 ③ 进化代数全部留痕可审计。
    周度机制复盘自动触发：轨道绩效总结 → 冠军衰退检测 → 衰退则进化引擎注入移民重启搜索。
    每周末自动跑一次 walk-forward 链式验证（历史当实盘，进化用临时状态不污染线上）。
    """
    try:
        # —— 周度机制复盘（每ISO周一次；到复盘日自动触发，也可 run.py review 手动）——
        try:
            rp = weekly_review(cfg, state)
            if rp:
                log.info("【周度机制复盘】→ %s", rp)
        except Exception:
            log.exception("周度复盘失败（不阻塞进化）")
        # —— walk-forward 链式验证（每ISO周一次：历史当实盘的滚动无未来函数轨道）——
        try:
            wk = f"{dt.date.today().isocalendar().year}-W{dt.date.today().isocalendar().week:02d}"
            if state.setdefault("meta", {}).get("last_wf_week") != wk:
                log.info("【walk-forward】本周首次运行：链式验证启动（历史当实盘）...")
                walk_forward(cfg)
                state["meta"]["last_wf_week"] = wk
                save_state(state)
        except Exception:
            log.exception("walk-forward 链式验证失败（不阻塞进化）")
        _, panel = qdata.full_panel(cfg)  # 增量更新（当日已更新则为空跑）
        state["auto"]["last_data_date"] = today_key
        save_state(state)
        # —— 本地分钟语料入库（每日；新浪1分钟仅滚动~9个交易日，不存即永久丢失）——
        try:
            r = minute_store.maybe_collect(cfg, panel)
            if not r.get("skipped"):
                log.info("【本地能力】分钟语料库 +%d 日（累计 %d 交易日）",
                         len(r.get("saved") or []), len(minute_store._stored_days()))
        except Exception:
            log.exception("分钟语料入库失败（不阻塞进化）")
        # —— 期货主力连续日更（CTA 自服务通道数据源；闸关也保鲜，开闸即用）——
        try:
            upd = update_futures_daily(cfg)
            if upd:
                log.info("【期货数据】主力连续日更 %d 品种：%s", len(upd), ",".join(upd))
        except Exception:
            log.exception("期货数据日更失败（不阻塞进化）")
        # —— 国债逆回购利率日更（GC001/204001，回测隔夜计息+模拟盘收盘借出用）——
        try:
            from quant.repo import update_repo_daily
            n_rates = update_repo_daily()
            if n_rates == 0:
                log.warning("【逆回购】利率日更拉取失败（回测/结算自动回退默认利率）")
        except Exception:
            log.exception("逆回购利率日更失败（不阻塞进化）")
        # —— 市场风格引擎：识别当下风格 → 验证冠军/各族近段 → 曝光系数与进化提示 ——
        try:
            regime_step(cfg, state, panel)
        except Exception:
            log.exception("风格引擎失败（不阻塞进化，沿用上次快照）")
        # —— 随机取点体检（每日）：团队在历史随机窗口的全规则压力验证 ——
        # 不过线 → 置位冠军衰退信号 → GA 注入移民重启搜索（验证闭环反哺进化）
        try:
            rpt = random_point_test(cfg, state, panel, seed=int(today_key))
            s = rpt["summary"]
            state.setdefault("stress_history", []).append({
                "date": dt.date.today().isoformat(),
                **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()}})
            state["stress_history"] = state["stress_history"][-30:]
            ok = (s["mean"] >= cfg.meta.stress_min_mean
                  and s["beat_cash_pct"] >= cfg.meta.stress_min_beat_pct)
            if ok:
                log.info("【随机取点体检】%d窗 均分%.3f | 跑赢持币%.0f%% | 跑赢基准%.0f%% | 最差%.3f",
                         s["windows"], s["mean"], s["beat_cash_pct"] * 100,
                         s["beat_bench_pct"] * 100, s["worst"])
                state["meta"]["stress_defense"] = False
            else:
                log.warning("【随机取点体检未过】均分%.3f 跑赢持币%.0f%% → 置位衰退信号(GA重启搜索) + "
                            "曝光系数减半(防御态，直至体检通过或新冠军上位)",
                            s["mean"], s["beat_cash_pct"] * 100)
                state["meta"]["champion_decay"] = True
                state["meta"]["stress_defense"] = True  # regime 引擎将尊重此防御上限
                state.setdefault("regime", {})["exposure_scale"] = 0.5
            save_state(state)
        except Exception:
            log.exception("随机取点体检失败（不阻塞进化）")
        # —— 防作弊审计（每日）：无未来函数抽查+复算一致性+先声明后揭示台账 ——
        # 用户红线要求：模拟验证不得提前知道走势/结果；审计为只读，不写 state。
        try:
            aud = run_audit_suite(cfg, state, panel=panel)
            if aud.get("passed"):
                log.info("【防作弊审计】✅ 通过：截断重算一致（无未来函数）+复算一致（无幻觉）"
                         "｜台账 logs/audit_ledger.jsonl")
            elif aud.get("reason") != "no_team":
                log.error("【防作弊审计】❌ 未通过！详情见 logs/audit_*.md——未排查前不得实盘")
        except Exception:
            log.exception("防作弊审计失败（不阻塞进化）")
        # —— 百人锦标赛：每晚全员前瞻结算（参数冻结的模拟实盘竞赛）+ 周六重赛——
        try:
            if not (state.get("arena") or {}).get("players"):
                arena.spawn_players(cfg, state)
            arena.advance_day(cfg, state, panel)
            wk = f"{dt.date.today().isocalendar().year}-W{dt.date.today().isocalendar().week:02d}"
            if dt.date.today().weekday() == cfg.meta.weekly_review_weekday \
                    and (state.get("arena") or {}).get("last_tournament_week") != wk:
                arena.run_tournament(cfg, state, panel=panel, label="周度锦标赛")
                state["arena"]["last_tournament_week"] = wk
                save_state(state)
        except Exception:
            log.exception("锦标赛推进失败（不阻塞进化）")
        ev = Evolver(cfg, panel, state)
        # —— GPU 广域海选（RTX 4070 SUPER）：万级参数批量筛查 → Top候选注入GA当移民 ——
        # 必须用训练期面板（与GA目标同窗）；不可用时自动跳过（CPU GA照常）
        try:
            if gpu_available():
                cands = gpu_screen(cfg, ev.train_panel,
                                   per_family=cfg.evolve.gpu_screen_per_family,
                                   top_k_out=cfg.evolve.gpu_screen_top)
                added = inject_to_population(state, cands, cap=int(cfg.evolve.population))
                if added:
                    log.info("【GPU海选】注入 %d 个广域候选进GA种群（Top分 %.3f）",
                             added, cands[0]["gpu_score"] if cands else 0.0)
                    save_state(state)
        except Exception:
            log.exception("GPU 海选失败（不阻塞进化）")
        target = _next_open_dt(dt.datetime.now()) - dt.timedelta(minutes=20)
        rounds = 0
        while dt.datetime.now() < target and rounds < 3000:
            left = (target - dt.datetime.now()).total_seconds()
            if left < 90:
                break
            # —— 联赛循环赛（用户指定机制）：随机1年窗开局，前10晋级+换血，
            #    连续3局稳定前10认证→基因注入GA种群参与团队竞争。高频迭代核心。
            #    时间盒 240→480s（用户指令"迭代频率疯狂加速"，批级常驻池已省20-30%开销） ——
            try:
                n_league = arena.run_rounds(cfg, state, panel=panel,
                                            time_budget_s=min(left, 480), persist=True)
                if n_league:
                    log.info("【联赛】本段开局 %d 局", n_league)
            except Exception:
                log.exception("联赛循环异常（不阻塞GA）")
            ev.run(time_budget_s=min(left, round_minutes * 60))
            rounds += 1
            time.sleep(10)
            # —— 可视化自动迭代：每轮进化后重生成仪表盘（浏览器挂着即实时"看盘"） ——
            try:
                render_dashboard(cfg, state)
            except Exception:
                log.debug("仪表盘重生成失败（不阻塞进化）")
            # —— 周期交接文档（用户指令2026-09-22：每周期落盘，新AI会话随时接手） ——
            try:
                from quant.handoff import write_handoff
                write_handoff(cfg, state, reason=f"闭市进化第{rounds}轮")
            except Exception:
                log.debug("HANDOFF 重生成失败（不阻塞进化）")
            # —— 盘中风格实时再校验（每4轮≈1小时刷新一次曝光系数，应对盘中风格突变）——
            if rounds % 4 == 0:
                try:
                    regime_step(cfg, state, panel)
                except Exception:
                    log.debug("盘中风格刷新失败（忽略）")
        prepare_orders(cfg, state, panel=panel, today_key=today_key)
        state["auto"]["last_prep_date"] = today_key
        state["auto"]["last_evolve_date"] = today_key
        save_state(state)
        log.info("闭市进化阶段结束：本轮 %d 轮 / 累计第%d代 / 冠军=%s（样本外晋升今日已试 %d 次）",
                 rounds, state["evolution"]["generation"],
                 (state.get("champion") or {}).get("strategy"),
                 state["evolution"].get("promote_count", 0))
    except Exception:
        log.exception("闭市进化异常（下一轮重试）")


def _prep_once(cfg, state, today_key: str) -> None:
    if state["auto"].get("last_prep_date") == today_key:
        return
    try:
        prepare_orders(cfg, state, today_key=today_key)
        state["auto"]["last_prep_date"] = today_key
        save_state(state)
    except Exception:
        log.exception("备单失败（盘中会话会兜底重试）")


def _sleep_until(target: dt.datetime) -> None:
    while True:
        remain = (target - dt.datetime.now()).total_seconds()
        if remain <= 0:
            return
        time.sleep(min(300, max(1, remain)))


def _sleep_until_next_open() -> None:
    now = dt.datetime.now()
    day = now.date()
    if clock.is_trade_date(day) and now.time() < dt.time(9, 20):
        target = dt.datetime.combine(day, dt.time(9, 20))
    else:
        d = day
        for _ in range(60):
            d += dt.timedelta(days=1)
            if clock.is_trade_date(d):
                break
        target = dt.datetime.combine(d, dt.time(9, 20))
    log.info("休眠至 %s（下一开市前）", target)
    _sleep_until(target)


def cmd_dashboard(args) -> None:
    """重生成可视化仪表盘；--watch 为独立看护循环（每分钟自动重渲染，不依赖主守护重启）。"""
    cfg, state = load_config(), load_state()
    path = render_dashboard(cfg, state)
    print(f"仪表盘已生成 → {path}")
    if not args.watch:
        print("用浏览器打开并保持窗口挂着即可，30秒自动刷新；守护每轮进化后会自动更新它。")
        return
    print(f"看护模式：每 {args.watch} 秒自动重渲染（Ctrl+C 退出）。")
    import time as _t
    while True:
        try:
            _t.sleep(max(20, args.watch))
            render_dashboard(load_config(), load_state())
        except KeyboardInterrupt:
            print("仪表盘看护退出")
            break
        except Exception:
            import logging
            logging.getLogger("run").exception("仪表盘重渲染失败（下一轮重试）")


def cmd_review(args) -> None:
    cfg, state = load_config(), load_state()
    path = weekly_review(cfg, state, force=True)
    if path:
        print(f"复盘报告 → {path}")
        with open(path, encoding="utf-8") as f:
            print(f.read())
    else:
        print("无数据可复盘")
    save_state(state)


def cmd_arena(args) -> None:
    cfg, state = load_config(), load_state()
    if args.players:
        cfg.arena.size = args.players
    if args.spawn:
        state["arena"] = {}
        print("重新派员：旧选手与前瞻轨道已清空")
    players = arena.spawn_players(cfg, state, force=bool(args.spawn))
    print(f"已派出 {len(players)} 名选手，各携 {cfg.arena.capital:,.0f} 元本金，全员本地运算")
    print("锦标赛开赛（并行回测中，约1-3分钟）...")
    rep = arena.run_tournament(cfg, state, period_days=args.period_days)
    if rep and rep.get("rows"):
        rows = rep["rows"]
        print("\n" + "=" * 78)
        print(f"百人锦标赛战绩 · 前10名（{len(rows)} 名完赛，口径=冻结参数历史分段模拟）")
        print(f"{'排名':<4}{'选手':<6}{'策略':<18}{'累计':>9}{'年化':>9}{'回撤':>8}{'夏普':>7}{'正收益段':>9}")
        for i, r in enumerate(rows[:10], 1):
            print(f"{i:<4}{r['id']:<6}{r['strategy']:<18}{r['total_return']*100:>+8.1f}%"
                  f"{r['cagr']*100:>+8.1f}%{r['max_dd']*100:>7.1f}%{r['sharpe']:>7.2f}"
                  f"{r['pos_periods']:>6}/{r['n_periods']}")
        med = float(np.median([r["total_return"] for r in rows]))
        print(f"中位 {med*100:+.1f}% | 最差 {rows[-1]['id']} {rows[-1]['total_return']*100:+.1f}%")
        print(f"完整分段战绩 → {rep['report']}（含逐段矩阵CSV）")
        print("优胜者基因已注入 GA 种群参与冠军竞争")
    save_state(state)


def cmd_regime(args) -> None:
    cfg, state = load_config(), load_state()
    print("加载数据...")
    _, panel = qdata.full_panel(cfg)
    snap = regime_step(cfg, state, panel)
    print("\n" + "=" * 60)
    print("当前市场风格 · 模型近段验证")
    print("=" * 60)
    for k in ("trend", "factor_style", "size_style", "breadth"):
        print(f"  {k}: {snap.get(k)}")
    print(f"  波动分位: {snap.get('vol_pct')}（高波={snap.get('vol_high')}）")
    cr = snap.get("champion_recent") or {}
    bs = snap.get("best_family_now") or {}
    if cr:
        print(f"  冠军近段({cfg.meta.recent_days}日): 夏普 {cr.get('sharpe')} / 收益 {cr.get('ret')}")
    if bs:
        print(f"  当前最适族: {bs.get('family')}（夏普 {bs.get('sharpe')}）")
    print(f"  曝光系数: ×{snap.get('exposure_scale')} | 风格错配: {snap.get('mismatch')} | "
          f"敌对风格: {snap.get('hostile')}")
    print("=" * 60)


def cmd_stress(args) -> None:
    cfg, state = load_config(), load_state()
    print("加载数据...")
    _, panel = qdata.full_panel(cfg)
    try:
        rpt = random_point_test(cfg, state, panel, n_windows=args.windows)
    except RuntimeError as e:
        sys.exit(str(e))
    s = rpt["summary"]
    print("\n" + "=" * 66)
    print(f"随机取点压力验证 · 冠军团队 {rpt['members']} × {s['windows']} 个随机窗口")
    print("=" * 66)
    print(f"{'窗口':<24}{'策略收益':>10}{'等权基准':>10}{'最大回撤':>10}{'复合分':>8}")
    for d in rpt["details"]:
        print(f"{d['window']:<26}{d['ret']*100:>9.2f}%{d['bench']*100:>9.2f}%"
              f"{d['max_dd']*100:>9.1f}%{d['score']:>8.3f}")
    print("-" * 66)
    print(f"均分 {s['mean']:.4f}（σ {s['std']:.4f}） | 跑赢持币 {s['beat_cash_pct']*100:.0f}% | "
          f"跑赢基准 {s['beat_bench_pct']*100:.0f}% | 最差 {s['worst']:.4f} / 最好 {s['best']:.4f}")
    verdict = (s["mean"] >= cfg.meta.stress_min_mean
               and s["beat_cash_pct"] >= cfg.meta.stress_min_beat_pct)
    print(f"体检结论：{'通过 ✅' if verdict else '未通过 ❌（今晚将置位衰退信号触发GA重启搜索）'}")
    # 报告落盘
    lines = [f"# 随机取点压力验证（{dt.datetime.now():%Y-%m-%d %H:%M}）",
             f"- 团队: {rpt['members']} | 窗口数: {s['windows']}（起点/长度均随机）",
             "", "| 窗口 | 策略收益 | 等权基准 | 最大回撤 | 复合分 |", "|---|---|---|---|---|"]
    for d in rpt["details"]:
        lines.append(f"| {d['window']} | {d['ret']*100:+.2f}% | {d['bench']*100:+.2f}% | "
                     f"{d['max_dd']*100:.1f}% | {d['score']} |")
    lines += ["", f"**均分 {s['mean']} | 跑赢持币 {s['beat_cash_pct']*100:.0f}% | "
              f"跑赢基准 {s['beat_bench_pct']*100:.0f}% | 最差 {s['worst']} | 结论："
              f"{'通过' if verdict else '未通过'}**"]
    path = os.path.join(LOGS_DIR, f"stress_{dt.date.today().strftime('%Y%m%d')}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"报告 → {path}")


def cmd_audit(args) -> None:
    """防作弊审计：证明模拟验证看不到未来（截断重算一致）+ 结果非幻觉（复算一致）。"""
    cfg, state = load_config(), load_state()
    print("加载数据（只读审计，不写账户状态）...")
    run_audit_suite(cfg, state)


def cmd_verify(args) -> None:
    cfg, state = load_config(), load_state()
    verify_execution(cfg, state, days=args.days)


def cmd_league(args) -> None:
    """联赛循环赛（手动）：随机1年窗口开局，前10晋级+换血，稳定前10认证。"""
    cfg, state = load_config(), load_state()
    if args.players:
        cfg.arena.size = args.players
    print("加载数据（增量更新）...")
    _, panel = qdata.full_panel(cfg)
    if not (state.get("arena") or {}).get("players"):
        arena.spawn_players(cfg, state)
    print(f"联赛开局：{cfg.arena.size} 名选手 × {cfg.arena.capital:,.0f} 元/人 | "
          f"一局=随机起点{cfg.arena.round_days}交易日（1年） | 前10晋级 | "
          f"连续{cfg.arena.qualify_streak}局稳定前10认证")
    n = arena.run_rounds(cfg, state, panel=panel, time_budget_s=args.minutes * 60)
    print(f"\n本批完成 {n} 局")
    for line in arena.arena_status(state):
        print(line)


def cmd_top10(args) -> None:
    """多维实战Top10：8维度各出前十（盈利最多/最稳定/概率最高/夏普/抗跌/极端存活/胜率/晋级）+ 前瞻轨道榜。"""
    cfg, state = load_config(), load_state()
    print(arena.dimension_report(cfg, state, top_n=args.top, min_rounds=args.min_rounds))


def cmd_minute(args) -> None:
    """本地能力中心：分钟语料库状态 + 全部本地算力资产盘点；--collect 手动补采。"""
    cfg = load_config()
    if args.collect:
        _, panel = qdata.full_panel(cfg)
        r = minute_store.maybe_collect(cfg, panel, force=args.force)
        print(f"入库结果: 新增 {len(r.get('saved') or [])} 个交易日"
              f"（窗口 {len(r.get('days') or [])} 日 × {r.get('n_codes', 0)} 标的）")
    st = minute_store.status()
    print("=" * 60)
    print("本地能力资产盘点（用户指令：能本地算就本地算）")
    print("=" * 60)
    for line in minute_store.capability_inventory(cfg):
        print("· " + line)
    print(f"· 分钟语料目录: {st['dir']}")
    print(f"· 消费接口: quant.minute_store.load_day('YYYYMMDD') → 全宇宙当日1分钟K线")
    # 资源利用率实测（用户指令2026-09-21：非实盘时间跑历史虚拟实战，不浪费算力）
    try:
        state = load_state()
        a = state.get("arena") or {}
        ps = (a.get("pstats") or {})
        n_max = max((s.get("n") or 0 for s in ps.values()), default=0)
        n_total = sum((s.get("n") or 0) for s in ps.values())
        g = a.get("game") or {}
        print("-" * 60)
        print(f"资源利用率：联赛累计 {a.get('round', 0)} 局 × 100 队"
              f"（每局=随机历史时间点1年窗全规则虚拟实战）")
        print(f"· 实战样本已累积 {n_total:,} 人·局（单选手最多 {n_max} 局）")
        print(f"· 覆盖时段：盘后15:06起 / 夜间 / 周末 / 交易日00:00-09:05（盘前进化）")
        print(f"· 玩法自进化：偏置{g.get('recent_bias', 0.2)}"
              f" 门槛{g.get('qualify_floor') or '默认'} 每30分钟一拍")
        print("· 已知空闲段：盘中会话09:25-15:06（会话优先，待首个交易日"
              "稳定后评估是否并行跑历史采样）")
    except Exception as e:  # noqa: BLE001
        print(f"(利用率统计失败: {e})")


def cmd_verdict(args) -> None:
    """「什么策略适合我」大样本裁决：族×风格实战矩阵+选才自检+实锤线。"""
    cfg, state = load_config(), load_state()
    print(arena.verdict_report(cfg, state, min_rounds=args.min_rounds))


def cmd_game(args) -> None:
    """玩法自进化面板：当前玩法参数 + 每半小时节拍的调整台账与公平审计记录。"""
    from quant import game_evo
    cfg, state = load_config(), load_state()
    print("\n".join(game_evo.game_status(state)))


def cmd_race(args) -> None:
    """百名交易员盘中实赛榜：100队冻结持仓×今日实时浮动，只读。"""
    cfg, state = load_config(), load_state()
    print(arena.live_race(cfg, state, top_n=args.top))


def cmd_sleeves(args) -> None:
    """多队并行分仓制面板：逐仓成员/权益/现金/停机/换人史（只读）。"""
    from quant import sleeves as qsl
    cfg, state = load_config(), load_state()
    if not state.get("sleeves"):
        print("分仓制未初始化（下次备单自动迁移：S1=现任冠军团队 | S2/S3=认证池多样性选队）")
        return
    from quant.decide import account_equity
    _, panel = qdata.full_panel(cfg)
    prices = {c: float(panel.close[c].dropna().iloc[-1]) if len(panel.close[c].dropna()) else 0.0
              for c in state["account"]["positions"]}
    from quant.futures import last_close
    for c in state["account"]["positions"]:
        if str(c).startswith("F."):
            prices[c] = last_close(str(c))
    print("=" * 62)
    print("多队并行分仓制（每仓独立10%停机线 · 队死换人资金保留 · 账户毁灭线80%兜底）")
    total = 0.0
    for sv in state["sleeves"]:
        seq = qsl.sleeve_equity(state, sv, prices)
        total += seq
        r = sv.get("risk") or {}
        hist = sv.get("history") or []
        n_pos = len(qsl.sleeve_positions(state, sv))
        ret = seq / float(sv.get("capital_start") or 1) - 1
        print("-" * 62)
        print(f"{qsl.sleeve_label(sv)} | 成员自 {sv.get('since')}")
        print(f"  权益 {seq:,.0f}（自起点 {ret:+.1%}）| 现金 {sv.get('cash', 0):,.0f} | "
              f"持仓 {n_pos} 只 | 高水位 {r.get('equity_high', 0):,.0f}")
        fielded = sv.get("fielded_ids") or []
        print(f"  换人 {sv.get('rotations', 0)} 次 | 历任选手 {len(fielded)} 人"
              f"{'（' + ','.join(str(x) for x in fielded[:6]) + '…）' if len(fielded) > 6 else ''}")
        for h in hist[-3:]:
            print(f"  {h.get('date')}: 权益 {h.get('equity'):,.0f} | 持仓 {h.get('n_pos')}"
                  f"{' | 停机' if h.get('halted') else ''}{' | 退役' if h.get('retired') else ''}")
    print("-" * 62)
    print(f"账户合计 {total:,.0f}（对照总权益 {account_equity(state, prices):,.0f}）")


def cmd_halt(args) -> None:
    state = load_state()
    with open(STOP_FILE, "w", encoding="utf-8") as f:
        f.write(dt.datetime.now().isoformat() + "\n")
    halt_now(state, "人工 halt 命令触发")
    print("已停机：STOP 文件已创建 + 风控停机标记。人工复盘后执行 run.py resume")


def cmd_blacklist(args) -> None:
    """负面清单维护与全量展示（用户四条规则的执行入口）。"""
    from quant import fundamental

    cfg, state = load_config(), load_state()
    bl = fundamental.load_blacklist()

    if args.action == "show":
        # 全量清单：手动部分 + 当前股票池的自动命中（亏损/暴雷/行业）
        try:
            uni = qdata.load_universe()
            names = dict(zip(uni["code"].astype(str), uni["name"].astype(str)))
            excl = fundamental.build_exclusions(cfg, uni["code"].tolist(), names,
                                                force_refresh=args.refresh)
        except Exception as e:  # noqa: BLE001
            excl = {}
            print(f"(自动命中计算失败: {e})")
        print("=" * 66)
        print("负面清单（四条规则：亏损/暴雷/衰亡行业/舆论负面 不做）")
        print(f"手动黑名单个股 {len(bl['codes'])} 只:")
        for c, r in bl["codes"].items():
            print(f"  {c}: {r}")
        print(f"排除行业关键词 {len(bl['industries'])} 个: {', '.join(bl['industries'])}")
        print(f"名称排除关键词: {', '.join(bl.get('names_contains', []))}")
        print("-" * 66)
        print(f"当前股票池自动命中 {len(excl)} 只（下次池刷新/备单即被剔除）:")
        by_reason: dict[str, list[str]] = {}
        for c, r in excl.items():
            by_reason.setdefault(r.split(":")[0], []).append(f"{c}{names.get(c, '')}")
        for k, lst in sorted(by_reason.items()):
            print(f"  [{k}] {len(lst)}只: {'; '.join(lst[:10])}{'...' if len(lst) > 10 else ''}")
        print("=" * 66)
    elif args.action == "add":
        if not args.code or len(args.code) != 6 or not args.code.isdigit():
            sys.exit("用法: run.py blacklist add 600000 舆论负面说明")
        reason = " ".join(args.reason) or "人工拉黑（未注明原因）"
        bl["codes"][args.code] = f"{reason} ({dt.date.today()})"
        fundamental.save_blacklist(bl)
        print(f"已拉黑 {args.code}: {reason}（备单/持仓三层强制执行，永久生效直至 remove）")
    elif args.action == "remove":
        if not args.code:
            sys.exit("用法: run.py blacklist remove 600000")
        if bl["codes"].pop(args.code, None) is not None:
            fundamental.save_blacklist(bl)
            print(f"已解除 {args.code}")
        else:
            print(f"{args.code} 不在黑名单中")
    elif args.action == "add-industry":
        if not args.code:
            sys.exit("用法: run.py blacklist add-industry 行业关键词")
        kw = args.code
        if kw not in bl["industries"]:
            bl["industries"].append(kw)
            fundamental.save_blacklist(bl)
        print(f"已排除行业关键词「{kw}」，当前: {', '.join(bl['industries'])}")
    elif args.action == "remove-industry":
        if not args.code:
            sys.exit("用法: run.py blacklist remove-industry 行业关键词")
        if args.code in bl["industries"]:
            bl["industries"].remove(args.code)
            fundamental.save_blacklist(bl)
        print(f"已移除行业关键词「{args.code}」，当前: {', '.join(bl['industries'])}")
    elif args.action == "refresh":
        df, rpt = fundamental.update_fundamentals(cfg, force=True)
        if df is not None:
            print(f"业绩数据已强制刷新：{rpt} 报告期 {len(df)} 只")
        else:
            print("业绩数据刷新失败（检查网络后重试）")



def cmd_gpu_screen(args) -> None:
    """GPU 广域海选（手动）：万级参数批量筛查 → Top候选注入GA种群。"""
    cfg, state = load_config(), load_state()
    if not gpu_available():
        print("GPU 不可用（无 CUDA / torch 未装）：海选跳过，GA 照常。")
        return
    print("加载数据（增量更新）...")
    _, panel = qdata.full_panel(cfg)
    ev = Evolver(cfg, panel, state)  # 用训练期面板（与GA目标同窗）
    cands = gpu_screen(cfg, ev.train_panel, per_family=args.per_family,
                       top_k_out=args.top)
    if not cands:
        print("未产出候选")
        return
    print(f"\nTop 候选（{len(cands)} 个，按 GPU 近似分降序）:")
    for c in cands[:15]:
        print(f"  {c['gpu_score']:.3f}  {c['strategy']:16s} {c['params']}")
    if args.inject:
        added = inject_to_population(state, cands, cap=int(cfg.evolve.population))
        save_state(state)
        print(f"\n已注入 {added} 个候选进 GA 种群（是否上位由精确适应度+闸门决定）")


def cmd_resume(args) -> None:
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)
    state = load_state()
    resume(state)
    print("已恢复：STOP 文件已删除，风控停机解除。auto 守护将自动继续。")


def cmd_reset_account(args) -> None:
    cfg, state = load_config(), load_state()
    reset_account(state, cfg.risk.initial_capital)
    save_state(state)
    print(f"模拟账户已重置为 {cfg.risk.initial_capital:,.0f} 元（进化进度保留）")


# ---------------------------------------------------------------- CLI

def main() -> None:
    _setup_logging()
    p = argparse.ArgumentParser(prog="run.py", description="Money 自进化量化交易系统")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="初始化：配置示例/日历/股票池/历史数据")

    sp = sub.add_parser("evolve", help="进化迭代")
    sp.add_argument("-g", "--gens", type=int, default=None, help="本次进化代数（默认配置值）")
    sp.add_argument("-m", "--minutes", type=int, default=30, help="时间盒（分钟），到时自动停")

    sub.add_parser("status", help="状态总览")
    sub.add_parser("stats", help="统计中心：好的坏的全量统计（逐笔胜负/离场归因/体检史/擂台/风控事件）")
    sub.add_parser("backtest", help="冠军团队全历史回测（资产组合口径）")

    sp = sub.add_parser("walkforward", help="链式滚动验证：历史当实盘（进化→组队→下段实盘化撮合）")
    sp.add_argument("-w", "--windows", type=int, default=None, help="滚动窗口数（默认配置 meta.wf_windows）")
    sp.add_argument("-g", "--gens", type=int, default=None, help="每窗进化代数（默认配置 meta.wf_gens）")

    sub.add_parser("prep", help="生成次日订单")

    sp = sub.add_parser("paper", help="模拟盘")
    sp.add_argument("--replay", type=int, default=None, metavar="N",
                    help="历史回放验证最近 N 个交易日（不传则盘中实时运行）")
    sp.add_argument("--force", action="store_true")

    sp = sub.add_parser("live", help="QMT 实盘会话")
    sp.add_argument("--force", action="store_true")

    sub.add_parser("qmt-scan", help="QMT 自动发现：扫描本机 userdata_mini，自动写回 config.json")

    sp = sub.add_parser("auto", help="全自动守护：开市交易/闭市24小时连续进化")
    sp.add_argument("-m", "--round-minutes", type=int, default=15,
                    help="闭市进化每轮时间上限（分钟），轮间歇息10秒，循环至下一开市")

    sub.add_parser("halt", help="紧急停机（STOP文件+风控停机）")
    sub.add_parser("resume", help="人工复盘后恢复")
    sp = sub.add_parser("gpu-screen", help="GPU 广域海选：万级参数批量筛查，Top候选注入GA种群")
    sp.add_argument("--per-family", type=int, default=None, help="每族采样参数组数（默认配置3000）")
    sp.add_argument("--top", type=int, default=None, help="每族取Top N（默认配置12）")
    sp.add_argument("--inject", action="store_true", help="注入 GA 种群（默认只展示）")
    sub.add_parser("review", help="手动触发周度机制复盘（总结→冠军衰退检测→机制调整）")
    sp = sub.add_parser("dashboard", help="手动重生成可视化仪表盘（浏览器打开30秒自动刷新）")
    sp.add_argument("--watch", type=int, default=0, metavar="秒",
                    help="看护模式：每N秒自动重渲染（如 --watch 60），与主守护解耦")
    sub.add_parser("regime", help="市场风格识别+模型近段验证（当前什么风格/什么策略有效）")
    sp = sub.add_parser("stress", help="随机取点压力验证：历史随机窗口检验冠军团队")
    sp.add_argument("-w", "--windows", type=int, default=None, help="随机窗口数（默认配置24）")
    sub.add_parser("audit", help="防作弊审计：无未来函数抽查+复算一致性+先声明后揭示台账")
    sp = sub.add_parser("arena", help="百人锦标赛：100名选手×10万同台竞技，分段出战绩")
    sp.add_argument("--spawn", action="store_true", help="强制重新派员（重置前瞻轨道）")
    sp.add_argument("--players", type=int, default=None, help="选手人数（默认配置100）")
    sp.add_argument("--period-days", type=int, default=None, help="战绩分段长度（默认20交易日/段）")
    sp = sub.add_parser("league", help="联赛循环赛：随机1年窗开局，前10晋级+换血，稳定前10认证")
    sp.add_argument("-m", "--minutes", type=int, default=30, help="本批开局时间盒（分钟）")
    sp.add_argument("--players", type=int, default=None, help="选手人数（默认配置100）")
    sp = sub.add_parser("verify", help="执行逻辑验证：近端真实分钟数据逐单检验撮合/止损/涨跌停假设")
    sp.add_argument("--days", type=int, default=40, help="近端回放窗口（交易日）")

    sp = sub.add_parser("blacklist", help="负面清单：亏损/暴雷/行业/黑名单（查看/维护/刷新业绩）")
    sp.add_argument("action", choices=["show", "add", "remove", "add-industry", "remove-industry", "refresh"],
                    help="show=全量清单(含自动命中) / add 编号 原因 / remove 编号 / add|remove-industry 行业关键词 / refresh=强制刷新业绩数据")
    sp.add_argument("code", nargs="?", default=None, help="股票/ETF 六位代码")
    sp.add_argument("reason", nargs="*", help="黑名单原因（舆论负面等，原样记录）")
    sp.add_argument("--refresh", action="store_true", help="show 时强制刷新业绩数据再展示")
    sub.add_parser("reset-account", help="模拟账户重置（保留进化进度）")
    sp = sub.add_parser("top10", help="多维实战Top10：8维度各出前十（盈利/稳定/概率/夏普/抗跌/极端/胜率/晋级）+前瞻榜")
    sp.add_argument("--top", type=int, default=10, help="每维度取前N名（默认10）")
    sp.add_argument("--min-rounds", type=int, default=20, help="入榜最低局数（默认20）")
    sp = sub.add_parser("minute", help="本地能力中心：分钟语料库状态+算力盘点（--collect 手动补采）")
    sp.add_argument("--collect", action="store_true", help="抓取滚动窗口分钟线并入库")
    sp.add_argument("--force", action="store_true", help="已存在的日文件也重新抓取覆盖")
    sp = sub.add_parser("verdict", help="「什么策略适合我」大样本裁决：族×风格实战矩阵+选才自检+实锤线")
    sp.add_argument("--min-rounds", type=int, default=50, help="入榜最低聚合局数（默认50）")
    sub.add_parser("game", help="玩法自进化面板：半小时节拍台账+公平审计记录")
    sp =     sub.add_parser("race", help="百名交易员盘中实赛榜：100队冻结持仓×今日实时浮动（只读）")
    sp.add_argument("--top", type=int, default=15, help="显示前N名（默认15）")
    sub.add_parser("sleeves", help="多队并行分仓制面板：逐仓成员/权益/停机/换人史（只读）")
    sub.add_parser("handoff", help="手动重生成 HANDOFF.md 周期交接文档（新AI会话接手包）")
    sub.add_parser("ctx", help="极简上下文快照（~300 token，新AI会话最省入口）")

    args = p.parse_args()
    actions = {
        "init": cmd_init, "evolve": cmd_evolve, "status": cmd_status, "stats": cmd_stats,
        "backtest": cmd_backtest, "walkforward": cmd_walkforward, "prep": cmd_prep,
        "paper": cmd_paper, "live": cmd_live, "auto": cmd_auto, "halt": cmd_halt,
        "qmt-scan": cmd_qmt_scan,
        "resume": cmd_resume, "review": cmd_review, "regime": cmd_regime,
        "stress": cmd_stress, "verify": cmd_verify, "arena": cmd_arena,
        "league": cmd_league, "gpu-screen": cmd_gpu_screen, "reset-account": cmd_reset_account,
        "blacklist": cmd_blacklist, "audit": cmd_audit, "dashboard": cmd_dashboard,
        "top10": cmd_top10, "minute": cmd_minute, "verdict": cmd_verdict,
        "game": cmd_game, "race": cmd_race, "sleeves": cmd_sleeves,
        "handoff": lambda a: (write_handoff(load_config(), load_state(), reason="CLI手动"),
                             print("HANDOFF.md 已重写 → " + os.path.join(ROOT, "HANDOFF.md"))),
        "ctx": lambda a: print(context_blob(load_config(), load_state())),
    }
    actions[args.cmd](args)


if __name__ == "__main__":
    main()
