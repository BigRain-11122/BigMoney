# -*- coding: utf-8 -*-
"""r312 bm-b wrap: state.json 312 + heartbeat (orders_ack FORMAT FIX:
whole-filename list rewrite per r312 kenglu -- the ack field had been
char-shattered for many rounds) + round report line. Clock faces use
datetime.now().astimezone().isoformat() (r302 law); epoch is a JSON int
(R170/R178 law); self-check asserts run BEFORE the caller commits."""
import glob
import json
import os
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now().astimezone()
NOW_ISO = NOW.isoformat()
EPOCH = int(time.time())


def state_312():
    p = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
    s = json.load(open(p, encoding="utf-8-sig"))
    s.update({
        "round_no": 312,
        "did": ("r312: S0 main 3v3 reconcile (bm-a r305 trio vs bm-b r311 "
                "trio, 27 UU resolved per bigmoney-conflict-resolve canon "
                "deep-ts probe F-20260927-01 local patch, zero loss, "
                "eb99d7c7..393c2042 pushed) + T-90 runner DELIVERED+GATED "
                "(scripts/decision_chain_e2e.py import-face t22/t34 reuse; "
                "selftest 23/23; G-REPRO 12/12 bit-equal real-fire 48.9s; "
                "x2 probe 36/36 + direction gate 36/36) + prereg zero-run "
                "amendments s9.2 (seed 20260929->20261001 collision "
                "t11_negday_ic, order law) + s9.3 (G-V3 leg-2 false premise "
                "v1-live vs v3-calibration, freshness+alphabet amendment) + "
                "x2 stage-A 9 shards POOLED (DECISION-CHAIN-E2E-X2-*) + S6 "
                "22 lanes rc=0 + CODELY 3 kenglu + hot/cold repack 6th "
                "batch 10231B<=10KB"),
        "verdict": "green",
        "next": ("T-90 harvest: autofill burns 9 x2 shards (~16.5k cells "
                 "est 60-90min aggregate) -> bm-b finalize round (needs "
                 "bm-local t34 base curves): finalize -> J-C/J-L/J-TARGET "
                 "verdict + four-ring localization + prereg s7/s8 backfill "
                 "+ LEDGER/decisions_chain ledger row; T-89 slice-1b runner "
                 "prospect_regime_segments.py -> pool next; v1-live vs v3 "
                 "divergence (ORANGE vs YELLOW @09-24) = GM face item "
                 "defense-line amendment input; 09-28 Monday first-new-bar "
                 "full chain; 10-01 monthly trio + REGIME_GUARD v3 date "
                 "gate; migration window to 09-29 12:00 editor-gated"),
        "last_round_ts": NOW_ISO,
        "last_result": "ok",
        "current_task": ("r312: T-90 runner built+gated+pooled (CEO "
                         "O-0758 most-important-asset lane); x2 stage-A "
                         "burn in autofill pool"),
        "updated_at": NOW_ISO,
    })
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)
    assert json.load(open(p, encoding="utf-8-sig"))["round_no"] == 312


def heartbeat():
    p = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
    h = json.load(open(p, encoding="utf-8-sig"))
    orders = sorted(os.path.basename(x) for x in
                    glob.glob(os.path.join(ROOT, "fleet", "orders",
                                           "O-*.md")))
    ack = orders                      # FORMAT FIX: whole filenames list
    h.update({
        "orders_ack": ack,
        "last_seen": NOW_ISO,
        "current_task": ("r312: T-90 runner built+gated+pooled; x2 "
                         "stage-A 9 shards burning via autofill"),
        "cpu_cores": os.cpu_count(),
        "heartbeat_epoch_utc": EPOCH,
        "clock_read": NOW_ISO,
        "verdict": ("green; r312: S0 main 3v3 reconcile zero-loss + T-90 "
                    "runner delivered+gated (G-REPRO 12/12 bit-equal, x2 "
                    "probe 36/36, selftest 23/23) + prereg zero-run "
                    "amendments s9.2 seed / s9.3 G-V3-leg2 (v1-live vs "
                    "v3-calibration false-premise, disclosed to GM) + 9 "
                    "x2 shards pooled ready + S6 22 lanes rc=0 + "
                    "orders_ack format FIXED (char-shatter legacy, whole-"
                    "filename list rewrite) + smoke 25/25 + orders 94/94 "
                    "double-scan zero new"),
    })
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(h, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)
    # ---- self-check asserts (smoke F7 faces, pre-commit)
    chk = json.load(open(p, encoding="utf-8-sig"))
    assert isinstance(chk["heartbeat_epoch_utc"], int) and \
        not isinstance(chk["heartbeat_epoch_utc"], bool), "epoch not JSON int"
    assert "T" in chk["clock_read"] and ("+08:00" in chk["clock_read"]
                                          or chk["clock_read"].endswith(
                                              "Z")), "clock not ISO+offset"
    ack_now = chk["orders_ack"]
    assert all(isinstance(x, str) and x.endswith(".md") and len(x) > 8
               for x in ack_now), "orders_ack not whole-filename tokens"
    assert set(orders) <= set(ack_now) and len(set(ack_now) & set(orders)) \
        == len(orders), "orders_ack set-diff self-check failed"
    print(f"heartbeat: epoch={EPOCH} int OK; clock={NOW_ISO} OK; "
          f"orders_ack {len(ack_now)} whole-filename tokens OK")


