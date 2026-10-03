# r622 bm-b closeout: state round_no 621->622, heartbeat, round report append
import json, time, datetime, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# ---- state.json (bm-b canonical per fleet/README.md S5) ----
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 622
st["round_no_label"] = "round 622 (bm-b)"
st["note"] = ("r622: J10 fund_family panel full-coverage fix -- _fund_family_state hardcoded 2-family list -> "
              "auto-discovery (research/FUND-*-P1.md glob + results/fund_*_p1 dirs union), DIVLOWVOL campaign "
              "first time on CEO dashboard (frozen, cells 2/2, NULLS 66/2000 live, SENS 7); DOM-equivalent "
              "live-fire acceptance PASS (real dashboard.html render JS + real dashboard_status.js via py_mini_racer, "
              "3/3 families visible); stale-takeover derive legal (bm-a hb stale 29min > 20min STALE_MIN). "
              "FUND NULLS trio burns alive after bm-a r629 ghost-claim release 15:39 (V 263/Q 164/D 66 of 2000, "
              "ETA ~10-06); DIVLOWVOL-SENS claimed by bm-a daemon 15:41. smoke 47/47; S6 33 legs rc0; "
              "S7 5/5; orders 151/151; D-19 4167b784 MATCH zero-action")
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at", "last_seen"):
    st[k] = now_iso
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-b.json ----
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hb_path, encoding="utf-8"))
try:
    import psutil
    cpu_u = psutil.cpu_percent(interval=1.0)
    vm = psutil.virtual_memory()
    free_ram = round(vm.available / 1024**3, 2)
    gpu_free = None
    try:
        import subprocess
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
        gpu_free = round(float(r.stdout.strip().splitlines()[0]) / 1024, 2)
    except Exception:
        gpu_free = hb.get("gpu_idle_vram_gb")
except Exception:
    cpu_u, free_ram, gpu_free = hb.get("cpu_util_pct"), hb.get("free_ram_gb"), hb.get("gpu_idle_vram_gb")
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["round_no"] = 622
hb["round_no_label"] = "round 622 (bm-b)"
hb["current_task"] = ("r622 done: J10 fund_family panel full coverage (DIVLOWVOL campaign now on CEO dashboard, "
                      "auto-discovery derive, DOM-equivalent acceptance PASS); FUND NULLS trio burns alive "
                      "(V 263/Q 164/D 66 of 2000, ETA ~10-06); DIVLOWVOL-SENS re-burn claimed by bm-a daemon")
hb["verdict"] = ("round 622: WM green red=false (probe window insufficient_history n=2 early-window honest); "
                 "smoke 47/47; S6 33/33 rc0 (dualrun streak 12, audit CLEAN burning-healthy); S7 5/5; "
                 "orders 151/151 zero unacked; D-19 4167b784 MATCH zero-action. "
                 "LIVE: FUND trio NULLS burns in flight (ETA ~10-06). "
                 "ARTIFACT: monitor/build_status.py fund_family auto-discovery + DIVLOWVOL on dashboard "
                 "(_r622bmb_dom_verify.py PASS). "
                 "NEXT: NULLS finish ~10-06 -> pool finalize <=48h; EM lane GM ruling <=48h")
hb["cpu_util_pct"] = cpu_u
hb["free_ram_gb"] = free_ram
hb["idle_ram_gb"] = free_ram
hb["ram_free_gb"] = free_ram
hb["ram_avail_gb"] = free_ram
if gpu_free is not None:
    hb["gpu_idle_vram_gb"] = gpu_free
    hb["gpu_idle_vram_mb"] = int(gpu_free * 1024)
    hb["gpu_free_vram_gb"] = gpu_free
    hb["gpu_free_vram_mb"] = int(gpu_free * 1024)
    hb["gpu_vram_free"] = gpu_free
