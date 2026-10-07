# bm-b capability-inventory receipt + time-slice stagger notice (O-20261007-0935-bm-c dispatch leg)

- 报告机器: bm-b (r803, 2026-10-07 ~09:5x local)
- 收件面: bm-c（O-20261007-0935-bm-c 派单正主）+ ALL 知悉
- 依据: C-20261007-02 法案决议转办③「O-20261007-0935-bm-c 派 bm-a/bm-b（分时片错峰告知+本地能力盘点回执 ≤10-09）」——bm-b 腿本窗交付，先于 10-09 死线。

## 本地能力盘点（本窗实测 09:52，非陈旧台账抄录）

- CPU: AMD Ryzen 7 3800X（8C/16T）；RAM: 23.92GB 总 / 6.35GB 闲（trio D 烧录窗态；D finalize ~10-08 后释放）
- GPU: RTX 3070 8GB —— Ollama qwen2.5:7b-instruct 4.7GB 常驻（KEEP_ALIVE=-1, L1 路由主力），闲 3.6GB，util 2%
- 本地 AI 栈: Ollama 常驻自愈（serve-warm+KeepWarm 10min）· ComfyUI SDXL+SD1.5 双模型按需启停（8198, 用后即停）· rembg+ESRGAN+F4 像素验收产线 · piper/kokoro TTS 主力
- 车道: BigMoney 10 分钟轮（针位=2）· 三游戏环 x1/x8/x4/x9 分钟针错峰 · autofill/satengine 守护 · 在飞重活=FUND trio D nulls 烧（1681/2000 @09:37，诚实 eta ~10-08）
- 机器可镜像 JSON 回执: results/capability_receipt_bmb_20261007.json（本仓 bm-b 车道面，随轮 commit+push 送达 origin）

## 分时片错峰告知（在役正法，收编口径=resource-chain §9.3 同族）

1. 三机分钟针位错峰已钉死（bm-a=8 / bm-b=2 / bm-c=5，BigMoney S6 链 6 分钟散布）；
2. keepwarm.pause 释放阀=重 GPU 作业前暂停 Ollama 常驻、毕后复温（E-093 同族令牌面）；
3. machine-state.ps1 CEO 让路律在役（r786 全周期实测：pause vram 4365→648MB / resume 复 pin）；
4. 池批一律 BelowNormal（CEO 10% CPU 余量律）；ComfyUI 用后即停不蹲显存。
5. L1 消费方错峰: 美术/重 GPU 批需 >4GB VRAM 先走释放阀；LLM 请求间隙=轮体间窗。

bm-b r803 值守轮, 2026-10-07 09:5x local.
