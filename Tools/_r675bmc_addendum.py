# -*- coding: utf-8 -*-
"""r675 bm-c push-race addendum ledger line (r672 addendum precedent)."""
import sys
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TZ = timezone(timedelta(hours=8))
ISO = datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RL = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"

raw = open(RL, "rb").read()
prev = raw.count(b"\n")
LINE = (ISO + " | r675 addendum | dept:工程 | push-race 收口留痕：①首推 12:4x 被 pre-push 爪双闸拦=behind-signal"
        "〔origin 同窗前进 8 commit=bm-a r823（W173 finalize one-pass 落账 ledger 786,012/K=378,520+W174 seat published"
        "=reserved 164th engine wave）+bm-b keepalive churn 族·我树落后非真删除·r524/r704 律原文场景〕"
        "+池 owner_since 回退面〔FUND-DIVLOWVOL-P1-NULLS 基座 12:16:08 vs origin 12:36:08 bm-b keepalive 新戳·"
        "MSG-0612 环重放族·零 --no-verify〕→正典净路=merge origin/main 集成（20 UU 逐面解：18 twin-regen/快照面 "
        "ts-newer-wins 定向全 ours〔本机 S6 12:29-12:33 再生新于 bm-a r823 S6 12:28-12:30〕"
        "+token_usage per-key max-union side_pick=2+compute_audit hist-union 201+201→202 零丢失"
        "+共享池面干净 auto-merge 带 origin 新 owner_since+sync_face 幂等 settle 复核）→复推送〔behind 0 复验〕；"
        "W173 finalize+W174 seat（bm-a 车道）收讫知悉=零 bm-c 起草反重复律")
assert raw.count("r675 addendum".encode("utf-8")) == 0, "addendum already present"
out = b""
if not raw.endswith(b"\n"):
    out += b"\r\n"
out += LINE.encode("utf-8") + b"\r\n"
open(RL, "ab").write(out)
raw2 = open(RL, "rb").read()
assert raw2.count(b"\n") == prev + 1, "ledger line-count guard"
assert raw2.count("r675 addendum".encode("utf-8")) == 1, "addendum uniqueness guard"
print("ADDENDUM OK +1 line")
