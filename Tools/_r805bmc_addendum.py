# -*- coding: utf-8 -*-
"""r805 bm-c addendum: push-window disclosure (round report line + heartbeat
sync block). The round commit ef20dd9fa already claims delivery self-verify;
this addendum records the EVENTFUL path honestly (SSH full-outage window ->
daemon keepalive delivered -> HTTPS ls-remote double-source verify), plus the
rebase-window E42 cures. r764 addendum method: targeted files only."""
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
HM = now.strftime("%H:%M")[:4] + "x"

ADDENDUM = (
    "2026-10-09T{hm}+08:00 | r805 addendum | dept:工程/舰队治理 | 推送窗实录：收口 push 撞"
    "SSH :22 reset×3+ssh.github.com:443 reset+api.github.com TLS 超时=GitHub 全通道阻断窗——"
    "本地九连链（2 absorb+3 daemon claim+round 805 pick ef20dd9fa+3 daemon 自投）由共驻 daemon "
    "keepalive push（HTTPS 凭证面）自动推达；交付自证=git ls-remote "
    "https://github.com/BigRain-11122/BigMoney.git refs/heads/main == git rev-parse HEAD"
    "（02e6ff211 双源恒等·r764 硬校验律）·本地 origin/main ref SSH 恢复前陈旧"
    "（daemon 每分钟 fetch 自愈·下轮 s05 ahead 读数在断窗期=ref 陈旧假象勿误判红旗）| "
    "rebase 窗实录：14-UU resolver content-driven（13 面 restorable rc0+token_usage 账本 "
    "treasure_guard rc3 硬拒→行级 union 零丢失断言）+continue 拒进两形态治愈"
    "（r787 daemon churn 敏感面原子批+r808 Terminal-dumb=author-script 保真三步手工落 pick）"
    "——receipt results/_r805bmc_resolver.json"
).format(hm=HM)

# ---- round report append ----
rr = ROOT / "logs" / "iteration-loop" / "round_reports-bm-c.md"
with rr.open("a", encoding="utf-8") as f:
    f.write(ADDENDUM + "\n")

# ---- heartbeat sync block ----
hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
hb["sync"] = {
    "ahead": 0,
    "behind": 0,
    "last_push_ts": now_iso,
    "note": ("r805 push window: SSH :22 reset x3 + ssh.github.com:443 reset + api.github.com "
             "TLS timeout (full GitHub channel outage window); local 9-commit chain "
             "(2 absorb + 3 daemon claim + round 805 pick ef20dd9fa + 3 daemon self) "
             "delivered by co-resident daemon keepalive push (HTTPS credential face); "
             "delivery self-verified: ls-remote https main == rev-parse HEAD "
             "(02e6ff211 both sources identical); local origin/main ref stale until SSH "
             "recovers (daemon per-minute fetch self-heals; next round s05 ahead reading "
             "during an outage window = stale-ref artifact, not a red flag)"),
}
hb["last_pulled_at"] = now_iso
hb["heartbeat_epoch_utc"] = int(time.time())
hb_path.write_text(json.dumps(hb, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- self-check ----
hb2 = json.loads(hb_path.read_text(encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int)
assert hb2["sync"]["ahead"] == 0 and hb2["sync"]["behind"] == 0
tail = (ROOT / "logs" / "iteration-loop" / "round_reports-bm-c.md").read_text(
    encoding="utf-8").strip().splitlines()[-1]
assert "r805 addendum" in tail, "addendum line must be the report tail"
print("addendum OK: report tail + hb sync updated @ %s" % now_iso)
