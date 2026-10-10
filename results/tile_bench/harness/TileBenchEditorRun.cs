using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Profiling;
using UnityEngine.Tilemaps;

// CPH4 low-tier 2D rendering benchmark - editor-batchmode route (r845).
// r844 diagnosis: hidden standalone player window never enters the player loop
// (zero-window law blocks the visible-window variant), so the player route is
// structurally incompatible with this machine's discipline. Here the EDITOR runs
// -batchmode (headless UI, graphics device present) and this script drives a
// manual render loop: every EditorApplication.update tick renders the camera into
// a fixed 1600x900 RenderTexture, then a 1x1 ReadPixels forces a GPU sync so the
// measured tick interval includes render submit + GPU drain + editor loop overhead.
// Honest caliber: numbers are a conservative lower bound vs a standalone player
// (player loop is lighter than the editor loop).
public static class TileBenchEditorRun
{
    class Seg
    {
        public List<float> ms = new List<float>(16384);
        public double avg;
        public double p99;
        public double max;
        public double min;
    }

    const float WARMUP = 2f;
    const float PAN_SPEED = 12f;
    const int RT_W = 1600;
    const int RT_H = 900;

    static int mapSize = 512;
    static int layers = 1;
    static float ortho = 17f;
    static float duration = 10f;
    static string outFile = "result.json";

    static Camera cam;
    static RenderTexture rt;
    static Texture2D syncTex;
    static Seg[] segs;
    static int phase; // 0=warmup 1=hold 2=pan 3=hold2
    static float phaseStart;
    static float lastT;
    static int tilesGround, tilesDeco;
    static double genSeconds;

    public static void Run()
    {
        try
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++)
            {
                if (args[i] == "-mapSize") mapSize = int.Parse(args[i + 1], CultureInfo.InvariantCulture);
                else if (args[i] == "-layers") layers = int.Parse(args[i + 1], CultureInfo.InvariantCulture);
                else if (args[i] == "-ortho") ortho = float.Parse(args[i + 1], CultureInfo.InvariantCulture);
                else if (args[i] == "-durationSec") duration = float.Parse(args[i + 1], CultureInfo.InvariantCulture);
                else if (args[i] == "-outFile") outFile = args[i + 1];
            }
            segs = new Seg[] { new Seg(), new Seg(), new Seg(), new Seg() };
            var sw = Stopwatch.StartNew();
            BuildWorld();
            genSeconds = sw.Elapsed.TotalSeconds;

            rt = new RenderTexture(RT_W, RT_H, 24);
            rt.Create();
            cam.targetTexture = rt;
            cam.aspect = (float)RT_W / RT_H;
            syncTex = new Texture2D(1, 1, TextureFormat.RGBA32, false);

