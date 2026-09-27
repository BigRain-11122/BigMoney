# r345 bm-b closeout: round-report line + state.json bump + heartbeat
# self-verify (r96 fresh-read-at-write law for all timestamps).
import json
import datetime

now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

line = (
 "2026-09-27T22:2x+08:00 | round 345 bm-b | dept:工程+舰队(5x对账轮) | "
 "WM=绿: red=false@22:00:29 lane healthy; probe 22:13 py 24.4% verdict=insufficient_history(单窗如实) "
 "local_batch_running=W2-A; RAM 1.79GB<4GB 禁重活零新活 | did: "
 "(1) S0 pull--rebase 快进 3919251d..f84502d4 零冲突(bm-c r110 件收); "
 "(2) S0.5 轮首双扫 orders 96/96 python 集合差集零未回执 + 集团决策台账 ../../docs 三路缺位诚实 "
 "no-op(r104/r107 同例) + inbox MSG-2010(bm-b->bm-a 件)非本机留其消费; "
 "(3) S1 smoke 25/25; "
 "(4) S2 双板 0 open(tasks 63 done+30 claimed 他人/job_list 空)+池 80 条(78 done+W2-A ready "
 "本机燃烧中+W2-B waiting); "
 "(5) **r344 指针项落地=autofill abort 腿所有权判别修复**: _claim_shard/_keepalive_claims 盲 "
 "rebase --abort(21:48:48 杀 r344 fold 首跑实弹)改为四面判别(外源 rebase 在飞跳过 pull+abort/"
 "'already a rebase' 拒绝签名否决/干净拒绝不 abort/自家 pull 冲突才 abort)+_mid_op() 单源助手"
 "(入口 r201 守卫复用零行为变化)+selftest S15g 语义更新+新腿 S15g2/g3/g4+S17f/g 全 PASS"
 "(py_compile PASS·hermetic 换元 fake_git 真仓零污染)+MSG-20260927-2222 通报全舰队"
 "(他机下轮 S0 拉取即自愈); "
 "(6) **5x HANDOVER 对账**=_r295bmb_ledger_scan 复跑 HEAD 286,551 实读平持"
 "(INTERNAL_BALANCE_FAIL=0/DUP=0/GAP 19 同谱·本窗零批 finalize)+bm-b round 345 核对行落盘 "
 "HANDOVER.md; "
 "(7) S6 30/30 rc=0 周日 no-op 家族(update_daily 0 新行 cutoff 09-24/regime ORANGE shadow "
 "hs300<MA200/clock ORANGE_COOL sleeves=4/lhb refetch 5209 零新 no-op/heat 周末/futures 覆盖/"
 "8 车道护栏诚实 no-op/fundamental 新鲜跳过/b_layer all_pass/t24_promotion 0/22 诚实/"
 "aggr-alloc-grid 纸盘幂等/astock+rev_osc bm-b 双道幂等/t35_export 再生 6 员 18 持仓 "
 "权益 5,996,645/daily_report faces=4/build_status/token)+live.paper+t35v+t24x2 新 bar 门合法"
 "跳过(下一 bar=周一 09-28 15:30); "
 "(8) W2-A 燃烧健康核查: parent 13148(15:12:51 起)+4 workers 15:40 起 ~14.4GB footprint "
 "no-kill 纪律维持·w2_results.json 未落=finalize 未到窗·W2B flip 双 dep 未满足+RAM 门 "
 "1.79<<12GB 保持 waiting; "
 "(9) 轮首遗留定性: results/_r339bmb_blobs2/=r339 已闭合冲突解 blob 冻结证据件"
 "(解已落地 c28b63c7+resolver 在链)不 add 不删留痕 "
 "| 证据: smoke 25/25+autofill SELFTEST ALL PASS(6 新腿)+_r295bmb_ledger_scan 断面+S6 30x "
 "rc=0+HANDOVER 345 行 "
 "| 下轮: W2-A finalize 收割窗(family 13148 续燃 ETA 滑窗·w2_results.json 落地即 done-flip "
 "池面+T-86 bm-a 票面回执)·W2B flip 只在 dep(2)+RAM>=12GB 双满足·周一 09-28: 09:15 T-91 s3 "
 "auto-fire(SIG/BARS-09-28 重放)+15:30 T-87 astock 首续拉+new-bar 全链(预检 8/8 绿)·r350 5x "
 "HANDOVER·10-01 月首轮三件套+REGIME_GUARD v3 日期门\n"
)
with open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8") as fh:
    fh.write(line)

st = json.load(open(r"logs\iteration-loop\state.json", encoding="utf-8"))
st["round_no"] = 345
st["did"] = ("r345 5x reconcile: autofill abort-ownership fix LANDED (r344 pitlaw tick-side closure: "
             "foreign-rebase skip + already-a-rebase veto + clean-refusal no-abort + ours-only abort, "
             "6 new selftest legs ALL PASS; MSG-2222 fleet notify) + 5x HANDOVER line (ledger 286,551 "
             "flat, GAP 19 same-spectrum, pool 80) + S6 30/30 rc=0 Sunday no-op family + orders 96/96 "
             "dual-scan + smoke 25/25 + W2-A burn healthy no-kill carry")
st["verdict"] = "green"
st["next"] = ("r346: W2-A finalize harvest (w2_results.json lands -> pool done-flip + T-86 bm-a receipt; "
              "no-kill discipline) + W2B flip ONLY when dep(2) W2-A finalize + RAM>=12GB both satisfied "
              "(then FIRST-SIGHT probe once + run per MSG-1912 SOP) + Mon 09-28: 09:15 T-91 s3 auto-fire "
              "+ 15:30 T-87 astock first increment + new-bar full chain (preflight 8/8) + r350 5x "
              "HANDOVER + 10-01 monthly trio + REGIME_GUARD v3 date gate")
st["last_round_ts"] = ts
st["last_result"] = "ok"
st["current_task"] = "r345 closed: autofill abort-ownership fix + 5x HANDOVER reconcile + S6 30/30"
for k in ("updated_at", "last_seen", "ts"):
    st[k] = ts
st.pop("last_task", None)
with open(r"logs\iteration-loop\state.json", "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# heartbeat: fresh-read epoch (JSON int, R170/R178 law) + T-separated
# clock_read (R262 law); orders_ack regenerated from the orders dir
# (enumeration contract, r65/r72/R54 family law).
import os
epoch = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
ack = sorted(f for f in os.listdir(r"fleet\orders")
             if f.startswith("O-") and f.endswith(".md"))
hb_path = r"fleet\machines\bm-b.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["round_no"] = 345
hb["loop_round"] = 345
hb["round"] = 345
hb["current_task"] = ("r345 closed: autofill abort-ownership fix (6 selftest legs) + 5x HANDOVER "
                      "reconcile (ledger 286,551 flat) + S6 30/30 + W2-A burn no-kill carry")
hb["orders_ack"] = ack
hb["n_orders_ack"] = len(ack)
with open(hb_path, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)

# self-verify: epoch int + clock_read T-sep + ack contract
hb2 = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in hb2["clock_read"] and " " not in hb2["clock_read"], "clock_read not T-sep"
dir_acks = set(f for f in os.listdir(r"fleet\orders")
               if f.startswith("O-") and f.endswith(".md"))
assert set(hb2["orders_ack"]) == dir_acks, "ack set != dir set"
print("closeout OK ts=" + ts + " epoch=" + str(epoch) + " acks=" + str(len(hb2["orders_ack"])))