def round_report():
    p = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
    line = (
        f"{NOW_ISO} | r312 bm-b | dept:研究+策略+舰队 | WM-VERDICT: 绿 "
        f"red=false（probe 08:59:15 insufficient_history n=1 新窗重累合法·"
        f"池 ready 10=饥饿解除·9 分片待 tick 认领） | did: S0 main 3v3 "
        f"重聚（bm-a r305 三连 vs bm-b r311 三连 27 UU 正典解：deep-ts "
        f"探针本地补 F-20260927-01+账本 union 203/2/600+twin 跟随+MM 增量 "
        f"r306 律四步，零丢失，eb99d7c7..393c2042 推上=上轮 addendum 欠账 "
        f"清偿）+S0.5 94 令零新增·decisions.md 本机缺位诚实 no-op（r104/"
        f"r107 先例）+心跳 orders_ack 字符碎裂古疾实证（2257 字符≈94×24）"
        f"→整体重写修复+写前 set-diff 自证入律 | S3 T-90 主交付闭环："
        f"runner scripts/decision_chain_e2e.py（import-face 零重写复用 "
        f"t22/t34 原语）selftest 23/23 hermetic+G-REPRO 12/12 位级实弹 "
        f"48.9s+x2 探针 36/36 格 10.3s+方向门 36/36 x2<base（r82 反转面 "
        f"陷阱缺席）+零跑修正案两件 s9.2（seed 20260929 撞 t11_negday_ic "
        f"→顺序律裁决 20261001 净位注册）s9.3（G-V3 leg-2 等值断言=虚假"
        f"前提：regime_state=v1 在役矩阵按律 O-2315 vs v3_state_series=v3 "
        f"校准层，探针实证 ORANGE vs YELLOW→改新鲜度+字母表+分歧披露，"
        f"判据零触碰）+x2 Stage-A 9 分片入池（r301 shards+r305 "
        f"workers_plan 双契约+T54 分片文件范式+~16.5k 格 autofill 续烧）"
        f"+T-90 票 progress_r312_bmb | S6 22 道 rc=0 周日诚实 no-op 面 "
        f"（audit CLEAN·池供给面 ready 10）| S4 CODELY 3 坑律入件+热冷整编"
        f"六批（r301/r299 迁档零丢失·10231B≤10KB 硬线） | 验证证据="
        f"results/_r312bmb_resolve.py 撞车解+logs run_x2_legacy_lA.log "
        f"36/36+G-REPRO 控制台 12/12+runnable_pool 9 分片 ready+"
        f"smoke 25/25 | 下轮指针=autofill 烧 9 分片→bm-b finalize 收割"
        f"轮（J-C/J-L/J-TARGET+断环四环+§7/§8 回填+16,566 格账本）·T-89 "
        f"slice-1b runner 次轮·v1/v3 分歧呈 GM 面待防线修法窗")
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n" + line + "\n")
    print(f"round report r312 line appended ({len(line)} chars)")


if __name__ == "__main__":
    state_312()
    heartbeat()
    round_report()
    print("r312 wrap DONE")
