# -*- coding: utf-8 -*-
"""r595 bm-a S7 close: round-report line replace, state, heartbeat, CODELY pit entry, inbox archive.
Laws: r583 (carry lists, update dynamic fields only), r530 (bytes in/out), r170/R178 (epoch int),
R262 (clock_read T-separated)."""
import json, os, shutil, time
from datetime import datetime

now = datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")          # 2026-10-02T22:xx:xx+08:00
stamp = now.strftime("%Y-%m-%d %H:%M")

# ---------- 1. round_reports-bm-a.md: replace the dead-session r595 line ----------
rp = "round_reports-bm-a.md"
raw = open(rp, "rb").read()
lines = raw.replace(b"\r\n", b"\n").split(b"\n")
idx = [i for i, l in enumerate(lines) if l.startswith(b"2026-10-02 21:5x | r595 |")]
assert len(idx) == 1, f"expected exactly 1 r595 line, got {len(idx)}"
newline = (
    f"{stamp} | r595 | watermark verdict=绿（red=false·引擎活 idle queue0=W115 bm-c 停靠合法态·py 低位=假期窗板空池静=合法 idle·22:06 probe rc0）；"
    f"当前活=猝死 r595 会话收养收口+双 FF 集成（5d234b3d→f7972fdb6→232ff349e·86 面分面 checkout·CODELY 零丢失 union 复活 bm-b r595 尾部吞掉的 r594 收养坑律条目+T-145 票 4 键 union）；"
    f"最近实物=scripts/fund_h_unlock_eval.py+results/fund_h_unlock_eval.json（T-145 leg(b)·H 行 7/8 解锁：4 直接+3 proxy·gross_profitability 续锁=利润表面缺位）+research/FACTOR_CENSUS_REGISTRY.md H-8 翻面（216→216 零丢失）+O-20261002-2124 回执节（A腿：FluxVerse c02dc3e·Humanoid→Human 编译修复+R1 fail-loud 32/20 停火·裁决指针呈 bm-c）；"
    f"O-2135 ack（T-146 YTD=GM 会话在执·bm-c r385 反双头公示·本机不认领禁重复开发）+W115 停靠 MSG 消费归档；"
    f"验证=smoke 47/47·S6 38 腿 rc0（dualrun ZERO-DRIFT 51/3·host 面 scorecard/dscore/dreport/liveusage/build 再生·假期数据腿全 no-op 合法）·attrition CLEAN 4 ledger·S7 自愈 4/4（loop pin :8 no-op+watchdog 重注册+双爪字节装）·D-19 MATCH 937A373D 零动作·orders 双扫差集=0（O-2135 本轮 ack）；"
    f"下轮指针=T-145 leg(c) 首批基本面族 prereg（value PE/PB+quality ROE/GP-proxy+dividend-lowvol·法定日锚定门继承+出场轴显式门 M02·10-09 窗验收 10-08）s1=数据就绪探针+value 族起草；bm-c 裁决 City3D 20/32 后 A腿一条命令重跑；本地未达 origin commit 数=0（push 后自证）"
).encode("utf-8")
lines[idx[0]] = newline
open(rp, "wb").write(b"\n".join(lines).replace(b"\n", b"\r\n"))
print("round report line replaced at", idx[0])

# ---------- 2. CODELY.md: append this round's pit law entry ----------
pit = (
    f"\n\n- [{stamp.replace(' ',' ')[:16]} r595 bm-a] CODELY.md 跨机尾部 append 互吞坑（双 FF union 实弹·零丢失治愈）：bm-b r595 的 CODELY append 以「替换尾部条目」而非「追加」落地——其工作树尾部缺 bm-a r594 收养坑律条目（分面 checkout 取了旧尾），append 后该条目从 origin 消失整一轮（本窗 S0 union 行集探针当场抓回：本地独有非空行=被吞条目·insert 回锚位）。诊断签名=origin 尾部时间序断档（r593 bm-a→r595 bm-b 缺 r594 bm-a）。修法=S0 集成对 CODELY 恒做行集双向差集探针（仅 origin-verbatim 收口=会固化他机吞条；仅保本地=丢他机新条）——正典=origin verbatim 底+复活 dropped 行插回时间锚位+本地独有行追加尾。How to apply：一切多机共享 append-only 记忆/法典件在 FF/收口后必跑行集探针勿信「origin 即正典」；他机条目在场性以本机已知集核对。"
).encode("utf-8")
with open("CODELY.md", "ab") as f:
    f.write(pit.replace(b"\n", b"\r\n"))
