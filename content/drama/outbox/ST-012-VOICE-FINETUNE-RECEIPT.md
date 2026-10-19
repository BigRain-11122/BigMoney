# ST-012 角色声微调回执（voice finetune · MANCANG v1 · bm-b）

> 站点=CONTENT-LOOP ST-012（gpu-night·10-19 11:21 播种，10-20 01:25 收口）；
> 承 ST-008/009/011 共底嗓债披露（MANCANG 与旁白同 voice_05 底）；
> 合法路径=ST-009 负发现（同底微调不可分离族 → 只上新底嗓说话人）=「新底嗓自举 + 微调」；
> 车道=GPU 8G（RTX 3070·fp16+grad_ckpt·Ollama 阀训练期开）；云端零调用。

## 一、结论

**七相全通（7/7），首训实跑成功。** 状态面=`results/drama_env/st012_voice_finetune.json`（state=done）。

三条 held-out 句（从未进训练集）由微调双权重合成，确定性声学判读：

| 样本 | 时长 | 采样率 | F0 中位 | 与底嗓 F0 相对差 | 谱心相对差 |
|---|---|---|---|---|---|
| 底嗓参考（自举 ep003_l02） | 3.19s | 22050 | 297.0 Hz | — | — |
| holdout_01 | 5.18s | 32000 | 322.6 Hz | 8.6% | 0.4% |
| holdout_02 | 3.22s | 32000 | 322.3 Hz | 8.5% | 9.6% |
| holdout_03 | 4.06s | 32000 | 325.3 Hz | 9.5% | 7.8% |

判读：三句 F0 彼此极稳（322.3–325.3Hz·跨度 <1%），且都在底嗓 15% 一致带内 → **微调后音色稳定收敛到自举底嗓，未回落为通用音**（ST-009 的失效模式未发生）。

## 二、相位证据

| 相位 | 产物 | 实锚 |
|---|---|---|
| bootstrap | `voice_train/st012/bootstrap/*.wav`（13 条·48.6s） | IndexTTS-2.5 零样本·新底嗓 voice_09.wav（避开现役 voice_04/05/07/12）·emo=happy（对齐 r998 满仓 cast happy6）·RTF 2.4–3.6 |
| cuda | runtime venv torch 2.14.1+cu130 / torchaudio 2.11.0+cu130 | `torch.cuda.is_available()=True`·device=RTX 3070；阿里云 cu130 镜像 ~22MB/s（pytorch.org 死慢，见 §四.1） |
| data | `corpus/train.list`（13 行 = VO sheet MANCANG 7 行 + 角色内补 6 行） | 48.6s 过诚实门 45s |
| prep | `exp/mancang-v1/{2-name2text,4-cnhubert,5-wav32k,7-sv_cn,6-name2semantic}` 各 13 行 | 四步每步产物行数断言 =13 |
| s2 | `exp/mancang-v1/logs_s2_v2Pro/G_233333333333.pth`（906.9MB） | v2Pro·batch 4·8 epochs·grad_ckpt；8 轮全跑，每轮 ~25s |
| s1 | `GPT_weights_v2Pro/mancang-v1-e1..e15.ckpt`（各 148MB） | v2Pro·batch 8·15 epochs·单进程；Epoch 0 loss 3423.9 → 15 轮完成 ~2 分钟 |
| verify | `voice_train/st012/ab/holdout_0{1,2,3}_ft.wav` | 3/3 合成成功·时长 3.2–5.2s·见 §一 |

## 三、Obsidian 级诚实边界

- 训练语料=**合成音**（IndexTTS 自举），非真人录音：音色可控但韵味上限受底模；真人录音语料=后续扩产站（见 W011 审计）。
- **人耳听感未过闸**：本次多模态听感通道未取到音频（如实记录，不代判）；确定性判据=F0/RMS/谱心代理面，**非 embedding 级音色同一性**（承 ST-009 边界）。
- 底嗓 voice_09 是试验选择（非正典定谳）；入行=ST-009 音色一致检复检 + manifest admission 后另开站，本站不写 voice_bank。
- 13 行语料接近下限（48.6s/45s）：一轮微调足以验证链路，但音色还原度**不足以直接投产**；扩产判据见 `content/drama/outbox/VOICE-CORPUS-AUDIT.md`（W011）。

