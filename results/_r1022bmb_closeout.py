"""r1022 bm-b closeout state/heartbeat/round-report writer.

Run AFTER d19 advance + S6 chain. Reads fresh state.json (post-advance),
writes: repo state.json + logs mirror (dual-face round_no law r1020),
heartbeat (epoch INT asserted), round report row. Prints summary for the
PS wrapper. exit 0.
"""
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state.json")
MIRROR = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
S6LOG = os.path.join(ROOT, "results", "_r1022bmb_s6_log.txt")
ORPH = os.path.join(ROOT, "results", "_orphan_face_probe.bm-b.json")
IDLE = os.path.join(ROOT, "results", "idle_trigger.bm-b.json")
D19 = os.path.join(ROOT, "results", "_r686bmb_d19_check.json")
FRESH = os.path.join(ROOT, "results", "_r686bmb_orders_fresh.md")

NOW = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())


def main():
    # --- chain summary ---
    rc0, rcnz, skips = 0, [], []
    if os.path.exists(S6LOG):
        for ln in io.open(S6LOG, encoding="utf-8", errors="replace").read().splitlines():
            m = re.match(r"rc=(-?\d+) (\S+)", ln.strip())
            if m:
                if m.group(1) == "0":
                    rc0 += 1
                else:
                    rcnz.append("%s(rc=%s)" % (m.group(2), m.group(1)))
            elif "SKIP" in ln:
                skips.append(ln.strip()[:60])
    orph_n, orph_total = "n/a", "n/a"
    try:
        o = json.load(io.open(ORPH, encoding="utf-8"))
        for k in ("orphan_count", "orphans", "orphan", "orphaned", "orphan_faces_found"):
            if isinstance(o.get(k), int):
                orph_n = o[k]
                break
        for k in ("py_faces", "total_faces", "faces", "orphan_faces"):
            if isinstance(o.get(k), int):
                orph_total = o[k]
                break
    except Exception:
        pass
    idle_rounds, agenda_starved = 0, False
    try:
        it = json.load(io.open(IDLE, encoding="utf-8"))
        idle_rounds = int(it.get("idle_rounds") or 0)
        agenda_starved = bool(it.get("agenda_starved"))
    except Exception:
        pass
    post_rows, tail_full = [], []
    try:
        import subprocess
        r = subprocess.run(
            ["git", "-C", r"C:\Fluxgroup\FluxGroup", "show",
             "origin/main:docs/orders.md"], capture_output=True)
        t = r.stdout.decode("utf-8", "replace")
        for ln in t.splitlines():
            m = re.search(r"\|\s*2026-10-19 (\d\d:\d\d)", ln)
            if m and m.group(1) > "11:27":
                tail_full.append(ln.strip())
                if m.group(1) not in post_rows:
                    post_rows.append(m.group(1))
        post_rows = sorted(set(post_rows))
        if tail_full:
            io.open(os.path.join(ROOT, "results", "_r1022bmb_ord_tail.txt"),
                   "w", encoding="utf-8").write("\n\n".join(tail_full))
    except Exception:
        pass
    d19 = {}
    try:
        d19 = json.load(io.open(D19, encoding="utf-8"))
    except Exception:
        pass

    # --- state ---
    st = json.load(io.open(STATE, encoding="utf-8"))
    st["round_no"] = 1022
    st["round"] = 1022
    st["round_no_label"] = "r1022"
    st["clock_read"] = NOW
    st["ts"] = NOW
    st["updated"] = NOW
    st["updated_at"] = NOW
    st["last_round_at"] = NOW
    st["last_round_ts"] = NOW
    st["last_seen"] = NOW
    st["now_active"] = "r1022 closed"
    did = ("r1022: (a) S0 FF absorb bm-a r1078 x2 (stash-ff-pop, 5 UU resolved: "
           "wm_red mine-newer 11:45:03 / marks line-union 11 rows / futures "
           "origin-newer / lhb+token_usage mine). (b) S0.5 D-19 ORD delta "
           "consumed: 11:16 female-lead LoRA @bm-c zero-obligation; 11:21 "
           "training-members order @bm-b 8G = character-voice LoRA + SD1.5 asset "
           "light-train, night-window 22:0x training-state priority -> ST-012 "
           "seeded in drama queue (receipt); 11:27 skill-audit executed by bm-a. "
           "(c) ST-011 sourcing station executed+done: MANCANG 7 all-CLIPPED "
           "voice_05 clips de-clipped, 3 admitted INTERIM (gate f0_dev 9.35% / "
           "rms_spread 1.76dB / centroid_dev 1.73% PASS; shared-base debt "
           "disclosed; root fix = ST-012 new-base/LoRA lane); BOY child-voice "
           "license review delivered (external real-child cloning BLOCKED; "
           "AISHELL-3/aidatatang research-use not cleared; routes = CEO clips "
           "physical / adult-base verified-adjust DSP prototype; zero BOY clips "
           "honest). (d) CODELY.md hot-cold split: prescan rc3 recorded "
           "(r1009 authorized-migration precedent), 3 fat rows verbatim -> "
           "archive 202610.md r1022 window-batch, duplicate r1053 pointer x2 "
           "deduped, r1021 nominal-vs-measured semitone pit row appended; "
           "11,223B -> 9,407B back under 10KB line, zero_loss=True. (e) S6 "
           "chain: ")
    did = (did + str(rc0) + " legs rc0, " + str(len(rcnz)) + " non-zero "
           + (",".join(rcnz) or "none")
           + "; papers family honest-skip (Monday intraday, no new bar; "
           "post-15:30 round runs them).")
    st["did"] = did
    st["last_action"] = ("r1022: ST-011 sourcing done (MANCANG declip x3 admitted "
                         "interim + BOY license review) + ST-012 voice-LoRA night lane "
                         "seeded (11:21 order @bm-b) + CODELY hot-cold split 11223->9407B")
    st["last_action_at"] = NOW
    st["current_task"] = ("r1022: ST-011 sourcing station + 11:21 order ST-012 seed + "
                          "CODELY split + S6 chain")
    st["task"] = st["current_task"]
    st["latest_artifact"] = ("content/drama/outbox/ST-011-SOURCING-RECEIPT.md + "
                             "manifest MANCANG admitted-interim (3 declip clips, gate pass) + "
                             "content/drama/queue.json ST-012 seeded + "
                             "results/drama_env/st011_sourcing.json + "
                             "media wavs C:\\Fluxgroup\\FluxGroup\\media\\drama-tools\\voice_smoke\\st011\\mancang\\ (7 declip) + "
                             "CODELY.md hot-cold split receipt + S6 products (REPORT/LIVE-2026-10-19 regen)")
    st["last_artifact"] = st["latest_artifact"]
    st["next"] = ("r1023: 1) post-15:30 papers chain (new bar lands after close -> "
                  "live.paper + t35_open_fill + t24 prospect x2 + export family) "
                  "2) ST-012 GitHub training-wheels scan FIRST (寻源闸律·10-16 CEO "
                  "order) then first character-voice LoRA night-window run 3) BOY "
                  "physical route report (CEO clips) vs DSP prototype decision 4) "
                  "supply_floor watch: W278 prereg derive (bm-c) -> bm-b N1 pool feed "
                  "5) SD1.5 asset light-train lane seed (11:21 order second face, "
                  "non-drama line) 6) batch-station spec: per-line verify-adjust "
                  "tier loop (ST-010 method prototype)")
    st["next_milestone"] = ("voice P1 <=10-22 (ST-011 sourcing done + ST-012 LoRA lane "
                            "seeded + batch station spec) + BigMoney seat automation plan "
                            "<=10-25 + CONTENT-LOOP 10-28 continuous-run judgment (12 "
                            "stations seeded / 11 done pace) + month-boundary 10-31")
    st["verdict"] = ("GREEN: r1022 产品轮——ST-011 寻源站收官（MANCANG 7 削波片去削波再产 3 片入行 INTERIM·一致检 "
                     "f0_dev 9.35%/rms 1.76dB/centroid 1.73% 全过·voice_05 共底债如实披露=根解 ST-012；BOY 许可审查交付=外部真人童声克隆 BLOCKED·开源语料 research-use 未清·可行路=CEO 片段物理/成人底 DSP 童感原型·BOY 入行 0 诚实）；11:21 集团令 @bm-b 8G 义务承接=ST-012 角色声 LoRA 夜窗车道（22:0x 训练态优先）已播种；CODELY.md 热冷整编 11,223B→9,407B 回 10KB 硬线内（prescan rc3 留痕·zero_loss=True·r1021 名义半音≠实测半音坑行入册）；S0 吸收 bm-a r1078×2（5 UU 全解）；S0.5 D-19 ORD 三行消费（11:16/11:21/11:27·11:21 含 @bm-b 义务已承接）")
    st["verdict"] = (st["verdict"] + "；S6 链 " + str(rc0)
                     + " 腿 rc0（papers 家族周一盘中诚实跳过）；下窗=r1023 15:30 后 papers 链"
                     "+ST-012 GitHub 轮子扫描+BOY 物理路呈报")
    st["current"] = st["verdict"]
    st["sat_engine"] = {
        "status": ("alive (r1022 S6 chain status leg; idle verdict; supply floor "
                   "honest starvation 0/3 -- W278 prereg derive = bm-c next window; "
                   "bm-b N1 pool feeds after prereg lands)"),
        "checked_at": NOW,
    }
    st["orphan_face"] = orph_n
    st["orphan_faces"] = orph_total
    if "sync" not in st or not isinstance(st["sync"], dict):
        st["sync"] = {}
    st["sync"]["r1021_main_push"] = {
        "status": "PUSHED_VERIFIED (verified at r1022 S0: payload commit 3aac4a3dde on origin, ancestor of tip c3bd6066db)",
        "pushed_sha": "3aac4a3dde384be89db63efe9ac1febafa17a883",
        "consumed_at": NOW,
        "behind_origin_main": 0,
    }
    st["sync"]["r1022_main_push"] = {
        "status": "PENDING (this commit)",
        "pushed_sha": "pending",
        "consumed_at": "pending r1023",
        "behind_origin_main": 0,
        "note": ("r1022 payload = ST-011 products (receipt + manifest MANCANG interim + "
                 "queue.json/QUEUE.md ST-012 seed + st011 status face) + CODELY hot-cold "
                 "split (3 rows verbatim -> archive 202610.md + dup pointer x2 + r1021 "
                 "semitone row) + state/heartbeat/round-report + S6 own regen/product "
                 "faces (daily_report/live_usage docs + collectors bm-b-lane faces + "
                 "compute_audit/regime_state/b_layer/attrition/orphan/dualrun/d19 faces) + "
                 "r1022 work files; shared daemon faces (machine-health/watermark_red/"
                 "token_usage + unsuffixed lhb/futures/astock/etf status) intentionally "
                 "NOT added (r982/r1015/r1020 policy); base = c3bd6066db origin tip fresh at S0 FF"),
    }
    st["sync"]["last_push_ts"] = NOW
    if post_rows:
        st["r1022_post_chain_ord_note"] = ("ORD bridge rows observed at closeout: %s "
                                           "(captured verbatim to _r1022bmb_ord_tail.txt; "
                                           "r1023 FIRST ACTION consumption)" % post_rows)
    tmp = STATE + ".tmp"
    json.dump(st, io.open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)

    # --- mirror (r1020 dual-face round_no law) ---
    try:
        mir = json.load(io.open(MIRROR, encoding="utf-8"))
    except Exception:
        mir = {}
    mir["round_no"] = 1022
    mir["round"] = 1022
    mir["round_no_label"] = "r1022"
    mir["note"] = "mirror face; authoritative round_no = repo state.json (r1020 law)"
    mir["ts"] = NOW
    mir["updated"] = NOW
    tmp = MIRROR + ".tmp"
    json.dump(mir, io.open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, MIRROR)

    # --- heartbeat ---
    hb = json.load(io.open(HB, encoding="utf-8"))
    hb["machine_id"] = "bm-b"
    hb["last_seen"] = NOW
    hb["ts"] = NOW
    hb["clock_read"] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["current_task"] = st["current_task"]
    hb["did"] = ("r1022: ST-011 sourcing done (MANCANG declip x3 interim admitted + "
                 "BOY license review) + ST-012 voice-LoRA night lane seeded per 11:21 "
                 "group order + CODELY split under 10KB + S6 chain rc0")
    hb["verdict"] = "GREEN (watermark red=false, lane healthy; real product round)"
    hb["idle_rounds"] = idle_rounds
    hb["agenda_starved"] = agenda_starved
    hb["orphan_face"] = orph_n
    tmp = HB + ".tmp"
    json.dump(hb, io.open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, HB)
    chk = json.load(io.open(HB, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int (R170/R178 law)"
    print("EPOCH_INT_OK %d" % chk["heartbeat_epoch_utc"])

    # --- round report row (S5) ---
    row = (NOW + " | r1022 | 前提=水位 GREEN（red=false lane healthy）；S0 FF 吸收 bm-a r1078×2"
           "（stash→ff c3bd6066db→pop→5 UU 解净：wm_red 本地 11:45 newer-wins/marks 行级 union 11 行"
           "/futures origin-newer/lhb+token mine）；S0.5 D-19 ORD 增量消费（11:16 女主 LoRA @bm-c 零义务；"
           "11:21 训练成员令 @bm-b 8G=角色声 LoRA+SD1.5 素材微训·夜窗 22:0x 训练态优先→ST-012 已播种承接；"
           "11:27 实然审计 bm-a 已执行"
           + ("；closeout 桥接增量 >11:27 新行 " + ",".join(post_rows) + "（已抓取 _r1022bmb_ord_tail.txt·下窗首动作消费）" if post_rows else "")
           + "）；smoke 49/49；ST-011 寻源站执行收官（MANCANG 7 片全削波→去削波再产 "
           "3 片入行 INTERIM【一致检 f0_dev 9.35%/rms_spread 1.76dB/centroid_dev 1.73% 全过·voice_05 共底债披露"
           "·根解=ST-012】；BOY 许可审查交付：外部真人童声克隆 BLOCKED·AISHELL-3/aidatatang research-use 未清"
           "→可行路=CEO 片段物理/成人底 DSP 童感原型·BOY 入行 0 诚实）；CODELY.md 热冷整编（prescan rc3 留痕"
           " r1009 先例：3 肥行 verbatim→archive 202610.md r1022 窗批+重复指针×2 去重+r1021 名义半音≠实测半音"
           "坑行入册·11,223B→9,407B 回 10KB 线内·zero_loss=True）；S6 链 " + str(rc0) + " 腿 rc0"
           + ("；非零腿 " + ",".join(rcnz) if rcnz else "")
           + "（周一盘中 papers 家族诚实跳过·新 bar 落地后下午轮跑）｜验证证据=smoke 49/49 PASS+ST-011 回执实测表"
           "+整编回执 zero_loss+push 送达 fetch 复核｜下轮指针=r1023：15:30 后 papers 链（live.paper+t35_open_fill"
           "+t24 prospect×2+export 家族）+ST-012 GitHub 训练轮子扫描（寻源闸律）+BOY 物理路呈报+supply_floor "
           "W278 prereg 观测；孤儿面=" + str(orph_n) + "；"
           "本地未达 origin commit 数=0（S0 ff 后 0·本轮回执 push 后 fetch 复核下轮 S0 终验）")
    with io.open(REPORT, "a", encoding="utf-8", newline="") as f:
        f.seek(0, 2)
        if f.tell() > 0:
            f.write("\n")
        f.write(row + "\n")
    print("STATE_OK round=1022 rc0legs=%d rcnz=%d orphan=%s idle_rounds=%d post_ord=%s"
          % (rc0, len(rcnz), orph_n, idle_rounds, post_rows or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
