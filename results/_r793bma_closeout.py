# -*- coding: utf-8 -*-
"""r793 bm-a round closeout: S5 round-report line + state round_no 791->793
(takeover window: r792 dead session already signed the pre-seat push, so this
window claims r793; state skipped the dead session's increment) + decisions
watermark consumption + heartbeat (epoch int + T-separated clock_read, R170/R178/
R262 laws). Fresh-read-modify-write per multi-writer file law (no replace tool)."""
import datetime
import json
import time

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+08:00" if now.utcoffset().total_seconds() == 8 * 3600 else now.strftime("%z"))
epoch = int(time.time())

# --- S5: round report line (append) ---
RR = r"logs/iteration-loop/round_reports-bm-a.md"
line = (
    f"{iso} | r793 bm-a (dept:工程+研究·S5 接管死会话 r792 半成品收口+常设线 W165 推进) | "
    "watermark verdict: 绿 (red=false lane=healthy; probe py 0.4% 低位=golden-week 合法 idle 白名单面: 板闭环 0 open 票+引擎 idle+W164 判决本窗收口) | "
    "当前活: W165 freeze 接力准备 (seat MSG-2026-10-06-205x 已发布 origin 4bdf63090+band gate ADMIT rc0 五腿; face probe→freeze edits→12 shards→finalize 归 r794 接力, r381 stall-drain 合法接力点) | "
    "最近实物: results/perpetual_faces/n1_w164_results.json 20:20 (ledger 764,012→766,212·pool K 356,520→358,720·skill_line_v2 1.1832→1.1833·voids LOWAMP-P1/P2) + fleet/inbox/MSG-2026-10-06-205x-bma-w165-seat.md 20:5x | "
    "下个里程碑: W165 finalize (r794 窗点火·K 358,720→360,920 预期·shards 12 分钟) | "
    "W164 finalize ONE-PASS (12/12 shards merged·r776 leg3 ledger_head PASS) + freeze verify rc0 9 legs (r781 双件血统) + pf selftest 9/9 + smoke 48/48 + S6 38/38 rc0 (98th) + "
    "rebase 2-UU post_review resolver (jsonl multiset union 6,837 行零丢失·计数断言形态修正=r482 族·REPORT 同日再生 take-origin r327/r329·r758 态机粘滞手落 pick 树) + "
    "集团决策面零涉本司新动作 (OSS 件 OH-20261005-bigmoney 在册核销 D-20261006-03·decisions 水位 8fdf1f57→5e13b9bd SHA-256 消费·orders CEO 物理件区零新行) + "
    "本地未达 origin commit 数=0 (push 后 fetch+ls-tree 双自证)\n"
)
with open(RR, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("S5: round report line appended")

# --- state: round_no + next + decisions watermark ---
ST = r"state-bm-a.json"
st = json.load(open(ST, encoding="utf-8"))
assert st["round_no"] == 791, f"unexpected round_no {st['round_no']}"
st["round_no"] = 793
st["last_round"] = 793
st["last_round_at"] = iso
st["last_round_ts"] = iso
st["last_decisions_sha"] = "5e13b9bd5bc7068213adccd0dba3ebd8e47c474ad9262dd544c12e85f3c9c91c"
st["last_decisions_at"] = iso
st["last_decisions_src"] = "group-tree origin blob (C:\\Users\\sjs20\\Desktop\\FluxGroup git show origin/main:docs/decisions.md, r786 law)"
st["next"] = "W165 freeze takeover: face probe (_r793bma_w165_face_probe.py from r792 bloodline) -> freeze edits (TOK/BACK value-map step r792->W165) -> prereg build -> freeze verify -> 12 shards burn -> finalize --wave 165"
st["last_action"] = "r793: W164 finalize takeover closeout + W165 pre-seat/gate published"
st["updated"] = iso
json.dump(st, open(ST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state: round_no 791->793, decisions watermark consumed, next pointer set")

# --- heartbeat ---
HB = r"fleet/machines/bm-a.json"
hb = json.load(open(HB, encoding="utf-8"))
hb["last_seen"] = iso
hb["ts"] = iso
hb["clock_read"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = hb.get("heartbeat_epoch_utc", epoch)
hb["current_task"] = "W165 freeze takeover ready (r794): face probe -> freeze edits -> shards -> finalize"
hb["verdict"] = "healthy: W164 finalized, W165 seated+gated, S6 38/38, smoke 48/48"
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262 law)"
print("heartbeat: written, epoch int + T-clock self-verified")
print("r793 closeout rc0")
