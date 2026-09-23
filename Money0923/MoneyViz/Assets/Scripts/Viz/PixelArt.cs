// MoneyViz · 程序化像素画工厂：小人/金币/皇冠/星星全部代码生成，零美术资产
using System.Collections.Generic;
using UnityEngine;

namespace MoneyViz
{
    public static class PixelArt
    {
        public const float PPU = 16f; // 16像素 = 1世界单位

        // ---------------- 像素小人模板（16x16，H头 E眼 B身 A徽章 L腿） ----------------
        static readonly string[] BodyTop = {
            "................",
            "................",
            ".....HHHHHH.....",
            "....HHHHHHHH....",
            "....HEHHHHEH....",
            "....HHHHHHHH....",
            ".....HHHHHH.....",
            "......BBBB......",
            "....BBBBBBBB....",
            "...BBBBBBBBBB...",
            "..BBBBBAABBBBB..",
            "..BB.BBBBBBB.BB.",
            ".....BBBBBB.....",
        };
        // 帧A：迈步（腿分开）；帧B：并腿
        static readonly string[] LegsA = { "...LL......LL...", "...LL......LL...", "................" };
        static readonly string[] LegsB = { ".....LLLL.......", ".....LL..LL.....", "................" };

        // 金币 8x8（Y亮 y暗 d暗心）
        static readonly string[] Coin = {
            "..YYYY..", ".YYyyYY.", "YYYyyYYY", "YYYddYYY",
            "YYYddYYY", "YYYyyYYY", ".YYyyYY.", "..YYYY..",
        };

        // 皇冠 8x5（Y金 R红宝石）
        static readonly string[] Crown = {
            "Y.Y.Y.Y.", "YYYYYYY.", "YRRRRRY.", "YYYYYYY.", "YYYYYYY.",
        };

        // 星星 7x7
        static readonly string[] Star = {
            "...S...", "..SSS..", "SSSSSSS", ".SSSSS.", "..SSS..", ".SS.S..", "S.....S",
        };

        static Sprite MakeSprite(string[] rows, Dictionary<char, Color32> map)
        {
            int w = rows[0].Length, h = rows.Length;
            var tex = new Texture2D(w, h, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point,
                wrapMode = TextureWrapMode.Clamp,
            };
            var px = new Color32[w * h];
            for (int y = 0; y < h; y++)
            {
                string row = rows[h - 1 - y]; // 像素画惯例：数组第一行是顶部
                for (int x = 0; x < w; x++)
                {
                    Color32 c;
                    px[y * w + x] = (x < row.Length && map.TryGetValue(row[x], out c)) ? c : new Color32(0, 0, 0, 0);
                }
            }
            tex.SetPixels32(px);
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, w, h), new Vector2(0.5f, 0.5f), PPU);
        }

        static Dictionary<char, Color32> CreatureMap(Color32 body, Color32 emblem, Color32 head, Color32 legs)
        {
            return new Dictionary<char, Color32> {
                { 'H', head }, { 'E', new Color32(25, 28, 38, 255) },
                { 'B', body }, { 'A', emblem }, { 'L', legs }, { '.', new Color32(0, 0, 0, 0) },
            };
        }

        /// <summary>生成小人帧。frame: 0=迈步 1=并腿</summary>
        public static Sprite CreatureFrame(Color32 body, Color32 emblem, Color32 head, int frame)
        {
            var rows = new List<string>(BodyTop);
            rows.AddRange(frame == 0 ? LegsA : LegsB);
            return MakeSprite(rows.ToArray(), CreatureMap(body, emblem, head, new Color32(38, 40, 52, 255)));
        }

        public static Sprite MakeCoin(Color32 c) { return MakeSprite(Coin, new Dictionary<char, Color32> { { 'Y', c }, { 'y', Dim(c, 0.75f) }, { 'd', Dim(c, 0.45f) } }); }
        public static Sprite MakeCrown() { return MakeSprite(Crown, new Dictionary<char, Color32> { { 'Y', new Color32(255, 200, 40, 255) }, { 'R', new Color32(220, 40, 60, 255) } }); }
        public static Sprite MakeStar(Color32 c) { return MakeSprite(Star, new Dictionary<char, Color32> { { 'S', c } }); }

        static Color32 Dim(Color32 c, float k)
        {
            return new Color32((byte)(c.r * k), (byte)(c.g * k), (byte)(c.b * k), c.a);
        }

        static Sprite _white;
        public static Sprite White()
        {
            if (_white == null)
            {
                var tex = new Texture2D(1, 1, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point };
                tex.SetPixel(0, 0, Color.white);
                tex.Apply();
                _white = Sprite.Create(tex, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f), PPU);
            }
            return _white;
        }

        // ---------------- 策略家族配色 ----------------
        public static FamilyLook Look(string family)
        {
            switch (family)
            {
                case "multifactor": return new FamilyLook(new Color32(150, 84, 210, 255), new Color32(255, 214, 90, 255));
                case "momentum": return new FamilyLook(new Color32(216, 64, 64, 255), new Color32(255, 255, 255, 255));
                case "dual_ma": return new FamilyLook(new Color32(70, 130, 230, 255), new Color32(160, 220, 255, 255));
                case "mean_rev": return new FamilyLook(new Color32(70, 190, 110, 255), new Color32(255, 120, 120, 255));
                case "donchian": return new FamilyLook(new Color32(235, 190, 60, 255), new Color32(120, 60, 20, 255));
                case "etf_trend": return new FamilyLook(new Color32(80, 210, 220, 255), new Color32(20, 60, 90, 255));
                case "rotation_28": return new FamilyLook(new Color32(240, 140, 50, 255), new Color32(255, 255, 255, 255));
                case "dual_momentum": return new FamilyLook(new Color32(170, 40, 90, 255), new Color32(255, 200, 60, 255));
                case "rsrs": return new FamilyLook(new Color32(230, 200, 90, 255), new Color32(120, 90, 255, 255));
                case "low_vol": return new FamilyLook(new Color32(160, 170, 185, 255), new Color32(60, 90, 255, 255));
                default: return new FamilyLook(new Color32(200, 200, 200, 255), new Color32(255, 255, 255, 255));
            }
        }

        public static readonly Color32 HeadColor = new Color32(235, 195, 155, 255);
        public static readonly Color32 ChampionBody = new Color32(255, 200, 40, 255);
        public static readonly Color32 ChampionEmblem = new Color32(160, 60, 200, 255);
    }

    public struct FamilyLook
    {
        public Color32 body;
        public Color32 emblem;
        public FamilyLook(Color32 b, Color32 e) { body = b; emblem = e; }
    }
}