hb["ts"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
json.dump(hb, open(hb_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-verify: epoch int + clock T-sep (smoke F7 face)
chk = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"].split("+")[0], "clock_read must be T-sep ISO"
print("heartbeat self-verify PASS: epoch int =", chk["heartbeat_epoch_utc"], "clock =", chk["clock_read"])

# ---- round report append (byte-append: file has legacy non-UTF8 bytes, never rewrite) ----
line = (
    "2026-10-03T15:57+08:00 | r622 bm-b (dept:\u5de5\u7a0b\u00b7J10 \u9762\u677f\u65cf\u5168\u666f\u9762\u8f6e) | "
    "[watermark verdict: \u7eff red=false lane=healthy; probe insufficient_history n=2 \u7a97\u65e9\u671f\u5408\u6cd5; "
    "audit CLEAN burning-healthy; dualrun ZERO-DRIFT streak 12] | "
    "\u5f53\u524d\u6d3b: FUND \u4e09\u65cf NULLS \u70e7\u5f55\u5728\u98de VALUE 263/QUALITY 164/DIVLOWVOL 66 of 2000 @15:4x"
    "\uff08bm-a r629 15:39 ghost-claim \u91ca\u653e\u540e daemon \u590d\u71c3\u00b7ETA ~10-06\uff09+ DIVLOWVOL-SENS bm-a daemon \u5df2\u9886 15:41"
    " + moneyflow IC \u53c2\u8003\u6279\u5019\u9762\u677f\uff08EM \u8f66\u9053 GM \u88c1\u51b3\u7a97\uff09 | "
    "\u6700\u8fd1\u5b9e\u7269: J10 \u57fa\u672c\u9762\u65cf\u6218\u5f79\u9762\u677f\u65cf\u5168\u666f\u4fee\u590d\u2014\u2014"
    "monitor/build_status.py _fund_family_state \u786c\u7f16\u7801\u4e24\u65cf\u6539\u81ea\u52a8\u53d1\u73b0"
    "\uff08research/FUND-*-P1.md glob + results/fund_*_p1 \u76ee\u5f55\u5e76\u96c6\uff09\u2192 DIVLOWVOL \u6218\u5f79\u9996\u6b21\u4e0a\u76d8 CEO \u53ef\u89c1"
    "\uff08frozen\u00b7\u5224\u683c 2/2\u00b7NULLS 66 \u5b9e\u65f6\u00b7SENS 7\u00b7\u6c60 claim \u9762\uff09\u00b7"
    "DOM \u7b49\u4ef7\u5b9e\u5f39\u9a8c\u6536 PASS\uff08dashboard.html \u771f\u6e32\u67d3 JS + \u771f\u6570\u636e py_mini_racer \u6267\u884c\u4e09\u65cf\u5168\u6e32\u67d3\uff09\u00b7"
    "stale-takeover derive \u5408\u6cd5\uff08bm-a hb \u964c 29min>20min STALE_MIN \u5f8b\uff09 | "
    "\u4e0b\u4e2a\u91cc\u7a0b\u7891: NULLS \u70e7\u6bd5\uff08~10-06\uff09\u2192\u6c60\u7ffb\u9762 finalize\uff08\u7a97\u226448h\uff09"
    "\u00b7\u4e09\u65cf\u5224\u51b3\u5165 family_verdicts \u9762\u677f\uff1bEM \u8f66\u9053 GM \u88c1\u51b3\u5019\u7968\uff08\u7a97\u226448h\uff09 | "
    "\u672c\u8f6e\u505a\u4e86: S0-1 \u951a\u5b9a bm-b; S0 churn-absorb x2+\u5e72\u51c0 rebase\uff08f184c1a\u2192a88bb73\uff09; "
    "S0.5 \u4ee4\u53cc\u626b 151/151 \u96f6\u672a\u56de\u6267+D-19 SHA 4167b784 MATCH \u96f6\u52a8\u4f5c\uff08blobless clone \u65b0\u9c9c\u8bfb\uff09; "
    "S1 smoke 47/47; S3 \u677f\u7a7a+\u6c60\u5065\u5eb7\u5224\u65e0\u65b0\u6ce2\uff08TRIAL_LABOR \u4e0d\u89e6\u53d1\uff09; "
    "\u5f00\u53d1\u961f\u5217\u6838\u9a8c=J12/J10/J13/J18b/Optuna/town \u5bf9\u9f50\u5168\u5df2\u4ea4\u4ed8\uff08J18b data.update 渲染\u5728\u4f4d\u5b9e\u8bc1\uff09"
    "\u2192 \u9009 J10 \u65cf\u5168\u666f\u7f3a\u53e3\u6536\u53e3; S6 33 \u817f rc0\uff08\u7eb8\u76d8\u65cf\u9ec4\u91d1\u5468\u65e0\u65b0 bar \u95e8\u8df3\uff09; "
    "S7 5/5\uff08loop pin=2 no-op+\u5176\u4ed6 watchdog \u5e42\u7b49\u91cd\u5efa+\u53cc\u722a\u88c5+attrition CLEAN+state 621\u2192622\uff09; "
    "inbox \u4e24\u4ef6=\u672c\u673a standing \u56de\u6267\u5019 GM \u672a\u89c1\u65b0\u4ee4 | "
    "\u9a8c\u8bc1\u8bc1\u636e: results/_r622bmb_dom_verify.py VERDICT:PASS \u4e09\u65cf\u53ef\u89c1+_r622bmb_dom_verdict.txt \u6e32\u67d3\u884c"
    "+_r622bmb_ff_check.txt \u4e09\u65cf\u8bfb\u6570+build_status \u518d\u751f rc0 3 families+S6 log+state round_no=622 \u81ea\u8bc1 | "
    "\u4e0b\u8f6e\u6307\u9488: \u2460\u70e7\u5f55 harvest+\u6c60\u7ffb\u9762\u5224\u5b9a\uff08\u4e09\u65cf NULLS \u5747\u5230 2000 \u65f6\uff09\u2461EM \u8f66\u9053 GM \u88c1\u51b3\u6d88\u8d39"
    "\u2462\u672c\u5730\u672a\u8fbe origin commit \u6570=0\uff08push \u540e\u81ea\u8bc1\u8865\u8bb0\uff09\u2463\u4e0b\u8f6e 5x=r625 HANDOVER \u6838\u5bf9"
)
with open(os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md"), "ab") as f:
    f.write(("\n" + line + "\n").encode("utf-8"))
print("round report appended:", len(line), "chars")
print("closeout done r622")
