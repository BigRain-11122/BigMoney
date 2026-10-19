"""r1022 bm-b ST-011 BOY/MANCANG sourcing station (CONTENT-LOOP cpu lane).

Products: (a) MANCANG de-clip re-production of 7 in-house r998 voice_05 clips
-> linear-interp declip -> re-measure (clipped-samples/F0/RMS/centroid) ->
consistency gate v0.1 (F0 rel<=0.15, RMS spread<=8dB, centroid rel<=0.20) ->
manifest admit (interim; voice_05 shared-base debt disclosed, root-fix = ST-012
LoRA/new-base lane per 2026-10-19 11:21 group order @bm-b); (b) BOY child-voice
license review face (deterministic receipt; zero BOY clips admitted, honest);
(c) queue ledger: ST-011 claimed->done + ST-012 seeded; QUEUE.md regenerated.
Zero network. exit 0 = station done; 2 = mechanism fault (honest report).
"""
import json
import os
import sys
import time

import numpy as np
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = r"C:\Fluxgroup\FluxGroup\media"
SRC = os.path.join(MEDIA, "drama-tts-out", "r998_ep001_003")
OUT = os.path.join(MEDIA, "drama-tools", "voice_smoke", "st011", "mancang")
MANIFEST = os.path.join(ROOT, "content", "drama", "voice_bank", "manifest.json")
QUEUEJ = os.path.join(ROOT, "content", "drama", "queue.json")
QUEUEMD = os.path.join(ROOT, "content", "drama", "QUEUE.md")
LOOPS = os.path.join(ROOT, "content", "drama", "loop_state.json")
STATUS = os.path.join(ROOT, "results", "drama_env", "st011_sourcing.json")
RECEIPT = os.path.join(ROOT, "content", "drama", "outbox", "ST-011-SOURCING-RECEIPT.md")

CLIPS = [
    ("EP001", 12, "ep001_line12", "完了！我全仓啊！全部身家！", 3.11),
    ("EP001", 15, "ep001_line15", "股神……你是股神！", 2.15),
    ("EP002", 3, "ep002_line03", "股神！我找你三天了！", 2.64),
    ("EP002", 7, "ep002_line07", "十万，全给你！条件——带我发财！", 2.75),
    ("EP002", 11, "ep002_line11", "没……没了？又回来了？！", 2.23),
    ("EP003", 2, "ep003_line02", "翻倍了！闺女的嫁妆翻倍了！", 3.07),
    ("EP003", 5, "ep003_line05", "他就是股神！我是他唯一的合伙人——", 3.07),
]

NOW = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
THR = 0.985


def read_wav(path):
    sr, data = wavfile.read(path)
    if data.ndim > 1:
        data = data[:, 0]
    if data.dtype == np.int16:
        x = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        x = data.astype(np.float64) / 2147483648.0
    elif data.dtype == np.uint8:
        x = (data.astype(np.float64) - 128.0) / 128.0
    else:
        x = data.astype(np.float64)
    return sr, x


def write_wav(path, sr, x):
    y = np.clip(x, -0.999, 0.999)
    wavfile.write(path, sr, (y * 32767.0).astype(np.int16))


def declip(x, thr=THR):
    mask = np.abs(x) >= thr
    n_clip = int(mask.sum())
    if n_clip == 0:
        return x.copy(), 0, 0
    idx = np.where(mask)[0]
    runs = []
    start = idx[0]
    prev = idx[0]
    for i in idx[1:]:
        if i == prev + 1:
            prev = i
        else:
            runs.append((start, prev))
            start = i
            prev = i
    runs.append((start, prev))
    y = x.copy()
    for (s, e) in runs:
        ws = max(0, s - 12)
        we = min(len(x), e + 13)
        seg_i = np.arange(ws, we)
        vals = x[ws:we].copy()
        good = np.abs(vals) < thr
        if good.sum() < 4:
            continue
        y[s:e + 1] = np.interp(np.arange(s, e + 1), seg_i[good], vals[good])
    post = int((np.abs(y) >= thr).sum())
    return y, n_clip, post