## 四、修法判例（上游兼容，全部本窗实锚）

1. **pytorch 官方源在本链路极慢 → 用阿里云镜像**：`https://mirrors.aliyun.com/pytorch-wheels/cu130/` 实测 22MB/s（官方源 1.9GiB 十余分钟无进展）。uv 用 `--find-links <mirror> --index-url <mirror>`。
2. **`prepare_datasets/*.py` 的 cwd 契约**：脚本内用 `now_dir/GPT_SoVITS/...` 拼内部包路径，必须在 **repo 根**跑；`text` 包要靠 PYTHONPATH 注入 `GPT_SoVITS/`。
3. **`1-get-text.py` 静默空转**：`clean_text(version=None)` 走错前端 → 全行异常被吞，产物 0 行；必须给 `version=v2Pro` 环境变量。
4. **G2PWModel 相对路径**：`chinese2.py` 硬编码 `GPT_SoVITS/text/G2PWModel`（相对 cwd），而真实模型在 `GPT_SoVITS/text/G2PWModel` → 在 repo 根建 junction 补齐（可逆·不复制 300MB）。
5. **`s2_train` 的 `data.exp_dir` ≠ `s2_ckpt_dir`**：前者指数据集目录（父层），后者指日志/权重目录（`logs_s2_<ver>` 子层）。混用会 `AssertionError` 于 `2-name2text.txt`。
6. **`1-get-text` / `3-get-semantic` 分片需合并**：webui 会把 `2-name2text-<part>.txt` 合并为 `2-name2text.txt`、`6-name2semantic-<part>.tsv` 加表头合并；headless 必须自己实现（本 driver 已做）。
7. **Windows 上 s1_train 的 DDP 崩溃**（torch 2.14+cu130·gloo）：`devices=-1` → `STATUS_ACCESS_VIOLATION 0xC0000005`；改 `devices=1`+`auto` → ckpt 回调 `strategy._lightning_module` 不存在；Windows **nccl=False**。正解=单进程 + 回调走 `trainer.lightning_module` + `bucket_sampler` 加 `dist.is_initialized()` 守卫。补丁件=`sentinel/work-items/st012-single-device-patch.py`（apply/revert·`.st012orig` 备份）与 `bucket_sampler.py` 内 `ST012` 注释行。
8. **`if_save_latest=True` 会删光 ckpt 目录**（含正在恢复的 ckpt）→ torch 2.6+ `weights_only` 恢复失败；headless 短训设 False，重启即从头跑（15 轮 ~2 分钟）。
9. **`inference_cli.py` 的 `--ref_text/--target_text` 是文件路径**，且参考音硬门 3–10s、输出固定名 `output.wav`（批量需自行改名）。

## 五、恢复义务

- Ollama 阀：训练期写入 `keepwarm.pause` + 停 keep-warm + `ollama stop`；**收尾已移除**，实测 `pause=False`、任务 Ready、`/api/tags` 4 模型可服务。
- 产物目录（gitignored）：`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_train\st012`；权重：`GPT_weights_v2Pro/`、`logs_s2_v2Pro/`（均在 media 区）。
- 上游改动清单（均为可回退的小补丁）：`s1_train.py`（ST012 标记）、`bucket_sampler.py`（ST012 注释 + `is_initialized` 守卫）、repo 根 `GPT_SoVITS/GPT_SoVITS/text/G2PWModel` junction。

## 六、下一步（候选站位）

- 语料扩产（W011 审计已出：60 集台词水位/各角色缺口）→ 1 分钟+ 语料二轮微调，再做 ST-009 复检入行。
- 其余角色：CH（主角·台词最多）、XIONG/XIONGWEI（同嗓带·DSP 分档已验，微调只服务新底嗓，故须先自举新底）。
- 人耳盲评站：本条 A/B 三句可作盲评素材，混入别角色以验"可辨认度"。