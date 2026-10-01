"""r339 bm-c post-finalize amend: round report line + state fields reflect the
same-round W32 one-pass close (宣称-实况一致律)."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- round report line amend -------------------------------------------------
rr = os.path.join(ROOT, "round_reports-bm-c.md")
txt = open(rr, encoding="utf-8", newline="").read()
old1 = "当前活=W32 finalize 待办（12/12 烧毕·appender 批推余 3 件）+T-131 基本面回填续拉（452→5229）"
new1 = "当前活=W32 同轮 finalize 已收口（一趟过全闭环：冻结→烧录→finalize→回填）+T-131 基本面回填续拉（452→5229）"
assert old1 in txt, "amend anchor 1 missing"
txt = txt.replace(old1, new1)
old2 = "engine appender 已推 6 件〔beb943c68 push_rc=0〕append_pending=3）｜"
new2 = ("engine appender 已推 6 件〔beb943c68 push_rc=0〕append_pending=3）"
        "＋**同轮 finalize 一趟过**（r310 完备性门 ls-tree 12/12 origin 在场〔首验 PS 单串捕获面误报 1/12 "
        "raw 直读核正〕·K=68,320==§0 投影·账本 prev=432,748 活头 derive+2,200=434,948 链线性·"
        "voids_applied=[LOWAMP-P1]·S5 4/4 PASS〔W32-only mu −0.10037 漂移 0.0088<0.02/sigma +0.06%/"
        "A p95 0.3021 Δ−0.0053/K-lift +0.0005 正向如实报〕·se_mu 收窄 0.000951→0.000936·"
        "§7/§8 同窗回填·r538 首跑未重跑）｜")
assert old2 in txt, "amend anchor 2 missing"
txt = txt.replace(old2, new2)
old3 = "下个里程碑=W32 finalize（K=68,320 预期·下轮窗≤1h）+T-131 回填完成（≈17h）+10-31 月界首考"
new3 = "下个里程碑=T-131 回填完成（≈17h）+W33 bm-a 槽位观察（W33+ 投影双净空）+10-31 月界首考"
assert old3 in txt, "amend anchor 3 missing"
txt = txt.replace(old3, new3)
with open(rr, "wb") as f:
    f.write(txt.encode("utf-8"))
print("round report amended (3 anchors)")

# --- state amend --------------------------------------------------------------
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["current_task"] = ("W32 CLOSED one-pass (K=68,320, ledger 434,948, S5 4/4, "
                      "backfilled); T-131 backfill in flight (~17h ETA); T-134 "
                      "s2 pick9 pending; W33=bm-a slot observation")
st["next"] = ("(r340)(a) T-131 backfill monitoring (three-face + quarantine; "
              "status-file write cadence observation noted); (b) T-134 s2 "
              "ninth-item evidence-order rescan (r304 law, remaining 30 "
              "single_core); (c) W33=bm-a slot observation (W33+ projection "
              "A 109_004..111_003 / B 41_601..41_800 both CLEAN per r339 gate "
              "receipt); (d) month-boundary first exam 10-31")
st["verify"] = ("r339: W32 ONE-PASS FULL CLOSE (21st engine wave, bm-c 7th owned; "
                "freeze+12/12 burn+finalize+backfill same round): banned-gate "
                "ADMIT + band-gate ADMIT (A 107_004..109_003 + B 41_401..41_600 "
                "arithmetic no-skip, 29-row scan) + n1 selftest W32 face + engine "
                "selftest 36/36 + r310 completeness 12/12 on origin (e387ddff0) + "
                "K=68,320 == projection + ledger 432,748+2,200=434,948 linear + "
                "S5 4/4 PASS (K-lift +0.0005 positive honest) + se_mu 0.000936 + "
                "§7/§8 backfilled one-pass (r538 no-rerun) + T-131 monitoring "
                "healthy (452/5229, face files 2381->2803 growing, pid 33316) + "
                "S6 37 legs rc0 (dualrun streak 25/3, audit CLEAN) + smoke 47/47 "
                "+ D-19 MATCH (753f99e8)")
st["did"] = ("r339 W32 one-pass full close (freeze -> 12/12 engine burn -> "
             "finalize K=68,320 -> backfill, fastest wave close) + S6 chain + "
             "bookkeeping")
raw = open(sp, "rb").read()
eol = "\r\n" if b"\r\n" in raw[:4000] else "\n"
s = json.dumps(st, ensure_ascii=False, indent=2)
if eol == "\r\n":
    s = s.replace("\n", "\r\n")
with open(sp, "wb") as f:
    f.write(s.encode("utf-8"))
print("state amended")
print("AMEND DONE")