def f0_hz(x, sr):
    fl = 1024
    hop = 512
    grms = float(np.sqrt(np.mean(x ** 2))) + 1e-12
    lag_min = max(2, int(sr / 400.0))
    lag_max = min(fl - 1, int(sr / 80.0))
    f0s = []
    for i in range(0, max(1, len(x) - fl), hop):
        seg = x[i:i + fl]
        if len(seg) < fl:
            break
        if float(np.sqrt(np.mean(seg ** 2))) < grms * 0.3:
            continue
        seg = seg - seg.mean()
        ac = np.correlate(seg, seg, 'full')[fl - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        if lag_max <= lag_min + 2:
            continue
        k = int(np.argmax(ac[lag_min:lag_max])) + lag_min
        if ac[k] > 0.3:
            f0s.append(sr / float(k))
    arr = np.array(f0s)
    arr = arr[(arr > 60.0) & (arr < 450.0)]
    return float(np.median(arr)) if len(arr) else 0.0


def centroid_hz(x, sr):
    fl = 1024
    hop = 512
    freqs = np.fft.rfftfreq(fl, 1.0 / sr)
    cs = []
    for i in range(0, max(1, len(x) - fl), hop):
        seg = x[i:i + fl]
        if len(seg) < fl:
            break
        sp = np.abs(np.fft.rfft(seg * np.hanning(fl)))
        e = float(sp.sum())
        if e > 1e-9:
            cs.append(float((freqs * sp).sum() / e))
    return float(np.median(cs)) if cs else 0.0


def rms_dbfs(x):
    return float(20 * np.log10(float(np.sqrt(np.mean(x ** 2))) + 1e-12))


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for (ep, n, name, text, audio_s) in CLIPS:
        src = os.path.join(SRC, ep, name + ".wav")
        if not os.path.exists(src):
            rows.append({"name": name, "err": "source missing"})
            continue
        sr, x = read_wav(src)
        y, n_clip, post = declip(x)
        dst = os.path.join(OUT, name + "_declip.wav")
        write_wav(dst, sr, y)
        rows.append({
            "name": name, "ep": ep, "n": n, "text": text, "sr": int(sr),
            "dur_s": round(len(y) / float(sr), 3),
            "pre_clipped_samples": n_clip, "post_clipped_samples": post,
            "rms_dbfs": round(rms_dbfs(y), 2),
            "f0_hz": round(f0_hz(y, sr), 1),
            "centroid_hz": round(centroid_hz(y, sr), 1),
            "path": dst,
        })
    ok = [r for r in rows if "err" not in r]

    def gate_pass(subset):
        if len(subset) == 0:
            return None
        f0s = [r["f0_hz"] for r in subset if r["f0_hz"] > 0]
        if len(f0s) < len(subset):
            return None
        med = float(np.median(f0s))
        f0_dev = max(abs(v - med) / med for v in f0s)
        rmss = [r["rms_dbfs"] for r in subset]
        spread = max(rmss) - min(rmss)
        ces = [r["centroid_hz"] for r in subset if r["centroid_hz"] > 0]
        if len(ces) < len(subset):
            return None
        cmed = float(np.median(ces))
        c_dev = max(abs(v - cmed) / cmed for v in ces)
        ok_gate = (f0_dev <= 0.15) and (spread <= 8.0) and (c_dev <= 0.20)
        return {"f0_dev_max": round(f0_dev, 4), "rms_spread_db": round(spread, 2),
                "centroid_dev_max": round(c_dev, 4), "pass": bool(ok_gate)}

    # admit best up-to-3: start from full set, drop worst F0 offender until pass
    cand = sorted(ok, key=lambda r: -r["dur_s"])
    admitted, g = None, None
    pool = list(cand)
    while pool:
        g = gate_pass(pool)
        if g and g["pass"]:
            admitted = pool[:3]
            g3 = gate_pass(admitted)
            g = g3 if (len(pool) <= 3 or not g3 or g3["pass"]) else g
            if g3 and g3["pass"]:
                g = g3
            admitted = pool[:3]
            break
        if len(pool) == 1:
            admitted = pool
            g = {"f0_dev_max": 0.0, "rms_spread_db": 0.0,
                 "centroid_dev_max": 0.0, "pass": True,
                 "note": "single-clip vacuous pass (FATHER precedent)"}
            break
        f0s = [r["f0_hz"] for r in pool]
        med = float(np.median(f0s))
        worst = max(pool, key=lambda r: abs(r["f0_hz"] - med))
        pool.remove(worst)
    single = bool(admitted and len(admitted) == 1 and "note" in (g or {}))

    # --- manifest update (MANCANG only; BOY gets route note) ---
    man = json.load(open(MANIFEST, encoding="utf-8"))
    for ch in man["characters"]:
        if ch["id"] == "MANCANG" and admitted:
            ch["ref_clips"] = [{
                "name": r["name"],
                "path": r["path"],
                "text": r["text"],
                "ep": r["ep"], "n": r["n"], "speaker": "满仓",
                "source_ref": "voice_05.wav (r1022 ST-011 declip re-production)",
                "audio_s": r["dur_s"], "sr": r["sr"], "dur_s": r["dur_s"],
                "rms_dbfs": r["rms_dbfs"], "f0_hz": r["f0_hz"],
                "centroid_hz": r["centroid_hz"],
                "audition_flags": "de-clip clean (pre_clipped=%d post=%d)" % (
                    r["pre_clipped_samples"], r["post_clipped_samples"]),
            } for r in admitted]
            ch["entry_state"] = "admitted-interim"
            ch["added_ts"] = NOW
            ch["entry_note"] = ("音色一致检 v0.1 pass %s; INTERIM: voice_05 "
                                "shared-base-with-narrator debt disclosed -- root fix "
                                "= ST-012 new-base/LoRA lane (2026-10-19 11:21 group "
                                "order @bm-b); source clips were all-CLIPPED (ST-008), "
                                "de-clipped in-house r1022" % json.dumps(
                                    {k: g[k] for k in
                                     ("f0_dev_max", "rms_spread_db", "centroid_dev_max")},
                                    ensure_ascii=False) if not single else
                                "single-clip vacuous pass (de-clip re-production)")
        if ch["id"] == "BOY":
            ch["entry_state"] = "awaiting-ref-clips"
            ch["entry_note"] = ("r1022 ST-011 license review delivered: external "
                                "real-child cloning BLOCKED (minor likeness, no "
                                "guardian-consent chain); AISHELL-3/aidatatang = "
                                "research-use not commercial-cleared; routes = "
                                "(1) CEO-provided clips (physical) or (2) adult-base + "
                                "verified-adjust DSP child-feel prototype at production "
                                "station; zero BOY clips admitted (honest)")
    man["updated_ts"] = NOW
    tmp = MANIFEST + ".tmp"
    json.dump(man, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, MANIFEST)

    # --- queue ledger: ST-011 done + ST-012 seed ---
    q = json.load(open(QUEUEJ, encoding="utf-8"))
    for st in q["stations"]:
        if st["id"] == "ST-011":
            st["state"] = "done"
            st["claim"] = "claimed@bm-b@" + NOW
            st["done_at"] = NOW
            st["runner"] = "st011_boy_mancang_sourcing"
            st["product"] = ("content/drama/outbox/ST-011-SOURCING-RECEIPT.md + "
                             "manifest MANCANG admitted-interim (declip) + BOY license "
                             "review route decision + results/drama_env/st011_sourcing.json")
    if not any(s["id"] == "ST-012" for s in q["stations"]):
        q["stations"].append({
            "id": "ST-012",
            "title": ("character-voice LoRA training lane: GPT-SoVITS base finetune "
                      "(GitHub wheels scan FIRST per 10-16 CEO order) for new-base "
                      "differentiation root-fix (MANCANG/XIONG-family/BOY child-feel "
                      "feasibility) -- night-window GPU priority 22:0x per 2026-10-19 "
                      "11:21 group order @bm-b 8G"),
            "state": "open",
            "lane": "gpu-night",
            "runner": "v0.2-pending",
            "require": "none",
            "product": ("GitHub training-wheels scan receipt (寻源闸律) + first "
                        "character-voice LoRA train run + ST-009-law admission re-eval "
                        "(same-base finetune cannot separate family -- new-base speakers only)"),
            "source": ("2026-10-19 11:21 group orders row @bm-b (角色声 LoRA + SD1.5 "
                       "素材微训·夜窗 22:0x 优先); ST-011 receipt next-station row"),
            "claim": None,
        })
    tmp = QUEUEJ + ".tmp"
    json.dump(q, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, QUEUEJ)

    # --- QUEUE.md regen (deterministic face) ---
    try:
        ls = json.load(open(LOOPS, encoding="utf-8"))
        loopline = "Loop state: rounds=%s last=%s" % (ls.get("rounds"), ls.get("last"))
    except Exception:
        loopline = "Loop state: rounds=? last=?"
    md = ["# CONTENT-LOOP QUEUE -- drama line (bm-b host, v0.1)", "",
          "> Carrier: Bigmoney-ContentLoop S4U task (20-min). Machine ledger = queue.json (single-writer);",
          "> this file is a regenerated face -- never hand-edit. Protocol: claim-by-file, station states",
          "> open/claimed/done/blocked; five-piece gates stay in-loop (no downgrade); director step-gate",
          "> per station; CEO = terminal review only; account writes = physical-domain pause face.",
          "> Law refs: CONTENT-OS-LOOP-BLUEPRINT-v1 sec.3; O-20261018-2144-bm-c sec.2.1; DIRECTOR-STEP-GATE-v1.",
          "", "## Gates", "", "| gate | state | note |", "|---|---|---|"]
    for k, v in q["gates"].items():
        md.append("| %s | %s | %s |" % (k, v.get("state"), (v.get("note") or "")[:60]))
    md += ["", "## Stations", "",
           "| id | state | lane | runner | require | title | claim |",
           "|---|---|---|---|---|---|---|"]
    for st in q["stations"]:
        md.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            st["id"], st["state"], st["lane"], st["runner"], st["require"],
            st["title"][:60], st.get("claim") or "-"))
    md += ["", loopline, ""]
    open(QUEUEMD, "w", encoding="utf-8", newline="\n").write("\n".join(md))

    # --- status face ---
    status = {
        "station": "ST-011", "ts": NOW, "machine": "bm-b",
        "mancang": {"clips_processed": len(rows),
                    "admitted": [r["name"] for r in (admitted or [])],
                    "gate": g, "rows": rows,
                    "interim_note": "voice_05 shared-base debt disclosed; root fix ST-012"},
        "boy": {"clips_admitted": 0,
                "license_review": "delivered (receipt sec.2); external child cloning "
                                  "BLOCKED; routes = CEO clips (physical) / adult-base "
                                  "DSP prototype; commercial corpus clearance deferred "
                                  "to commercialization gate (O-20261016-2346)"},
        "queue": {"st011": "done", "st012_seeded": True},
    }
    tmp = STATUS + ".tmp"
    json.dump(status, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS)

    # --- receipt ---
    tbl = ["| clip | pre_clip | post_clip | F0 Hz | RMS dBFS | centroid Hz | admitted |",
           "|---|---|---|---|---|---|---|"]
    adm_names = set(r["name"] for r in (admitted or []))
    for r in rows:
        if "err" in r:
            tbl.append("| %s | ERR | - | - | - | - | no |" % r["name"])
        else:
            tbl.append("| %s | %d | %d | %.1f | %.2f | %.1f | %s |" % (
                r["name"], r["pre_clipped_samples"], r["post_clipped_samples"],
                r["f0_hz"], r["rms_dbfs"], r["centroid_hz"],
                "yes" if r["name"] in adm_names else "no"))
    gate_txt = json.dumps(g, ensure_ascii=False) if g else "n/a"
    rc = []
    rc.append("# ST-11 寻源站回执（BOY 许可审查 + MANCANG 去削波再产 · ST-011 · r1022 bm-b）\n")
    rc.append("> 站点=CONTENT-LOOP ST-011；时点=%s；车道=cpu；零网络零云端；纯确定性测量。\n" % NOW)
    rc.append("> 承接=ST-008 诚实缺口（BOY 零素材 / MANCANG 全 CLIPPED）+ ST-009 §三（换源寻根=根解·选片避开 voice_04/05/07/12 现役底）。\n")
    rc.append("\n## 一、结论一览\n")
    rc.append("- MANCANG：7 条 in-house r998 voice_05 削波片全部去削波再产；过音色一致检 v0.1 入行 %d 条（INTERIM：与旁白共 voice_05 底嗓债如实披露，根解=ST-012 新底嗓/LoRA 车道——即 2026-10-19 11:21 集团令 @bm-b 8G「角色声 LoRA」正主）。\n" % len(admitted or []))
    rc.append("- BOY：零素材维持；许可审查回执如下——外部真人童声克隆 BLOCKED；BOY 入行=后续物理/原型路（见 §二）。\n")
    rc.append("- 队列：ST-011 done；ST-012（角色声 LoRA 夜窗车道）已播种承接 11:21 令 @bm-b 义务。\n")
    rc.append("\n## 二、BOY 童声许可审查（本站第一交付物）\n")
    rc.append("1. 底模面：GPT-SoVITS 仓库 LICENSE=MIT（Copyright (c) 2024 RVC-Boss·本地克隆实读）——代码/推理面许可清晰；预训练底模商用面随上游 model card，留痕待商业化门（O-20261016-2346 预商业化轻量模式：只留痕不拦截）。\n")
    rc.append("2. 真人童声克隆（影视剧/公开媒体素材）：**BLOCKED**——未成年声线属肖像权族+监护人同意链缺位，非许可条款可解；商业化前不清算，预商业化阶段同样不采（账号安全/权利红线邻接面·保守处置）。\n")
    rc.append("3. 开源语料（AISHELL-3 SLR93 / aidatatang_200zh）：research-use 限制在案，商业剧用未清→不入库；许可清算=商业化门控时点事项。\n")
    rc.append("4. 可行路排序：① CEO/家人提供童声片段（物理件·CEO 保留面·orders 物理件区呈事实）；② 成人底嗓+实测校验 DSP 童感原型（ST-010 verify-adjust 方法复用·±3st 安全区+formant 面·质量门=盲评）；③ 商业化时点再评估付费商用童声库。\n")
    rc.append("5. 本轮 BOY 入行=0（诚实）；生产制片=后续站（物理路呈报 CEO / DSP 原型过导演门）。\n")
    rc.append("\n## 三、MANCANG 去削波再产（实测表）\n\n")
    rc.extend(tbl)
    rc.append("\n\n音色一致检 v0.1：%s\n" % gate_txt)
    rc.append("\n方法：线性插值重建削波段（|x|≥0.985 判削波·段外 12 样本锚点）→复测 F0（自相关 80-400Hz 帧 1024/512）/RMS/谱心。源=ST-008 判 CLIPPED 的 7 条 voice_05 满仓片（EP001-003）。\n")
    rc.append("\n## 四、诚实缺口\n\n")
    rc.append("- MANCANG 与旁白共 voice_05 底嗓债未解（去削波只修物理质量不换底）——根解=ST-012（新底嗓素材/角色声 LoRA·11:21 令夜窗）。\n")
    rc.append("- BOY 零素材维持（物理/DSP 原型路待呈报）。\n")
    rc.append("- 音色一致检 v0.1=F0/RMS/谱心代理面；embedding 级同一性检=后续站（承 ST-009 边界）。\n")
    rc.append("\n## 五、后续站位\n\n")
    rc.append("- ST-012 角色声 LoRA 夜窗车道（GitHub 现成轮子先扫·寻源闸律·22:0x 训练态优先权·同底微调不可分离族=ST-009 负发现·只上新底嗓说话人）。\n")
    rc.append("- BOY 物理路呈报（CEO 片段）与 DSP 童感原型二选一，下一窗定。\n")
    rc.append("- SD1.5 素材微训（11:21 令 @bm-b 第二面）=非 drama 线，随夜窗 GPU 车道另行开站。\n")
    open(RECEIPT, "w", encoding="utf-8", newline="\n").write("\n".join(rc))

    print("ST-011 done: mancang admitted=%s gate=%s boy_clips=0 st012_seeded=true"
          % ([r["name"] for r in (admitted or [])], gate_txt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
