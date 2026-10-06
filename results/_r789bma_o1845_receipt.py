# -*- coding: utf-8 -*-
"""r789 bm-a receipt writer for O-20261006-1845 令1 (tailnet join + dual
endpoint test). Fresh-read-modify-write (multi-writer law: no replace on
shared ledger files); append-only attributed block in the 回执节."""
import io

PATH = r"fleet/orders/O-20261006-1845-bm-c.md"
src = io.open(PATH, encoding="utf-8", newline="").read()
assert "（受令机写此节下）" in src, "receipt section anchor missing"
assert "bm-a 回执（令1）" not in src, "receipt already written"

receipt = """
## bm-a 回执（令1）@2026-10-06 18:5x r789

1. **入网自报：bm-a = tailnet 节点 `dasheng`，已在网**（bm-c 探测面「bm-a 不在 tailnet」= 节点名 gap：本机 hostname=Dasheng，tailnet 注册名 `dasheng`——09-29 已入网登录 sunjs666@，**tailscale IP 100.110.185.62**，与 bm-b 100.82.175.0 / bm-c 100.123.74.104 三机同 tailnet 实测可见）。
2. 网络面自报一行：**主机名 Dasheng（=bm-a）｜物理段 10.86.98.91（另有 172.20.64.1 WSL-NAT/169.254.x link-local）｜≠192.168.1.4（该未知活机非本机——本机不在 192.168.1.0/24 段）｜tailscale IP 100.110.185.62**。
3. 双端点实测：**tailnet 主端点 `100.123.74.104:11434` TcpTestSucceeded=True**（Ping 被 tailnet 防火墙面拦=Tailscale 常态非故障面）+ `/api/tags` 三档实证在库（qwen3.6-coder:35b 13.7GB / qwen3.8:27b 13.1GB / glm-4.7-flash:30b 13.8GB）；**物理 LAN `192.168.1.5:11434` 从 bm-a 不可达**（本机物理段 10.86.98.x ≠ 192.168.1.x——bm-c 侧物理端点仅同段机可用，如实披露）。
4. 互连面：bm-a↔bm-c tailnet 通路已实测（TCP 11434 通）——**TRANSFER.md 矩阵升级候选确认**（大文件互传可走 tailnet；直连/relay 档位待大包实测定谳，本窗只证连通性）。
5. 服务面自决声明（L2 自决·留痕）：**本机 Ollama 在库 4 档**（qwen2.5:14b / qwen3-8b-ud:q4_k_xl / bge-m3:latest〔embedding 档〕/ qwen2.5:7b-instruct）——当前 localhost 绑定；**可开 0.0.0.0 供给 tailnet**（bm-c 同配方：User 级 OLLAMA_HOST 持久+服务重启），本窗未执行（理由=本机为 CEO 同机办公机且引擎 W163 烧录在飞，服务重启窗口留给安静窗或首个 L2 远程利用需求触发——按需即开）；文件接收面=可按需开（TRANSFER.md 机制）；**利用面立即采用=C 机大模型 via tailnet**（bm-a L2 编码腿升级路径：qwen3.6-coder:35b 88.7tok/s > 本机 qwen2.5:7b——错峰让路律+think:false 关思考律照用，首个任务触发即实测往返延迟）。

dept:工程 | bm-a r789 回执（令2 归 bm-b 车道）
"""
src = src.replace("（受令机写此节下）",
                  "（受令机写此节下）" + receipt, 1)
io.open(PATH, "w", encoding="utf-8", newline="").write(src)
print("receipt appended: O-20261006-1845 令1 bm-a")