print("CODELY pit entry appended", len(pit), "bytes; file size:", os.path.getsize("CODELY.md"))

# ---------- 3. heartbeat fleet/machines/bm-a.json (dynamic fields only, r583) ----------
hb_path = "fleet/machines/bm-a.json"
hb = json.load(open(hb_path, encoding="utf-8"))
ack = hb.setdefault("orders_ack", [])
new_order = "O-20261002-2135-bm-c.md"
if new_order not in ack:
    ack.append(new_order)
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = int(time.time())  # JSON int (R170/R178)
hb["clock_read"] = ts                          # T-separated (R262)
hb["current_task"] = "r595 bm-a: dead-session estate landed (O-2124 A-leg + T-145 leg(b) H-row unlock) + double FF integration; next = T-145 leg(c) first fundamental family preregs"
hb["verdict"] = "healthy: engine alive idle (W115 parked by bm-c per O-2115 supply-priority), S6 38 legs rc0, smoke 47/47"
json.dump(hb, open(hb_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
h2 = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int)
assert "T" in h2["clock_read"]
print("heartbeat updated: ack", len(ack), "epoch int ok")

# ---------- 4. state-bm-a.json ----------
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 596
st["last_round"] = "r595"
st["last_round_at"] = ts
st["last_round_ts"] = ts
st["updated"] = ts
st["did"] = ("r595: dead-session estate adopted+landed (O-2124 City3D A-leg receipt: FluxVerse c02dc3e Humanoid->Human compile fix + R1 fail-loud 32/20 stop-fire, ruling pointer to bm-c; "
             "T-145 leg(b): scripts/fund_h_unlock_eval.py + results/fund_h_unlock_eval.json H-row 7/8 unlock (4 direct hml=1/pb, ep=1/pe_ttm, roe=roe_q, smb=ln(mv) + 3 proxy cma/asset_growth/rmw; "
             "1 stay-locked gross_profitability=income-statement face absent) + FACTOR_CENSUS_REGISTRY H-8 flip 216->216 zero loss) "
             "+ S0 double pure-FF (5d234b3d->f7972fdb6->232ff349e, 86 faces curated, CODELY zero-loss union resurrecting the bm-b-r595-tail-swallowed r594 entry, T-145 ticket 4-key union) "
             "+ O-2135 acked (T-146 YTD = GM executing, anti-double-head, no claim) + W115-park MSG consumed+archived + new pit law: CODELY cross-machine tail-append swallow (line-set probe law)")
st["verify"] = ("smoke 47/47; S6 38 legs rc0 (dualrun ZERO-DRIFT 51/3; host faces regenerated; Golden-Week data legs idempotent no-op); attrition guard CLEAN 4 ledgers; "
                "engine alive rc0 idle queue0 (W115 parked state); S7 self-heal 4/4 (loop pin :8 no-op, watchdog re-registered, both claws installed byte-match); "
                "D-19 MATCH 937A373D zero action; orders double-scan diff=0 (147 acked incl O-2135 this round)")
st["next"] = ("T-145 leg(c) FIRST FUNDAMENTAL FAMILY PREREGS (value PE/PB, quality ROE/GP-proxy, dividend-lowvol TTM-yield+lowvol; statutory-date anchoring gate inherited from leg(a) PIT audit; "
              "exit-axis explicit dual gate M02; due 10-09 window, acceptance 10-08); s1 next round = data-readiness probe + value-family prereg draft; "
              "City3D A-leg one-command re-run after bm-c ruling (roster 20 vs 32); W116+ seat taking frozen while N1 parked (bm-c seat retained)")
st["current_task"] = "r595 bm-a: estate landed + integrated at 232ff349e; next round opens T-145 leg(c) s1 (data probe + value-family prereg)"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state updated: round_no", st["round_no"])

# ---------- 5. inbox: MSG-2200 -> processed ----------
src = "fleet/inbox/MSG-2026-10-02-2200-bmc-ALL-w115-park.md"
dst = "fleet/inbox/processed/MSG-2026-10-02-2200-bmc-ALL-w115-park.md"
if os.path.exists(src):
    shutil.move(src, dst)
    print("MSG-2200 archived to processed/")
else:
    print("MSG-2200 already moved")
print("S7-BOOK-OK", ts)
