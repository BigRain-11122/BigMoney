// MoneyViz · 状态读取器：轮询交易系统 state/state.json，解析为可视化模型；
// 找不到状态时进入演示模式（合成数据），保证打开即有画面。
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using UnityEngine;

namespace MoneyViz
{
    public class GenRec
    {
        public int gen;
        public float bestScore, meanScore, sigmaBoost;
        public string family;
    }

    public class TradeRec
    {
        public string date, code, side, reason;
        public int shares;
    }

    public class VizState
    {
        public bool demo;
        public int generation;
        public float bestScore, meanScore, sigmaBoost;
        public int promoteCount;
        public string championFamily = "", championParams = "", promotedAt = "";
        public float holdoutScore, holdoutCagr, holdoutDd, holdoutSharpe, holdoutWin;
        public int retiredCount;
        public double cash, equityHigh, lastEquity;
        public int positionCount;
        public bool halt; public string haltReason = "";
        public string dailyBreaker = "";
        public List<GenRec> recentGens = new List<GenRec>();
        public List<GenRec> top10 = new List<GenRec>();  // 用户指定核心机制：Top10循环迭代（gen=排名）
        public string regimeLine = "", arenaLine = "";   // 市场风格引擎 / 锦标赛战报（换季清零后为空）
        // —— 200人实时联赛（每秒一局的主战场直播）
        public int leagueRound, playersCount, qualifiedCount;
        public string leagueWindow = "", leagueBest = "";
        public List<string> newQualified = new List<string>();
        public List<TradeRec> recentTrades = new List<TradeRec>();
        public List<double> trackEquity = new List<double>();
        public List<string> tradeDates = new List<string>();
    }

    public class StateFeeder : MonoBehaviour
    {
        public event Action<VizState> OnRefresh;
        public VizState Current;

        string statePath, calPath;
        int demoTick;

        IEnumerator Start()
        {
            LocatePaths();
            while (true)
            {
                Current = (statePath != null && File.Exists(statePath)) ? ReadReal() : MakeDemo();
                if (calPath != null && File.Exists(calPath)) ReadCalendar(Current);
                if (OnRefresh != null) OnRefresh(Current);
                yield return new WaitForSeconds(2.0f);
            }
        }

        // 向上逐级查找 Money 根目录（state/state.json 与 data/trade_dates.csv）
        void LocatePaths()
        {
            string dir = Application.dataPath; // .../MoneyViz/Assets
            for (int k = 0; k < 5; k++)
            {
                string cand = Path.Combine(dir, "state", "state.json");
                if (File.Exists(cand)) { statePath = cand; calPath = Path.Combine(dir, "data", "trade_dates.csv"); return; }
                string up = Path.GetFullPath(Path.Combine(dir, ".."));
                if (up == dir) break;
                dir = up;
            }
            statePath = null;
        }

        void ReadCalendar(VizState s)
        {
            try
            {
                s.tradeDates.Clear();
                string[] lines = File.ReadAllLines(calPath);
                for (int i = 1; i < lines.Length; i++)
                {
                    string t = lines[i].Trim();
                    if (t.Length >= 10) s.tradeDates.Add(t.Substring(0, 10));
                }
            }
            catch (Exception) { }
        }

