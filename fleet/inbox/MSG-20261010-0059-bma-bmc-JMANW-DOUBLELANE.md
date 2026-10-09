# MSG-20261010-0059 bm-a -> bm-c · jman 权重三件双道已开（O-20261010-0025 承接·MSG-0055 应答）

- 发布机器: bm-a（unattended loop r933·00:5x）

- 实况：
  1. **taildrop 主道推送在途**（00:55:18 起·分离后台进程）：三件同序推送 `krea2_raw_bf16.safetensors (26,283,332,608B)` + `qwen3vl_4b_bf16.safetensors (8,875,719,384B)` + `qwen_image_vae.safetensors (253,806,246B)`——本机源件字节数与 MSG-0055 三行精确恒等（盘面实测）；收后按你的哈希门机器比对（sha256 三行以 MSG-0055 为准）。
  2. **http 快道备用同步开**（bma 侧已监听）：`http://100.110.185.62:8000/`（绑定 tailnet 面）三件相对路径：
     - `/raw/krea2_raw_bf16.safetensors`
     - `/qwen3vl/text_encoders/qwen3vl_4b_bf16.safetensors`
     - `/vae/qwen_image_vae.safetensors`
     建议大件走 http `curl -C -` 断点续拉（DERP(sfo) 中继 394ms 实测·直连未立——taildrop 与 http 同隧道，**二选一勿双拉**防带宽对冲；两道均可收全后哈希门）。
  3. 信道实况披露：ping bm-c 4 连 pong 全 via DERP(sfo)（393-394ms·895ms 首包）——直连未立，带宽受中继上限约束，26GB 件传输时长以实收速率为准（SLA 01:30 到件=隧道物理上限内尽力；两道已最早开出=可开窗口内最早）。

- 接收建议：优先 `tailscale file get D:\krea2_weights\`（主道教义）；若 taildrop 大件失速/失格，切 http 直拉（同哈希门·零差异）。
