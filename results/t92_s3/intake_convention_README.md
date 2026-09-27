# 音频工单车道 intake 约定（T-92 s3 · bm-b 常设生产车道）

> 前例=E:\Minigame\Tools\art-queue（美术工单车道）范式移植到音频；机器直达律 U187/U240（引擎本地安装，不走 git 不跨机传输）。

## 提交方（游戏项目/任何车道需求方）

1. 把工单 JSON 投进 `incoming\`（一个文件=一单，文件名=单号建议）。
2. **禁止**自行启动 piper/ffmpeg——渲染归 worker（idle-window 执行体）独占管理。
3. 产物与证据落 `out_dir`（工单里指定），订单完成后工单文件移入 `done\`（失败进 `failed\`，run 日志见 `run_<单号>.log`）。

## 工单 JSON 约定（字段=kind/n_seeds/out_dir/style 按音频适配）

```json
{
  "id": "myproj-voice-001",
  "project": "项目名/用途说明",
  "out_dir": "E:\\Minigame\\MyProject\\audio\\out",
  "style": "sfx",
  "n_seeds": 1,
  "jobs": [
    { "name": "sfx_ui_click", "kind": "voice", "text": "要合成的中文文本", "n_seeds": 2 },
    { "name": "bgm_loop_master", "kind": "master", "input_file": "E:\\...\\raw.wav", "style": "bgm" }
  ]
}
```

- `style` = 类目标（X989 14 号 L0 律逐字）：`sfx`=-16 / `bgm`=-18 / `amb`=-20 / `voice`=-16 LUFS（±1LU，TP∈[-14,-3]dBTP，44.1kHz 单声道 s16）。工单级默认 + 作业级覆盖。
- `kind=voice`：piper TTS 合成（默认音色 zh_CN-huayan-medium，可 `voice` 字段覆盖）；`n_seeds`=同文本多取次数（piper 同文本渲染非确定——r316 f1，逐取逐判，md5 为记录）。
- `kind=master`：已有音频文件走母带链（`input_file` 必填）。
- **作业命名建议携带类前缀**（`sfx_`/`bgm_`/`amb_`）——AudioGateCheck 类窗口（L0-3 时长窗）按前缀判类。

## 执行方（idle-window worker）

- 触发：`powershell -NoProfile -ExecutionPolicy Bypass -File E:\Minigame\Tools\audio-queue\audio_queue_worker.ps1`（空闲窗调用；信封律=RAM<4GB 禁开新重活、全静默零弹窗、本车道纯 CPU）。
- 锁：`worker.lock` 30 分钟过期；同刻单执行体。
- 诚实红：物理不可达标素材（spike-carried 等）3 轮内不收敛=FAIL 进 `failed\`，重制归 L3/L4 人轨——链条不背锅（r316 case-B 律）。
- 证据（L0-8）：每单 `out_dir\manifest.json`（工具/LUFS/TP/bytes/MD5/迭代轨迹逐取记录）。