            phase = 0;
            phaseStart = lastT = Time.realtimeSinceStartup;
            EditorApplication.update += Tick;
        }
        catch (Exception e)
        {
            Fail(e.ToString());
        }
    }

    static void BuildWorld()
    {
        // 4 runtime-generated 32px tile variants (grass/road/plaza/sidewalk + pixel noise)
        Tile[] variants = new Tile[4];
        Color[] bases =
        {
            new Color(0.30f, 0.55f, 0.25f), new Color(0.42f, 0.44f, 0.48f),
            new Color(0.78f, 0.66f, 0.45f), new Color(0.55f, 0.40f, 0.30f)
        };
        for (int v = 0; v < 4; v++)
        {
            var tex = new Texture2D(32, 32, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point,
                wrapMode = TextureWrapMode.Clamp
            };
            var px = new Color[32 * 32];
            var rng = new System.Random(1234 + v);
            for (int i = 0; i < px.Length; i++)
            {
                float n = (float)rng.NextDouble() * 0.18f - 0.09f;
                px[i] = new Color(Mathf.Clamp01(bases[v].r + n), Mathf.Clamp01(bases[v].g + n),
                    Mathf.Clamp01(bases[v].b + n), 1f);
            }
            tex.SetPixels(px);
            tex.Apply();
            var spr = Sprite.Create(tex, new Rect(0, 0, 32, 32), new Vector2(0.5f, 0.5f), 32f);
            var t = ScriptableObject.CreateInstance<Tile>();
            t.sprite = spr;
            variants[v] = t;
        }

        var gridGo = new GameObject("Grid");
        gridGo.AddComponent<Grid>();
        for (int L = 0; L < layers; L++)
        {
            var tmGo = new GameObject("TM" + L);
            tmGo.transform.SetParent(gridGo.transform, false);
            var tm = tmGo.AddComponent<Tilemap>();
            var tr = tmGo.AddComponent<TilemapRenderer>();
            tr.sortingOrder = L;

            int n = mapSize * mapSize;
            var positions = new Vector3Int[n];
            var tiles = new TileBase[n];
            var rng = new System.Random(77 + L);
            int put = 0, k = 0;
            for (int x = 0; x < mapSize; x++)
            {
                for (int y = 0; y < mapSize; y++)
                {
                    positions[k] = new Vector3Int(x, y, 0);
                    if (L > 0)
                    {
                        bool sparse = rng.NextDouble() < 0.30;
                        tiles[k] = sparse ? variants[3] : null; // deco layer 30% fill
                        if (sparse) put++;
                    }
                    else
                    {
                        tiles[k] = variants[(x * 7 + y * 13) & 3];
                        put++;
                    }
                    k++;
                }
            }
            tm.SetTiles(positions, tiles);
            tm.ResizeBounds();
            tm.CompressBounds();
            if (L > 0) tilesDeco += put;
            else tilesGround += put;
        }

        var camGo = new GameObject("Cam");
        cam = camGo.AddComponent<Camera>();
        cam.orthographic = true;
        cam.orthographicSize = ortho;
        cam.nearClipPlane = -50f;
        cam.farClipPlane = 100f;
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = new Color(0.08f, 0.10f, 0.16f, 1f);
        cam.transform.position = new Vector3(mapSize / 2f, mapSize / 2f, 0f);
    }

    static void Tick()
    {
        float now = Time.realtimeSinceStartup;
        float dtMs = (now - lastT) * 1000f;
        lastT = now;
        float t = now - phaseStart;
        if (phase == 0 && t >= WARMUP) { phase = 1; phaseStart = now; }
        else if (phase == 1 && t >= duration * 0.3f) { phase = 2; phaseStart = now; }
        else if (phase == 2 && t >= duration * 0.4f) { phase = 3; phaseStart = now; }
        else if (phase == 3 && t >= duration * 0.3f) { Finish(); return; }

        if (phase == 2)
        {
            float d = PAN_SPEED * dtMs * 0.001f;
            var p = cam.transform.position;
            p.x += d;
            p.y += d;
            float lim = Mathf.Max(ortho + 1f, mapSize - ortho - 1f);
            if (p.x > lim) p.x = Mathf.Max(ortho, mapSize - lim);
            if (p.y > lim) p.y = Mathf.Max(ortho, mapSize - lim);
            cam.transform.position = p;
        }

        if (!RenderFrame()) return; // fatal render error already handled

        // dt of this tick carries the render+sync cost of the previous tick
        if (phase > 0) segs[phase].ms.Add(dtMs);
    }

    static bool RenderFrame()
    {
        try
        {
            cam.Render();
            var prev = RenderTexture.active;
            RenderTexture.active = rt;
            syncTex.ReadPixels(new Rect(0, 0, 1, 1), 0, 0); // force GPU pipeline drain
            syncTex.Apply();
            RenderTexture.active = prev;
            return true;
        }
        catch (Exception e)
        {
            EditorApplication.update -= Tick;
            Fail("render failed: " + e.Message);
            return false;
        }
    }

    static void Fail(string why)
    {
        try
        {
            string errPath = outFile.EndsWith(".json") ? outFile.Substring(0, outFile.Length - 5) + ".err.txt" : outFile + ".err.txt";
            string dir = Path.GetDirectoryName(Path.GetFullPath(errPath));
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            File.WriteAllText(errPath, why + "\n");
        }
        catch { }
        EditorApplication.Exit(2);
    }

    static void Stats(Seg s)
    {
        if (s.ms.Count == 0) return;
        var arr = new float[s.ms.Count];
        s.ms.CopyTo(arr);
        Array.Sort(arr);
        double sum = 0;
        foreach (float v in arr) sum += v;
        s.avg = sum / arr.Length;
        s.p99 = arr[(int)(0.99 * (arr.Length - 1))];
        s.max = arr[arr.Length - 1];
        s.min = arr[0];
    }

    static string F(double v) { return v.ToString("F3", CultureInfo.InvariantCulture); }

    static void Finish()
    {
        EditorApplication.update -= Tick;
        for (int i = 1; i <= 3; i++) Stats(segs[i]);
        float aspect = (float)RT_W / RT_H;
        double visPerLayer = (2.0 * ortho) * (2.0 * ortho * aspect);
        long wsMb = Environment.WorkingSet / (1024 * 1024);
        if (wsMb <= 0) wsMb = Process.GetCurrentProcess().WorkingSet64 / (1024 * 1024);
        long reservedMb = Profiler.GetTotalReservedMemoryLong() / (1024 * 1024);

        string json =
"{\n" +
" \"mode\": \"editor-batchmode-manual-render\",\n" +
" \"args\": {\"mapSize\": " + mapSize + ", \"layers\": " + layers + ", \"ortho\": " + F(ortho) +
", \"durationSec\": " + F(duration) + ", \"panSpeed\": " + PAN_SPEED + "},\n" +
" \"env\": {\"gpu\": \"" + SystemInfo.graphicsDeviceName + "\", \"gpuMemMB\": " + SystemInfo.graphicsMemorySize +
", \"cpu\": \"" + SystemInfo.processorType + "\", \"ramGB\": " + (SystemInfo.systemMemorySize / 1024.0).ToString("F1", CultureInfo.InvariantCulture) +
", \"unityVersion\": \"" + Application.unityVersion + "\", \"res\": \"" + RT_W + "x" + RT_H +
" RT (editor batchmode)\", \"fullscreen\": false, \"vsync\": 0, \"targetFps\": -1},\n" +
" \"map\": {\"tilesGround\": " + tilesGround + ", \"tilesDeco\": " + tilesDeco +
", \"totalTiles\": " + (tilesGround + tilesDeco) + ", \"genSeconds\": " + F(genSeconds) + "},\n" +
" \"mem\": {\"workingSetMB\": " + wsMb + ", \"reservedMB\": " + reservedMb + "},\n" +
" \"visibleTilesPerFrame\": {\"perLayer\": " + F(visPerLayer) + ", \"total\": " + F(visPerLayer * layers) + "},\n" +
" \"segments\": {\n" +
"  \"hold1\": {\"n\": " + segs[1].ms.Count + ", \"avgMs\": " + F(segs[1].avg) + ", \"p99Ms\": " + F(segs[1].p99) +
", \"maxMs\": " + F(segs[1].max) + "},\n" +
"  \"pan\": {\"n\": " + segs[2].ms.Count + ", \"avgMs\": " + F(segs[2].avg) + ", \"p99Ms\": " + F(segs[2].p99) +
", \"maxMs\": " + F(segs[2].max) + "},\n" +
"  \"hold2\": {\"n\": " + segs[3].ms.Count + ", \"avgMs\": " + F(segs[3].avg) + ", \"p99Ms\": " + F(segs[3].p99) +
", \"maxMs\": " + F(segs[3].max) + "}\n" +
" }\n" +
"}\n";
        try
        {
            string dir = Path.GetDirectoryName(Path.GetFullPath(outFile));
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            File.WriteAllText(outFile, json);
        }
        catch (Exception e)
        {
            Fail("write failed: " + e.Message);
            return;
        }
        EditorApplication.Exit(0);
    }
}
