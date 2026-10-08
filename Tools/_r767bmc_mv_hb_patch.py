# -*- coding: utf-8 -*-
"""r767 bm-c MV-task heartbeat patch: splice MV continuation block into
fleet/machines/bm-c.json next/did + refresh liveness stamps (epoch JSON-int
per R170/R178, clock_read T-separated ISO per R262). Same splice face as
Tools/_r767bmc_mv_state_patch.py; worktree face for r768 absorb."""
import json
import time
import datetime

HP = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json"

MV_BLOCK = (
    "MV CEO 令在飞（S3 最高优先·O-20261008-1715/1755-bm-c·承接回执已落集团 orders.md "
    "d1cd7a550f）：r768 续作=umt5 enc GGUF 源调研下载+ComfyUI-GGUF/VHS 节点装+SDXL 关键帧+"
    "Wan2.2-TI2V-5B-Q4_K_M i2v（Q4_K_M 已 sha256 校验落盘 3.43GB·VAE 在途 results/"
    "_r767bmc_wan_fetch.log）+调色链+字幕/遮幅/AIGC+门链自检→outbound 20s 样片+完工回执；"
    "完工后恢复=qwen 重载+DraftTick enable。详见 state-bm-c.json next MV block。|| "
)

with open(HP, encoding="utf-8") as fh:
    hb = json.load(fh)

for key in ("next", "next_pointer"):
    if key in hb and not str(hb[key]).startswith("MV CEO"):
        hb[key] = MV_BLOCK + str(hb[key])
if "did" in hb and "O-20261008-1715" not in hb["did"]:
    hb["did"] = ("r767 late-window addendum: CEO MV order accepted (receipt d1cd7a550f, "
                 "qwen unloaded + DraftTick disabled, Wan2.2 Q4_K_M fetched sha256-OK); "
                 "see next MV block. || " + hb["did"])

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
for k in ("last_seen", "last_seen_at", "updated", "updated_at", "ts", "last_run_at",
          "last_ts", "clock_read"):
    if k in hb:
        hb[k] = now
hb["heartbeat_epoch_utc"] = epoch

with open(HP, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

h2 = json.load(open(HP, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and not isinstance(
    h2["heartbeat_epoch_utc"], str), "epoch must be JSON int"
assert "T" in h2["clock_read"] and "+" in h2["clock_read"], "clock T-separated"
assert str(h2["next"]).startswith("MV CEO") and "O-20261008-1715" in h2["did"]
print("MV_HB_PATCH_OK: next/did spliced, liveness %s epoch=%d" % (now, epoch))
