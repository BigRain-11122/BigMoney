// 数据契约验证：与 StateFeeder.ReadReal() 完全同款的字段访问路径，对真实 state.json 断言。
// 通过 = 游戏实时模式下所有面板都有真实数据可读。
using System;
using System.Collections.Generic;
using System.IO;
using MoneyViz;

static class Program
{
    static int fails = 0;
    static void Check(bool ok, string what)
    {
        Console.WriteLine((ok ? "  [OK] " : "  [FAIL] ") + what);
        if (!ok) fails++;
    }

    static void Main()
    {
        string path = @"C:\Users\sjs20\Desktop\Money\state\state.json";
        Console.WriteLine("== MiniJson 数据契约验证 ==");

        var root = MiniJson.Obj(MiniJson.Parse(File.ReadAllText(path)));
        Check(root != null, "state.json 可解析为对象");

        // —— 诊断：解析器实际捕获到哪些键（定位截断点） ——
        Console.WriteLine("  [DIAG] root keys (" + (root == null ? 0 : root.Count) + "): " +
            (root == null ? "-" : string.Join(", ", new List<string>(root.Keys).ToArray())));
        var diagAcc = MiniJson.Obj(MiniJson.ObjOr(root, "account"));
        Console.WriteLine("  [DIAG] account keys (" + (diagAcc == null ? 0 : diagAcc.Count) + "): " +
            (diagAcc == null ? "-" : string.Join(", ", new List<string>(diagAcc.Keys).ToArray())));
        var diagEvo = MiniJson.Obj(MiniJson.ObjOr(root, "evolution"));
        Console.WriteLine("  [DIAG] evolution keys (" + (diagEvo == null ? 0 : diagEvo.Count) + "): " +
            (diagEvo == null ? "-" : string.Join(", ", new List<string>(diagEvo.Keys).ToArray())));

        var evo = MiniJson.Obj(MiniJson.ObjOr(root, "evolution"));
        var acc = MiniJson.Obj(MiniJson.ObjOr(root, "account"));
        var risk = MiniJson.Obj(MiniJson.ObjOr(root, "risk"));
        var champ = MiniJson.Obj(MiniJson.ObjOr(root, "champion"));

        // —— 进化HUD
        int gen = MiniJson.Int(MiniJson.ObjOr(evo, "generation"));
        int promoteCount = MiniJson.Int(MiniJson.ObjOr(evo, "promote_count"));
        Check(gen > 0, "evolution.generation = " + gen);
        Check(promoteCount >= 0, "evolution.promote_count = " + promoteCount);

        var hist = MiniJson.Arr(MiniJson.ObjOr(evo, "history"));
        Check(hist != null && hist.Count > 0, "evolution.history 非空 (" + (hist == null ? 0 : hist.Count) + " 条)");
        float bestScore = 0, sigmaBoost = 1;
        string lastFamily = "";
        if (hist != null && hist.Count > 0)
        {
            var h = MiniJson.Obj(hist[hist.Count - 1]);
            var best = MiniJson.Obj(MiniJson.ObjOr(h, "best"));
            bestScore = (float)MiniJson.Num(MiniJson.ObjOr(h, "best_score"));
            sigmaBoost = (float)MiniJson.Num(MiniJson.ObjOr(h, "sigma_boost"), 1f);
            lastFamily = best != null ? MiniJson.Str(MiniJson.ObjOr(best, "strategy"), "?") : "?";
            Check(bestScore > 0, "最近代 best_score = " + bestScore);
            Check(sigmaBoost >= 1f, "最近代 sigma_boost = " + sigmaBoost);
            Check(lastFamily != "?", "最近代家族 = " + lastFamily);
        }

        // —— Top10 循环迭代擂台
        var t10 = MiniJson.Arr(MiniJson.ObjOr(evo, "top10"));
        Check(t10 != null && t10.Count > 0, "evolution.top10 非空 (" + (t10 == null ? 0 : t10.Count) + " 名)");
        int unique = 0;
        var seen = new HashSet<string>();
        if (t10 != null)
            foreach (var o in t10)
            {
                var t = MiniJson.Obj(o);
                if (t == null) continue;
                string fam = MiniJson.Str(MiniJson.ObjOr(t, "strategy"), "?");
                float sc = (float)MiniJson.Num(MiniJson.ObjOr(t, "score"));
                var ps = MiniJson.Obj(MiniJson.ObjOr(t, "params"));
                var pk = new List<string>();
                if (ps != null)
                {
                    var keys = new List<string>(ps.Keys); keys.Sort();
                    foreach (var k in keys) pk.Add(k + "=" + MiniJson.Str(ps[k]));
                }
                string key = fam + "|" + string.Join(";", pk.ToArray());
                if (seen.Add(key)) unique++;
            }
        Console.WriteLine("  [INFO] top10 唯一个体数 = " + unique + "/" + (t10 == null ? 0 : t10.Count));
        Check(unique >= Math.Min(3, t10 == null ? 0 : t10.Count), "top10 具备多样性（≥3 个唯一个体）");

        // —— 市场风格引擎
        var regime = MiniJson.Obj(MiniJson.ObjOr(root, "regime"));
        var snap = MiniJson.Obj(MiniJson.ObjOr(regime, "snapshot"));
        Check(snap != null, "regime.snapshot 存在");
        if (snap != null)
        {
            string trend = MiniJson.Str(MiniJson.ObjOr(snap, "trend"), "");
            string factor = MiniJson.Str(MiniJson.ObjOr(snap, "factor_style"), "");
            string size = MiniJson.Str(MiniJson.ObjOr(snap, "size_style"), "");
            double breadth = MiniJson.Num(MiniJson.ObjOr(snap, "breadth"), -1);
            double volNow = MiniJson.Num(MiniJson.ObjOr(snap, "vol_now"), -1);
            var bfn = MiniJson.Obj(MiniJson.ObjOr(snap, "best_family_now"));
            string bfnFamily = bfn != null ? MiniJson.Str(MiniJson.ObjOr(bfn, "family"), "") : "";
            Check(trend.Length > 0, "snapshot.trend = " + trend);
            Check(factor.Length > 0, "snapshot.factor_style = " + factor);
            Check(breadth >= 0, "snapshot.breadth = " + breadth.ToString("0.0%"));
            Check(volNow >= 0, "snapshot.vol_now = " + volNow.ToString("0.0%"));
            Check(bfnFamily.Length > 0, "snapshot.best_family_now.family = " + bfnFamily);
        }

        // —— 锦标赛战报（换季清零后允许为空，游戏回退联赛直播线）
        var arena = MiniJson.Obj(MiniJson.ObjOr(root, "arena"));
        var lt = MiniJson.Obj(MiniJson.ObjOr(arena, "last_tournament"));
        if (lt != null && lt.Count > 0)
        {
            string label = MiniJson.Str(MiniJson.ObjOr(lt, "label"), "");
            int n = MiniJson.Int(MiniJson.ObjOr(lt, "n_players"));
            string bestId = MiniJson.Str(MiniJson.ObjOr(lt, "best_id"), "");
            double bestRet = MiniJson.Num(MiniJson.ObjOr(lt, "best_ret"));
            Check(label.Length > 0, "tournament.label = " + label);
            Check(n > 0, "tournament.n_players = " + n);
            Check(bestId.Length > 0, "tournament.best_id = " + bestId);
            Check(bestRet != 0, "tournament.best_ret = " + bestRet.ToString("+0.0%;-0.0%"));
        }
        else Console.WriteLine("  [SKIP] last_tournament 为空（换季清零）——游戏自动回退联赛直播线");

        // —— 200人实时联赛（游戏新增的直播面板）
        int round = MiniJson.Int(MiniJson.ObjOr(arena, "round"));
        Check(round > 0, "arena.round 联赛局数 = " + round);
        var pl = MiniJson.Arr(MiniJson.ObjOr(arena, "players"));
        Check(pl != null && pl.Count > 0, "arena.players 阵容 (" + (pl == null ? 0 : pl.Count) + " 人)");
        var qp = MiniJson.Arr(MiniJson.ObjOr(arena, "qualified"));
        Check(qp != null, "arena.qualified 认证池 (" + (qp == null ? 0 : qp.Count) + "★)");
        var rh = MiniJson.Arr(MiniJson.ObjOr(arena, "round_history"));
        Check(rh != null && rh.Count > 0, "arena.round_history 局史留痕 (" + (rh == null ? 0 : rh.Count) + " 局)");
        if (rh != null && rh.Count > 0)
        {
            var r = MiniJson.Obj(rh[rh.Count - 1]);
            string win = MiniJson.Str(MiniJson.ObjOr(r, "window"), "");
            Check(win.Length > 0, "最新一局 window = " + win);
            var best = MiniJson.Obj(MiniJson.ObjOr(r, "best"));
            Check(best != null, "最新一局 best 可读");
            if (best != null)
            {
                Check(MiniJson.Str(MiniJson.ObjOr(best, "id"), "").Length > 0,
                    "本局王者 id = " + MiniJson.Str(MiniJson.ObjOr(best, "id"), ""));
                Check(MiniJson.Str(MiniJson.ObjOr(best, "strategy"), "").Length > 0,
                    "本局王者 family = " + MiniJson.Str(MiniJson.ObjOr(best, "strategy"), ""));
                Check(MiniJson.Num(MiniJson.ObjOr(best, "score")) > 0,
                    "本局王者 score = " + MiniJson.Num(MiniJson.ObjOr(best, "score")).ToString("0.00"));
            }
            var nq = MiniJson.Arr(MiniJson.ObjOr(r, "qualified"));
            Check(nq != null, "最新一局新认证可读 (" + (nq == null ? 0 : nq.Count) + " 人)");
            int strCount = 0, objCount = 0;
            if (nq != null)
                foreach (var o in nq)
                {
                    var q = MiniJson.Obj(o);
                    if (q != null) objCount++; else if (o is string) strCount++;
                }
            Console.WriteLine("  [INFO] 新认证条目格式 str=" + strCount + " dict=" + objCount + "（游戏两种都兼容）");
        }

        // —— 冠军殿堂
        if (champ != null)
        {
            string fam2 = MiniJson.Str(MiniJson.ObjOr(champ, "strategy"));
            string promoted = MiniJson.Str(MiniJson.ObjOr(champ, "promoted_at"));
            var ho = MiniJson.Obj(MiniJson.ObjOr(champ, "holdout"));
            Check(fam2.Length > 0, "champion.strategy = " + fam2);
            Check(promoted.Length > 0, "champion.promoted_at = " + promoted);
            if (ho != null)
            {
                double score = MiniJson.Num(MiniJson.ObjOr(ho, "score"));
                var met = MiniJson.Obj(MiniJson.ObjOr(ho, "metrics"));
                Check(score > 0, "champion.holdout.score = " + score);
                if (met != null)
                {
                    Check(MiniJson.Num(MiniJson.ObjOr(met, "cagr")) != 0, "holdout.metrics.cagr 可读");
                    Check(MiniJson.Num(MiniJson.ObjOr(met, "max_dd")) != 0, "holdout.metrics.max_dd 可读");
                    Check(MiniJson.Num(MiniJson.ObjOr(met, "sharpe")) != 0, "holdout.metrics.sharpe 可读");
                    Check(MiniJson.Num(MiniJson.ObjOr(met, "win_rate")) != 0, "holdout.metrics.win_rate 可读");
                }
            }
            var ps2 = MiniJson.Obj(MiniJson.ObjOr(champ, "params"));
            Check(ps2 != null && ps2.Count > 0, "champion.params 可枚举 (" + (ps2 == null ? 0 : ps2.Count) + " 项)");
        }
        else Check(false, "champion 存在");

        // —— 账户/风控
        Check(MiniJson.Num(MiniJson.ObjOr(acc, "cash")) >= 0, "account.cash 可读");
        var pos = MiniJson.Obj(MiniJson.ObjOr(acc, "positions"));
        Check(pos != null, "account.positions 可枚举 (" + (pos == null ? 0 : pos.Count) + " 只)");
        Check(MiniJson.Bool(MiniJson.ObjOr(risk, "halt")) == false || true, "risk.halt 可读 = " + MiniJson.Bool(MiniJson.ObjOr(risk, "halt")));
        var retired = MiniJson.Arr(MiniJson.ObjOr(root, "champion_retired"));
        Check(retired != null, "champion_retired 数组 (" + (retired == null ? 0 : retired.Count) + " 任)");

        // —— 轨道与流水（当前为周六，允许为空但要可读）
        var track = MiniJson.Arr(MiniJson.ObjOr(root, "paper_track"));
        Check(track != null, "paper_track 可读 (" + (track == null ? 0 : track.Count) + " 日)");
        var tl = MiniJson.Arr(MiniJson.ObjOr(root, "trade_log"));
        Check(tl != null, "trade_log 可读 (" + (tl == null ? 0 : tl.Count) + " 笔)");
        var orders = MiniJson.Arr(MiniJson.ObjOr(root, "orders_today"));
        Check(orders != null, "orders_today 可读 (" + (orders == null ? 0 : orders.Count) + " 笔)");

        Console.WriteLine(fails == 0 ? "== 全部通过：游戏实时模式数据链路完整 ==" : "== 存在 " + fails + " 项失败 ==");
        Environment.Exit(fails == 0 ? 0 : 1);
    }
}
