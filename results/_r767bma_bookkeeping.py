# -*- coding: utf-8 -*-
"""r767 bm-a S5/S7 bookkeeping: round report line + state 767 + heartbeat."""
import io
import json
import time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

REPORT_LINE = (
    f"{ts} | round 767 (bm-a, dept:研究+工程·W153 finalize+W154 freeze 全弧+D-20261005-08 Step1 回执轮) | "
    "[watermark verdict: 绿 (red=false lane healthy; py low-with-work-cands = LEGAL burn face: W154 engine burn in flight)] | "
    "当前活: W154 引擎烧录在飞 (tick verdict ignited:n1w154-2of12 pid=61108·shards_done_total 402 增长面) | "
    "最近实物: results/perpetual_faces/n1_w153_results.json (W153 finalize one-pass 09:07·ledger 732,611·K=334,520·judged 四预测键机证全过) + "
    "W154 冻结四件面 scripts/perpetual_faces.py+n1.py (origin 3095cb47e·A 353_604..355_603 阶梯第十三例 E36/B 355_604..355_803 own-A leg2) + "
    "results/_r767bma_wrapper_step1_audit.json (D-20261005-08 Step1 回执·104 调用位点·0 rc0-stderr 数据消费者·Step2 r723 已在位) | "
    "做了什么: S0 churn-absorb 14f8e4b6e 后 rebase (r758 假拒绝手落 commit+quit+branch -f 治愈·attrition scan 1-UU newer-wins bm-c r608 侧) "
    "+ merge 吸收双 peer 波 (bm-c r608 + bm-b r769/770 closeout wave-2·r759 幻影回退面 merge-mode 治愈)·pre-push 爪 ring-replay 拦=r759 幻影面 (origin 新波 runnable_pool claim-refresh 未吸收) 走正法非 --no-verify; "
    "W153 finalize one-pass (pre 332,320 mu -0.0928/sigma 0.2450 → W153-only 2,200 mu -0.099262/sigma 0.2485 → merged 334,520 mu -0.0928/sigma 0.2451·"
    "K-lift 1.1805→1.1806 +0.0001 @n_eff 730,411·A p95 0.3089 (W152 锚 0.3366 差 -0.0277)·se_mu 0.000424·mu_delta_w153_vs_w152ext -0.004692·"
    "sec5 四预测键机证全过 0.0064<0.02/+1.40%<10pc/-0.0277<0.05/+0.0001<=0.02·canon flip NOT performed) + sec7/sec8 同窗回填 (n1_w153_results 冻结实测键·零改判据·W154+ 投影承接); "
    "W154 冻结全弧: pre-seat probe rc0 ADMIT (leg0 151 行尾 W153/序数 144/bma 70·leg3 origin 空档双查) → 席位 MSG-090x 推 origin dd1702d11 先于冻结 (r565 律·W153 finalize 产品同 commit·behind-3 bm-b wave merge 吸收后送达) → "
    "band gate 全腿 rc0 ADMIT (leg0b 席位在 origin+零外机席·leg1 双窗 derive 逐位恒等·leg2 零冲突+空档·leg3 W155+ 投影 A 355_604..357_603/B 355_804..356_003 hops 0/0 naive-B-inside-naive-A·W154-B-refuses-W155-A 阶梯预期) → "
    "37-needle xform (两形 checklist PASS·sec7/8 占位 W155 承接) + 禁开闸 ADMIT 0 + 冻结四件面 AST PASS (pf N1_BANDS 152 行尾 W154+WAVE_CONFIGS 程序化括号保持包裹+物化腿+PASS 片段) + 双 selftest (pf 9/9+n1 W154 face) + 冻结 commit 3095cb47e 送达 + 引擎 tick 点火 LIVE; "
    "D-20261005-08 wrapper Step1 调用点审计 (104 位点=97 default+3 StdoutOnly+4 IncludeStderr 显式 opt-in 显示尾面·0 未分类 rc0-stderr 数据消费者·18 外部 silent-git 引用=四犯全翻前史+正典 r511-3 在册·Step2 默认翻已 r723 在位·第五犯闸 patrol 10-12 复核·回执窗 10-07 12:00 提前一天落); "
    "S6 链 38/38 rc0 首过 142.6s (金周 no-new-bar 诚实 no-op族·REPORT/LIVE-2026-10-06 再生·scorecard/build_status host=bm-a 执笔); "
    "D-19 双消费 (dec 7674E37B/ord 2E73244B 双 MATCH r766 已消费 00:09 批·水位键 EOL/源变体更正入 state·零新行零动作) + orders 双扫零未回执 | "
    "verify: n1_w153_results.json + _r767bma_w154_probe_receipt.json + _r767bma_w154_band_gate.json + _r767bma_wrapper_step1_audit.json + _r767bma_s6_facts.json (38 legs) + "
    "smoke 48/48 (S1) + attrition CLEAN (4 ledgers·healed 注记照录) + S7 四件套绿 (loop pin8 :28 链在位+watchdog 活+pre-commit/pre-push 双爪 content-match) + 心跳 epoch int 自证 | "
    "下轮指针: r768 = (a) W154 burn watch 12/12 → finalize one-pass + sec7/sec8 同窗回填 + ledger 732,611+2,200=734,811; "
    "(b) W155 冻结窗 (naive A 355_604..357_603 将被本波 B 带 355_604..355_803 拒→阶梯第十四例 re-derive MANDATORY·B naive 355_804..356_003 落 naive-A 窗内→own-A 保留 leg2·E36 卡); "
    "(c) 10-07 12:00 wrapper Step1 回执窗到窗核收取面翻面; (d) 10-07 D-06 收口窗; (e) 10-09 数据链 G3 重启\n"
)

