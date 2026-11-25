"""r2116 fix addendum: round-report line + heartbeat smoke verdict correction."""
import io
import json
from datetime import datetime

NOW = datetime.now().astimezone()
ISO = NOW.isoformat(timespec="seconds")

FIX = ("三条红已清：①`idx_fut_proxy_noise` 重算 -> `CHECK_OK re-derived byte-for-byte`；"
       "②③`etf_book_phase_admission` / `etf_book_start_grid` 停在 11-24 而闸面板已 11-25（STALE FACE_BEHIND_GATE）"
       "-> 跑 writer 重算（`evidence_cutoff=2026-11-25`，check 6/6 与 rc0），未放宽任何腿")

# round report addendum
rp = "logs/iteration-loop/round_reports-bm-c.md"
text = io.open(rp, "rb").read().decode("utf-8")
if not text.endswith("\n"):
    text += "\n"
text += (f"| {ISO} | r2116-fix | bm-c | 冒烟在本轮跑出的三条红已清：{FIX}；commit **7f6871b681**（代理噪声面重算+收口三面）"
         "与 **9598dba289**（两枚 ETF 面重算）均已直推 origin/main，fetch 后 **0/0**。"
         "全量冒烟仍在跑（`logs/smoke_r2116.log`），其 summary 行与三红在整轮里的复跑留待下一窗。\n")
io.open(rp, "wb").write(text.encode("utf-8"))

# heartbeat
hb_path = "fleet/machines/bm-c.json"
raw = io.open(hb_path, "rb").read().decode("utf-8")
hb = json.loads(raw)
assert json.dumps(hb, ensure_ascii=False, indent=1) == raw.replace("\r\n", "\n").rstrip("\n")
hb["smoke_verdict"] = ("detached run logs/smoke_r2116.log was still going at round end; it surfaced three reds "
                       "(proxy noise off by one bp of level offset; two ETF faces one bar behind the gate panel), "
                       "all three re-derived green this round -- the suite summary and its re-run stay the next-window pointer")
hb["smoke_note"] = hb["smoke_verdict"]
hb["r2116_reds"] = FIX
hb["last_seen"] = ISO
hb["ts"] = ISO
out = json.dumps(hb, ensure_ascii=False, indent=1).replace("\n", "\r\n")
io.open(hb_path, "wb").write(out.encode("utf-8"))
print("OK", ISO)