        VizState ReadReal()
        {
            var s = new VizState();
            try
            {
                var root = MiniJson.Obj(MiniJson.Parse(File.ReadAllText(statePath)));
                if (root == null) return MakeDemo();
                var evo = MiniJson.Obj(MiniJson.ObjOr(root, "evolution"));
                var acc = MiniJson.Obj(MiniJson.ObjOr(root, "account"));
                var risk = MiniJson.Obj(MiniJson.ObjOr(root, "risk"));
                var champ = MiniJson.Obj(MiniJson.ObjOr(root, "champion"));

                s.generation = MiniJson.Int(MiniJson.ObjOr(evo, "generation"));
                s.promoteCount = MiniJson.Int(MiniJson.ObjOr(evo, "promote_count"));
                var hist = MiniJson.Arr(MiniJson.ObjOr(evo, "history"));
                if (hist != null)
                {
                    int from = Math.Max(0, hist.Count - 12);
                    for (int i = from; i < hist.Count; i++)
                    {
                        var h = MiniJson.Obj(hist[i]);
                        if (h == null) continue;
                        var best = MiniJson.Obj(MiniJson.ObjOr(h, "best"));
                        var g = new GenRec
                        {
                            gen = MiniJson.Int(MiniJson.ObjOr(h, "gen")),
                            bestScore = (float)MiniJson.Num(MiniJson.ObjOr(h, "best_score")),
                            meanScore = (float)MiniJson.Num(MiniJson.ObjOr(h, "mean_score")),
                            sigmaBoost = (float)MiniJson.Num(MiniJson.ObjOr(h, "sigma_boost"), 1f),
                            family = best != null ? MiniJson.Str(MiniJson.ObjOr(best, "strategy"), "?") : "?",
                        };
                        s.recentGens.Add(g);
                    }
                    if (s.recentGens.Count > 0)
                    {
                        var last = s.recentGens[s.recentGens.Count - 1];
                        s.bestScore = last.bestScore; s.meanScore = last.meanScore; s.sigmaBoost = last.sigmaBoost;
                    }
                }
                if (acc != null)
                {
                    s.cash = MiniJson.Num(MiniJson.ObjOr(acc, "cash"));
                    s.equityHigh = MiniJson.Num(MiniJson.ObjOr(acc, "equity_high"));
                    var pos = MiniJson.Obj(MiniJson.ObjOr(acc, "positions"));
                    if (pos != null) s.positionCount = pos.Count;
                }
                if (risk != null)
                {
                    s.halt = MiniJson.Bool(MiniJson.ObjOr(risk, "halt"));
                    s.haltReason = MiniJson.Str(MiniJson.ObjOr(risk, "halt_reason"));
                    s.dailyBreaker = MiniJson.Str(MiniJson.ObjOr(risk, "daily_breaker_date"));
                }
                if (champ != null)
                {
                    s.championFamily = MiniJson.Str(MiniJson.ObjOr(champ, "strategy"));
                    s.promotedAt = MiniJson.Str(MiniJson.ObjOr(champ, "promoted_at"));
                    var ps = MiniJson.Obj(MiniJson.ObjOr(champ, "params"));
                    if (ps != null)
                    {
                        var keys = new List<string>(ps.Keys); keys.Sort();
                        var parts = new List<string>();
                        foreach (var k in keys) parts.Add(k + "=" + MiniJson.Str(ps[k]));
                        s.championParams = string.Join(" ", parts.ToArray());
                    }
                    var ho = MiniJson.Obj(MiniJson.ObjOr(champ, "holdout"));
                    if (ho != null)
                    {
                        s.holdoutScore = (float)MiniJson.Num(MiniJson.ObjOr(ho, "score"));
                        var met = MiniJson.Obj(MiniJson.ObjOr(ho, "metrics"));
                        if (met != null)
                        {
                            s.holdoutCagr = (float)MiniJson.Num(MiniJson.ObjOr(met, "cagr"));
                            s.holdoutDd = (float)MiniJson.Num(MiniJson.ObjOr(met, "max_dd"));
                            s.holdoutSharpe = (float)MiniJson.Num(MiniJson.ObjOr(met, "sharpe"));
                            s.holdoutWin = (float)MiniJson.Num(MiniJson.ObjOr(met, "win_rate"));
                        }
                    }
                }
                var retired = MiniJson.Arr(MiniJson.ObjOr(root, "champion_retired"));
                if (retired != null) s.retiredCount = retired.Count;

                // —— Top10 循环迭代擂台（用户指定核心机制）
                var t10 = MiniJson.Arr(MiniJson.ObjOr(evo, "top10"));
                if (t10 != null)
                {
                    for (int r = 0; r < t10.Count; r++)
                    {
                        var t = MiniJson.Obj(t10[r]);
                        if (t == null) continue;
                        s.top10.Add(new GenRec
                        {
                            gen = r + 1,
                            family = MiniJson.Str(MiniJson.ObjOr(t, "strategy"), "?"),
                            bestScore = (float)MiniJson.Num(MiniJson.ObjOr(t, "score")),
                        });
                    }
                }

                // —— 市场风格引擎快照
                var regime = MiniJson.Obj(MiniJson.ObjOr(root, "regime"));
                var snap = MiniJson.Obj(MiniJson.ObjOr(regime, "snapshot"));
                if (snap != null)
                {
                    s.regimeLine = string.Format("市场风格：{0} · {1} · {2}盘占优 · 宽度{3:0%} · 波动{4:0.0%}",
                        MiniJson.Str(MiniJson.ObjOr(snap, "trend"), "?"),
                        MiniJson.Str(MiniJson.ObjOr(snap, "factor_style"), ""),
                        MiniJson.Str(MiniJson.ObjOr(snap, "size_style"), ""),
                        MiniJson.Num(MiniJson.ObjOr(snap, "breadth")),
                        MiniJson.Num(MiniJson.ObjOr(snap, "vol_now")));
                    var bfn = MiniJson.Obj(MiniJson.ObjOr(snap, "best_family_now"));
                    if (bfn != null)
                        s.regimeLine += " · 当前最适族：" + MiniJson.Str(MiniJson.ObjOr(bfn, "family"), "?");
                }

                // —— 锦标赛战报（换季清零后为空，游戏回退联赛直播线）
                var arena = MiniJson.Obj(MiniJson.ObjOr(root, "arena"));
                var lt = MiniJson.Obj(MiniJson.ObjOr(arena, "last_tournament"));
                if (lt != null && lt.Count > 0 && MiniJson.Str(MiniJson.ObjOr(lt, "best_id"), "").Length > 0)
                {
                    s.arenaLine = string.Format("锦标赛：{0} · {1}人参赛 · 最佳 {2} {3:+0.0%;-0.0%}",
                        MiniJson.Str(MiniJson.ObjOr(lt, "label"), ""),
                        MiniJson.Int(MiniJson.ObjOr(lt, "n_players")),
                        MiniJson.Str(MiniJson.ObjOr(lt, "best_id"), ""),
                        MiniJson.Num(MiniJson.ObjOr(lt, "best_ret")));
                }

                // —— 200人实时联赛（每秒一局，游戏的主战场直播）
                s.leagueRound = MiniJson.Int(MiniJson.ObjOr(arena, "round"));
                var pl = MiniJson.Arr(MiniJson.ObjOr(arena, "players"));
                s.playersCount = pl != null ? pl.Count : 0;
                var qpool = MiniJson.Arr(MiniJson.ObjOr(arena, "qualified"));
                s.qualifiedCount = qpool != null ? qpool.Count : 0;
                var rh = MiniJson.Arr(MiniJson.ObjOr(arena, "round_history"));
                if (rh != null && rh.Count > 0)
                {
                    var r = MiniJson.Obj(rh[rh.Count - 1]);
                    if (r != null)
                    {
                        s.leagueWindow = MiniJson.Str(MiniJson.ObjOr(r, "window"), "");
                        var best = MiniJson.Obj(MiniJson.ObjOr(r, "best"));
                        if (best != null)
                            s.leagueBest = MiniJson.Str(MiniJson.ObjOr(best, "id"), "?") + " · " +
                                           MiniJson.Str(MiniJson.ObjOr(best, "strategy"), "?") + " " +
                                           ((float)MiniJson.Num(MiniJson.ObjOr(best, "score"))).ToString("0.00");
                        var nq = MiniJson.Arr(MiniJson.ObjOr(r, "qualified"));
                        if (nq != null)
                            for (int i = 0; i < nq.Count; i++)
                            {
                                var q = MiniJson.Obj(nq[i]);
                                if (q != null)  // dict 格式
                                    s.newQualified.Add(MiniJson.Str(MiniJson.ObjOr(q, "id"), "?") + " " +
                                                       MiniJson.Str(MiniJson.ObjOr(q, "strategy"), ""));
                                else if (nq[i] is string)  // 历史格式：纯ID
                                    s.newQualified.Add((string)nq[i]);
                            }
                    }
                }

                var track = MiniJson.Arr(MiniJson.ObjOr(root, "paper_track"));
                if (track != null)
                {
                    int from = Math.Max(0, track.Count - 120);
                    for (int i = from; i < track.Count; i++)
                    {
                        var t = MiniJson.Obj(track[i]);
                        if (t == null) continue;
                        s.trackEquity.Add(MiniJson.Num(MiniJson.ObjOr(t, "equity")));
                    }
                    if (s.trackEquity.Count > 0) s.lastEquity = s.trackEquity[s.trackEquity.Count - 1];
                }
                var tl = MiniJson.Arr(MiniJson.ObjOr(root, "trade_log"));
                if (tl != null)
                {
                    int from = Math.Max(0, tl.Count - 40);
                    for (int i = from; i < tl.Count; i++)
                    {
                        var t = MiniJson.Obj(tl[i]);
                        if (t == null) continue;
                        s.recentTrades.Add(new TradeRec
                        {
                            date = MiniJson.Str(MiniJson.ObjOr(t, "date")),
                            code = MiniJson.Str(MiniJson.ObjOr(t, "code")),
                            side = MiniJson.Str(MiniJson.ObjOr(t, "side")),
                            reason = MiniJson.Str(MiniJson.ObjOr(t, "reason")),
                            shares = MiniJson.Int(MiniJson.ObjOr(t, "shares")),
                        });
                    }
                }
            }
            catch (Exception) { return MakeDemo(); }
            return s;
        }

