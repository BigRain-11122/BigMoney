import json, os, time, datetime

now = datetime.datetime.now().astimezone()
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+" if now.utcoffset() >= datetime.timedelta(0) else "-") + format(abs(int(now.utcoffset().total_seconds()) // 3600), "02d") + ":" + format(abs(int(now.utcoffset().total_seconds()) % 3600 // 60), "02d")
now_plain = now.strftime("%Y-%m-%d %H:%M")

# 1. CODELY.md pit entry (append, UTF-8)
pit = ("- [2026-10-03 13:5x r625 bm-a] \u6570\u636e\u53e3\u5f84\u95f8\u4e09\u5751\u590d\u5408\uff08divlowvol off-caliber containment \u5b9e\u5f39\u00b7r615 \u65cf\u6269\u5c55\uff09\uff1a"
       "\u2460\u53e3\u5f84\u95f8\u6309\u6570\u636e\u9762\u5168\u8986\u76d6\u2014\u2014off-caliber \u7f13\u5b58\uff08p1c_stock 688/689 amt 100x\uff09\u7684\u4e00\u5207\u6d88\u8d39 runner \u5168\u90e8\u6c60 sig \u90fd\u8981\u843d crash_fuse keep-block"
       "\uff08\u672c\u7a97\u521d\u7248\u53ea\u843d\u5f53\u7a97\u70e7\u7684 nulls/sens\uff0c\u6f0f cell-x1/x2 done \u9762\u4e0e\u91cd\u70e7\u9762\u2014\u2014\u8865\u5168 4 sig \u540e 13:48 \u53cc tick REFUSE \u5b9e\u8bc1\uff09\uff1b"
       "fuse \u62e6\u622a\u5224\u636e=sig+code_sha256 \u5339\u914d\u5373\u62d2\u3001\u4e0d\u770b count\u2192count=0 \u8bda\u5b9e\u6761\u76ee\u5408\u6cd5\uff08\u6ce8\u8bb0\u5199\u660e data-caliber \u975e crash-loop\uff09\uff1b\u95f8\u968f runner hash \u6f02\u79fb\u81ea\u52a8\u6e05=r617 \u5df2\u77e5\u8fb9\u754c\u3002"
       "\u2461\u843d\u95f8\u4e0e daemon tick \u7ade\u6001\u2014\u2014\u843d\u95f8\u524d\u5fc5\u67e5\u5728\u98de\u70e7\uff08\u672c\u7a97 13:34 NULLS/13:38 SENS \u4e24\u6b21 launch \u90fd\u843d\u5728\u95f8\u524d 1-2 \u5206\u949f\uff0c\u6d3b\u70e7\u8981\u624b\u5de5\u6740+\u5b64\u513f pool \u5de5\u4eba\u6e05\u70b9\uff08r614 \u6e05\u70b9\u5f8b\uff09\uff1b"
       "PS \u6740\u5faa\u73af\u52ff\u63a5 Select -First N\u2014\u2014\u7ba1\u9053\u65e9\u505c\u4e2d\u6b62\u4e0a\u6e38 foreach=48 \u5b64\u513f\u53ea\u6740 3 \u7684\u5b9e\u5f39\uff09\u3002"
       "\u2462\u6d3b\u8fdb\u7a0b stderr \u9501\u6321 cherry-pick/checkout \u8def\u5f84\uff08croc camping pid \u6301 _recv2.err \u53e5\u67c4\uff1acherry-pick abort\u2192\u6740\u8fdb\u7a0b\u89e3\u9501\u2192\u540c\u7801\u91cd\u542f camping\uff08\u5bf9\u7aef\u96f6\u52a8\u4f5c\uff09\u2192stderr \u6362\u65b0\u6587\u4ef6\u3002"
       "How to apply\uff1a\u89c1 off-caliber \u6279\u5148\u67e5\u6570\u636e\u9762\u6d88\u8d39\u5168\u96c6\u518d\u843d\u95f8\uff1b\u6740\u70e7\u6279\u7236\u8fdb\u7a0b\u540e\u5fc5\u6e05 multiprocessing \u5b64\u513f\uff1b\u88ab\u9501\u8def\u5f84\u7684 git \u64cd\u4f5c=\u6740\u6301\u9501\u8fdb\u7a0b\u6362\u6587\u4ef6\u540d\uff0ccamping \u7c7b\u53ef\u91cd\u542f\u5373\u6062\u590d\u3002\n")
with open("CODELY.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(pit)

# 2. round report line
rr = (f"{now_iso} | r625 | S0: r624 estate absorbed via rebase fake-refuse->quit->cherry-pick(locked)->construct-merge "
      f"(8 UU: 6 json newer-wins + 2 jsonl line-union r294), pushed; T-156 recv re-armed pid 67588 (same code/relay, "
      f"stderr ->_r625bma_croc_recv3.err); DIVLOWVOL off-caliber full containment: 2 burns killed (13:34 NULLS pid60524 "
      f"/ 13:38 SENS pid23136, zero product writes), 48 orphan pool workers reaped, crash-fuse keep-block all 4 sigs "
      f"(count=0 honest data-caliber gate, r615 family), live REFUSE evidence 13:48:03+13:48:40, x1/x2 cell results "
      f"quarantined results/fund_divlowvol_p1/OFF_CALIBER_NOTE.md, MSG-1351 sent to bm-b; 6 chain tasks re-registered "
      f"(daemon died 13:44-13:46 window, cause unknown, revived+verified); S6: dualrun rc0 ZERO-DRIFT / audit rc0 "
      f"(FLAG:cap_violation pre-kill window 76py@100%) / daily rc0 / regime rc0 ORANGE / scorecard rc0 27.4s / "
      f"d-score rc0 / build_status rc0 / token rc0 | smoke 47/47 | next: T-156 pairing watch -> post-verify "
      f"re-burn divlowvol x1/x2 + unblock, bm-b heartbeat ask pending | local-not-on-origin=0\n")
with open("round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(rr)

# 3. state round_no
sp = "state-bm-a.json"
d = json.load(open(sp, encoding="utf-8"))
d["round_no"] = 625
tmp = sp + ".tmp"
json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
os.replace(tmp, sp)
print("state round_no -> 625")

# 4. heartbeat
import psutil
hb = "fleet/machines/bm-a.json"
h = json.load(open(hb, encoding="utf-8"))
h["last_seen"] = now_iso
h["current_task"] = ("r625: DIVLOWVOL off-caliber containment complete (4-sig fuse gate, x1/x2 quarantined, "
                     "MSG-1351 to bm-b); T-156 recv camping pid 67588 waiting-for-sender; 6 chain tasks revived")
h["cpu_pct"] = round(psutil.cpu_percent(interval=1), 1)
h["free_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
h["verdict"] = ("py_low_board_clear (legal idle: FUND-QUALITY+DIVLOWVOL = transfer-gated fuse keep-blocks "
                "awaiting T-156 verify; NULLS 2000-draw = bm-b in-flight)")
epoch = int(time.time())
assert isinstance(epoch, int)
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
tmp = hb + ".tmp"
json.dump(h, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
os.replace(tmp, hb)
chk = json.load(open(hb, encoding="utf-8"))
print("heartbeat epoch type:", type(chk["heartbeat_epoch_utc"]).__name__, "| clock:", chk["clock_read"], "| cpu:", chk["cpu_pct"], "| ram:", chk["free_ram_gb"])
