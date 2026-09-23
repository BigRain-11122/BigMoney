// MoneyViz · 主场景构建器：《进化竞技场》
// 打开项目直接按 Play：自动接管任意场景，程序化搭建全部画面。
// 数据来源：交易系统 state/state.json（找不到自动进入演示模式）。
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;
using UnityEngine.UI;

namespace MoneyViz
{
    public static class VizLauncher
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Launch()
        {
            if (GameObject.Find("MoneyVizRoot") != null) return;
            var go = new GameObject("MoneyVizRoot");
            go.AddComponent<VizBootstrap>();
        }
    }

    public class Creature
    {
        public GameObject go;
        public Transform bodyTf;
        public SpriteRenderer rend;
        public TextMesh label;
        public Sprite[] frames = new Sprite[2]; // 0=迈步 1=站立
        public float bodyY;
        public string family = "";
        public float score;
    }

    public class VizBootstrap : MonoBehaviour
    {
        Font font;
        StateFeeder feeder;
        VizState prev;

        // HUD
        Text modeText, genText, clockText, championText, championSub, retiredText;
        Text cashText, equityText, posText, promoteText, alarmText, trackNote;
        Text regimeText, arenaText, leagueText;
        Image sigmaFill, sigmaBar;
        RawImage chartImg;
        Texture2D chartTex;
        Image alarmOverlay;

        // 世界
        readonly List<Creature> arena = new List<Creature>();
        Creature champion;
        GameObject championCrown, championPlatform;
        TextMesh championWorldLabel, arenaTitle;
        string lastTradeSig = "", lastQualifiedSig = "";
        float prevSigma = 1f;

        static readonly Color32 ColDim = new Color32(150, 158, 178, 255);
        static readonly Color32 ColGreen = new Color32(90, 235, 150, 255);
        static readonly Color32 ColGold = new Color32(255, 206, 84, 255);
        static readonly Color32 ColRed = new Color32(255, 92, 92, 255);
        static readonly Color32 ColWhite = new Color32(235, 240, 250, 255);

        // ------------------------------------------------ 启动搭建

        void Start()
        {
            LoadFont();
            CleanScene();
            SetupCamera();
            BuildBackground();
            BuildGround();
            BuildHUD();
            BuildChampionHall();
            BuildChart();
            feeder = gameObject.AddComponent<StateFeeder>();
            feeder.OnRefresh += OnState;
        }

        void LoadFont()
        {
            string[] osFonts = { "Microsoft YaHei", "SimHei", "Microsoft Sans Serif" };
            foreach (var f in osFonts)
            {
                font = Font.CreateDynamicFontFromOSFont(f, 24);
                if (font != null) return;
            }
            font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        }

        void CleanScene()
        {
            var all = UnityEngine.Object.FindObjectsOfType<Transform>();
            foreach (var t in all)
                if (t.parent == null && t.name != "MoneyVizRoot")
                    Destroy(t.gameObject);
        }

        void SetupCamera()
        {
            var camGo = new GameObject("VizCam");
            var cam = camGo.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 7.4f;
            cam.transform.position = new Vector3(0, 0.4f, -10);
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color32(10, 13, 24, 255);
            camGo.tag = "MainCamera";
        }

        void BuildBackground()
        {
            for (int i = 0; i < 80; i++)
            {
                var star = MakeSpriteGo("star" + i, PixelArt.White(), new Vector3(
                    UnityEngine.Random.Range(-14f, 14f), UnityEngine.Random.Range(-6f, 8.5f), 2f));
                star.transform.localScale = Vector3.one * UnityEngine.Random.Range(0.05f, 0.12f);
                var starRend = star.GetComponent<SpriteRenderer>();
                starRend.color = new Color(1, 1, 1, UnityEngine.Random.Range(0.05f, 0.22f));
                starRend.sortingOrder = 0;
            }
        }

        void BuildGround()
        {
            var g = MakeSpriteGo("ground", PixelArt.White(), new Vector3(0, -3.6f, 1f));
            g.transform.localScale = new Vector3(34, 0.26f, 1);
            var gRend = g.GetComponent<SpriteRenderer>();
            gRend.color = new Color32(26, 32, 52, 255);
            gRend.sortingOrder = 2;
        }

        GameObject MakeSpriteGo(string name, Sprite sp, Vector3 pos)
        {
            var go = new GameObject(name);
            go.transform.position = pos;
            var r = go.AddComponent<SpriteRenderer>();
            r.sprite = sp;
            return go;
        }

        // ------------------------------------------------ HUD（屏幕空间）

        Canvas MakeCanvas()
        {
            var cgo = new GameObject("HUD", typeof(Canvas));
            var canvas = cgo.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = cgo.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280, 720);
            return canvas;
        }

        Text MakeText(Transform parent, string name, Vector2 anchor, Vector2 pos, int sizePx,
                      TextAnchor align, Color32 col)
        {
            var go = new GameObject(name, typeof(Text));
            var rt = (RectTransform)go.transform;
            rt.SetParent(parent, false);
            rt.anchorMin = rt.anchorMax = rt.pivot = anchor;
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(600, sizePx + 8);
            var txt = go.GetComponent<Text>();
            txt.font = font; txt.fontSize = sizePx; txt.alignment = align; txt.color = col;
            txt.horizontalOverflow = HorizontalWrapMode.Overflow;
            txt.verticalOverflow = VerticalWrapMode.Overflow;
            txt.text = "";
            return txt;
        }

        Image MakePanel(Transform parent, string name, Vector2 anchor, Vector2 pos, Vector2 size, Color32 col)
        {
            var go = new GameObject(name, typeof(Image));
            var rt = (RectTransform)go.transform;
            rt.SetParent(parent, false);
            rt.anchorMin = rt.anchorMax = rt.pivot = anchor;
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;
            var img = go.GetComponent<Image>();
            img.sprite = PixelArt.White();
            img.color = col;
            img.type = Image.Type.Simple;
            img.preserveAspect = false;
            return img;
        }

        void BuildHUD()
        {
            var canvas = MakeCanvas();

            var title = MakeText(canvas.transform, "title", new Vector2(0, 1), new Vector2(20, -30), 26,
                TextAnchor.MiddleLeft, ColWhite);
            title.text = "MONEY · 自进化交易竞技场";
            modeText = MakeText(canvas.transform, "mode", new Vector2(0, 1), new Vector2(22, -58), 15,
                TextAnchor.MiddleLeft, ColDim);
            regimeText = MakeText(canvas.transform, "regime", new Vector2(0, 1), new Vector2(22, -80), 15,
                TextAnchor.MiddleLeft, new Color32(120, 200, 255, 255));
            arenaText = MakeText(canvas.transform, "arenaLine", new Vector2(0, 1), new Vector2(22, -102), 15,
                TextAnchor.MiddleLeft, new Color32(255, 170, 90, 255));
            leagueText = MakeText(canvas.transform, "leagueLine", new Vector2(0, 1), new Vector2(22, -124), 15,
                TextAnchor.MiddleLeft, ColGold);

            genText = MakeText(canvas.transform, "gen", new Vector2(0.5f, 1), new Vector2(0, -32), 24,
                TextAnchor.MiddleCenter, ColGreen);

            // σ 变异风暴表
            sigmaBar = MakePanel(canvas.transform, "sigmaBar", new Vector2(0.5f, 1), new Vector2(0, -58),
                new Vector2(220, 10), new Color32(40, 48, 70, 255));
            sigmaFill = MakePanel(canvas.transform, "sigmaFill", new Vector2(0.5f, 1), new Vector2(0, -58),
                new Vector2(2, 10), new Color32(120, 130, 255, 255));
            var sigmaLabel = MakeText(canvas.transform, "sigmaLabel", new Vector2(0.5f, 1), new Vector2(0, -74), 13,
                TextAnchor.MiddleCenter, ColDim);
            sigmaLabel.text = "变异步长 σ（停滞自适应风暴）";

            clockText = MakeText(canvas.transform, "clock", new Vector2(1, 1), new Vector2(-20, -32), 18,
                TextAnchor.MiddleRight, ColGold);

            // 右侧冠军面板
            MakePanel(canvas.transform, "champPanel", new Vector2(1, 0.5f), new Vector2(-170, 130), new Vector2(320, 250),
                new Color32(16, 20, 36, 210));
            var champTitle = MakeText(canvas.transform, "champTitle", new Vector2(1, 0.5f), new Vector2(-170, 232), 18,
                TextAnchor.MiddleCenter, ColGold);
            champTitle.text = "冠军殿堂";
            championSub = MakeText(canvas.transform, "champName", new Vector2(1, 0.5f), new Vector2(-170, 200), 20,
                TextAnchor.MiddleCenter, ColWhite);
            championText = MakeText(canvas.transform, "champMetrics", new Vector2(1, 0.5f), new Vector2(-170, 152), 15,
                TextAnchor.MiddleCenter, ColGreen);
            retiredText = MakeText(canvas.transform, "retired", new Vector2(1, 0.5f), new Vector2(-170, 40), 13,
                TextAnchor.MiddleCenter, ColDim);

            // 左下账户面板
            MakePanel(canvas.transform, "accPanel", new Vector2(0, 0), new Vector2(190, 130), new Vector2(350, 150),
                new Color32(16, 20, 36, 210));
            cashText = MakeText(canvas.transform, "cash", new Vector2(0, 0), new Vector2(20, 168), 17,
                TextAnchor.MiddleLeft, ColWhite);
            equityText = MakeText(canvas.transform, "eq", new Vector2(0, 0), new Vector2(20, 144), 17,
                TextAnchor.MiddleLeft, ColGreen);
            posText = MakeText(canvas.transform, "pos", new Vector2(0, 0), new Vector2(20, 120), 15,
                TextAnchor.MiddleLeft, ColDim);
            promoteText = MakeText(canvas.transform, "promote", new Vector2(0, 0), new Vector2(20, 96), 15,
                TextAnchor.MiddleLeft, ColDim);

            // 顶部警报条
            alarmText = MakeText(canvas.transform, "alarm", new Vector2(0.5f, 1), new Vector2(0, -100), 22,
                TextAnchor.MiddleCenter, ColRed);
            alarmOverlay = MakePanel(canvas.transform, "alarmOverlay", new Vector2(0.5f, 0.5f), Vector2.zero,
                new Vector2(4000, 2000), new Color32(255, 30, 30, 0));
            alarmOverlay.rectTransform.SetAsFirstSibling();

            trackNote = MakeText(canvas.transform, "trackNote", new Vector2(0.5f, 0), new Vector2(0, 160), 14,
                TextAnchor.MiddleCenter, ColDim);
        }

        // ------------------------------------------------ 冠军殿堂（世界空间）

        void BuildChampionHall()
        {
            championPlatform = MakeSpriteGo("champPlatform", PixelArt.White(), new Vector3(4.5f, -1.35f, 0));
            championPlatform.transform.localScale = new Vector3(3.4f, 0.3f, 1);
            championPlatform.GetComponent<SpriteRenderer>().color = new Color32(196, 148, 32, 255);
            championPlatform.GetComponent<SpriteRenderer>().sortingOrder = 5;

            championCrown = MakeSpriteGo("crown", PixelArt.MakeCrown(), new Vector3(4.5f, 2.2f, 0));
            championCrown.GetComponent<SpriteRenderer>().sortingOrder = 20;
            championCrown.SetActive(false);

            championWorldLabel = MakeWorldText("champLabel", new Vector3(4.5f, 2.9f, 0), 44, ColGold, "");
            arenaTitle = MakeWorldText("arenaTitle", new Vector3(-3.9f, 4.7f, 0), 48, ColDim, "Top10 循环迭代擂台");
        }

        TextMesh MakeWorldText(string name, Vector3 pos, int sizePx, Color32 col, string text)
        {
            var go = new GameObject(name);
            go.transform.position = pos;
            go.transform.localScale = Vector3.one * 0.09f;
            var tm = go.AddComponent<TextMesh>();
            tm.font = font;
            var mr = go.GetComponent<MeshRenderer>();
            mr.sharedMaterial = font.material;
            mr.sortingOrder = 30;
            tm.fontSize = sizePx;
            tm.characterSize = 1;
            tm.anchor = TextAnchor.MiddleCenter;
            tm.alignment = TextAlignment.Center;
            tm.color = col;
            tm.text = text;
            return tm;
        }

        // ------------------------------------------------ 权益像素曲线

        void BuildChart()
        {
            chartTex = new Texture2D(256, 64, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point };
            var canvas = FindObjectOfType<Canvas>();
            var go = new GameObject("chart", typeof(RawImage));
            var rt = (RectTransform)go.transform;
            rt.SetParent(canvas.transform, false);
            rt.anchorMin = rt.anchorMax = rt.pivot = new Vector2(0.5f, 0);
            rt.anchoredPosition = new Vector2(0, 14);
            rt.sizeDelta = new Vector2(512, 128);
            chartImg = go.GetComponent<RawImage>();
            chartImg.texture = chartTex;
        }

        void RedrawChart(VizState s)
        {
            int W = 256, H = 64;
            var px = new Color32[W * H];
            var bg = new Color32(14, 18, 32, 255);
            for (int i = 0; i < px.Length; i++) px[i] = bg;

            var eq = s.trackEquity;
            if (eq == null || eq.Count < 2)
            {
                // 无轨道：画一条中间虚线占位
                for (int x = 0; x < W; x += 6)
                    for (int y = 30; y < 34; y++) px[y * W + x] = new Color32(70, 80, 110, 255);
                chartTex.SetPixels32(px); chartTex.Apply();
                return;
            }
            double min = eq[0], max = eq[0];
            foreach (var v in eq) { if (v < min) min = v; if (v > max) max = v; }
            if (max - min < 1) max = min + 1;
            int n = eq.Count;
            int prevY = -1;
            for (int x = 0; x < W; x++)
            {
                int idx = (int)((long)x * (n - 1) / (W - 1));
                double val = eq[idx];
                int y = (int)((val - min) / (max - min) * (H - 10)) + 5;
                if (prevY >= 0)
                {
                    int y0 = Mathf.Min(prevY, y), y1 = Mathf.Max(prevY, y);
                    for (int yy = y0; yy <= y1; yy++)
                        if (yy >= 0 && yy < H) px[yy * W + x] = ColGreen;
                }
                else if (y >= 0 && y < H) px[y * W + x] = ColGreen;
                prevY = y;
            }
            // 基线（起点）
            int by = (int)((eq[0] - min) / (max - min) * (H - 10)) + 5;
            for (int x = 0; x < W; x += 4)
                if (by >= 0 && by < H) px[by * W + x] = new Color32(120, 128, 150, 255);
            chartTex.SetPixels32(px);
            chartTex.Apply();
        }

        // ------------------------------------------------ 状态刷新与事件

        void OnState(VizState s)
        {
            bool first = (prev == null);
            bool championChanged = !first && prev != null &&
                (s.championFamily != prev.championFamily || s.holdoutScore != prev.holdoutScore ||
                 s.promotedAt != prev.promotedAt);

            // —— HUD
            modeText.text = s.demo ? "演示模式（未找到 state/state.json）" : "实时连接：Money 交易系统";
            modeText.color = s.demo ? ColRed : ColGreen;
            genText.text = "第 " + s.generation + " 代   best=" + s.bestScore.ToString("0.0000") +
                           "   mean=" + s.meanScore.ToString("0.0000");
            float sig = Mathf.Clamp01((s.sigmaBoost - 1f) / 1.5f);
            sigmaFill.rectTransform.sizeDelta = new Vector2(Mathf.Max(2f, 220f * sig), 10);
            sigmaFill.rectTransform.anchoredPosition = new Vector2(-(220f - sigmaFill.rectTransform.sizeDelta.x) / 2f, -58);
            sigmaFill.color = s.sigmaBoost > 1.6f ? ColRed : new Color32(120, 130, 255, 255);
            cashText.text = "现金  ¥" + s.cash.ToString("N0", CultureInfo.InvariantCulture);
            equityText.text = "轨道权益  ¥" + s.lastEquity.ToString("N0", CultureInfo.InvariantCulture) +
                              "   高位 ¥" + s.equityHigh.ToString("N0", CultureInfo.InvariantCulture);
            posText.text = "持仓 " + s.positionCount + " 只   退休冠军 " + s.retiredCount + " 任";
            promoteText.text = "今日晋升尝试 " + s.promoteCount + " / 12（样本外磨刷保护）";
            regimeText.text = s.regimeLine;
            arenaText.text = s.arenaLine;
            leagueText.text = s.leagueRound > 0
                ? string.Format("联赛直播 第 {0} 局 · {1}人 · 认证池 {2}★ · 窗口 {3} · 本局王 {4}",
                    s.leagueRound.ToString("N0", CultureInfo.InvariantCulture), s.playersCount, s.qualifiedCount,
                    s.leagueWindow, s.leagueBest)
                : "";
            retiredText.text = "晋升于 " + s.promotedAt;

            if (!string.IsNullOrEmpty(s.championFamily))
            {
                championSub.text = "现任冠军：" + s.championFamily;
                championText.text = string.Format("样本外分 {0:0.000}  |  年化 {1:+0.0%;-0.0%}  回撤 {2:0.0%}\n夏普 {3:0.00}  胜率 {4:0.0%}",
                    s.holdoutScore, s.holdoutCagr, s.holdoutDd, s.holdoutSharpe, s.holdoutWin);
            }
            else
            {
                championSub.text = "（进化中，暂无冠军）";
                championText.text = "晋升闸：样本外分≥0.35 · 回撤≤10% · 随机16窗全过";
            }

            // —— 竞技场（最近各代最优小人，地台高度=真实适应度）
            UpdateArena(s);

            // —— 事件
            if (!first)
            {
                if (s.sigmaBoost > prevSigma + 0.01f)
                    StartCoroutine(StormFx((int)(6 * (s.sigmaBoost - prevSigma)) + 4));
                string sig_ = s.recentTrades.Count > 0
                    ? s.recentTrades[s.recentTrades.Count - 1].code + s.recentTrades[s.recentTrades.Count - 1].shares +
                      s.recentTrades[s.recentTrades.Count - 1].date
                    : "";
                if (sig_ != lastTradeSig && sig_ != "")
                {
                    StartCoroutine(CoinFx(5));
                    lastTradeSig = sig_;
                }
                if (championChanged)
                    StartCoroutine(Coronation(s));
                string qsig = string.Join("|", s.newQualified.ToArray());
                if (qsig.Length > 0 && qsig != lastQualifiedSig)
                {
                    StartCoroutine(StarFx(Mathf.Min(14, 4 + 3 * s.newQualified.Count)));
                    lastQualifiedSig = qsig;
                }
            }

            RedrawChart(s);
            trackNote.text = s.trackEquity.Count >= 2
                ? "账户轨道（冠军定型后·逐日收盘）"
                : "账户轨道等待首个交易日收盘结算…";
            UpdateAlarm(s);
            prevSigma = s.sigmaBoost;
            prev = s;
            if (first && !string.IsNullOrEmpty(s.championFamily))
                StartCoroutine(Coronation(s, fast: true));
        }

        void UpdateAlarm(VizState s)
        {
            // 出局机制：停机/毁灭线均为收盘结算口径（日熔断已于 2026-09-21 废止，与沪深现行规则一致）
            alarmText.text = s.halt ? "■ 组合停机（收盘结算判定）：" + s.haltReason : "";
        }

        // ------------------------------------------------ 竞技场

        void UpdateArena(VizState s)
        {
            // 优先展示用户指定的核心机制：Top10 循环迭代擂台；种群收敛期（唯一个体<3）或无数据时退化为最近各代最优
            bool isTop10 = s.top10 != null && s.top10.Count >= 3;
            var gens = isTop10 ? s.top10 : s.recentGens;
            if (arenaTitle != null)
                arenaTitle.text = isTop10 ? "Top10 循环迭代擂台（地台高度=真实适应度）" : "最近各代最优";
            int show = Mathf.Min(10, gens.Count);
            // 清多余槽位
            while (arena.Count > show)
            {
                Destroy(arena[arena.Count - 1].go);
                if (arena[arena.Count - 1].label != null) Destroy(arena[arena.Count - 1].label.gameObject);
                arena.RemoveAt(arena.Count - 1);
            }
            float minS = 1, maxS = 0;
            for (int i = 0; i < show; i++) { if (gens[i].bestScore < minS) minS = gens[i].bestScore; if (gens[i].bestScore > maxS) maxS = gens[i].bestScore; }
            if (maxS - minS < 0.001f) { minS -= 0.001f; maxS += 0.001f; }

            for (int i = 0; i < show; i++)
            {
                var g = gens[i];
                while (arena.Count <= i) arena.Add(NewCreatureSlot(i));
                var c = arena[i];
                if (c.family != g.family)
                {
                    c.family = g.family;
                    var look = PixelArt.Look(g.family);
                    c.frames[0] = PixelArt.CreatureFrame(look.body, look.emblem, PixelArt.HeadColor, 0);
                    c.frames[1] = PixelArt.CreatureFrame(look.body, look.emblem, PixelArt.HeadColor, 1);
                    c.rend.sprite = c.frames[1];
                    if (c.label != null) Destroy(c.label.gameObject);
                    c.label = MakeWorldText("lbl" + i, Vector3.zero, 40, ColDim, g.family);
                    c.label.transform.localScale = Vector3.one * 0.06f;
                }
                float h = 0.25f + 1.7f * (g.bestScore - minS) / (maxS - minS);
                float x = -8.1f + i * 0.86f;
                c.score = g.bestScore;
                c.go.transform.position = new Vector3(x, -3.35f, 0);
                c.bodyY = h + 0.55f;
                c.bodyTf.localPosition = new Vector3(0, c.bodyY, 0);
                // 地台（扎根地面，不随呼吸浮动）
                var ped = c.go.transform.Find("ped");
                if (ped != null)
                {
                    ped.localScale = new Vector3(0.62f, h, 1);
                    ped.localPosition = new Vector3(0, h / 2f, 0.1f);
                    var pr = ped.GetComponent<SpriteRenderer>();
                    pr.color = new Color32(30, 38, 60, 255);
                    if (i == show - 1) pr.color = new Color32(40, 120, 90, 255); // 最新一代高亮
                }
                c.label.transform.position = new Vector3(x, -3.35f + h + 1.45f, 0);
                c.label.text = (isTop10 ? "#" + g.gen + " " : "") + g.family + " " + g.bestScore.ToString("0.00");
            }
        }

        Creature NewCreatureSlot(int i)
        {
            var c = new Creature();
            c.go = new GameObject("creature" + i);
            c.go.transform.position = new Vector3(-9f + i * 0.9f, -3.35f, 0);
            var bodyGo = new GameObject("body");
            bodyGo.transform.SetParent(c.go.transform, false);
            c.bodyTf = bodyGo.transform;
            c.rend = bodyGo.AddComponent<SpriteRenderer>();
            c.rend.sortingOrder = 10;
            bodyGo.transform.localPosition = new Vector3(0, 0.55f, 0);
            var pedGo = new GameObject("ped");
            pedGo.transform.SetParent(c.go.transform, false);
            var pr = pedGo.AddComponent<SpriteRenderer>();
            pr.sprite = PixelArt.White();
            pr.sortingOrder = 5;
            return c;
        }

        // ------------------------------------------------ 加冕仪式

        IEnumerator Coronation(VizState s, bool fast = false)
        {
            string fam = string.IsNullOrEmpty(s.championFamily) ? "?" : s.championFamily;
            // 旧冠军退场
            if (champion != null)
            {
                var old = champion;
                float t = 0;
                Vector3 from = old.go.transform.position;
                Vector3 to = from + new Vector3(-6, 1.2f, 0);
                while (t < 0.7f)
                {
                    t += Time.deltaTime;
                    old.go.transform.position = Vector3.Lerp(from, to, t / 0.7f);
                    var col = old.rend.color; col.a = Mathf.Lerp(1, 0, t / 0.7f); old.rend.color = col;
                    yield return null;
                }
                Destroy(old.go);
                if (old.label != null) Destroy(old.label.gameObject);
            }
            // 新冠军从左侧登台
            var look = PixelArt.Look(fam);
            var c = new Creature();
            c.family = fam;
            c.frames[0] = PixelArt.CreatureFrame(PixelArt.ChampionBody, PixelArt.ChampionEmblem, PixelArt.HeadColor, 0);
            c.frames[1] = PixelArt.CreatureFrame(PixelArt.ChampionBody, PixelArt.ChampionEmblem, PixelArt.HeadColor, 1);
            c.go = new GameObject("championCreature");
            c.rend = c.go.AddComponent<SpriteRenderer>();
            c.rend.sortingOrder = 12;
            c.rend.sprite = c.frames[1];
            c.go.transform.localScale = Vector3.one * 1.5f;
            Vector3 a = fast ? new Vector3(4.5f, -1.05f, 0) : new Vector3(-10f, -1.05f, 0);
            Vector3 b = new Vector3(4.5f, -1.05f, 0);
            c.go.transform.position = a;
            champion = c;
            float dur = fast ? 0.2f : 1.1f;
            float t2 = 0;
            while (t2 < dur)
            {
                t2 += Time.deltaTime;
                c.go.transform.position = Vector3.Lerp(a, b, t2 / dur);
                c.rend.sprite = c.frames[(int)(t2 / 0.12f) % 2];
                yield return null;
            }
            c.rend.sprite = c.frames[1];
            // 皇冠落下（落在冠军头顶）
            championCrown.SetActive(true);
            Vector3 crownFrom = new Vector3(4.5f, 4.5f, 0), crownTo = new Vector3(4.5f, -0.08f, 0);
            float t3 = 0;
            while (t3 < 0.45f)
            {
                t3 += Time.deltaTime;
                championCrown.transform.position = Vector3.Lerp(crownFrom, crownTo, t3 / 0.45f);
                yield return null;
            }
            championWorldLabel.text = "冠军 · " + fam + "（样本外 " + s.holdoutScore.ToString("0.000") + "）";
            // 彩带
            for (int i = 0; i < 26; i++)
            {
                Color32 col = i % 2 == 0 ? ColGold : new Color32(120, 130, 255, 255);
                var fx = MakeSpriteGo("confetti" + i, PixelArt.White(), new Vector3(4.5f, 1.2f, -1));
                fx.transform.localScale = Vector3.one * 0.1f;
                fx.GetComponent<SpriteRenderer>().color = col;
                StartCoroutine(FxFall(fx, new Vector3(UnityEngine.Random.Range(-3.2f, 3.2f), UnityEngine.Random.Range(0.5f, 2.4f), 0), 1.4f));
            }
            yield break;
        }

        // ------------------------------------------------ 特效

        IEnumerator FxFall(GameObject g, Vector3 vel, float life)
        {
            float t = 0;
            var sp = g.GetComponent<SpriteRenderer>();
            while (t < life)
            {
                t += Time.deltaTime;
                vel.y -= 4.5f * Time.deltaTime;
                g.transform.position += vel * Time.deltaTime;
                var col = sp.color; col.a = 1 - t / life; sp.color = col;
                yield return null;
            }
            Destroy(g);
        }

        IEnumerator CoinFx(int n)
        {
            var coin = PixelArt.MakeCoin(new Color32(255, 200, 50, 255));
            for (int i = 0; i < n; i++)
            {
                var g = MakeSpriteGo("coin" + i, coin, new Vector3(UnityEngine.Random.Range(-7.5f, 0f), 0.5f, -1));
                g.GetComponent<SpriteRenderer>().sortingOrder = 20;
                g.transform.localScale = Vector3.one * 0.8f;
                StartCoroutine(FxFall(g, new Vector3(UnityEngine.Random.Range(-0.8f, 0.8f), UnityEngine.Random.Range(2.5f, 4.5f), 0), 1.2f));
                yield return new WaitForSeconds(0.06f);
            }
        }

        IEnumerator StormFx(int n)
        {
            var bolt = PixelArt.MakeStar(new Color32(255, 70, 70, 255));
            for (int i = 0; i < n; i++)
            {
                var g = MakeSpriteGo("storm" + i, bolt, new Vector3(
                    UnityEngine.Random.Range(-8.5f, 6f), UnityEngine.Random.Range(5.5f, 7.5f), -1));
                g.GetComponent<SpriteRenderer>().sortingOrder = 20;
                g.transform.localScale = Vector3.one * UnityEngine.Random.Range(0.5f, 1.1f);
                StartCoroutine(FxFall(g, new Vector3(UnityEngine.Random.Range(-0.4f, 0.4f), UnityEngine.Random.Range(-2.5f, -1.2f), 0), 1.6f));
            }
            yield break;
        }

        // 认证星雨：联赛有人连胜3局晋级认证池时触发（金色星星落下）
        IEnumerator StarFx(int n)
        {
            var star = PixelArt.MakeStar(new Color32(255, 216, 90, 255));
            for (int i = 0; i < n; i++)
            {
                var g = MakeSpriteGo("certstar" + i, star, new Vector3(
                    UnityEngine.Random.Range(-8.5f, 6f), UnityEngine.Random.Range(5.5f, 7.5f), -1));
                g.GetComponent<SpriteRenderer>().sortingOrder = 20;
                g.transform.localScale = Vector3.one * UnityEngine.Random.Range(0.45f, 0.95f);
                StartCoroutine(FxFall(g, new Vector3(UnityEngine.Random.Range(-0.4f, 0.4f), UnityEngine.Random.Range(-1.8f, -0.7f), 0), 1.8f));
                yield return new WaitForSeconds(0.05f);
            }
        }

        // ------------------------------------------------ 时钟

        void Update()
        {
            // 警报红晕脉冲
            if (prev != null)
            {
                float target = prev.halt ? 0.26f : 0f;
                float pulse = target > 0 ? (0.7f + 0.3f * Mathf.Sin(Time.time * 6f)) * target : 0f;
                var c = alarmOverlay.color; c.a = pulse; alarmOverlay.color = c;
            }
            // 小人原地呼吸（只动身体，地台不动）
            for (int i = 0; i < arena.Count; i++)
            {
                var c = arena[i];
                if (c.bodyTf != null)
                    c.bodyTf.localPosition = new Vector3(0, c.bodyY + Mathf.Sin(Time.time * 2.2f + i) * 0.035f, 0);
            }
            if (feeder != null && feeder.Current != null)
                clockText.text = ClockText(feeder.Current);
        }

        string ClockText(VizState s)
        {
            var now = DateTime.Now;
            string today = now.ToString("yyyy-MM-dd");
            bool tradeDay = s.tradeDates != null && s.tradeDates.Contains(today);
            var t = now.TimeOfDay;
            var open = new TimeSpan(9, 30, 0);
            var noonClose = new TimeSpan(11, 30, 0);
            var pmOpen = new TimeSpan(13, 0, 0);
            var close = new TimeSpan(15, 0, 0);
            if (tradeDay)
            {
                if (t >= open && t < noonClose) return "交易中（上午）";
                if (t >= pmOpen && t < close) return "交易中（下午）";
                if (t >= noonClose && t < pmOpen) return "午间休市";
                if (t >= new TimeSpan(9, 25, 0) && t < open) return "集合竞价临近";
                if (t < open) return "今日开市 " + (open - t).ToString(@"hh\:mm\:ss");
                return "已收盘 · " + NextOpen(s, now);
            }
            return "休市 · " + NextOpen(s, now);
        }

        string NextOpen(VizState s, DateTime now)
        {
            DateTime target = now.Date.AddDays(1).Add(new TimeSpan(9, 30, 0));
            if (s.tradeDates != null && s.tradeDates.Count > 0)
            {
                foreach (var d in s.tradeDates)
                {
                    DateTime dt;
                    if (DateTime.TryParseExact(d, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out dt)
                        && dt.Date >= now.Date)
                    {
                        if (dt.Date == now.Date)
                        {
                            if (now.TimeOfDay < new TimeSpan(9, 25, 0)) return "今日开市 " + (new TimeSpan(9, 30, 0) - now.TimeOfDay).ToString(@"hh\:mm\:ss");
                            target = now.Date.AddDays(1).Add(new TimeSpan(9, 30, 0));
                            foreach (var d2 in s.tradeDates)
                            {
                                DateTime dt2;
                                if (DateTime.TryParseExact(d2, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out dt2) && dt2 > target)
                                { target = dt2.Date.Add(new TimeSpan(9, 30, 0)); break; }
                            }
                        }
                        else target = dt.Date.Add(new TimeSpan(9, 30, 0));
                        break;
                    }
                }
            }
            else
            {
                DateTime d = now.Date;
                for (int i = 0; i < 7; i++) { d = d.AddDays(1); if (d.DayOfWeek != DayOfWeek.Saturday && d.DayOfWeek != DayOfWeek.Sunday) break; }
                target = d.Add(new TimeSpan(9, 30, 0));
            }
            var span = target - now;
            if (span.TotalDays >= 1) return "距开市 " + (int)span.TotalDays + "天 " + span.ToString(@"hh\:mm\:ss");
            return "距开市 " + span.ToString(@"hh\:mm\:ss");
        }
    }
}
