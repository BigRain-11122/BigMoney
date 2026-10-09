# -*- coding: utf-8 -*-
"""r808 bm-c closeout addendum: delivery-chain trail row + sync note.
Records the honest post-close delivery chain that happened AFTER the main
round-808 close row was committed: 3x push rejection (bm-a r919 in-flight),
pull --rebase with 1 UU (pool_core_samples.jsonl tail-race, union 13 lines
ts-chronological), picks 2/3 saturation marker pollution (r825-class, healed
4380a35cf), pre-push claw block (4 bm-a estate files in deletion set =
stale-base artifact, NOT a real deletion), merge origin/main 64f6087be
(zero overlap clean), push OK, HTTPS ls-remote == HEAD 86500b3eb."""
import json, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
HM = now.strftime("%H:%M")[:4] + "x"
epoch = int(time.time())
HEAD = "86500b3eb"

row = (
    "2026-10-09T{hm}+08:00 | r808 addendum | dept:工程（收口后送达链实录·r805 sync-note 先例法） | "
    "本地未达 origin commit 数=0（HTTPS ls-remote==HEAD 86500b3eb 双源恒等自证） | "
    "送达链：主收口 commit a9486d0d1 push 撞 bm-a r919 在途 3 commit（b8a9a9112 tip）→daemon 活跃面吸收 2 连"
    "（4034967c7/20da59fff·tight-window）→pull --rebase 停 pick1 单 UU=pool_core_samples.jsonl 尾追竞态"
    "（他方 12 行 W199 采样 vs 我方 1 行 w17 采样·union 13 行 ts 时间序零丢失·resolver=Tools/_r808bmc_rebase_resolve.py）"
    "→picks2/3 期间 saturation 双面冲突标记被续入 commit（rebase 提交绕过 pre-commit 爪·r825 类实弹）"
    "→heal commit 4380a35cf（盘面 daemon 清版 0 标记验证后吸收·73 行标记清除）"
    "→push 撞 pre-push 爪拦截（删除集含 bm-a 4 件 r919 estate 文件=_r919bma_{{closeout_writes,hb_report,s05scan,s6_driver}}.py"
    "·根因=我方 rebase 基座 b8a9a9112 旧于其 estate closeout commit 64f6087be=陈基伪删除非真删）"
    "→正法=merge origin/main 64f6087be（7 件全 bm-a 面+4 estate 文件·与我 95 件零交集·ort 自动合并净）"
    "→push OK 送达自证 | 教训入池：rebase continue 的 add+continue 原子环在 daemon 高频活写面上必须带标记守卫"
    "（add 前扫盘面标记·daemon 未覆盖即等待·本窗实弹=污染续入 2 commit 后靠 heal 收口）"
).format(hm=HM)

rr_path = ROOT / "logs" / "iteration-loop" / "round_reports-bm-c.md"
with rr_path.open("a", encoding="utf-8") as f:
    f.write(row + "\n")

sync_note = (
    "r808 closeout delivery chain: push x3 rejected (bm-a r919 in-flight pushes) -> pull --rebase "
    "(1 UU pool_core_samples.jsonl tail-race, union 13 lines ts-chronological, zero loss) -> picks 2/3 "
    "saturation marker pollution healed (4380a35cf, r825-class) -> pre-push claw block (4 bm-a estate "
    "files in deletion set = stale-base artifact, NOT real deletion) -> merge origin/main 64f6087be "
    "(zero-overlap clean) -> push OK -> delivery self-verified HTTPS ls-remote == HEAD (86500b3eb)"
)

for path, in (((ROOT / "state-bm-c.json"),), ((ROOT / "fleet" / "machines" / "bm-c.json"),)):
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["head_sha"] = HEAD
    obj["sync"] = {"ahead": 0, "behind": 0, "last_push_ts": now_iso, "note": sync_note}
    for k in ("ts", "updated", "updated_at"):
        if k in obj:
            obj[k] = now_iso
    if path.name == "bm-c.json":
        obj["heartbeat_epoch_utc"] = epoch
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")

hb2 = json.loads((ROOT / "fleet" / "machines" / "bm-c.json").read_text(encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert hb2["head_sha"] == HEAD
print("addendum OK: rr row + sync note + head_sha=%s ts=%s" % (HEAD, now_iso))
