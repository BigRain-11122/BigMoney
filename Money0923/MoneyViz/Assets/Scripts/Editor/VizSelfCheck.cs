// MoneyViz · 编辑器自检：菜单 Tools/MoneyViz/数据自检
// 不进 Play 模式即可验证 交易系统→游戏 的数据链路完整性；全部通过后按 Play 即是完整可视化。
using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace MoneyViz.EditorTools
{
    public static class VizSelfCheck
    {
        static int fails;
        static readonly List<string> lines = new List<string>();

        static void Check(bool ok, string what)
        {
            lines.Add((ok ? "  [OK] " : "  [FAIL] ") + what);
            if (!ok) fails++;
        }

        [MenuItem("Tools/MoneyViz/数据自检 (State Data Check)")]
        static void Run()
        {
            fails = 0;
            lines.Clear();
            lines.Add("== MoneyViz 数据自检 ==");

            string path = LocateState();
            Check(path != null, "定位 state/state.json");
            if (path == null)
            {
                lines.Add("  搜索路径：从 Assets 向上 5 层查找 Money 根目录。");
                Dump();
                return;
            }
            lines.Add("  路径: " + path);

            var root = MiniJson.Obj(MiniJson.Parse(File.ReadAllText(path)));
            Check(root != null, "MiniJson 解析成功");
            if (root == null) { Dump(); return; }
            Check(root.Count >= 10, "根对象键数 = " + root.Count + "（截断会导致键数过少）");

            var evo = MiniJson.Obj(MiniJson.ObjOr(root, "evolution"));
            var acc = MiniJson.Obj(MiniJson.ObjOr(root, "account"));
            var champ = MiniJson.Obj(MiniJson.ObjOr(root, "champion"));
            var risk = MiniJson.Obj(MiniJson.ObjOr(root, "risk"));
            var regime = MiniJson.Obj(MiniJson.ObjOr(root, "regime"));
            var arena = MiniJson.Obj(MiniJson.ObjOr(root, "arena"));

            // —— 进化 HUD
            Check(evo != null, "evolution 存在");
            if (evo != null)
            {
                int gen = MiniJson.Int(MiniJson.ObjOr(evo, "generation"));
                Check(gen > 0, "generation = " + gen);
                var hist = MiniJson.Arr(MiniJson.ObjOr(evo, "history"));
                Check(hist != null && hist.Count > 0, "history 条数 = " + (hist == null ? 0 : hist.Count));

                var t10 = MiniJson.Arr(MiniJson.ObjOr(evo, "top10"));
                int unique = 0;
                if (t10 != null)
                {
                    var seen = new HashSet<string>();
                    foreach (var o in t10)
                    {
                        var t = MiniJson.Obj(o);
                        if (t == null) continue;
                        var ps = MiniJson.Obj(MiniJson.ObjOr(t, "params"));
                        var pk = new List<string>();
                        if (ps != null)
                        {
                            var keys = new List<string>(ps.Keys); keys.Sort();
                            foreach (var k in keys) pk.Add(k + "=" + MiniJson.Str(ps[k]));
                        }
                        string key = MiniJson.Str(MiniJson.ObjOr(t, "strategy"), "?") + "|" +
                                     string.Join(";", pk.ToArray());
                        if (seen.Add(key)) unique++;
                    }
                }
                lines.Add("  [INFO] top10 唯一个体 = " + unique + "/" + (t10 == null ? 0 : t10.Count));
                Check(unique >= 3, "top10 多样性（≥3 个唯一个体）");
            }

            // —— 市场风格引擎
            var snap = regime != null ? MiniJson.Obj(MiniJson.ObjOr(regime, "snapshot")) : null;
            Check(snap != null, "regime.snapshot 存在");
            if (snap != null)
            {
                Check(MiniJson.Str(MiniJson.ObjOr(snap, "trend")).Length > 0,
                    "市场风格 trend = " + MiniJson.Str(MiniJson.ObjOr(snap, "trend")));
                var bfn = MiniJson.Obj(MiniJson.ObjOr(snap, "best_family_now"));
                Check(bfn != null, "当前最适族 = " +
                      (bfn == null ? "-" : MiniJson.Str(MiniJson.ObjOr(bfn, "family"))));
            }

            // —— 锦标赛战报
            var lt = arena != null ? MiniJson.Obj(MiniJson.ObjOr(arena, "last_tournament")) : null;
            Check(lt != null, "arena.last_tournament 存在");
            if (lt != null)
            {
                lines.Add("  [INFO] 锦标赛: " + MiniJson.Str(MiniJson.ObjOr(lt, "label")) +
                          " · " + MiniJson.Int(MiniJson.ObjOr(lt, "n_players")) + "人 · 最佳 " +
                          MiniJson.Str(MiniJson.ObjOr(lt, "best_id")) + " " +
                          MiniJson.Num(MiniJson.ObjOr(lt, "best_ret")).ToString("+0.0%;-0.0%"));
            }

            // —— 冠军殿堂
            Check(champ != null, "champion 存在");
            if (champ != null)
            {
                var ho = MiniJson.Obj(MiniJson.ObjOr(champ, "holdout"));
                lines.Add("  [INFO] 冠军: " + MiniJson.Str(MiniJson.ObjOr(champ, "strategy")) +
                          " · 样本外分 " +
                          (ho == null ? "-" : MiniJson.Num(MiniJson.ObjOr(ho, "score")).ToString("0.000")));
            }

            // —— 账户与风控
            Check(acc != null, "account 存在");
            if (acc != null)
                lines.Add("  [INFO] 现金 = " + MiniJson.Num(MiniJson.ObjOr(acc, "cash")).ToString("N0"));
            Check(risk != null, "risk 存在");
            if (risk != null)
                Check(!MiniJson.Bool(MiniJson.ObjOr(risk, "halt")), "风控未停机");

            lines.Add(fails == 0
                ? "== 自检通过：数据链路完整，按 Play 进入《进化竞技场》 =="
                : "== 自检存在 " + fails + " 项失败（看上方 FAIL 行） ==");
            Dump();
        }

        static void Dump()
        {
            string all = string.Join("\n", lines.ToArray());
            if (fails == 0) Debug.Log("<color=#7CFFB0>" + all + "</color>");
            else Debug.LogError(all);
            EditorUtility.DisplayDialog("MoneyViz 自检",
                fails == 0 ? "数据链路完整 ✓\n\n现在按 ▶ Play 就是完整可视化竞技场。" :
                    "存在 " + fails + " 项失败。\n详情见 Console。", "好");
        }

        static string LocateState()
        {
            string dir = Application.dataPath;
            for (int k = 0; k < 5; k++)
            {
                string cand = Path.Combine(dir, "state", "state.json");
                if (File.Exists(cand)) return cand;
                string up = Path.GetFullPath(Path.Combine(dir, ".."));
                if (up == dir) break;
                dir = up;
            }
            return null;
        }
    }
}