io.open(r"round_reports-bm-a.md", "a", encoding="utf-8", newline="\n").write(
    REPORT_LINE)

# --- state update: round 767 + D-19 watermarks (canonical blob-hash form) ---
sp = r"state-bm-a.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 767
st["last_round"] = "r767"
st["last_round_at"] = ts
st["last_round_ts"] = epoch
st["last_decisions_sha"] = ("7674e37bf0625df0b45725b91d2d4063"
                             "bf2cdd9d349188f878e388cfd17de766")
st["last_decisions_at"] = ts
st["last_decisions_src"] = "git show origin/main:docs/decisions.md (blob bytes sha256)"
st["last_orders_sha"] = ("2e73244b75f295874240839cc7e5dacb"
                         "1dee2c48603d02535f89e1275c562241")
st["last_orders_at"] = ts
st["current_task"] = "W154 engine burn in flight (n1w154); r768 finalize next"
st["last_action"] = "W153 finalize one-pass + W154 freeze full arc + wrapper Step1 receipt"
st["next"] = "r768: W154 finalize + W155 freeze window"
st["updated"] = ts
st["ts"] = ts
st["notes"] = ("r767: W153 finalize 732,611/K334,520 judged one-pass; W154 freeze "
               "3095cb47e (A 353_604..355_603 stairs 13th E36 + B 355_604..355_803 "
               "own-A leg2) ignited; D-20261005-08 Step1 receipt 104 sites zero "
               "rc0-stderr consumers; S6 38/38 rc0; watermarks EOL-variant "
               "corrected to canonical blob hashes (dec 7674E37B/ord 2E73244B)")
io.open(sp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1))
chk = json.load(io.open(sp, encoding="utf-8"))
assert chk["round_no"] == 767
print("state 767 written; round_no =", chk["round_no"])

# --- heartbeat: fleet/machines/bm-a.json ---
hp = r"fleet\machines\bm-a.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = ts
hb["current_task"] = "W154 engine burn in flight (n1w154); r768 finalize next"
hb["verdict"] = "loaded_ok (W154 engine burn active; S6 38/38 rc0; board clear)"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
try:
    import psutil
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    cpu = psutil.cpu_percent(interval=0.3)
    hb["idle_ram_gb"] = ram_free
    hb["cpu_pct"] = cpu
except Exception:
    pass
io.open(hp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1))
chk2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk2.get("heartbeat_epoch_utc"), int), "epoch must be int"
assert "T" in chk2.get("clock_read", ""), "clock_read must be T-separated"
print("heartbeat written; epoch int =", chk2["heartbeat_epoch_utc"],
      "| clock =", chk2["clock_read"])
