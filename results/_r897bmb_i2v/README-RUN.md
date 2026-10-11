# 专辑 i2v 本地机队批 · 执行手册（CEO 令 2026-10-11 晚「视频还是本地弄吧，我的机队全部加入」）

云端积分批作废（A/B/C 案撤）·本地零积分·三机全加入。产物=纯画面 mp4（音轨禁令·装配端配歌）。

## 0 一次性准备（每机）
```bat
:: 1) 拉包（FluxGroup 仓）
git pull
:: 2) 拉 53 帧（media gitignored 不走 git·bm-c :8800 常驻分发）
curl -f -C - http://100.123.74.104:8800/album-frames-v22.zip -o album-frames-v22.zip
python -m zipfile -e album-frames-v22.zip <FluxGroup仓库根>\media\mv-album-001-jay\
```
解出后应有 `<repo>\media\mv-album-001-jay\frames\XQ_*.png / KN_*.png` 共 53 件。

## 1 权重就绪
- 768P 正片（bm-c/bm-a）：int8 DiT + turbo 4step LoRA + NVFP4 文本编码 + video VAE（f16）——文件名各机可不同，客户端启动时按 int8/convrot、turbo/4step、nvfp4、video/fp16 关键词自动匹配本机文件名（匹配不到=缺件，先补权重）
- 480P animatic（bm-b）：同上但 DiT=int4_convrot
- ComfyUI ≥0.36 起 8188

## 2 跑批（长批一律 pythonw 常驻·勿前台）
```bat
:: bm-a（可爱女人 KN 29 单·768P int8）
pythonw h3_i2v_album.py --repo <repo> --lane bma  *> 日志见下
:: bm-b（全 53 单·480P int4 animatic 预览线）
pythonw h3_i2v_album.py --repo <repo> --lane bmb
:: bm-c（星晴 XQ 24 单+V2_KFL 插队·768P int8·清单=run-bmc-v1.json）
pythonw h3_i2v_album.py --repo <repo> --lane bmc
```
启动正法（PowerShell）：
```powershell
Start-Process <pythonw.exe> -ArgumentList 'h3_i2v_album.py','--repo','<repo>','--lane','bma' -WindowStyle Hidden -RedirectStandardOutput <repo>\media\mv-album-001-jay\log-bma.out.txt -RedirectStandardError <repo>\media\mv-album-001-jay\log-bma.err.txt
```
（脚本路径用绝对路径；pythonw+双 redirect=脱离会话常驻·会话死批不死）

## 3 断点续跑 / 让路
- SKIP 断点续跑：产物 >100KB 即跳过；中断后重跑同一命令即续
- CEO 用机让路律照常：pause 后批被杀属预期，CEO 全面开工/复役后重跑命令即续
- 种子确定性：seed=id-MD5 派生，重跑同单同种子同画

## 4 回收规则
- 停滞 >4h 的单（如对端让路窗长）：另一台 768P 机 `--only ID1,ID2` 认领补跑（--only 优先于 lane 过滤）
- 完成回执：progress-&lt;lane&gt;.jsonl + fails-&lt;lane&gt;.txt（落各自 media/ 区）

## 5 硬律
- 不动他窗 ComfyUI 队列项（FIFO 共服）
- int4 产物=animatic 预览专用，不进正片（判例在册）
- 产物只落 media/（gitignored）·不上 git
- 长度网格 17k+5·fps24·变速在装配端做（本批直出常速）
