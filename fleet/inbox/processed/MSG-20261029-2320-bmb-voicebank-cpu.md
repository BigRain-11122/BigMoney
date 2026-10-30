# MSG-20261029-2320-bmb-voicebank-cpu — 音色库 CPU 分片派工（bm-a / bm-c 各领 2–3 条声线）

- 发出：bm-b 交互会话，2026-10-29 23:20
- 依据：CEO 令「机队这么多 CPU 核心数多的机器，丢给他们 不要浪费算力」
- 代码：`Tools/voicebank/` 已上链（commit **2d4d269a**），各机下次拉取即可用

## 一、这份工作是什么

给生产线建「素人音色库」。单条声线的 CPU 段（下载→降噪→ASR→切段）很吃 CPU、不吃 GPU，
正好适合分给各机；训练段（SoVITS）留在有 GPT-SoVITS 的机器上。

质量闸（不合格一律判负，不许凑数）：单人可辨（F0 四分位距/中位数 < 0.75）、语料 ≥ 8 分钟、
静音/说话能量比 ≤ 0.30、44.1 kHz 保真、全程降噪。

## 二、每台机器要跑的三步

```powershell
# 0) 依赖（一次装好；python 用本机任意 3.10+ 环境）
pip install -i https://mirrors.aliyun.com/pypi/simple/ faster-whisper numpy noisereduce zhconv bilibili-api-python

# 1) 选人：按分配的主题搜候选（输出包内返回 mid/bvid/时长/播放）
python Tools\voicebank\vb_worker.py --help      # 看参数

# 2) 出语料（CPU 段，只在本地跑，不训练）
#    --jobs 取「物理核数/2」，16C→8，32C→12
python Tools\voicebank\vb_worker.py --voice bmc-v01 --bvids BV1xx,BV1yy --minutes 25 --jobs 12 --out <本机盘>\voicebank\shards
```

产物：`<out>\<voice>\seg\*.wav`（44.1 kHz）+ `exp\list.txt` + `SHARD.json`。
**不要自行训练**：训练统一在装好 GPT-SoVITS 的机器上做（bm-b 现在能训，bm-c 若已装可升级为训练机）。

## 三、分片

| 机器 | 领活 | 主题（每人一个声音，不要同一人拆两机） | 产能建议 |
|---|---|---|---|
| bm-c（16C/32T） | 3 条 | ①川渝男声唠嗑 ②粤语讲古 ③中年女声电台 | jobs=12，夜间跑 |
| bm-a | 2 条 | ④老年男声说书 ⑤东北女声日常 | 白天让路时段勿跑 |
| bm-b（本机） | 2 条 | ⑥气声/低语女声 ⑦少年男声 | 与 GPU 训练错峰 |

## 四、回报格式（回到本 inbox）

```
MSG-<日期>-<时刻>-<节点>-voicebank.md
- voice: bmc-v01 / bma-v04 …
- 来源 bvid + 说话人 mid
- 语料：段数 / 分钟 / F0 中位
- 闸门：单人可分? 静音比? 噪声底?
- shard 路径：<本机绝对路径>
- 备注：哪些候选被判负及原因（避免他机重复筛）
```

## 五、注意

- 只跑 CPU 段，别抢生产车道的 GPU；
- 不要用多人有声剧、直播切片、带 BGM 的素材（会被闸门判负）；
- 下载只用 `vb_worker.py` 内建的最高码率通道（184 kbps AAC 上限），不要转码降质。
## 六、回传通道已打通（2026-10-29 23:2x 实测）

跨机大文件走 **Taildrop**（本机 `tailscale file cp` 对 bm-a/bm-c 均 rc=0 入队）：

```powershell
# 在机队节点：把 shard 打包后直接投给 bm-b
Compress-Archive -Path <out>\<voice>\seg,<out>\<voice>\exp\list.txt -DestinationPath <out>\<voice>.zip
tailscale file cp <out>\<voice>.zip bm-b:

# 收货侧（bm-b）：
tailscale file get --conflict overwrite E:\Fluxgroup\.codely-cli\voicebank\_inbox
```

配套：`Tools/voicebank/vb_assets.py` 把一条已训练声线打成自包含资产
（model.pth + ref.wav + demo + meta + corpus.zip），落在 `voicebank\assets\<voice>\`，
索引 `assets\INDEX.jsonl`。机队若自行训练，同样用这个脚本打包后 Taildrop 回传。