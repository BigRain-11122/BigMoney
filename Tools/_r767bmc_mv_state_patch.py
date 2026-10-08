# -*- coding: utf-8 -*-
"""r767 bm-c MV-task state patch: splice CEO-order MV continuation pointer
into state-bm-c.json next/next_pointer/did fields (worktree face; r768
round-start absorb will commit it -- same own-face pattern as r767 first
half). Purpose: r768 tick reads worktree state next pointer -> sees MV task
without waiting for full ORD-delta re-analysis. Non-destructive: fields are
prepended with the MV block, existing r768 BigMoney pointer kept verbatim."""
import json

SP = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json"

MV_BLOCK = (
    "MV CEO 令在飞（S3 最高优先·O-20261008-1715/1755-bm-c·承接回执已落集团 orders.md "
    "d1cd7a550f·≤1h SLA 23min 达成）：20 秒完成片级样片全链——r768 续作点=①umt5-xxl text "
    "encoder GGUF 源调研下载（ModelScope city96/QuantStack 双 404·web_search 全面查镜像·"
    "fallback=Comfy-Org wan_2.1 repackaged fp8 safetensors 原生 CLIPLoader 通道）②ComfyUI-GGUF"
    "+VideoHelperSuite 节点安装（custom_nodes 现仅 Manager/DD-Translation/aux）③验收 "
    "results/_r767bmc_wan_fetch.log（Q4_K_M 3.43GB+VAE 1.41GB 下载已点火 pythonw 分离·"
    "8 段并行 20s 内 >1.2GB·sha256 三闸校验内置）④SDXL 关键帧（sd_xl_base_1.0 在位·暖橙一统"
    "+玻璃青唯一冷色·禁中国风·六模块提示词+负面词三模块 20-30%）⑤Wan2.2-TI2V-5B-Q4_K_M i2v "
    "视频段（首帧锚图法·77-97s 副歌窗·24fps 直用）⑥调色全链（分频三带实测+halation gblur "
    "sigma14+screen+灰基 softlight 颗粒 0.45+dither 暗角）⑦窗内歌词字幕+2.35:1 遮幅+AIGC "
    "显著标识+乐句切点对轴（77.0=bar35）⑧门链自检（三律+三病清零+帧级人眼）→ 出口 "
    "cph4/fleet/mv0001-handover/outbound/MV0001_爱在西元前_20s样片_v1.mp4 + 完工回执"
    "（十二项清单逐项打勾·落集团 orders.md）→ 完工后恢复面：qwen3.6-coder:35b 重载（keep_alive "
    "Forever）+MiniGameComfyDraftTick enable。R 件正典=cph4/research/ 六波（HANDOVER.md §6 清单）"
    "；移交包=cph4/fleet/mv0001-handover/（23 件）。|| "
)

with open(SP, encoding="utf-8") as fh:
    state = json.load(fh)

for key in ("next", "next_pointer"):
    if key in state and not state[key].startswith("MV CEO"):
        state[key] = MV_BLOCK + state[key]
if "did" in state and "O-20261008-1715" not in state["did"]:
    state["did"] = ("r767 late-window addendum: CEO MV order O-20261008-1715/1755-bm-c "
                    "accepted (receipt d1cd7a550f, qwen unloaded + DraftTick disabled, "
                    "Wan2.2 Q4_K_M+VAE fetch ignited); see next pointer MV block. || "
                    + state["did"])

with open(SP, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)

s2 = json.load(open(SP, encoding="utf-8"))
assert s2["next"].startswith("MV CEO"), "MV block splice failed"
assert s2["next_pointer"].startswith("MV CEO"), "MV block splice failed (ptr)"
assert "O-20261008-1715" in s2["did"], "did addendum failed"
print("MV_STATE_PATCH_OK: next/next_pointer/did spliced, "
      "round_no=%d kept" % s2["round_no"])