        // ---------------- 演示模式（未找到 state.json 时） ----------------
        static readonly string[] DemoFamilies = { "multifactor", "rotation_28", "rsrs", "dual_momentum", "mean_rev", "low_vol", "donchian", "momentum" };

        VizState MakeDemo()
        {
            demoTick++;
            var s = new VizState { demo = true, generation = 120 + demoTick * 3, sigmaBoost = 1f, promoteCount = demoTick % 12 };
            float baseScore = 0.80f + 0.01f * Mathf.Sin(demoTick * 0.2f);
            s.bestScore = baseScore + Mathf.Min(0.14f, demoTick * 0.002f);
            s.meanScore = s.bestScore - 0.12f;
            for (int i = 0; i < 10; i++)
            {
                s.recentGens.Add(new GenRec
                {
                    gen = s.generation - (9 - i),
                    bestScore = 0.78f + 0.02f * Mathf.Sin((demoTick - (9 - i)) * 0.2f) + 0.01f * i,
                    meanScore = 0.66f + 0.02f * i,
                    sigmaBoost = (i == 3 || i == 4) ? 2.5f : 1f,
                    family = DemoFamilies[(demoTick + i) % DemoFamilies.Length],
                });
            }
                        s.championFamily = "multifactor";
                        s.championParams = "演示参数 w_lowvol=0.42 top_k=3";
                        s.holdoutScore = 0.8765f; s.holdoutCagr = 0.132f; s.holdoutDd = -0.043f;
                        s.holdoutSharpe = 1.57f; s.holdoutWin = 0.69f;
                        s.retiredCount = 2; s.cash = 72000; s.equityHigh = 101000; s.lastEquity = 100650;
                        s.positionCount = 3;
                        for (int i = 0; i < 10; i++)
                            s.top10.Add(new GenRec
                            {
                                gen = i + 1,
                                family = DemoFamilies[(demoTick + i * 3) % DemoFamilies.Length],
                                bestScore = 0.92f - 0.025f * i + 0.01f * Mathf.Sin(demoTick * 0.3f + i),
                            });
                        s.regimeLine = "市场风格：震荡 · 反转有效 · 均衡盘占优 · 宽度32% · 波动10.8% · 当前最适族：mean_rev";
                        s.arenaLine = "锦标赛：周度锦标赛 · 100人参赛 · 最佳 P020 +80.2%";
                        s.leagueRound = 12175 + demoTick;
                        s.playersCount = 200; s.qualifiedCount = 200;
                        s.leagueWindow = "2023-09-05~2024-09-19";
                        s.leagueBest = "G922815 · multifactor 0.85";
                        if (demoTick % 4 == 0) s.newQualified.Add("N" + (928000 + demoTick));
                        for (int i = 0; i < 40; i++)
                            s.trackEquity.Add(100000 + 600 * Mathf.Sin(i * 0.4f) + i * 16);
                        s.recentTrades.Add(new TradeRec { date = "demo", code = "600900", side = "buy", reason = "rebalance", shares = 5300 });
                        return s;
                    }
                }
            }
